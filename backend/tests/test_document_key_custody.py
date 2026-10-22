"""Somente material sintético; nenhuma chave operacional é carregada."""

import unittest
from collections.abc import Mapping
from unittest.mock import patch

from app.crypto_documents import DocumentCrypto, DocumentKeySet
from app.document_key_custody import KeyCustodyError, validate_document_keyring
from app.document_key_rotation import prepare_encryption_rotation


class DocumentKeyCustodyTests(unittest.TestCase):
    def setUp(self):
        self.old = DocumentKeySet("old", b"E" * 32, b"L" * 32)
        self.older = DocumentKeySet("older", b"O" * 32, b"L" * 32)

    def test_stable_lookup_and_historical_cipher_compatible_with_rotation(self):
        old_crypto = validate_document_keyring({"old": self.old},
                                                current_key_id="old")
        context = dict(kind="CPF", entity="user_identity", field="cpf",
                       record_id="00000000-0000-4000-8000-000000000101")
        old_envelope = old_crypto.encrypt("52998224725", **context)
        rotated = prepare_encryption_rotation(
            {"old": self.old}, new_key_id="new", new_encryption_key=b"N" * 32)
        new = validate_document_keyring(
            {"old": self.old,
             "new": DocumentKeySet("new", b"N" * 32, b"L" * 32)},
            current_key_id="new")
        self.assertIsInstance(new, DocumentCrypto)
        self.assertEqual(new.decrypt(old_envelope, **context), "52998224725")
        self.assertEqual(new.lookup_hmac("52998224725", kind="CPF"),
                         old_crypto.lookup_hmac("52998224725", kind="CPF"))
        self.assertEqual(rotated.lookup_hmac("52998224725", kind="CPF"),
                         new.lookup_hmac("52998224725", kind="CPF"))

    def test_rejects_alternate_lookup_and_reused_cipher_material(self):
        cases = (
            {"old": self.old, "other": DocumentKeySet("other", b"O" * 32, b"X" * 32)},
            {"old": self.old, "other": DocumentKeySet("other", b"E" * 32, b"L" * 32)},
            {"old": DocumentKeySet("old", b"L" * 32, b"L" * 32)},
            {"old": self.old, "other": DocumentKeySet("other", b"L" * 32, b"L" * 32)},
        )
        for keys in cases:
            with self.subTest(count=len(keys)):
                with self.assertRaisesRegex(KeyCustodyError,
                                            "^DOCUMENT_KEYRING_INVALID$"):
                    validate_document_keyring(keys, current_key_id="old")

    def test_missing_malformed_or_mismatched_material_fails_closed(self):
        for keys, current in (
            ({}, "old"), ({"old": self.old}, "missing"),
            ({"old": DocumentKeySet("wrong", b"E" * 32, b"L" * 32)}, "old"),
            ({"old": DocumentKeySet("old", b"short", b"L" * 32)}, "old"),
            ({"old": DocumentKeySet("old", b"E" * 32, b"short")}, "old"),
            ({"invalid key": self.old}, "invalid key"),
            (None, "old"),
        ):
            with self.subTest(current=current, type=type(keys).__name__):
                with self.assertRaises(KeyCustodyError):
                    validate_document_keyring(keys, current_key_id=current)

    def test_adapter_errors_are_redacted(self):
        class BrokenMapping(Mapping):
            def __iter__(self): return iter(("old",))
            def __len__(self): return 1
            def __getitem__(self, key): raise RuntimeError("SECRET")
            def items(self): raise RuntimeError("SECRET")

        with self.assertRaises(KeyCustodyError) as caught:
            validate_document_keyring(BrokenMapping(), current_key_id="old")
        self.assertEqual(str(caught.exception), "DOCUMENT_KEYRING_INVALID")
        self.assertIsNone(caught.exception.__cause__)

    def test_no_implicit_file_network_or_database_access(self):
        with patch("builtins.open") as file, patch("socket.socket") as network:
            with patch("psycopg.connect") as db:
                validate_document_keyring({"old": self.old},
                                          current_key_id="old")
        file.assert_not_called()
        network.assert_not_called()
        db.assert_not_called()
