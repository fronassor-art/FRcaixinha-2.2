import unittest
from app.crypto_documents import DocumentCrypto, DocumentCryptoError, DocumentKeySet, derive_key

class DocumentCryptoTests(unittest.TestCase):
    def setUp(self):
        self.crypto=DocumentCrypto({"k1":DocumentKeySet("k1",b"e"*32,b"l"*32)},current_key_id="k1")
        self.kw=dict(kind="CPF",entity="user_identity",field="cpf",record_id="id-1")
    def test_cpf_round_trip(self):
        e=self.crypto.encrypt("529.982.247-25",**self.kw); self.assertEqual(self.crypto.decrypt(e,**self.kw),"52998224725")
    def test_cpf_leading_zero_is_preserved(self):
        e=self.crypto.encrypt("042.236.650-14",**self.kw); self.assertEqual(self.crypto.decrypt(e,**self.kw),"04223665014")
    def test_cnpj_round_trip(self):
        kw=dict(kind="CNPJ",entity="contracting_party",field="tax_id",record_id="id-2"); e=self.crypto.encrypt("11222333000181",**kw); self.assertEqual(self.crypto.decrypt(e,**kw),"11222333000181")
    def test_cnpj_alphanumeric_round_trip(self):
        kw=dict(kind="CNPJ",entity="contracting_party",field="tax_id",record_id="id-2"); e=self.crypto.encrypt("12ABC34501DE35",**kw); self.assertEqual(self.crypto.decrypt(e,**kw),"12ABC34501DE35")
    def test_tamper_and_context_rejected(self):
        e=bytearray(self.crypto.encrypt("52998224725",**self.kw)); e[-1]^=1
        with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_AUTHENTICATION_FAILED"): self.crypto.decrypt(bytes(e),**self.kw)
        e=self.crypto.encrypt("52998224725",**self.kw)
        with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_AUTHENTICATION_FAILED"): self.crypto.decrypt(e,**{**self.kw,"record_id":"id-2"})
    def test_invalid_documents_rejected(self):
        for kind,value in (("CPF","00000000000"),("CNPJ","00000000000000"),("CNPJ","not-a-cnpj")):
            with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_INVALID"): self.crypto.encrypt(value,kind=kind,entity="user_identity",field="document",record_id="id-1")
    def test_lookup_hmac_is_deterministic_with_domain_separation(self):
        cpf=self.crypto.lookup_hmac("52998224725",kind="CPF"); cpf_masked=self.crypto.lookup_hmac("529.982.247-25",kind="CPF")
        cnpj=self.crypto.lookup_hmac("11222333000181",kind="CNPJ")
        self.assertEqual(cpf,cpf_masked); self.assertEqual(len(cpf),32); self.assertNotEqual(cpf,cnpj)
    def test_nonce_changes(self): self.assertNotEqual(self.crypto.encrypt("52998224725",**self.kw),self.crypto.encrypt("52998224725",**self.kw))
    def test_hkdf_domains_are_separate(self): self.assertNotEqual(derive_key(b"m"*32,purpose="enc-cpf",key_id="k1"),derive_key(b"m"*32,purpose="lookup-cpf",key_id="k1"))
    def test_truncated_and_unknown_envelopes_rejected(self):
        e=self.crypto.encrypt("52998224725",**self.kw)
        bad_nonce=bytearray(e); bad_nonce[11] ^= 1
        with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_AUTHENTICATION_FAILED"): self.crypto.decrypt(bytes(bad_nonce),**self.kw)
        for bad in (e[:10],e[:-1],b"FRC-DOC"+bytes((99,2))+b"k1"+e[-28:]):
            with self.assertRaises(DocumentCryptoError): self.crypto.decrypt(bad,**self.kw)
        unknown=bytearray(e); unknown[8]=2; unknown[9:11]=b"k9"
        with self.assertRaisesRegex(DocumentCryptoError,"KEY_ID_UNKNOWN"): self.crypto.decrypt(bytes(unknown),**self.kw)
    def test_key_id_is_authenticated_even_when_material_is_reused(self):
        keys={"k1":DocumentKeySet("k1",b"e"*32,b"l"*32),"k2":DocumentKeySet("k2",b"e"*32,b"m"*32)}
        source=DocumentCrypto(keys,current_key_id="k1"); e=bytearray(source.encrypt("52998224725",**self.kw))
        e[8]=2; e[9:11]=b"k2"
        with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_AUTHENTICATION_FAILED"): source.decrypt(bytes(e),**self.kw)
    def test_malformed_key_id_and_context_rejected(self):
        e=self.crypto.encrypt("52998224725",**self.kw)
        malformed=bytearray(e); malformed[8]=1; malformed[9]=0xff
        with self.assertRaisesRegex(DocumentCryptoError,"KEY_ID_INVALID"): self.crypto.decrypt(bytes(malformed),**self.kw)
        with self.assertRaisesRegex(DocumentCryptoError,"CONTEXT_INVALID"): self.crypto.decrypt(e,**{**self.kw,"field":"cpf|other"})
    def test_key_repr_and_errors_are_redacted(self):
        self.assertNotIn("eeee",repr(DocumentKeySet("k1",b"e"*32,b"l"*32)))
        with self.assertRaisesRegex(DocumentCryptoError,"DOCUMENT_INVALID") as ctx: self.crypto.encrypt("529.982.247-26",**self.kw)
        self.assertNotIn("529",str(ctx.exception))

if __name__ == "__main__": unittest.main()
