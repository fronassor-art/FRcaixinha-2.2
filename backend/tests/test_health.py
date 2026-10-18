"""Testes ASGI em processo, sem servidor ou acesso à rede."""

import unittest

import httpx

from app.main import app, create_app


class HealthTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_health_returns_exact_json(self) -> None:
        response = await self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/json")
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response.content, b'{"status":"ok"}')

    async def test_health_rejects_post(self) -> None:
        response = await self.client.post("/health")
        self.assertEqual(response.status_code, 405)
        self.assertIn("GET", response.headers["allow"])

    async def test_unknown_route_returns_404(self) -> None:
        response = await self.client.get("/missing")
        self.assertEqual(response.status_code, 404)

    async def test_factory_creates_independent_applications(self) -> None:
        first = create_app()
        second = create_app()
        self.assertIsNot(first, second)
        self.assertIsNot(first, app)
        self.assertIsNot(first.state, second.state)
        first.state.marker = "first-only"
        self.assertFalse(hasattr(second.state, "marker"))
        self.assertFalse(hasattr(app.state, "marker"))

        async def first_only() -> dict[str, bool]:
            return {"first": True}

        first.add_api_route("/first-only", first_only)
        for application, expected in ((first, 200), (second, 404), (app, 404)):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=application),
                base_url="http://testserver",
            ) as client:
                self.assertEqual((await client.get("/first-only")).status_code, expected)
                self.assertEqual((await client.get("/health")).content, b'{"status":"ok"}')
