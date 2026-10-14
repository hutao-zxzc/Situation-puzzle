"""
review_service.py - 对局复盘服务
===============================
独立于 llm_service 的复盘模块，提供：
1. AI 智能复盘（调用 LLM 生成深度分析）
2. 本地复盘（不依赖 LLM，纯逻辑生成）
3. 多种复盘格式（简洁 / 详细 / 统计）

使用方式：
    from review_service import generate_review
    review = await generate_review(...)
"""

import json
import re
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class ReviewFormat(str, Enum):
    """复盘输出格式"""
    FULL = "full"          # 完整复盘（含亮点、盲区、评分）
    SIMPLE = "simple"      # 简洁复盘（仅汤底 + 统计）
    STATS = "stats"        # 纯统计（无 LLM 调用，零延迟）


@dataclass
class GameReview:
    """复盘结果数据结构"""
    total_rounds: int
    hints_used: int
    status: str                    # won / lost / ended / revealed
    title: str                     # 谜题标题
    soup_surface: str              # 汤面
    soup_base: str                 # 汤底
    highlights: str                # 推理亮点
    blind_spots: str               # 盲区分析
    verdict: str                   # 总体评价
    efficiency_score: int          # 效率评分 0-100
    key_details_found: List[str]   # 已发现的关键线索
    key_details_missed: List[str]  # 遗漏的关键线索
    reasoning_path: List[Dict[str, str]]  # 推理路径摘要

    def to_dict(self) -> dict:
        """转为可 JSON 序列化的字典"""
        return {
            "total_rounds": self.total_rounds,
            "hints_used": self.hints_used,
            "status": self.status,
            "title": self.title,
            "soup_surface": self.soup_surface,
            "soup_base": self.soup_base,
            "highlights": self.highlights,
            "blind_spots": self.blind_spots,
            "verdict": self.verdict,
            "efficiency_score": self.efficiency_score,
            "key_details_found": self.key_details_found,
            "key_details_missed": self.key_details_missed,
            "reasoning_path": self.reasoning_path,
        }


# ============== 本地复盘逻辑（零 LLM 依赖）==============

_STOPWORDS = {
    "的", "了", "是", "在", "和", "有", "被", "把", "给", "就",
    "都", "而", "及", "与", "或", "一个", "没有", "不是", "这个",
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "他", "她", "它", "们", "吗", "呢", "啊", "吧", "么",
}

_SPECIAL_SINGLE = set("男女死血刀药毒火水酒绳锁钥匙钱")  # 保留的单字


def _extract_keywords(text: str) -> List[str]:
    """从文本中提取关键词用于匹配"""
    text = text.lower()
    tokens = re.findall(r'[\u4e00-\u9fff]{1,4}|[a-z]+', text)

    keywords = []
    for t in tokens:
        if len(t) >= 2 and t not in _STOPWORDS:
            keywords.append(t)
        elif len(t) == 1 and t in _SPECIAL_SINGLE and t not in _STOPWORDS:
            keywords.append(t)

    seen = set()
    result = []
    for kw in keywords:
        if kw not in seen and len(result) < 6:
            seen.add(kw)
            result.append(kw)
    return result


def _local_detect_found_clues(
    history: List[Dict[str, Any]],
    key_details: List[str]
) -> tuple[List[str], List[str]]:
    """
    基于关键词匹配，检测玩家已发现 / 遗漏的关键线索。
    不调用 LLM，纯本地逻辑。
    """
    all_text = " ".join([
        f"{h.get('question', '')} {h.get('answer', '')}"
        for h in history
    ]).lower()

    found = []
    missed = []
    for clue in key_details:
        keywords = _extract_keywords(clue)
        if any(kw in all_text for kw in keywords):
            found.append(clue)
        else:
            missed.append(clue)
    return found, missed


def _local_build_reasoning_path(
    history: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """构建推理路径摘要"""
    path = []
    for i, h in enumerate(history):
        q = h.get("question", "")
        a = h.get("answer", "")

        if q.startswith("【提示】") or q == "【提示】":
            path.append({
                "round": str(i + 1),
                "type": "hint",
                "summary": q[:30] + "..." if len(q) > 30 else q,
            })
            continue
        if q.startswith("【我猜到了】"):
            path.append({
                "round": str(i + 1),
                "type": "guess",
                "summary": q[:30] + "..." if len(q) > 30 else q,
            })
            continue

        qtype = "explore"
        if "是" in a:
            qtype = "confirm"
        elif "否" in a:
            qtype = "eliminate"
        elif "无关" in a or "部分" in a:
            qtype = "explore"

        path.append({
            "round": str(i + 1),
            "type": qtype,
            "summary": q[:30] + "..." if len(q) > 30 else q,
        })
    return path


def _calc_efficiency(
    rounds: int, hints: int, found: int, total_clues: int, status: str
) -> int:
    """计算效率评分 0-100"""
    score = 50

    if total_clues > 0:
        score += int((found / total_clues) * 25)
    else:
        score += 15

    if rounds <= 10:
        score += 15
    elif rounds <= 20:
        score += 8
    elif rounds <= 30:
        score += 3

    score += max(0, (3 - hints) * 3)

    if status == "won":
        score += 10
    elif status in ("lost",):
        score -= 10

    return max(0, min(100, score))


def _generate_highlights(
    found: List[str], history: List[Dict[str, Any]], status: str
) -> str:
    """生成推理亮点文本"""
    if status == "won":
        parts = ["🎉 恭喜猜中真相！"]
    else:
        parts = ["👏 积极参与了推理过程。"]

    if found:
        parts.append(f"成功触及了 {len(found)} 个关键线索。")
        if len(found) >= 2:
            parts.append("对核心信息的抓取相当敏锐。")
    else:
        parts.append("尝试了多种推理方向。")

    yes_count = sum(1 for h in history if "是" in h.get("answer", ""))
    if yes_count > 0:
        parts.append(f"通过 {yes_count} 次确认性问题逐步缩小了范围。")

    return " ".join(parts)


def _generate_blind_spots(
    missed: List[str], history: List[Dict[str, Any]]
) -> str:
    """生成盲区分析文本"""
    if not missed:
        return "✨ 关键线索全部触及，没有明显盲区！"

    parts = [f"遗漏了 {len(missed)} 个关键线索。"]

    unrelated_count = sum(1 for h in history if "无关" in h.get("answer", ""))
    no_count = sum(1 for h in history if "否" in h.get("answer", ""))

    if unrelated_count > 3:
        parts.append("部分提问方向偏离了案件核心，建议更聚焦汤面细节。")
    elif no_count > 5:
        parts.append("多次得到否定回答，说明排除了不少错误假设，但可能绕了些弯路。")
    else:
        parts.append("可以尝试从不同角度（时间、动机、物品）展开提问。")

    return " ".join(parts)


def _generate_verdict(
    status: str, efficiency: int, rounds: int, missed: int
) -> str:
    """生成总体评价"""
    if status == "won":
        if efficiency >= 85:
            return "🏆 完美推理！思维缜密，效率极高。"
        elif efficiency >= 60:
            return "✅ 推理成功！逻辑清晰，再接再厉。"
        else:
            return "✅ 猜中了！虽然过程曲折，但坚持就是胜利。"
    elif status == "lost":
        if missed > 2:
            return "💪 关键线索发现不足，下次更仔细分析汤面细节。"
        else:
            return "💪 已经很接近了，差点就能解开谜底！"
    else:
        if efficiency >= 70:
            return "👍 推理方向正确，放弃有点可惜。"
        else:
            return "🔄 复盘完毕，吸取经验再来一局吧！"


def _local_generate_review(
    soup_surface: str,
    soup_base: str,
    key_details: List[str],
    history: List[Dict[str, Any]],
    hints_used: int,
    status: str,
    title: str,
) -> GameReview:
    """纯本地逻辑生成复盘，不调用 LLM。"""
    total_rounds = len(history)
    found, missed = _local_detect_found_clues(history, key_details)
    reasoning_path = _local_build_reasoning_path(history)
    efficiency = _calc_efficiency(total_rounds, hints_used, len(found), len(key_details), status)
    highlights = _generate_highlights(found, history, status)
    blind_spots = _generate_blind_spots(missed, history)
    verdict = _generate_verdict(status, efficiency, total_rounds, len(missed))

    return GameReview(
        total_rounds=total_rounds,
        hints_used=hints_used,
        status=status,
        title=title,
        soup_surface=soup_surface,
        soup_base=soup_base,
        highlights=highlights,
        blind_spots=blind_spots,
        verdict=verdict,
        efficiency_score=efficiency,
        key_details_found=found,
        key_details_missed=missed,
        reasoning_path=reasoning_path,
    )


# ============== LLM 复盘（增强版）==============

async def _llm_generate_review(
    soup_surface: str,
    soup_base: str,
    key_details: List[str],
    history: List[Dict[str, Any]],
    hints_used: int,
    status: str,
    title: str,
    llm_config: dict,
) -> Optional[GameReview]:
    """
    调用 LLM 生成更丰富的复盘。如果 LLM 调用失败返回 None，上层会 fallback 到本地复盘。
    """
    history_text = "\n".join(
        [f"第{i+1}轮: {h.get('question','')} → {h.get('answer','')}" for i, h in enumerate(history)]
    )

    prompt = f"""你是海龟汤游戏的复盘分析师。请对玩家的游戏过程进行深度复盘。

【汤面】
{soup_surface}

【汤底】
{soup_base}

【关键线索】
{chr(10).join(f"- {k}" for k in key_details)}

【游戏结果】
状态: {status}
消耗提示: {hints_used} 次

【完整问答记录】
{history_text}

请严格按照以下 JSON 格式输出（不要加 markdown 代码块标记，直接输出 JSON）：
{{
  "total_rounds": {len(history)},
  "highlights": "推理亮点：总结玩家提出的最有价值的问题和推理方向（2-3句话）",
  "blind_spots": "盲区分析：指出玩家忽略的线索或走入的误区（2-3句话）",
  "verdict": "总体评价：对玩家推理能力的简短评价（1-2句话）",
  "efficiency_score": 0到100的效率评分数字,
  "key_details_found": ["已发现的关键线索1", "线索2"],
  "key_details_missed": ["遗漏的关键线索1", "线索2"]
}}

注意：
1. highlights 要具体，指出哪些提问体现了好的推理
2. blind_spots 要指出玩家漏掉了哪些关键线索
3. key_details_found 和 key_details_missed 必须来自上面的【关键线索】列表
4. 语气友好鼓励，不要过于批评
5. 只输出 JSON，不要任何其他文字"""

    api_key = llm_config.get("api_key", "")
    base_url = llm_config.get("base_url", "https://api.openai.com/v1")
    model = llm_config.get("model", "gpt-3.5-turbo")

    if not api_key:
        return None

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个海龟汤游戏复盘分析师，只输出纯 JSON，不加任何 markdown 标记。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)

            reasoning_path = _local_build_reasoning_path(history)

            found = [c for c in result.get("key_details_found", []) if c in key_details]
            missed = [c for c in result.get("key_details_missed", []) if c in key_details]

            covered = set(found) | set(missed)
            for clue in key_details:
                if clue not in covered:
                    _f, _m = _local_detect_found_clues(history, [clue])
                    if _m:
                        missed.append(clue)
                    else:
                        found.append(clue)

            return GameReview(
                total_rounds=len(history),
                hints_used=hints_used,
                status=status,
                title=title,
                soup_surface=soup_surface,
                soup_base=soup_base,
                highlights=result.get("highlights", "推理过程积极。"),
                blind_spots=result.get("blind_spots", "部分线索未能及时发现。"),
                verdict=result.get("verdict", "继续努力！"),
                efficiency_score=result.get("efficiency_score", 50),
                key_details_found=found,
                key_details_missed=missed,
                reasoning_path=reasoning_path,
            )
    except Exception:
        return None


# ============== 统一入口 ==============

async def generate_game_review(
    soup_surface: str,
    soup_base: str,
    key_details: List[str],
    history: List[Dict[str, Any]],
    hints_used: int,
    status: str,
    title: str,
    llm_config: Optional[dict] = None,
    format: ReviewFormat = ReviewFormat.FULL,
) -> GameReview:
    """
    生成对局复盘的主入口。
    """
    if format == ReviewFormat.STATS:
        return _local_generate_review(
            soup_surface, soup_base, key_details, history,
            hints_used, status, title
        )

    if llm_config and llm_config.get("api_key"):
        llm_review = await _llm_generate_review(
            soup_surface, soup_base, key_details, history,
            hints_used, status, title, llm_config
        )
        if llm_review is not None:
            if format == ReviewFormat.SIMPLE:
                llm_review.highlights = ""
                llm_review.blind_spots = ""
                llm_review.reasoning_path = []
            return llm_review

    return _local_generate_review(
        soup_surface, soup_base, key_details, history,
        hints_used, status, title
    )


# ============== 兼容旧接口 ==============

async def generate_review(
    soup_surface: str,
    soup_base: str,
    key_details: list,
    history: list,
    hints_used: int,
    status: str,
    llm_config: dict,
) -> dict:
    """
    兼容旧版 llm_service.generate_review 的接口。
    返回与原来相同的 dict 结构，方便 main.py 无缝替换。
    """
    review = await generate_game_review(
        soup_surface=soup_surface,
        soup_base=soup_base,
        key_details=key_details,
        history=history,
        hints_used=hints_used,
        status=status,
        title="",
        llm_config=llm_config,
        format=ReviewFormat.FULL,
    )
    d = review.to_dict()
    return {
        "total_rounds": d["total_rounds"],
        "hints_used": d["hints_used"],
        "highlights": d["highlights"],
        "blind_spots": d["blind_spots"],
        "soup_base": d["soup_base"],
        "verdict": d["verdict"],
        "status": d["status"],
        "efficiency_score": d["efficiency_score"],
        "key_details_found": d["key_details_found"],
        "key_details_missed": d["key_details_missed"],
        "reasoning_path": d["reasoning_path"],
    }
