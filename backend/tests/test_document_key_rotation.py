"""Synthetic keys and documents only; no persisted HMAC is changed."""

import unittest

from app.crypto_documents import DocumentCrypto, DocumentCryptoError, DocumentKeySet
from app.document_key_rotation import prepare_encryption_rotation


class DocumentKeyRotationTests(unittest.TestCase):
    def setUp(self):
        self.old = DocumentKeySet("old", b"E" * 32, b"L" * 32)
        self.context = dict(kind="CPF", entity="user_identity", field="cpf",
                            record_id="00000000-0000-4000-8000-000000000101")

    def test_old_envelope_decrypts_and_lookup_remains_identical(self):
        original = DocumentCrypto({"old": self.old}, current_key_id="old")
        envelope = original.encrypt("52998224725", **self.context)
        new = prepare_encryption_rotation({"old": self.old}, new_key_id="new",
                                          new_encryption_key=b"N" * 32)
        self.assertEqual(new.decrypt(envelope, **self.context), "52998224725")
        self.assertEqual(new.lookup_hmac("52998224725", kind="CPF"),
                         original.lookup_hmac("52998224725", kind="CPF"))
        self.assertEqual(new.lookup_hmac("11222333000181", kind="CNPJ"),
                         original.lookup_hmac("11222333000181", kind="CNPJ"))
        latest = new.encrypt("52998224725", **self.context)
        self.assertNotEqual(latest, envelope)
        self.assertEqual(new.decrypt(latest, **self.context), "52998224725")
        with self.assertRaisesRegex(DocumentCryptoError, "KEY_ID_UNKNOWN"):
            original.decrypt(latest, **self.context)

    def test_multiple_old_encryption_keys_remain_available(self):
        older = DocumentKeySet("older", b"O" * 32, b"L" * 32)
        old_ring = {"older": older, "old": self.old}
        envelope = DocumentCrypto(old_ring, current_key_id="older").encrypt(
            "52998224725", **self.context)
        new = prepare_encryption_rotation(old_ring, new_key_id="new",
                                          new_encryption_key=b"N" * 32)
        self.assertEqual(new.decrypt(envelope, **self.context), "52998224725")
        self.assertEqual(set(old_ring), {"older", "old"})

    def test_changed_lookup_or_reused_cipher_key_is_rejected(self):
        mismatched = DocumentKeySet("other", b"O" * 32, b"X" * 32)
        with self.assertRaisesRegex(DocumentCryptoError, "LOOKUP_KEY_ROTATION_BLOCKED"):
            prepare_encryption_rotation({"old": self.old, "other": mismatched},
                                        new_key_id="new", new_encryption_key=b"N" * 32)
        with self.assertRaisesRegex(DocumentCryptoError, "ENCRYPTION_KEY_INVALID"):
            prepare_encryption_rotation({"old": self.old}, new_key_id="new",
                                        new_encryption_key=b"E" * 32)
        with self.assertRaisesRegex(DocumentCryptoError, "ROTATION_KEY_RING_INVALID"):
            prepare_encryption_rotation({"old": self.old}, new_key_id="old",
                                        new_encryption_key=b"N" * 32)

    def test_repr_and_errors_do_not_expose_keys(self):
        self.assertNotIn("LLLL", repr(self.old))
        with self.assertRaises(DocumentCryptoError) as caught:
            prepare_encryption_rotation({"old": self.old}, new_key_id="new",
                                        new_encryption_key=b"bad")
        self.assertNotIn("bad", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
