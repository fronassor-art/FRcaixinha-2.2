# C16-R12.105 — ADR Fase 2/Pacote 5: paridade ORM × minuta Alembic (OFFLINE)

**Data:** 22/10/2026. **Issue:** #44. **Baseline de entrada:** `df5a6788b249b887f1e07f7459c6605aff881a75`. A migração `f2p4_20261022` **não** está aplicada em banco. O último estado PostgreSQL 18.2 auditado somente leitura, C16-R12.99, tinha `alembic_version=c16r5_20261020`, 18 tabelas incluindo `alembic_version`, 0 índices inválidos e 0 constraints não validadas.

## Decisão de escopo

Introduzir **somente** as quatro declarações ORM em `backend/app/db/models.py`, sem criar outros serviços, bancos, sessions, login, chave real, integração API ou migration. A minuta `backend/migrations/versions/f2p4_20261022_auth_bootstrap_draft.py` continua congelada **neste pacote** para que a paridade se faça contra um artefato independente; C15/C16 também permanecem congeladas. O programa Alembic `env.py` faz referência a `Base.metadata`; os quatro modelos são declarativos e não acessam PostgreSQL.

| Tabela | Modelo ORM | Chaves e contratos declarados |
| --- | --- | --- |
| `identity_credentials` | `IdentityCredential` | FK identity, UNIQUE identity_id, status e digest `scrypt` |
| `email_confirmation_challenges` | `EmailConfirmationChallenge` | FK identity, UNIQUE verifier, expiração 10min e não-consumo simultâneo com revogação |
| `registration_idempotency` | `RegistrationIdempotency` | UNIQUE origin/attempt, FKs identity e contracting_party, TTL 15min, estado reservado/concluído |
| `identity_sessions` | `IdentitySession` | FK identity, UNIQUE verifier, TTL ≤15min, revogação |

As novas classes estão no **mesmo** `Base.metadata` dos 17 modelos anteriores, totalizando 21 tabelas em memória. Um modelo ORM na memória não representa uma tabela criada no banco. O único PostgreSQL autoritativo continua com a estrutura C15/C16 até uma autorização futura.

## Testes propostos

`test_db_auth_bootstrap_orm_parity.py` renderiza `revision.upgrade()` com `MigrationContext(dialect_name="postgresql", as_sql=True)` e compara as declarações com `CreateTable`/`CreateIndex` SQLAlchemy sem conexão. A normalização textual remove apenas diferenças de espaços, ordem de linhas de constraints e escape de % para efeito de comparação. Os testes C15/C16 preservam as verificações da história e dos artefatos congelados, agora distinguindo 17 tabelas anteriores das quatro novas. `test_db_auth_bootstrap_migration_draft.py` continua certificando que nada é aplicado ou conectado.

**Limite probatório:** compilação de SQL e testes unitários não demonstram DDL executada em PostgreSQL, concorrência, unicidade em transações, políticas de acesso, isolamento multi-tenant, recuperação de dados, retenção LGPD, revogação persistida ou rollback real.

## Gaps BLOQUEANTES para aplicar a migration, não para revisar a paridade offline

1. `registration_idempotency` tem FKs independentes para identity e contracting_party; elas não certificam que PF está vinculada à mesma identidade ou que PJ tem o representante correto. Exigir desenho de integridade atômica com provas/testes, sem aceitar claims cliente.
2. `email_confirmation_challenges` não guarda o e-mail da época de emissão; o algoritmo offline vincula a mensagem ao e-mail, mas um adaptador real deve recuperar/revalidar contato e finalidade de fonte confiável **na mesma transação de consumo único**. Replay, corrida e mudança de e-mail ainda não são testados no banco.
3. `registration_idempotency` exige guarda de corridas sob UNIQUE, reconsulta segura, fingerprint da requisição, escopo confiável e limpeza de reservas expiradas. O prazo de 15 minutos no CHECK não elimina registros automaticamente. Política LGPD de retenção, desbloqueio de CPF/e-mail PENDENTE legítimo e abuso devem ser aprovados.
4. `identity_credentials` ACTIVE, `user_identities` ATIVA e e-mail confirmado exigem coerência na camada transacional; nenhuma mudança de status habilita papel, licença, Pix ou direito financeiro. Credenciais e sessões só podem operar com keyring e autenticação reais previamente autorizados.
5. O `downgrade` proposto executa DROP TABLE das quatro novas estruturas: é destrutivo de dados futuros. Exigir backup PostgreSQL atual, ensaio de recuperação especificamente autorizado, plano de reversão e janela antes de qualquer tentativa real. Git AGE protege **código**, não dados PG.
6. Aplicações da migration, `alembic upgrade/downgrade/stamp`, SQL DDL/DML, base paralela persistente, chaves em produção, envio e-mail/SMS, login público e operações financeiras permanecem **BLOQUEADOS**.

## Checkpoint de proteção

Backup Git base `FRcaixinha_2_2_C16_R12_103_df5a6788b249.bundle.age`, SHA256 `363dbcdd3867c4184b8d7acab5091ff8562a3e61b0fa6a00680d78f4ab514d52`, cópia privada Drive ID `1sRWLNudxbERLlc2VXTOjEAwtArSxbjNC`, reportada verificada em C16-R12.104. Não recriar backup do PostgreSQL por reflexo nem executar restauração sem autorização própria.

**Gate:** pacote P5 = paridade ORM **proposta, sujeita a CI oficial no SHA final e auditoria independente**. Gate G3-C para migrar PostgreSQL permanece NÃO AUTORIZADO; G3-D/G3-E não iniciados.
