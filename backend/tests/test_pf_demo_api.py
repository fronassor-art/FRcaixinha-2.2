"""Testes da API PF demonstrativa, sem rede, banco ou dados reais."""

import unittest

import httpx

from app.main import app as standard_app
from app.pf_demo_api import create_demo_app


VALID = {
    "name": "Pessoa Sintetica",
    "cpf": "529.982.247-25",
    "email": "demo@example.com",
    "phone": "(91) 91234-5678",
}


class PfDemoApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.demo_app = create_demo_app()
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.demo_app),
            base_url="http://demo.test",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def test_valid_input_returns_preliminary_non_operational_result(self) -> None:
        response = await self.client.post("/demo/pf/pre-registration", json=VALID)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertRegex(body["case_ref"], r"^demo-[0-9a-f]{32}$")
        self.assertEqual(body["status"], "PRELIMINARY_DEMO_ONLY")
        self.assertFalse(body["operational"])
        self.assertFalse(body["identity_verified"])
        self.assertFalse(body["access_granted"])
        self.assertFalse(body["persisted"])
        self.assertNotIn("529", response.text)
        self.assertNotIn("demo@example.com", response.text)
        self.assertNotIn("Pessoa Sintetica", response.text)

    async def test_invalid_fields_fail_closed_without_echoing_personal_values(self) -> None:
        for field, value in (
            ("cpf", "52998224726"),
            ("email", "invalid"),
            ("phone", "00912345678"),
        ):
            with self.subTest(field=field):
                payload = {**VALID, field: value}
                response = await self.client.post("/demo/pf/pre-registration", json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json(), {"detail": "DEMO_INPUT_INVALID"})
                self.assertNotIn(value, response.text)

    async def test_unexpected_fields_are_rejected_without_echo(self) -> None:
        payload = {**VALID, "password": "synthetic-secret"}
        response = await self.client.post("/demo/pf/pre-registration", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {"detail": "DEMO_INPUT_INVALID"})
        self.assertNotIn("synthetic-secret", response.text)

    async def test_standard_app_does_not_publish_demo_route(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=standard_app),
            base_url="http://standard.test",
        ) as client:
            response = await client.post("/demo/pf/pre-registration", json=VALID)
        self.assertEqual(response.status_code, 404)

    async def test_demo_app_has_no_persistence_or_external_dependency_contract(self) -> None:
        response = await self.client.post("/demo/pf/pre-registration", json=VALID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual((await self.client.get("/docs")).status_code, 404)
        self.assertEqual((await self.client.get("/redoc")).status_code, 404)
        response = await self.client.post("/demo/pf/pre-registration", json=VALID)
        self.assertEqual(set(response.json()), {
            "case_ref", "status", "operational", "identity_verified",
            "access_granted", "persisted",
        })


if __name__ == "__main__":
    unittest.main()
