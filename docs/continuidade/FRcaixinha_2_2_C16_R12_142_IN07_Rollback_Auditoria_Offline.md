# C16-R12.142 — Correção de senha e auditoria de rollback IN-07 (OFFLINE)

**Data:** 23/10/2026 (America/Belem)<br>
**Issues/PRs:** #46, #55 (código DRAFT), #54 (plano DRAFT)<br>
**Baseline autoritativo:** `main@751da8f8f380fc45d58de68cf707a3c2f9149777` (sem merge).<br>
**Banco principal:** PostgreSQL 18.2 `frcaixinha_2_2_dev`, Alembic `c16r5_20261020`, F2P4 **NÃO AUTORIZADA/APLICADA**.

## 1. Falha reproduzida, causa e correção mínima (IN-02)

**Vulnerabilidade sintética:** o futuro escritor de cadastro `g3c_initial_registration_pg.py` validava `PasswordDigest.encoded` só por tipo, tamanho e prefixo `scrypt$v1$`. Uma string com salt/hash codificados inválidos passava a guarda de pré-escrita e chegava a `connection.execute`. O CHECK do banco de dados da F2P4 também aceita o mesmo prefixo e não garante a estrutura do hash; portanto a confiança exclusiva nessa coluna não seria segura.

**Teste primeiro:** novo `test_prepared_digest_with_fake_scrypt_fields_is_denied_before_sql`. [CI #39963721059](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/39963721059) no commit `ad84dbe2426f0160a6fa6cf033feba7ea285efac` reproduziu a falha: `Ran 416 tests`, `FAILED (failures=1)`; `connection.execute` havia sido chamado.

**Correção mínima:** reutiliza `_decode_digest` já existente em `app.offline_credentials` para validar versão, parâmetros scrypt, salt/resultado em base64, tamanho e forma antes de qualquer SQL. A fixture agora usa salt e hash sintéticos **com estrutura correta** (não credencial real). Nenhum teste removido. [CI #39963902300](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/39963902300), HEAD `1e4c7f6da0a4ae3df7e5b671587a995bd71bad24`: `No broken requirements found`, `Ran 416 tests in 2.612s`, `OK`. **416/416 PASS**.

**Limite explícito:** `_decode_digest` prova apenas formato; **não prova** origem confiável nem posse da senha, nem substitui scrypt em autenticação. O writer continua desabilitado fora da PR.

## 2. Inventário IN-07 — downgrade destrutivo ainda existe

`backend/app/g3c_f2p4_rollback_audit_offline.py` introduz inspeção AST **somente leitura** de `f2p4_20261022_auth_bootstrap_draft.downgrade`, retornando relatório `DowngradeRisk`. Não é mecanismo de proteção instalado no Alembic. Declara **`authorized_to_execute=False` incondicional**, e a função proposta de política `require_nondestructive_approval` falha fechada, mas **não é invocada por Alembic**.

O inventário identifica, na ordem real de downgrade:
- **Quatro DROP TABLE**: `identity_sessions`, `registration_idempotency`, `email_confirmation_challenges`, `identity_credentials`.
- **Três DROP INDEX**: `ix_identity_sessions_identity_expires`, `ix_registration_idempotency_expires`, `ix_email_confirmation_challenges_identity_expires`.

`backend/tests/test_g3c_f2p4_rollback_audit_offline.py` adiciona 7 testes: enumeração dos riscos, bloqueio mesmo de um downgrade fictício vazio sem autorização, chamadas dinâmicas/desconhecidas tratadas como não verificadas, dados inválidos, e ausência de execução física de operações `op.drop_table`/`op.drop_index` ou conexão PostgreSQL durante inspeção.

A minuta original F2P4 e os **testes históricos aprovados** `test_db_auth_bootstrap_migration_draft.py` e `test_g3c4_in07_in08_offline.py` **não foram alterados**. Eles deliberadamente demonstram risco ao renderizar os DDL offline. Não mascarar isso como segurança operacional.

**CI acumulada:** [run #39964432423](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/39964432423) no commit `29aa6a0bd8925f6ed79404f28fda3f08b0f0f6d8`: `pip check` PASS, `Ran 423 tests in 3.525s`, `OK`, job success. Total = **339 testes offline históricos + 84 novos**.

## 3. Pacote de revisão independente — deve ser feito fora desta autoria

Este relatório é **autorrevisão**, não parecer independente do Codex. Solicitar ao Codex Cloud autorizado, usando o SHA da PR #55 da hora do teste, ao menos:

1. Revisar `g3c_initial_registration_pg.py` para origem server-side confiável de `InitialRegistrationIntent`, fingerprint/HMAC, unicidade de CPF/e-mail/CNPJ, `ON CONFLICT`, `RESERVED` expirado, duas sessões concorrentes, savepoint, transação **externa** e resultado devolvido antes do commit.
2. Revisar `g3c_completed_replay_pg.py`, `g3c_session_pg.py` e `g3c_email_confirmation_pg.py`: ordem de locks, `FOR UPDATE`/`FOR SHARE`, relógio após espera, e-mail A→B→A, credencial alterada, concorrência contra suspensão, falha parcial, consumo único, atualização `email_verified_at`.
3. Validar **sem aplicar no banco principal** as propostas DDL `g3c_updated_at_trigger_plan_offline.py` e `g3c_artifact_invalidation_plan_offline.py`: PG18 trigger order, deadlocks, row-level locks, timestamps e recursão de UPDATE; migração corretiva apropriada após F2P4 sob aprovação expressa.
4. Concluir se é necessária troca do `downgrade` destrutivo por bloqueio efetivamente instalado na migration, migration de compensação forward-only, ou outro procedimento provadamente recuperável. A **auditoria AST não protege o comando Alembic**.
5. Auditar limites jurídicos/antifraude IN-06/IN-08 de identidade PF/PJ e retenção/expurgo: **não inventar** política legal nem reatribuir CPF/CNPJ por TTL; identificar decisões que exigem aprovação do proprietário.
6. Exigir teste integrado com PostgreSQL **efêmero isolado**, separado do banco principal, autorizado previamente; demonstrar 2+ conexões e locks, deadlock/retry, idempotência, rollback, restauração e limpeza efêmera, não substituir por mocks.
7. Preservar 339 testes anteriores, não remover falhas, validar dependências pinadas com `pip check`, `unittest discover` e revisar diff/CI no SHA exato.

**Parecer esperado:** `PASS/FAIL/BLOCKED` por item com evidência, problema reproduzido, correção mínima, reteste e regressões. Revisão independente ainda **NOT_RUN**. A CI GitHub não equivale à auditoria do Codex.

## 4. Portões ainda pendentes

- **IN-07 NÃO RESOLVIDO operacionalmente:** `downgrade` F2P4 existente é destrutivo; proposta de auditoria não está conectada ao Alembic. Alteração da migration exige proposta técnica + revisão/decisão específicas.
- **IN-05 NÃO RESOLVIDO operacionalmente:** triggers de timestamps/revogação somente propostos como strings. Possível inversão de locks/deadlocks; sem teste real PostgreSQL.
- **IN-02/03/04:** código preparatório e testes unitários/SQL compilado, sem PostgreSQL/concorrência real; não há API ativa.
- **IN-06/08:** retenção jurídica, contestação/titularidade PF-PJ e destinação de reservas não aprovadas; não promover ou apagar dados.
- **F2P4:** não autorizada, não aplicada. Nenhuma mudança no PostgreSQL/Termux/main ou backup consolidado nesta entrega.

**Sequência aprovada pelo proprietário:** fechar desenvolvimento/testes offline → auditoria independente/autorizações → integração GitHub/Termux/checkup e ensaios PG específicos autorizados → backups consolidados Git/PG AGE com prova de restauração e Drive. Backups C16-R12.131/132R1/136 continuam preservados. Backup preventivo antes de risco estrutural autorizado continua obrigatório.

## 5. Nota posterior — C16-R12.161 (23/10/2026)

As referências acima aos quatro `DROP TABLE` e três `DROP INDEX` descrevem o downgrade **histórico** da F2P4 na época deste checkpoint. Elas permanecem como contraexemplo auditável, não como comportamento executável atual. A correção C16-R12.147 foi consolidada no commit `c4709eeb9bd6e9d38af929fc958c9698d58fb5db`: a função executável `downgrade()` da F2P4 agora lança `RuntimeError("F2P4_DOWNGRADE_NOT_AUTHORIZED")` antes de qualquer DDL. A auditoria C16-R12.160 confirmou esse comportamento no commit `c3b8936bb498a0aa935195a0472f6c1a63df9958`.

A [Backend CI #40036882864](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40036882864) concluiu com `SUCCESS` no commit `c3b8936bb498a0aa935195a0472f6c1a63df9958`, com **446 testes** conforme a evidência da execução. A PR #55 permanece **draft, aberta e sem merge**.

O bloqueio do `downgrade()` **não autoriza** o `upgrade()` F2P4, não comprova rollback físico no PostgreSQL e não habilita uso operacional. Provas reais de locks, concorrência, SAVEPOINTs, triggers e rollback ainda dependem de autorização específica. As limitações contratuais, jurídicas e financeiras históricas acima permanecem válidas.
