import asyncio
import httpx

async def test_llm():
    # 在这里填入你的真实配置
    llm_config = {
        "api_key": "sk-你的真实APIKey",  # ← 修改这里
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2-6"  # 或你用成功的模型名
    }
    
    api_key = llm_config["api_key"].strip()
    base_url = llm_config["base_url"].rstrip("/")
    model = llm_config["model"]
    
    print(f"base_url: {base_url}")
    print(f"model: {model}")
    print(f"key_len: {len(api_key)}")
    print(f"key_prefix: {api_key[:10]}...")
    print(f"key_suffix: ...{api_key[-4:]}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        print(f"\nstatus: {resp.status_code}")
        print(f"response: {resp.text[:500]}")

if __name__ == "__main__":
    asyncio.run(test_llm())
