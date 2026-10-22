"""Cifra e busca exata de CPF/CNPJ sem persistência ou efeitos externos."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, hmac, re
from secrets import token_bytes
from typing import Mapping
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from app.document_validation import normalize_cnpj, normalize_cpf

class DocumentCryptoError(ValueError):
    """Erro estável que nunca inclui PII, chaves ou ciphertext."""

@dataclass(frozen=True, slots=True, repr=False)
class DocumentKeySet:
    key_id: str
    encryption_key: bytes
    lookup_key: bytes
    def __repr__(self) -> str:
        return "DocumentKeySet(key_id=<redacted>, keys=<redacted>)"

_MAGIC=b"FRC-DOC"; _VERSION=1; _NONCE_SIZE=12
_KEY_ID=re.compile(r"[A-Za-z0-9._-]{1,32}", re.ASCII)
_TOKEN=re.compile(r"[A-Za-z0-9._:-]{1,128}", re.ASCII)
_KIND={"CPF": normalize_cpf, "CNPJ": normalize_cnpj}

def _valid_token(value: object) -> bool:
    return isinstance(value,str) and _TOKEN.fullmatch(value) is not None

def derive_key(master_key: bytes, *, purpose: str, key_id: str) -> bytes:
    if not isinstance(master_key,bytes) or len(master_key)<32:
        raise DocumentCryptoError("MASTER_KEY_INVALID")
    if not _valid_token(purpose) or not _valid_token(key_id):
        raise DocumentCryptoError("KEY_CONTEXT_INVALID")
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=f"FRCAIXINHA/{purpose}/{key_id}".encode("ascii")).derive(master_key)

def _aad(kind: str, entity: str, field: str, record_id: str, key_id: str) -> bytes:
    if kind not in _KIND or not _KEY_ID.fullmatch(key_id or "") or not all(_valid_token(v) for v in (entity,field,record_id)):
        raise DocumentCryptoError("CONTEXT_INVALID")
    return b"|".join((b"FRCAIXINHA-DOCUMENT-AEAD",str(_VERSION).encode("ascii"),
                      kind.encode("ascii"),entity.encode("ascii"),field.encode("ascii"),record_id.encode("ascii"),key_id.encode("ascii")))

def _canonical(value: object, kind: str) -> str:
    normalizer=_KIND.get(kind)
    if normalizer is None: raise DocumentCryptoError("DOCUMENT_KIND_INVALID")
    result=normalizer(value)
    if result is None: raise DocumentCryptoError("DOCUMENT_INVALID")
    return result

class DocumentCrypto:
    """Operações puras; nenhum método abre recursos externos."""
    def __init__(self, keys: Mapping[str,DocumentKeySet], *, current_key_id: str):
        if not keys or not _KEY_ID.fullmatch(current_key_id or ""):
            raise DocumentCryptoError("KEY_RING_INVALID")
        copied=dict(keys)
        if current_key_id not in copied: raise DocumentCryptoError("CURRENT_KEY_UNKNOWN")
        for key_id,material in copied.items():
            if (not _KEY_ID.fullmatch(key_id or "") or material.key_id != key_id
                or not isinstance(material.encryption_key,bytes) or len(material.encryption_key)!=32
                or not isinstance(material.lookup_key,bytes) or len(material.lookup_key)<32):
                raise DocumentCryptoError("KEY_MATERIAL_INVALID")
        self._keys=copied; self._current_key_id=current_key_id
    def encrypt(self,value: object,*,kind: str,entity: str,field: str,record_id: str)->bytes:
        canonical=_canonical(value,kind); material=self._keys[self._current_key_id]
        nonce=token_bytes(_NONCE_SIZE); aad=_aad(kind,entity,field,record_id,material.key_id)
        ciphertext=AESGCM(material.encryption_key).encrypt(nonce,canonical.encode("ascii"),aad)
        key_bytes=material.key_id.encode("ascii")
        return _MAGIC+bytes((_VERSION,len(key_bytes)))+key_bytes+nonce+ciphertext
    def decrypt(self,envelope: bytes,*,kind: str,entity: str,field: str,record_id: str)->str:
        if not isinstance(envelope,bytes) or len(envelope)<len(_MAGIC)+2+_NONCE_SIZE+16 or envelope[:len(_MAGIC)]!=_MAGIC:
            raise DocumentCryptoError("ENVELOPE_INVALID")
        offset=len(_MAGIC); version,key_length=envelope[offset:offset+2]; offset+=2
        if version!=_VERSION or not 1<=key_length<=32: raise DocumentCryptoError("ENVELOPE_VERSION_INVALID")
        end_key=offset+key_length
        try: key_id=envelope[offset:end_key].decode("ascii")
        except UnicodeDecodeError as exc: raise DocumentCryptoError("KEY_ID_INVALID") from exc
        if not _KEY_ID.fullmatch(key_id): raise DocumentCryptoError("KEY_ID_INVALID")
        material=self._keys.get(key_id)
        if material is None: raise DocumentCryptoError("KEY_ID_UNKNOWN")
        nonce=envelope[end_key:end_key+_NONCE_SIZE]
        aad = _aad(kind, entity, field, record_id, key_id)
        try: plaintext=AESGCM(material.encryption_key).decrypt(nonce,envelope[end_key+_NONCE_SIZE:],aad)
        except (InvalidTag,ValueError) as exc: raise DocumentCryptoError("DOCUMENT_AUTHENTICATION_FAILED") from exc
        try: decoded=plaintext.decode("ascii")
        except UnicodeDecodeError as exc: raise DocumentCryptoError("DOCUMENT_AUTHENTICATION_FAILED") from exc
        return _canonical(decoded,kind)
    def lookup_hmac(self,value: object,*,kind: str)->bytes:
        canonical=_canonical(value,kind); material=self._keys[self._current_key_id]
        domain = b"FRCAIXINHA/LOOKUP/v1/" + kind.encode("ascii")
        return hmac.new(material.lookup_key, domain + b"|" + canonical.encode("ascii"), hashlib.sha256).digest()
