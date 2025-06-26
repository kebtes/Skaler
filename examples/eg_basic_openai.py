import asyncio

from skaler import APIProvider, ProxyPool, SkaleManager


async def main():
    openai = APIProvider(name="openai_key_1", key="sk-abc", limit_per_minute=60)
    claude = APIProvider(name="claude_key", key="sk-xyz", limit_per_minute=50)

    proxies = ProxyPool([
        "http://user:pass@proxy1.com",
        "http://user:pass@proxy2.com"
    ])

    skaler = SkaleManager(
        providers=[openai, claude],
        proxies=proxies
    )

    response = await skaler.send_request(
        url="https://api.openai.com/v1/completions",
        method="POST",
        data={"prompt":"hello", "max_tokens":10}
    )

    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    asyncio.run(main())
