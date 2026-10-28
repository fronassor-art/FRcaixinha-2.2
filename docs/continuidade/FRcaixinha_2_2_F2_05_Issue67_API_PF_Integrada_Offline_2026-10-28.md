# F2-05 / Issue #67 — API PF integrada, preparação offline

**Natureza:** nota técnica de implementação e proposta de persistência, não adendo normativo. Baseline Git `db14cc30091fa22fb90980fe7df9720640a8d2b3`; G2-F2-05-API-PF-INTEGRADA-R1. Nenhuma conexão PostgreSQL, migration, autenticação real, confirmação real ou concessão financeira integra este pacote. A Issue #67 permanece aberta até comprovar os gates aplicáveis.

## A. Contrato e componentes reutilizados

O Contrato Técnico Mestre 3.1-A exige nome/CPF, e-mail válido e confirmado, telefone com DDD; validação formal não prova titularidade. A seção 6.1-A trata ingresso de membro por convite e não autoriza criar Membership neste fluxo. IN06-R2 é proposta, não política de decisão positiva; IN08 ainda não define retenção física. O Adendo v1.2 citado em AGENTS.md não está versionado nesta árvore; prevalecem o contrato aprovado, AGENTS.md e os checkpoints vigentes, sem inferir decisão ausente.

| Requisito | Componente existente | Estado neste pacote |
|---|---|---|
| Formato e normalização PF | `identity_draft.prepare_person_draft` | Reutilizado pelo serviço; não é prova civil |
| Recebimento HTTP neutro | `pf_demo_api.create_demo_app` | Isolado, opt-in, HTTP 202 sem referência pública |
| Duplicidade/idempotência na instância | `TransientPreRegistrationStore` | HMAC efêmero, índices CPF/e-mail, lock e replay |
| Confirmação simulada | `PfPreRegistrationService` | Token efêmero; expiração, uso único, limite de cinco falhas de confirmação e revogação interna |
| CPF protegido para futura escrita | `identity_document_protection` / `crypto_documents` | Cifra AES-GCM e lookup HMAC já existentes; NÃO chamados pelo endpoint anônimo |
| Identidade e parte preliminares | `identity_registration_offline` | Preparação protegida, sem inserir ou ativar |
| Escrita com sujeito autenticado | `identity_persistence_contract` | Exige `ResolvedAuthSubject` e sessão confiável; não fabricar para candidato anônimo |
| Bootstrap e adaptador PG proposto | `initial_registration_bootstrap`, `g3c_initial_registration_pg` | Propostas existentes com credencial/challenge; não são persistência da demonstração |

A aplicação principal `app.main` não monta a rota PF. A tela Flutter local da PR #69 não consulta backend. A resposta 202 neutra protege status/corpo/cabeçalhos nos cenários testados, mas não prova resistência temporal ou contra abuso em infraestrutura real.

## B. Fluxo offline executável

1. A fábrica de demonstração cria um serviço e armazenamento próprios; o payload formal é validado e normalizado.
2. A chave de idempotência e os identificadores normalizados geram HMACs de domínios separados. A verificação de replay e duplicidade ocorre sob o mesmo lock. O retorno HTTP permanece neutro para solicitações formalmente válidas.
3. A referência e o token ficam apenas no serviço injetado. Não há rota pública de consulta, confirmação ou revogação. O token simulado pode expirar, ser consumido uma vez, bloquear após cinco falhas de confirmação ou ser revogado internamente com o segredo válido. A revogação não tem contador próprio de tentativas e não é exposta por HTTP. Nenhuma dessas transições comprova posse real de contato.
4. Falhas inesperadas do validador ou armazenamento são reduzidas a erro genérico sem ecoar dados pessoais; a solicitação não concede identidade, sessão, papel, tenant, licença, membro ou finanças.

A instância transitória não oferece durabilidade, coordenação entre processos, retenção aprovada ou custódia de chave. Seu HMAC efêmero não deve ser reutilizado como índice persistente. Não há status privado consultável por mera referência.

## C. Proposta de persistência no PostgreSQL único — NÃO EXECUTADA

A rota anônima atual não pode chamar `prepare_preliminary_write_intent`: este contrato exige sujeito e sessão verificados, indisponíveis no pré-cadastro. Também não pode chamar `g3c_initial_registration_pg` como se fosse a gravação desta solicitação: esse adaptador proposto escreve `UserIdentity`, `ContractingParty`, credencial e desafio sob transação externa, com origem, chaves e confirmação ainda não operacionais.

Para persistência futura, definir em G2 separada qual fronteira será aprovada:

- **Após autenticação confiável:** reutilizar `UserIdentity` (CPF cifrado, lookup HMAC único, e-mail único por índice funcional), `ContractingParty` preliminar e `PreliminaryRegistrationStore`; resolver F2-07, origem da sessão, IN06 e consentimento aplicável antes de escrever.
- **Solicitação anônima durável, se exigida:** propor migration Alembic própria, sujeita a revisão, para armazenar somente referência interna, digests separados de origem/idempotência/CPF/e-mail, payload mínimo cifrado, estado preliminar, desafio protegido e metadados estritamente necessários. Não incluir segredo em claro nem conceder vínculo operacional. Chaves devem vir de custódia aprovada, com rotação/recuperação e acesso restrito. Prazos de expurgo dependem de IN08; TTL de token não define retenção.
- Em ambos os casos, usar uma transação lógica por operação, `UNIQUE` e tratamento de conflito concorrente no PostgreSQL, locks ou `INSERT ... ON CONFLICT` revisados, comparação de fingerprint sem eco de PII, replay durável entre processos/reinícios e falha fechada em erro de armazenamento. A reserva expirada não deve ser reapropriada por suposição: os índices únicos atuais de `registration_idempotency` são permanentes, mesmo após expiração.
- Confirmar em gate físico separado a revisão Alembic efetiva, existência de constraints e testes sintéticos em transações com duas conexões, concorrência, rollback, replay, isolamento tenant/ciclo quando houver vínculo, rotação de chave e falhas parciais. Antes de qualquer migration real: G2 de banco, backup PostgreSQL separado e recuperação validada.

O projeto já contém a minuta `f2p4_20261022_auth_bootstrap_draft.py` e testes offline do adaptador `g3c_initial_registration_pg.py`. Este pacote não altera nenhum dos dois. Não há prova nesta G2 de que o esquema físico autoritativo coincide com os metadados ORM.

## D. Critérios A–G da Issue #67

| Critério | Resultado desta G2 | Limite para aceite integral |
|---|---|---|
| A — diagnóstico | PASS por inspeção de contrato, modelos, rotas e adaptadores | Revisar Adendo externo se trouxer regra aplicável |
| B — endpoint/serviço | PASS apenas na demonstração isolada | Consulta autenticada e API operacional dependem F2-07 |
| C — segurança/dados | PASS offline para HMAC efêmero, resposta neutra e negativas | Custódia de chaves, prova civil e concorrência PG pendentes |
| D — confirmação/transições | PASS apenas para token simulado; revogação interna adicionada | Canal verificável real, aceite e IN06/IN08 pendentes |
| E — persistência | PREPARADA por proposta e reuso identificado, não executada | Schema/migration se necessária, transações PG e testes físicos sob G2 |
| F — testes | PASS na demonstração offline: Master executou HTTPX/ASGI direcionado, `570/570` testes e `pip check` no Python Debian 3.13.5 antes do commit, com SHA-256 dos arquivos conferidos; [Backend CI 40714092011](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40714092011) no head `0c7ae5ea4af8c543b956e2ff9bbf1f399151cb0c` confirmou `570/570` e dependências PASS; [signal 40714092028](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40714092028) PASS | Testes físicos PostgreSQL, autenticação real e proteções operacionais ainda não executados; não extrapolar os testes offline |
| G — integração/proteção | PARCIAL: commit/push e [PR #70](https://github.com/fronassor-art/FRcaixinha-2.2/pull/70) OPEN com 3 arquivos; CI PASS e revisão independente somente leitura, com restrições offline | G2 específica de merge, sincronização Termux, regressão pós-merge e AGE consolidado recuperável/offsite pendentes |

Esta matriz registra os resultados oficiais e CI do head de código `0c7ae5ea4af8c543b956e2ff9bbf1f399151cb0c`. O presente ajuste é exclusivamente documental: não altera os dois arquivos Python nem implica repetição de CI sobre um SHA documental posterior. Não declarar testes no novo SHA se não forem executados; os blobs de código devem ser comparados no checkout. `DEMO_READY` não equivale a `OPERATIONAL_READY`; a Issue #67 não pode ser encerrada por este pacote isolado.
