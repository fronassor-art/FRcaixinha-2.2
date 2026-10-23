# C16-R12.123 — G3-C.4 / IN-01 e IN-02: matriz de provas OFFLINE

**Data:** 23/10/2026, America/Belem. **Issue:** #46. **Base Git examinada:** `main@2df05b027bd1f4fdf8c8eebea9344d264c5ae0e6`. **Escopo:** documento e testes unitarios sinteticos offline, sem SQL real, migration, REST, e-mail ou pagamento. **Estado deste pacote:** PROPOSTO PARA REVISAO, nao e aprovacao de implementacao transacional.

## 1. Marco anterior e fronteira de autorizacao

- G3-C.3: **PASS** no Termux conforme evidencias C16-R12.122R1 na Issue #46: restore AGE real em PostgreSQL 18 descartavel e isolado, 18 tabelas, Alembic `c16r5_20261020`, indices/constraints, parada/descarte, `MAIN_AFTER=PASS`, saida 0. Comparacao READ ONLY das contagens das 18 tabelas da origem: `SOURCE_DATA_PARITY=PASS`, saida 0. As 17 tabelas de negocio estavam vazias no snapshot; comparacao de contagens nao equivale a comparacao linha a linha de dados futuros.
- Banco unico autorizado: `frcaixinha_2_2_dev` em `127.0.0.1:5432`. Migration `f2p4_20261022` existe somente no codigo e **nao foi aplicada**. Preservar backups Git/AGE ja verificados; nao criar segundo ambiente persistente.
- PR #48 e um runbook antigo que ainda descreve dispensa temporaria do ensaio; sua afirmacao `NOT_RUN` foi superada pela prova C16-R12.122R1. Nao integrar a PR #48 como relato atualizado.
- Os testes deste pacote **nao** requerem PostgreSQL, nao conectam na base principal e **nao comprovam isolamento serializavel, concorrencia nem persistencia**. Avaliacao/DDL, adaptador SQL, migrations e ensaio transacional precisam de revisao e autorizacao especificas.

## 2. Evidencia de codigo utilizada

| Evidencia no baseline | Conclusao delimitada |
| --- | --- |
| `backend/app/identity_registration_offline.py` prepara PF com `pf_user_id=identity.id` e PJ com `representative_user_id=identity.id` | O objeto preparado associa identificadores, mas nao e a garantia de uma futura linha SQL |
| `backend/app/identity_persistence_contract.py` valida esses vinculos em `prepare_preliminary_write_intent` e expoe `PreliminaryRegistrationStore.commit_once` como protocolo | Ha verificacao offline antes da escrita; ainda nao existe prova de commit atomico |
| `backend/app/db/models.py` / `backend/migrations/versions/f2p4_20261022_auth_bootstrap_draft.py` trazem FKs isoladas `registration_idempotency.identity_id` e `party_id` | FKs separadas nao garantem que PF aponte para o mesmo `pf_user_id` nem que PJ aponte para o `representative_user_id` correto |
| `backend/app/initial_registration_bootstrap.py`: `InitialAttemptLookup.find_completed` e porta abstrata; um resultado negativo leva a preparacao de novo candidato | Dois candidatos podem ter mesmo `origin_digest`/`attempt_digest` e IDs diferentes antes de persistir; ainda falta arbitragem transacional |
| A minuta traz `UNIQUE(origin_digest, attempt_digest)` e `CHECK` para `RESERVED/COMPLETED` e TTL | UNIQUE pode arbitrar conflito na gravação, mas sozinho nao especifica retorno/reconsulta atomica, titularidade, reclamacao de reservas expiradas ou tratamento de falhas |

## 3. IN-01 — Vinculo identidade / parte e legitimidade

**Regra a provar na futura persistencia:** ao transformar tentativa em `COMPLETED`, `registration_idempotency.identity_id` deve corresponder **exatamente** ao `pf_user_id` da parte PF ou ao `representative_user_id` da parte PJ referenciada. As FKs devem continuar validas e nenhuma representacao PJ sera considerada verificada/APTA pela simples inscricao.

| Caso | Nivel | Criterio objetivo |
| --- | --- | --- |
| IN01-O1 | OFFLINE | Objeto PF validamente preparado aceita pre-intencao; substituicao de `pf_user_id` por outra identidade recusa com `WRITE_INTENT_INVALID` |
| IN01-O2 | OFFLINE | Objeto PJ validamente preparado aceita pre-intencao; substituicao de `representative_user_id` recusa com `WRITE_INTENT_INVALID` |
| IN01-T1 | PostgreSQL **NAO AUTORIZADO** | Uma tentativa `COMPLETED` com FKs individualmente validas mas cruzadas para outra identidade/parte deve ser impedida pelo mecanismo aprovado |
| IN01-T2 | PostgreSQL **NAO AUTORIZADO** | Concorrencia entre alteracao de representante PJ e conclusao de tentativa nao pode concluir com vinculo desatualizado |
| IN01-T3 | PostgreSQL **NAO AUTORIZADO** | Erro/rollback nunca deixa tentativa `COMPLETED` desvinculada nem linha parcial de identidade/parte |
| IN01-T4 | PostgreSQL **NAO AUTORIZADO** | PF nao preenche representante; PJ nao preenche `pf_user_id`; nenhuma tentativa cria papel financeiro, permissao ou aprovacao da representacao |

**Decisao tecnica ainda pendente:** comparar opcao de restricao composta com chaves unicas apropriadas, trigger transacional ou checagem com locking consistente; rejeitar solucao baseada apenas em `SELECT` anterior ao commit. Descrever exatamente a ordem de bloqueios, provas de serializacao, mudanca de representante e tratamento de erro antes de modificar migration. FKs compostas precisarao considerar PF/PJ e nulabilidade; nao presumir que bastem sem revisar o modelo.

## 4. IN-02 — Idempotencia transacional e replay seguro

**Regra a provar:** uma mesma combinacao de origem confiavel, chave de tentativa e fingerprint tem no maximo **um** cadastro concluido. Repeticao valida retorna IDs persistidos; mudanca de fingerprint/origem, expiracao, conflito ou tentativa de apropriacao nao cria identidade adicional nem devolve segredo de desafio.

| Caso | Nivel | Criterio objetivo |
| --- | --- | --- |
| IN02-O1 | OFFLINE | Dois lookups negativos para mesma tentativa produzem candidatos com mesmos HMACs e IDs provisorios diferentes; isto explicita o limite da interface |
| IN02-O2 | Historico offline ja coberto | `test_initial_registration_bootstrap.py` cobre replay `COMPLETED`, conflito por alteracao de origem/senha, expiracao, objeto de storage malformado e replay sem novo segredo |
| IN02-T1 | PostgreSQL **NAO AUTORIZADO** | 2+ transacoes concorrentes com mesma origem/chave/fingerprint: so um commit, demais retornam os mesmos IDs depois de reconsulta confiavel |
| IN02-T2 | PostgreSQL **NAO AUTORIZADO** | Mesma origem/chave e fingerprint diferente: conflito sem novo cadastro, sem IDs de terceiro e sem vazamento de dados |
| IN02-T3 | PostgreSQL **NAO AUTORIZADO** | Origens distintas nao compartilham replay por mero conhecimento de chave; digests e resolucao pertencem ao escopo confiavel |
| IN02-T4 | PostgreSQL **NAO AUTORIZADO** | Falha apos `RESERVED`, deadlock, conflito UNIQUE, timeout ou cancelamento: rollback/retentativa conforme politica aprovada, sem registro `COMPLETED` sem casal identidade/parte valido |
| IN02-T5 | PostgreSQL **NAO AUTORIZADO** | `COMPLETED` expirado e `RESERVED` expirado nao implicam apropriacao, reuso automatico inseguro ou exclusao sem politica de retencao |
| IN02-T6 | PostgreSQL **NAO AUTORIZADO** | Simultaneidade PF/PJ, CPF/e-mail/CNPJ pre-reservados e troca de representante nao permitem assumir identidade ou criar privilegio |

**Candidato de arquitetura, NAO DECIDIDO:** transacao unica de reserva/validacao/escrita/conclusao, arbitragem por UNIQUE e locking ou isolamento adequados, tratamento explicito do conflito (com savepoint/retry completo quando necessario) e reconsulta atomica do fingerprint e vinculos. O adaptador futuro deve evitar `SELECT` negativo seguido de `INSERT` nao protegido. Falhas de concorrencia devem preservar estados e nao depender de ordem conveniente do agendador.

## 5. Entregavel de testes e evidencia

Arquivo novo: `backend/tests/test_g3c4_in01_in02_offline.py`.

- `test_in01_pf_identity_link_matches_or_rejects_before_write`
- `test_in01_pj_representative_link_matches_or_rejects_before_write`
- `test_in02_two_negative_lookups_only_create_competing_candidates`

**Execucao proposta para revisão no ambiente ja existente**, sem instalar dependencias: `python -B -m pytest -q backend/tests/test_g3c4_in01_in02_offline.py` (a partir da raiz, se a configuracao de import existente suportar), ou `cd backend && python -B -m pytest -q tests/test_g3c4_in01_in02_offline.py`; validar primeiro interpreter/venv existente. Executar tambem os testes de regressao `test_identity_persistence_contract.py`, `test_initial_registration_bootstrap.py` e `test_identity_registration_offline.py` no mesmo ambiente, sem alterar a base. Registrar versao do codigo, comando e codigo de saida real; nao declarar teste executado apenas por sintaxe ou PR criada.

**Criterios para fechar esta subetapa:** revisao independente do diff, execucao dos 3 testes e regressao no executor autorizado, sem chamadas a PostgreSQL e sem alteracao do banco, comprovadas por evidencias. Esta subetapa nao fecha IN-01/IN-02 transacionais; esses seguem `BLOCKED` ate projeto e autorizacao especificos.

## 6. Governanca

Uma raiz Termux `~/FRcaixinha_2.2`, banco autoritativo unico, sem migration `f2p4`, sem ALTER/DDL/DML, sem reset de senha, sem segundo banco persistente, sem segredo em logs, sem merge automatico. GitHub branch e PR DRAFT sao apenas controle de mudancas do mesmo repositorio; preservar o backup Git e o dump AGE comprovados em G3-C.2/C.3. Em qualquer falha real, diagnosticar, corrigir minimamente e repetir antes de declarar PASS.
