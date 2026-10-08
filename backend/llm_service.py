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
            f"Q: {h['question']} -> A: {h['answer']} ({h['type']})" for h in history
        ) or "（无）"

        system_prompt = f"""你是海龟汤游戏裁判。根据汤底严格判定玩家问题，只回答四个字之一。

【汤面】{soup_surface}
【汤底】{soup_base}
【关键细节】{', '.join(key_details)}
【历史问答】
{history_text}

规则：
- "是"=问题描述符合汤底事实
- "否"=问题与汤底事实矛盾
- "无关"=问题与汤底无直接关联
- "部分相关"=问题部分正确但不完全准确

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
                      {"role": "user", "content": f"玩家提问：{question}"}],
            llm_config=llm_config,
            temperature=0.3 if not self._is_reasoning_model(llm_config.get("model", "")) else 1.0
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

llm_service = LLMService()
