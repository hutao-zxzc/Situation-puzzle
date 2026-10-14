import httpx
from typing import Optional

class LLMService:
    """LLM 服务 - 每次请求传入配置"""

    def _is_reasoning_model(self, model: str) -> bool:
        """判断是否为推理模型（思考过程消耗大量 token）"""
        m = model.lower()
        return any(k in m for k in ("k2-", "k2_", "k2.6", "deepseek-r", "o1", "o3"))

    async def _chat(self, messages: list, llm_config: dict, temperature: float = 0.7) -> str:
        """通用聊天接口"""
        api_key = llm_config.get("api_key", "").strip().replace("\n", "").replace("\r", "")
        base_url = llm_config.get("base_url", "https://api.moonshot.cn/v1").rstrip("/")
        model = llm_config.get("model", "kimi-latest")

        # 安全调试日志（不暴露 key）
        print(f"[LLM] base_url={base_url}, model={model}, key_len={len(api_key)}")

        if not api_key:
            raise ValueError("API Key 未设置，请点击右上角 ⚙️ 配置")

        is_reasoning = self._is_reasoning_model(model)

        # 推理模型只支持 temperature=1，且需要更大 max_tokens
        if is_reasoning:
            temperature = 1.0
            max_tokens = 4096
        else:
            # 普通模型：temperature 可调，token 需求小
            max_tokens = 512

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        # 推理模型：在 user 消息中强制要求直接回答
        if is_reasoning:
            for m in reversed(messages):
                if m.get("role") == "user":
                    m["content"] = m["content"] + "\n\n【禁止思考过程，直接输出最终答案，不要解释】"
                    break

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            if resp.status_code == 404:
                try:
                    err_detail = resp.json()
                except:
                    err_detail = resp.text[:200]
                raise ValueError(
                    f"LLM API 返回 404。\n"
                    f"请求URL: {base_url}/chat/completions\n"
                    f"模型: {model}\n"
                    f"错误详情: {err_detail}\n"
                    f"可能原因：\n"
                    f"1. Base URL 错误\n"
                    f"2. 模型名称错误\n"
                    f"3. API Key 对应的账户未开通该模型"
                )
            elif resp.status_code == 401:
                raise ValueError(
                    f"API Key 认证失败（401）。\n"
                    f"请确认 API Key 正确且未过期。"
                )
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]
            content = choice.get("content", "").strip()

            # 推理模型可能把答案放在 reasoning_content
            if not content and "reasoning_content" in choice:
                reasoning = choice["reasoning_content"].strip()
                lines = [l.strip() for l in reasoning.split('\n') if l.strip()]
                if lines:
                    content = lines[-1]

            if not content:
                raise ValueError("LLM 返回空内容，请检查模型配置或重试")

            return content

    async def generate_puzzle(self, llm_config: dict) -> dict:
        """生成新的海龟汤题目"""
        system_prompt = """你是海龟汤游戏出题专家。请生成一个经典的海龟汤谜题。

要求：
1. 汤面要简短、诡异、引人入胜（100字以内）
2. 汤底要合理、有反转、出人意料（200字以内）
3. 提供3-5个关键细节

【极其重要】直接输出严格JSON，不要markdown代码块，不要思考过程：
{"title":"题目名称","soup_surface":"汤面内容...","soup_base":"汤底真相...","key_details":["关键细节1","关键细节2","关键细节3"]}"""

        content = await self._chat(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": "请生成一个新的海龟汤谜题，返回严格JSON格式。"}],
            llm_config=llm_config,
            temperature=0.9 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0
        )

        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        puzzle = json.loads(content)
        return puzzle

    async def judge_question(self, soup_surface: str, soup_base: str, key_details: list,
                           history: list, question: str, llm_config: dict) -> dict:
        """判定玩家提问——严格模式：只回答是/否/无关/部分相关"""
        history_text = "\n".join(
            f"  之前第{i+1}轮: 问「{h['question']}」→ 答「{h['answer']}」(判定：{h['type']})" 
            for i, h in enumerate(history)
        ) or "（尚无历史问答）"

        system_prompt = f"""你是海龟汤游戏裁判。你需要判定的是【当前玩家提问】，历史记录仅供参考。

【汤面】{soup_surface}
【汤底】{soup_base}
【关键细节】{', '.join(key_details)}

【历史问答记录（仅供参考，不要复制之前的答案）】
{history_text}

【判定规则】
- "是"=当前问题描述符合汤底事实
- "否"=当前问题与汤底事实矛盾
- "无关"=当前问题与汤底无直接关联
- "部分相关"=当前问题部分正确但不完全准确

【极其重要】你的回答必须是以下严格JSON格式，禁止任何额外文字、禁止思考过程、禁止解释：
{{"type":"是","answer":"最多10字","reasoning":"最多15字"}}
或
{{"type":"否","answer":"最多10字","reasoning":"最多15字"}}
或
{{"type":"无关","answer":"最多10字","reasoning":"最多15字"}}
或
{{"type":"部分相关","answer":"最多10字","reasoning":"最多15字"}}
"""

        content = await self._chat(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"【当前需要你判定的玩家提问】：{question}\n\n请严格根据汤底判断这个新问题，不要重复之前问题的答案。"}],
            llm_config=llm_config,
            temperature=0.5 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0
        )

        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # 兜底：从文本中提取关键词
            text = content.lower()
            if "是" in text and "否" not in text and "无关" not in text:
                result = {"type": "是", "answer": "是的", "reasoning": "符合汤底"}
            elif "否" in text:
                result = {"type": "否", "answer": "不是", "reasoning": "与汤底矛盾"}
            elif "无关" in text:
                result = {"type": "无关", "answer": "无关", "reasoning": "无直接关联"}
            elif "部分" in text:
                result = {"type": "部分相关", "answer": "部分正确", "reasoning": "部分符合"}
            else:
                result = {"type": "无关", "answer": "无法判定", "reasoning": "请重新提问"}

        return result

    async def judge_guess(self, soup_surface: str, soup_base: str, guess: str, llm_config: dict) -> dict:
        """判定玩家猜真相"""
        system_prompt = f"""你是海龟汤游戏裁判。玩家尝试猜测汤底真相。

【汤面】{soup_surface}
【汤底】{soup_base}

请判断玩家的猜测是否正确。如果玩家猜到了核心真相（关键情节正确），即使细节有偏差也算正确。

【极其重要】直接输出严格JSON，禁止任何额外文字、禁止思考过程、禁止解释：
{{"correct":true,"feedback":"最多20字反馈"}}
或
{{"correct":false,"feedback":"最多20字反馈"}}"""

        content = await self._chat(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": f"玩家猜测：{guess}"}],
            llm_config=llm_config,
            temperature=0.3 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0
        )

        import json
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        return result

    async def generate_hint(self, soup_surface: str, soup_base: str, key_details: list,
                            history: list, used_hints: int, llm_config: dict) -> str:
        """生成提示——模糊线索不泄底，但必须紧扣当前汤面"""
        history_text = "\n".join(
            f"Q: {h['question']} -> A: {h['answer']} ({h['type']})" for h in history
        ) or "（无）"

        # 根据已用次数选择提示方向
        hint_levels = [
            "暗示汤面中某个被忽视的具体物件或场景细节（不透露其真实作用）",
            "暗示某个角色的异常行为或心理状态（不点明动机）",
            "暗示时间、空间或因果关系中隐藏的矛盾点（不揭露真相）"
        ]
        level = hint_levels[min(used_hints, len(hint_levels) - 1)]

        system_prompt = f"""你是海龟汤游戏的提示生成器。请严格基于以下汤面内容，生成一条有针对性的提示。

【汤面原文】{soup_surface}
【汤底（仅你可见，绝对不可泄露）】{soup_base}
【关键线索】{', '.join(key_details)}
【已进行的问答】
{history_text}

【当前提示要求】{level}

【生成规则】
1. 提示必须紧扣上面【汤面原文】中出现的具体人、物、场景或事件，不能泛泛而谈
2. 提示应该指向汤底中的某个真实元素，但不能直接说出来
3. 禁止输出"仔细观察""注意细节""换个角度"这类万能套话
4. 只输出1句话的提示内容，不要任何前缀"""

        try:
            hint = await self._chat(
                messages=[
                    {"role": "system", "content": "你是海龟汤提示生成器。提示必须基于当前汤面的具体内容，不能是通用建议。只输出1句话。"},
                    {"role": "user", "content": system_prompt}
                ],
                llm_config=llm_config,
                temperature=0.6 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0,
            )
            # 清理可能的前缀
            hint = hint.strip().strip('"').strip("'").strip('【】')
            if hint.startswith('提示：') or hint.startswith('💡'):
                hint = hint.split('：', 1)[-1].strip()
            return hint
        except Exception:
            # fallback 也基于汤面关键词生成
            import re
            nouns = re.findall(r'[\u4e00-\u9fa5]{2,4}', soup_surface)
            # 去掉常见停用词
            stop = ['一个', '一只', '一条', '一天', '晚上', '白天', '突然', '发现', '然后', '但是', '可是']
            keywords = [w for w in nouns if w not in stop and len(w) >= 2][:3]
            keyword = keywords[0] if keywords else "场景"
            fallbacks = [
                f"那个{keyword}似乎隐藏着比表面看起来更复杂的含义...",
                f"当所有人都在关注{keyword}时，真正重要的东西可能被忽略了...",
                f"重新审视{keyword}出现前后的时间线，也许顺序并不是你以为的那样..."
            ]
            return fallbacks[min(used_hints, len(fallbacks) - 1)]

    async def generate_review(self, soup_surface: str, soup_base: str, key_details: list,
                              history: list, hints_used: int, status: str, llm_config: dict) -> dict:
        """AI 生成复盘分析"""
        history_text = "\n".join(
            f"第{i+1}轮: {h['question']} -> {h['answer']} ({h['type']})" for i, h in enumerate(history)
        ) or "（无问答记录）"

        system_prompt = f"""你是海龟汤游戏的复盘分析师。请对玩家的游戏过程进行复盘。

【汤面】{soup_surface}
【汤底】{soup_base}
【关键线索】{', '.join(key_details)}
【游戏结果】{status}
【消耗提示数】{hints_used}
【完整问答记录】
{history_text}

请用以下 JSON 格式输出复盘：
{{
  "total_rounds": 总回合数（数字）,
  "hints_used": 消耗提示数（数字）,
  "highlights": "推理亮点：总结玩家提出的最有价值的问题和推理方向（2-3句话）",
  "blind_spots": "盲区分析：指出玩家忽略的线索或走入的误区（2-3句话）",
  "soup_base": "完整汤底（原文）",
  "verdict": "总体评价：对玩家推理能力的简短评价"
}}

注意：
1. highlights 要具体，指出哪些提问体现了好的推理
2. blind_spots 要指出玩家漏掉了哪些关键线索
3. 语气友好鼓励，不要过于批评
4. 只输出 JSON，禁止任何额外文字"""

        try:
            content = await self._chat(
                messages=[{"role": "system", "content": "你是一个游戏复盘分析师，只输出 JSON 格式的复盘结果。"},
                          {"role": "user", "content": system_prompt}],
                llm_config=llm_config,
                temperature=0.7 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0,
            )
            import json
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
        except Exception:
            return {
                "total_rounds": len(history),
                "hints_used": hints_used,
                "highlights": "玩家积极提问，尝试了多种推理方向。",
                "blind_spots": "部分关键线索未能及时发现，建议更仔细地分析汤面细节。",
                "soup_base": soup_base,
                "verdict": "继续努力，下次一定能更快破案！"
            }

llm_service = LLMService()
