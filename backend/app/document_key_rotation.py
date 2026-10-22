"""Offline preparation of encryption-key rotation with a stable lookup key.

No key is generated, persisted or retrieved here. The caller supplies every
historical encryption key until all matching envelopes have been re-encrypted.
"""

import hmac
from typing import Mapping

from app.crypto_documents import DocumentCrypto, DocumentCryptoError, DocumentKeySet


def prepare_encryption_rotation(
    existing: Mapping[str, DocumentKeySet], *, new_key_id: str,
    new_encryption_key: bytes,
) -> DocumentCrypto:
    """Select a new cipher key while keeping the one global lookup HMAC key.

    A changed lookup key is rejected; its future rotation requires a separate
    atomic database migration with duplicate checks and a write freeze.
    """
    if (not existing or not isinstance(new_key_id, str)
            or new_key_id in existing or not all(
                isinstance(key_id, str) and isinstance(material, DocumentKeySet)
                for key_id, material in existing.items()
            )):
        raise DocumentCryptoError("ROTATION_KEY_RING_INVALID")
    keys = dict(existing)
    # Validate all historical entries with the existing implementation first.
    DocumentCrypto(keys, current_key_id=next(iter(keys)))
    stable_lookup_key = next(iter(keys.values())).lookup_key
    if any(not hmac.compare_digest(item.lookup_key, stable_lookup_key)
           for item in keys.values()):
        raise DocumentCryptoError("LOOKUP_KEY_ROTATION_BLOCKED")
    if (not isinstance(new_encryption_key, bytes) or len(new_encryption_key) != 32
            or any(hmac.compare_digest(item.encryption_key, new_encryption_key)
                   for item in keys.values())):
        raise DocumentCryptoError("ENCRYPTION_KEY_INVALID")
    keys[new_key_id] = DocumentKeySet(
        key_id=new_key_id,
        encryption_key=new_encryption_key,
        lookup_key=stable_lookup_key,
    )
    return DocumentCrypto(keys, current_key_id=new_key_id)
