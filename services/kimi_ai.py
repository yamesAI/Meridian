import requests
import logging

logger = logging.getLogger(__name__)


class KimiAI:
    """Wrapper for Moonshot (Kimi) AI chat completions API."""

    BASE_URL = "https://api.moonshot.cn/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "moonshot-v1-8k",
        temperature: float = 0.85,
    ) -> str:
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
