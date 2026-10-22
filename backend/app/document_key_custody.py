"""Validação offline de material documental fornecido pelo custodiante.

Não lê arquivos, ambiente ou KMS, nem cria ou destrói chaves.
"""

import hmac
from collections.abc import Mapping

from app.crypto_documents import DocumentCrypto, DocumentKeySet


class KeyCustodyError(ValueError):
    """Erro estável; não inclui IDs de chave nem material sensível."""


def validate_document_keyring(
    supplied: Mapping[str, DocumentKeySet], *, current_key_id: str,
) -> DocumentCrypto:
    """Aceita cifra exclusiva por versão e uma única chave HMAC global estável."""
    try:
        if (not isinstance(supplied, Mapping) or not supplied
                or not isinstance(current_key_id, str)):
            raise ValueError
        items = tuple(supplied.items())
        keys = dict(items)
        if len(keys) != len(items) or current_key_id not in keys:
            raise ValueError
        lookup_key = None
        cipher_keys: list[bytes] = []
        for key_id, material in items:
            if (not isinstance(key_id, str)
                    or not isinstance(material, DocumentKeySet)
                    or material.key_id != key_id
                    or not isinstance(material.encryption_key, bytes)
                    or len(material.encryption_key) != 32
                    or not isinstance(material.lookup_key, bytes)
                    or len(material.lookup_key) < 32):
                raise ValueError
            if lookup_key is None:
                lookup_key = material.lookup_key
            elif not hmac.compare_digest(lookup_key, material.lookup_key):
                raise ValueError
            if hmac.compare_digest(material.encryption_key, material.lookup_key):
                raise ValueError
            if any(hmac.compare_digest(material.encryption_key, old)
                   for old in cipher_keys):
                raise ValueError
            cipher_keys.append(material.encryption_key)
        # Also rejects a historical cipher key used as the lookup key.
        if any(hmac.compare_digest(key, lookup_key) for key in cipher_keys):
            raise ValueError
        return DocumentCrypto(keys, current_key_id=current_key_id)
    except Exception:
        raise KeyCustodyError("DOCUMENT_KEYRING_INVALID") from None
