"""Testes do fluxo PF demonstrativo, sem rede, banco ou dados reais."""

import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import UUID

import httpx

from app.main import app as standard_app
from app.pf_demo_api import create_demo_app
from app.pf_preregistration import (
    PfPreRegistrationService,
    PreRegistrationError,
    PreRegistrationState,
    TransientPreRegistrationStore,
)


VALID = {
    "name": "Pessoa Sintetica",
    "cpf": "529.982.247-25",
    "email": "demo@example.com",
    "phone": "(91) 91234-5678",
}
_NEUTRAL = {"detail": "DEMO_REQUEST_RECEIVED", "operational": False}
_PATH = "/demo/pf/pre-registration"


class PfDemoApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.store = TransientPreRegistrationStore()
        self.demo_app = create_demo_app(self.store)
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=self.demo_app),
            base_url="http://demo.test",
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()

    async def _submit(self, key: str, payload: dict[str, str] = VALID) -> httpx.Response:
        return await self.client.post(
            _PATH, headers={"Idempotency-Key": key}, json=payload,
        )

    def _assert_neutral(self, response: httpx.Response) -> None:
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json(), _NEUTRAL)
        self.assertNotIn("case_ref", response.text)
        self.assertNotIn("529", response.text)
        self.assertNotIn("demo@example.com", response.text)
        self.assertNotIn("Pessoa Sintetica", response.text)

    def _assert_same_public_response(self, first: httpx.Response, second: httpx.Response) -> None:
        self._assert_neutral(first)
        self._assert_neutral(second)
        self.assertEqual(first.content, second.content)
        self.assertEqual(dict(first.headers), dict(second.headers))

    async def test_valid_input_returns_neutral_non_operational_ack(self) -> None:
        response = await self._submit("demo-1")
        self._assert_neutral(response)
        self.assertEqual(len(self.store._by_ref), 1)
        self.assertEqual(next(iter(self.store._by_ref.values())).state, PreRegistrationState.PRELIMINARY)

    async def test_invalid_fields_fail_closed_without_echoing_personal_values(self) -> None:
        for field, value in (
            ("cpf", "52998224726"),
            ("email", "invalid"),
            ("phone", "00912345678"),
        ):
            with self.subTest(field=field):
                response = await self._submit(field, {**VALID, field: value})
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json(), {"detail": "DEMO_INPUT_INVALID"})
                self.assertNotIn(value, response.text)
        self.assertEqual(len(self.store._by_ref), 0)

    async def test_invalid_format_independent_of_existing_identity(self) -> None:
        await self._submit("existing")
        invalid_before = await self._submit("invalid-one", {**VALID, "phone": "invalid"})
        invalid_after = await self._submit(
            "invalid-two", {**VALID, "cpf": "123.456.789-09",
                            "email": "other@example.com", "phone": "invalid"},
        )
        self.assertEqual(invalid_before.status_code, 422)
        self.assertEqual(invalid_before.content, invalid_after.content)
        self.assertEqual(dict(invalid_before.headers), dict(invalid_after.headers))

    async def test_name_length_matches_existing_identity_validator_and_model(self) -> None:
        accepted = await self._submit("name-200", {**VALID, "name": "A" * 200})
        rejected = await self._submit(
            "name-201", {**VALID, "cpf": "123.456.789-09",
                         "email": "other@example.com", "name": "A" * 201},
        )
        self._assert_neutral(accepted)
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(rejected.json(), {"detail": "DEMO_INPUT_INVALID"})
        self.assertEqual(len(self.store._by_ref), 1)

    async def test_invalid_name_is_rejected_without_record(self) -> None:
        response = await self._submit("invalid-name", {**VALID, "name": "1234"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {"detail": "DEMO_INPUT_INVALID"})
        self.assertEqual(len(self.store._by_ref), 0)

    async def test_normalized_equivalent_payload_replays_one_internal_record(self) -> None:
        first = await self._submit("normalized")
        second = await self._submit("normalized", {
            **VALID, "name": " Pessoa  Sintetica ",
            "cpf": "52998224725", "email": "DEMO@EXAMPLE.COM",
            "phone": "91912345678",
        })
        self._assert_same_public_response(first, second)
        self.assertEqual(len(self.store._by_ref), 1)
        self.assertEqual(len(self.store._by_key), 1)

    async def test_unexpected_fields_are_rejected_without_echo(self) -> None:
        response = await self._submit("extra", {**VALID, "password": "synthetic-secret"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json(), {"detail": "DEMO_INPUT_INVALID"})
        self.assertNotIn("synthetic-secret", response.text)
        self.assertEqual(len(self.store._by_ref), 0)

    async def test_idempotent_replay_has_same_public_result_and_one_internal_ref(self) -> None:
        first = await self._submit("repeat-1")
        ref = next(iter(self.store._by_ref))
        second = await self._submit("repeat-1")
        self._assert_same_public_response(first, second)
        self.assertEqual(set(self.store._by_ref), {ref})
        self.assertEqual(len(self.store._by_key), 1)

    async def test_idempotency_conflict_and_duplicate_are_neutral(self) -> None:
        first = await self._submit("conflict")
        ref = next(iter(self.store._by_ref))
        conflict = await self._submit("conflict", {**VALID, "email": "other@example.com"})
        renamed = await self._submit("conflict", {**VALID, "name": "Outra Pessoa Sintetica"})
        duplicate = await self._submit("other-key")
        for response in (conflict, renamed, duplicate):
            self._assert_same_public_response(first, response)
        self.assertEqual(set(self.store._by_ref), {ref})
        self.assertEqual(len(self.store._by_key), 1)

    async def test_cpf_email_and_phone_variants_are_neutral_without_duplicate_records(self) -> None:
        first = await self._submit("first")
        ref = next(iter(self.store._by_ref))
        variants = (
            ("cpf-reused", {**VALID, "email": "other@example.com"}),
            ("email-reused", {**VALID, "cpf": "123.456.789-09"}),
            ("phone-changed", {**VALID, "phone": "(91) 91234-5679"}),
        )
        for key, payload in variants:
            with self.subTest(key=key):
                response = await self._submit(key, payload)
                self._assert_same_public_response(first, response)
                for value in payload.values():
                    self.assertNotIn(value, response.text)
        self.assertEqual(set(self.store._by_ref), {ref})
        self.assertEqual(len(self.store._by_cpf), 1)
        self.assertEqual(len(self.store._by_email), 1)

    async def test_distinct_person_can_reuse_phone_with_same_public_result(self) -> None:
        first = await self._submit("person-one")
        second = await self._submit(
            "person-two", {**VALID, "cpf": "123.456.789-09", "email": "other@example.com"},
        )
        self._assert_same_public_response(first, second)
        self.assertEqual(len(self.store._by_ref), 2)

    async def test_public_confirmation_and_private_status_routes_are_absent(self) -> None:
        created = await self._submit("confirm")
        self._assert_neutral(created)
        ref = next(iter(self.store._by_ref))
        token = "synthetic-token"
        known = await self.client.post(f"{_PATH}/{ref}/confirm-contact", json={"code": token})
        unknown = await self.client.post(
            f"{_PATH}/00000000-0000-0000-0000-000000000000/confirm-contact",
            json={"code": "wrong"},
        )
        status = await self.client.get(f"{_PATH}/{ref}")
        self.assertEqual(known.status_code, 404)
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(known.content, unknown.content)
        self.assertEqual(status.status_code, 404)
        self.assertNotIn(str(ref), created.text + known.text + status.text)
        self.assertNotIn(token, created.text + known.text + status.text)
        self.assertEqual(self.store.by_ref(ref).state, PreRegistrationState.PRELIMINARY)

    async def test_confirmation_is_simulated_only_inside_service(self) -> None:
        service = PfPreRegistrationService(self.store)
        created = service.submit(**VALID, idempotency_key="service-confirm")
        token = created._confirmation_token
        confirmed = service.confirm_contact(request_ref=created.request_ref, token=token)
        self.assertEqual(confirmed.state, PreRegistrationState.CONTACT_CONFIRMED)
        self.assertFalse(confirmed.identity_verified)
        self.assertFalse(confirmed.access_granted)
        self.assertFalse(confirmed.persisted)
        self.assertNotIn(token, repr(confirmed))

    async def test_invalid_confirmation_and_unexpected_service_failure_fail_closed(self) -> None:
        service = PfPreRegistrationService(self.store)
        created = service.submit(**VALID, idempotency_key="bad-confirm")
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=created.request_ref, token="wrong")
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=UUID(int=0), token="wrong")
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=created.request_ref, token="é")

        def unexpected_failure(*args, **kwargs):
            raise PreRegistrationError("UNEXPECTED")

        self.store.register = unexpected_failure
        internal = await self._submit("internal-failure", {
            **VALID, "cpf": "123.456.789-09", "email": "other@example.com",
        })
        self.assertEqual(internal.status_code, 500)
        self.assertEqual(internal.json(), {"detail": "DEMO_REQUEST_REJECTED"})
        self.assertNotIn("123.456.789-09", internal.text)

    async def test_unexpected_storage_and_lookup_failures_do_not_echo_data(self) -> None:
        secret = VALID["cpf"]
        with patch.object(self.store, "register", side_effect=RuntimeError(secret)):
            storage = await self._submit("store-fault")
        with patch.object(self.store, "lookup_digest", side_effect=RuntimeError(secret)):
            lookup = await self._submit("lookup-fault")
        for response in (storage, lookup):
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {"detail": "DEMO_REQUEST_REJECTED"})
            self.assertNotIn(secret, response.text)
        self.assertEqual(len(self.store._by_ref), 0)

    async def test_missing_or_invalid_idempotency_key_is_rejected(self) -> None:
        service = PfPreRegistrationService(TransientPreRegistrationStore())
        with self.assertRaisesRegex(PreRegistrationError, "^IDEMPOTENCY_KEY_MISSING$"):
            service.submit(**VALID, idempotency_key=None)
        with self.assertRaisesRegex(PreRegistrationError, "^IDEMPOTENCY_KEY_INVALID$"):
            service.submit(**VALID, idempotency_key="bad key")
        missing = await self.client.post(_PATH, json=VALID)
        invalid = await self._submit("bad key")
        self.assertEqual(missing.status_code, 422)
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(missing.json(), {"detail": "DEMO_INPUT_INVALID"})
        self.assertEqual(invalid.json(), {"detail": "DEMO_REQUEST_REJECTED"})
        self.assertEqual(len(self.store._by_ref), 0)

    async def test_standard_app_does_not_publish_demo_route(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=standard_app), base_url="http://standard.test",
        ) as client:
            response = await client.post(_PATH, json=VALID)
        self.assertEqual(response.status_code, 404)

    async def test_demo_app_disables_docs_and_exposes_no_private_routes(self) -> None:
        response = await self._submit("docs")
        self._assert_neutral(response)
        self.assertEqual((await self.client.get("/docs")).status_code, 404)
        self.assertEqual((await self.client.get("/redoc")).status_code, 404)
        schema = (await self.client.get("/openapi.json")).json()
        self.assertEqual(set(schema["paths"]), {_PATH})
        self.assertIn("202", schema["paths"][_PATH]["post"]["responses"])
        self.assertNotIn("confirm-contact", str(schema))


class PfPreRegistrationServiceTests(unittest.TestCase):
    def test_transient_store_keeps_only_keyed_lookups(self) -> None:
        store = TransientPreRegistrationStore()
        receipt = PfPreRegistrationService(store).submit(**VALID, idempotency_key="privacy-key")
        record = store.by_ref(receipt.request_ref)
        self.assertIsNotNone(record)
        self.assertFalse(hasattr(record, "person"))
        for value in (*VALID.values(), "privacy-key", receipt._confirmation_token):
            self.assertNotIn(value, str(vars(store)))
        self.assertEqual(len(record.cpf_lookup), 32)
        self.assertEqual(len(record.email_lookup), 32)
        self.assertNotEqual(record.cpf_lookup, record.email_lookup)

    def test_simultaneous_same_key_replays_one_record(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        barrier = Barrier(4)

        def submit(_: int):
            barrier.wait(timeout=5)
            return service.submit(**VALID, idempotency_key="parallel-same")

        with ThreadPoolExecutor(max_workers=4) as pool:
            receipts = list(pool.map(submit, range(4)))
        self.assertEqual(len({item.request_ref for item in receipts}), 1)
        self.assertEqual(sum(not item.idempotent_replay for item in receipts), 1)
        self.assertEqual(len(store._by_ref), 1)

    def test_simultaneous_distinct_keys_do_not_duplicate_identity(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        barrier = Barrier(4)

        def submit(index: int):
            barrier.wait(timeout=5)
            try:
                return service.submit(**VALID, idempotency_key=f"parallel-{index}")
            except PreRegistrationError as exc:
                return exc.args[0]

        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes = list(pool.map(submit, range(4)))
        self.assertEqual(sum(not isinstance(item, str) for item in outcomes), 1)
        self.assertEqual(outcomes.count("DUPLICATE_PRE_REGISTRATION"), 3)
        self.assertEqual(len(store._by_ref), 1)
        self.assertEqual(len(store._by_cpf), 1)
        self.assertEqual(len(store._by_email), 1)

    def test_transitions_and_token_are_transient(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        created = service.submit(**VALID, idempotency_key="service-1")
        self.assertEqual(created.state, PreRegistrationState.PRELIMINARY)
        self.assertFalse(created.identity_verified)
        self.assertFalse(created.access_granted)
        self.assertFalse(created.persisted)
        self.assertTrue(created._confirmation_token)
        confirmed = service.confirm_contact(
            request_ref=created.request_ref,
            token=created._confirmation_token,
        )
        self.assertEqual(confirmed.state, PreRegistrationState.CONTACT_CONFIRMED)
        self.assertFalse(confirmed.identity_verified)
        self.assertFalse(confirmed.access_granted)

    def test_service_rejects_bad_token_and_repr_redacts(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        created = service.submit(**VALID, idempotency_key="service-2")
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=created.request_ref, token="wrong")
        self.assertNotIn(VALID["cpf"], repr(created))
        self.assertNotIn(VALID["email"], repr(created))
        self.assertNotIn(created._confirmation_token, repr(created))

    def test_confirmation_token_expires_at_ten_minutes(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        tick = [100.0]
        with patch("app.pf_preregistration.monotonic", side_effect=lambda: tick[0]):
            created = service.submit(**VALID, idempotency_key="expires")
            token = created._confirmation_token
            tick[0] = 700.0
            with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
                service.confirm_contact(request_ref=created.request_ref, token=token)
        record = store.by_ref(created.request_ref)
        self.assertEqual(record.state, PreRegistrationState.PRELIMINARY)
        self.assertTrue(record.token_revoked)
        self.assertEqual(record.audit_events, ("SUBMITTED", "CONTACT_CONFIRMATION_EXPIRED"))

    def test_confirmation_locks_after_five_failed_attempts(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        created = service.submit(**VALID, idempotency_key="lock")
        token = created._confirmation_token
        for _ in range(5):
            with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
                service.confirm_contact(request_ref=created.request_ref, token="wrong")
        record = store.by_ref(created.request_ref)
        self.assertEqual(record.failed_confirmation_attempts, 5)
        self.assertTrue(record.token_revoked)
        self.assertEqual(record.audit_events[-1], "CONTACT_CONFIRMATION_LOCKED")
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=created.request_ref, token=token)
        self.assertEqual(store.by_ref(created.request_ref).failed_confirmation_attempts, 5)
        self.assertNotIn(token, repr(record))
        self.assertNotIn(token, str(vars(store)))

    def test_consumed_token_cannot_confirm_twice(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        created = service.submit(**VALID, idempotency_key="consume")
        token = created._confirmation_token
        confirmed = service.confirm_contact(request_ref=created.request_ref, token=token)
        self.assertFalse(confirmed.contact_confirmation_required)
        with self.assertRaisesRegex(PreRegistrationError, "CONTACT_CONFIRMATION_INVALID"):
            service.confirm_contact(request_ref=created.request_ref, token=token)
        replay = service.submit(**VALID, idempotency_key="consume")
        self.assertTrue(replay.idempotent_replay)
        self.assertEqual(replay.state, PreRegistrationState.CONTACT_CONFIRMED)
        self.assertEqual(replay._confirmation_token, "")
        record = store.by_ref(created.request_ref)
        self.assertEqual(record.audit_events, ("SUBMITTED", "CONTACT_CONFIRMED_SIMULATED"))
        self.assertEqual(record.confirmation_token_digest, "")

    def test_confirmation_storage_failure_is_closed_and_does_not_grant_access(self) -> None:
        store = TransientPreRegistrationStore()
        service = PfPreRegistrationService(store)
        created = service.submit(**VALID, idempotency_key="replace-fault")
        with patch.object(store, "replace", side_effect=RuntimeError(VALID["cpf"])):
            with self.assertRaisesRegex(PreRegistrationError, "^PRE_REGISTRATION_UNAVAILABLE$"):
                service.confirm_contact(
                    request_ref=created.request_ref, token=created._confirmation_token,
                )
        record = store.by_ref(created.request_ref)
        self.assertEqual(record.state, PreRegistrationState.PRELIMINARY)
        self.assertEqual(record.audit_events, ("SUBMITTED",))
        self.assertFalse(created.identity_verified)
        self.assertFalse(created.access_granted)

    def test_instances_do_not_share_identities_or_hmac_keys(self) -> None:
        first_store = TransientPreRegistrationStore()
        second_store = TransientPreRegistrationStore()
        first = PfPreRegistrationService(first_store).submit(
            **VALID, idempotency_key="same-key",
        )
        second = PfPreRegistrationService(second_store).submit(
            **VALID, idempotency_key="same-key",
        )
        self.assertNotEqual(first.request_ref, second.request_ref)
        self.assertEqual(len(first_store._by_ref), 1)
        self.assertEqual(len(second_store._by_ref), 1)
        self.assertNotEqual(
            first_store.by_ref(first.request_ref).cpf_lookup,
            second_store.by_ref(second.request_ref).cpf_lookup,
        )



if __name__ == "__main__":
    unittest.main()
