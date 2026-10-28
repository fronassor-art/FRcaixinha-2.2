# F2-05 / Issue #67 — preparação de persistência PF offline R1

**Escopo:** proposta técnica executável isolada para revisão; baseline `main@8643f13466d57e6d38d4db418c00b8d59e279167`. Não há rota nova, conexão PostgreSQL real, migration, DDL/DML, cadastro, contato ou autenticação operacional. A Issue #67 permanece aberta.

## Reuso e fronteiras

| Necessidade | Componente já existente | Uso nesta R1 |
| --- | --- | --- |
| Dados PF protegidos | `identity_registration_offline`, `identity_document_protection`, `crypto_documents` | `PreparedRegistration` validado; CPF cifrado com AAD e lookup HMAC conferidos novamente antes da escrita proposta |
| Sujeito confiável | `trusted_auth_subject`, `offline_credentials` | Assertion verificada por porta injetada, sessão atual pelo relógio PostgreSQL da transação; UUID do sujeito deve ser o UUID da identidade preparada |
| Contrato preliminar | `identity_persistence_contract` | Reusa `prepare_preliminary_write_intent` e `PreliminaryCommitResult`; não trata `ResolvedAuthSubject` construído de campos anônimos como prova |
| Transação e replay | `g3c_pg_transaction_guard`, `g3c_completed_replay_pg`, `RegistrationIdempotency` | Exige conexão PostgreSQL/psycopg dentro de transação externa, reserva `ON CONFLICT DO NOTHING`, SAVEPOINT, replay verificado e conclusão condicional |
| Esquema | `UserIdentity`, `ContractingParty`, `RegistrationIdempotency` e F2P4 | Somente SQLAlchemy compilado; nenhuma tabela, coluna ou migration nova nesta proposta |

O adaptador `pf_preliminary_persistence_pg.py` recebe conexão e dependências explicitamente. Ele não abre conexão, não faz `commit()` ou `rollback()` externo e não é importado por `app.main` nem pela API demonstrativa anônima. Sua única escrita proposta insere `UserIdentity.status=PENDENTE`, `ContractingParty.status=PRELIMINAR` e uma tentativa idempotente `COMPLETED`. Não cria credencial, desafio de e-mail, `RoleGrant`, `Membership`, `Tenant`, licença ou operação financeira. O retorno é interno e nunca contém token de contato.

O digest de origem, tentativa e fingerprint usa HMAC de domínios separados com chave de servidor injetada, nunca material claro persistido no registro idempotente. O fingerprint usa o lookup HMAC de CPF e os campos PF normalizados; ciphertext aleatório não altera replay. A chave de documento e a chave de digest precisam de custódia, rotação e recuperação aprovadas antes de uso real. A resolução do sujeito requer verificador de assertions confiável de F2-07; **nenhuma sessão é fabricada por este pacote**. A vinculação `auth.subject_id == identity.id` limita esta proposta a uma origem confiável que consiga afirmar o UUID definitivo de identidade ainda não inserida; o fluxo operacional para prover esse fato continua pendente.

## Constraints e falhas

O ORM e a revisão Alembic F2P4 já possuem unicidade de CPF lookup, e-mail em `lower(email)`, `auth_subject` e `(origin_digest, attempt_digest)`; há FK composta de replay para a parte e identidade e CHECKs de estados e duração. Nenhuma alteração física é proposta nesta R1. A presença real dessas constraints no PostgreSQL autoritativo **não foi conferida nesta G2**. O mesmo esquema também é usado pela proposta `g3c_initial_registration_pg`; os HMACs têm domínio PF distinto para evitar colisão de escopo.

Uma reserva concorrente preexistente só pode retornar IDs após `fetch_verified_completed_replay`, conferência do UUID autenticado, `auth_subject` persistido e sessão ainda válida. `RESERVED` anterior, fingerprint divergente, erro SQL ou duplicidade CPF/e-mail negam a operação com erro interno neutro; nenhuma reserva expirada é reapropriada. Falha após reserva ou INSERT sai do contexto de SAVEPOINT por exceção. O chamador continua responsável por decidir o COMMIT/ROLLBACK da transação externa e por manter a assertion/sessão confiável. Testes com mocks verificam a sequência de controle, **não** provam atomicidade ou concorrência física.

## Testes e gates

O novo teste `test_pf_preliminary_persistence_pg_offline.py` cobre SQL compilado, replay/fingerprint, reserva concorrente simulada por conflito, CPF/e-mail duplicados por falha injetada, sessão inválida/expirada/revogada, documento adulterado, falha de cripto, SAVEPOINT e ausência de acesso. Validação oficial no Debian PRoot, Python 3.13.5: **14/14 testes PF PASS** (0 erros, 0 falhas; 0.209s), **regressão completa 584/584 PASS** (0 erros, 0 falhas; 5.904s) e **pip check PASS** (sem requisitos quebrados). Os dois erros iniciais dos subtestes de CPF e e-mail duplicados foram corrigidos exclusivamente no mock de uuid4, alinhando o identificador simulado à reserva esperada. A proteção PF_WRITE_DENIED permaneceu inalterada. Os resultados são sintéticos e não comprovam persistência física PostgreSQL. O Python Termux deste executor não possui `cryptography`; nenhuma instalação é autorizada. Não há ensaio físico PostgreSQL.

Para ativação futura são necessários G2 separados para verificador/sessão F2-07 e emissão segura do UUID definitivo, custódia de chaves, política de titularidade/contestação IN06, retenção/expurgo IN08, validação de schema físico e concorrência em duas conexões, revisão de segurança e eventual integração por PR. TTL de 15 minutos da reserva não define retenção legal. O backup consolidado está adiado pelo Master; esta R1 não o solicita nem gera.
