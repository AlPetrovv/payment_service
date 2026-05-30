import httpx


class WebhookSender:
    """Single-attempt webhook delivery over a shared HTTP client"""

    def __init__(self, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(timeout=timeout)

    async def send(self, url: str, payload: dict) -> None:
        response = await self._client.post(url, json=payload)
        response.raise_for_status()

    async def aclose(self) -> None:
        await self._client.aclose()
