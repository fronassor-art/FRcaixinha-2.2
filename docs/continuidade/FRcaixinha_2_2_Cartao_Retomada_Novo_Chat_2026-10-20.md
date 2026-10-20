# FRCAIXINHA 2.2 — CARTÃO OBRIGATÓRIO DE RETOMADA DE CHAT

**Data-base:** 20/10/2026 — C15-R7. **Consultar atualização posterior antes de agir.**

> **Escopo exclusivo FRcaixinha 2.2**. Não começar do zero. Não criar ambiente, banco ou clone extra. Nunca reabrir incidente corrigido antes de consultar o Documento Mestre v1.1 (ADR/ERR) e a auditoria Fase1–C15. Não misturar projetos.

**Autoridade:** Contrato Técnico Mestre FINAL_APROVADO de 16/10/2026; Documento Mestre de Instruções v1.1 (20/10), subordinado ao contrato; Caderno de 17/10 como plano histórico. **Este cartão não concede autorização.**

**Repositório/raiz:** `fronassor-art/FRcaixinha-2.2` em `~/FRcaixinha_2.2`; `main` = `0316c3cc29aa6966033e52d5d21d5f378683ba97` (PR #17 merged). PRs #1–#4 fundação FastAPI/Flutter/CI/APK. PRs #5–#17 Fase 2 até C15.

**Código e testes:** primeira migration `revision=c15r2_20261020`, `down_revision=None`, 15 modelos/tabelas e 18 índices, integrada à `main`; **89/89 PASS** em Python 3.13.5 Debian PRoot + GitHub Actions (PR #17). `LicenseSubscription` **ainda ausente**. Cadastro PF/PJ, autenticação/convites e isolamento efetivo NÃO concluidos. Fase 2 NÃO concluída.

**Única base:** PG Termux 18.2, `frcaixinha_2_2_dev`, `frc22_owner`, `127.0.0.1:5432`, data dir `$PREFIX/var/lib/frcaixinha_2_2_pg18`. Conexão READ ONLY PASS; inspeção anterior encontrou 0 tabelas de aplicação regulares/particionadas, `alembic_version` ausente. **MIGRATION NÃO APLICADA; NÃO EXECUTAR SQL DE ESCRITA sem gate específico.**

**Backup Git C15:** AGE/scrypt com senha apenas em Termux; `FRcaixinha_2_2_C15_FINAL_0316c3cc29aa.bundle.age`, SHA256 `d77fc40bbedd54c98e04e5d92d87cc493c514dcfffe01340be3af6732a274919`; recuperação independente Git PASS; Drive privado file id `1KiryYKBrG4muW6VYE9f3wQEAS72obMeI`; byte-a-byte remoto PASS.

**Backup PG separado:** `frcaixinha_2_2_dev_20261018_173109_8123.dump.age`, SHA256 `95991140611c029d923e62baa05bcae3a4c0e8341fa5b1ac6ab11f5e7503b027`; integridade local/remota verificada, mas **restauração SQL NOT_RUN**.

**Falhas antigas com soluções:**

- PRoot aninhado → executar Debian `.venv` em sessão independente do Termux; Python 3.13.5 (não Python 3.14 auxiliar); não reinstalar pacotes.
- Alembic host mismatch → `host(inet_server_addr())`, guard PG18 estrito; escrita bloqueada por padrão.
- PostgreSQL antes não respondia → cluster original iniciado com preflight, agora acesso validado; **não criar novo cluster**.
- AGE prompt confuso → `git bundle create --quiet`; senha interativa privada.
- AGE `git bundle verify -` SIGPIPE 141 → `age -d "$PART" | { git bundle verify -; cat >/dev/null; }`.
- AGE `.partial` → apagar apenas parcial verificado, após consentimento; teste de recuperação Git bare e checksum Drive.
- Codex Cloud proxy `proxy:8080` falhava em 18/10; **ponte Cloud NÃO comprovada**; não burlar proxy, fallback Termux.

**Fluxo obrigatório:** Codex trabalha no escopo, PARA e relata falta de acesso; ChatGPT consulta ADR/ERR, prepara comando para Termux; proprietário executa em Termux/PRoot independente e envia saída; ChatGPT valida; Codex só retoma com resultado e gate vigentes. Erro resolvido vira ADR/ERR versionado, não memória informal.

**Próxima pendência IMEDIATA:** versionar **a atualização documental v1.1 e este cartão** por revisão Git própria no mesmo repositório (nenhum código/SQL); ainda não publicado na `main`. Só então discutir C16 auditoria pré-migration PostgreSQL somente leitura; upgrade/downgrade e qualquer DDL requerem autorização separada.

**Protocolo no novo chat:** confirmar acesso aos três documentos, citar último SHA, checar se houve checkpoint posterior e **não oferecer reinstalação, nova base, recuperação ou pesquisa repetida sem causa nova documentada**. Validar contratualmente qualquer nova proposta.
