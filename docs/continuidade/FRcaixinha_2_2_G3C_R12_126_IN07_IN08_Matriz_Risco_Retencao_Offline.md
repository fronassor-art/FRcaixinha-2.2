# C16-R12.126 — G3-C.4 / IN-07 e IN-08: downgrade e retenção OFFLINE

**Data:** 23/10/2026 (America/Belem). **Referência de governança:** Issue #46. **Baseline:** `main@b1ff819eed23788b3e56df1da284bd458d3f55a3`. **Estado:** PROPOSTO PARA AUDITORIA INDEPENDENTE; não autoriza merge, SQL real, Alembic upgrade/downgrade/stamp ou expurgo.

## 1. Contexto e separação das evidências

Este é o último par da lista de **oito invariantes** IN-01 a IN-08 do G3-C.4, não o encerramento dos testes financeiros, testes reais de concorrência/SQL ou fases G3-D/G3-E. Até este checkpoint:
- IN-01/IN-02 **offline**: PR #49 integrada em `b1ff819eed23788b3e56df1da284bd458d3f55a3`; PostgreSQL transacional segue BLOCKED.
- IN-03/IN-04: PR #50 DRAFT, CI #39940783041 **318/318 PASS** sobre a `main` anterior, ainda sem auditoria independente formal/merge.
- IN-05/IN-06: PR #51 DRAFT, CI #39941508196 **318/318 PASS** sobre essa mesma `main`, ainda sem auditoria independente/merge.
- Este IN-07/IN-08 parte de **main**, não das PRs #50/#51: até integrá-las e rodar CI cumulativo não se pode atribuir ao repositório os 10 + 10 casos ainda pendentes.

Banco autoritativo único: `frcaixinha_2_2_dev`, Termux PostgreSQL 18.2, Alembic comprovado em checkpoint anterior `c16r5_20261020`. O arquivo `backend/migrations/versions/f2p4_20261022_auth_bootstrap_draft.py` é **minuta de código, não migration aplicada**. Nenhum SQL real ou inventário novo do banco foi executado para esta proposta. O ensaio G3-C.3 de restauração AGE foi PASS, mas não justifica downgrade destrutivo.

## 2. IN-07 — rollback seguro, sem destruição automática

Na minuta F2P4, `downgrade()` contém três `op.drop_index` e quatro `op.drop_table` para as tabelas: `identity_sessions`, `registration_idempotency`, `email_confirmation_challenges`, `identity_credentials` (ordem inversa da criação). Embora não utilize `CASCADE` nem remova as tabelas históricas `user_identities`/`contracting_parties`, **DROP TABLE apaga os registros que a tabela já contenha**. Inexistência de linhas não pode ser presumida em operação futura. Um downgrade de esquema não é restauração de dados.

| ID | Evidência pretendida | Gate |
| --- | --- | --- |
| IN07-O1 | Compilar `downgrade` offline e comprovar exatamente quatro `DROP TABLE`, três `DROP INDEX`, ordem inversa e ausência de `CASCADE` | Teste offline do risco |
| IN07-O2 | Constatar que o código do downgrade não tem verificação de contagem de linhas nem cópia dos dados; sua compilação não contém `INSERT/COPY` recuperável | **Contraexemplo**: não prova segurança nem rollback real |
| IN07-O3 | Compilar upgrade e downgrade e mostrar que `CREATE TABLE` seguida de `DROP TABLE` não preserva os dados inseridos entre ambas | **Contraexemplo** |
| IN07-T1 | Antes de aplicar F2P4, aprovar procedimento que **vete downgrade destrutivo automático**, proponha correção forward, reconciliação ou recuperação autenticada de backup conforme cenário | PostgreSQL, BLOQUEADO |
| IN07-T2 | Exercitar falhas, bloqueios, transações e recuperação real em executor isolado autorizado, preservando dados e avaliando consistência dos dados posteriores ao backup | PostgreSQL, BLOQUEADO |

**Decisão operacional futura, não implementada:** proibir uso rotineiro de `alembic downgrade` que elimine tabelas com dados. Em incidente, diagnosticar causa e preferir migration corretiva forward. Qualquer restauração de backup pode sobrescrever alterações posteriores e requer plano de reconciliação e autorização próprios; o backup G3-C.3 não constitui autorização para isso. **Não alterar histórico congelado** ou minuta no âmbito desta PR; eventual mudança exige nova migration/projeto de aprovação específica.

## 3. IN-08 — validade não equivale a retenção física

Os CHECKs de F2P4 e os modelos definem TTL **máximo do intervalo emissão–expiração**, não exclusão automática:
- `email_confirmation_challenges`: `issued_at` a `expires_at`, no máximo **10 minutos**;
- `registration_idempotency`: `created_at` a `expires_at`, no máximo **15 minutos**;
- `identity_sessions`: `issued_at` a `expires_at`, no máximo **15 minutos**.

Eles não impedem que uma linha **já expirada permaneça fisicamente armazenada**. Os índices em `expires_at` melhoram buscas, mas **não constituem jobs**. As UNIQUE de verificadores e de `(origin_digest, attempt_digest)` continuam válidas independentemente do estado de expiração. O relógio confiável do banco, retenção aprovada e controle transacional são exigências futuras.

| ID | Evidência pretendida | Gate |
| --- | --- | --- |
| IN08-O1 | Verificar CHECKs de prazo em metadados ORM; não há `DELETE` nem relógio corrente nas expressões | OFFLINE |
| IN08-O2 | Índices de expiração existem para três tabelas, mas não implementam expurgo | OFFLINE |
| IN08-O3 | UNIQUE continua geral, sem predicado de `expires_at`: não libera reserva expirada | OFFLINE |
| IN08-O4 | Exemplo puramente em memória mostra reserva `RESERVED` expirada continuando na coleção | **Contraexemplo**, não comprova PostgreSQL |
| IN08-O5 | Desafio expira exatamente aos 10 minutos; sessão expira exatamente aos 15 minutos nos contratos offline, mesmo que o stub ainda retenha registro | OFFLINE |
| IN08-T1 | Provar que consumo/replay inválidos expiram no limite usando hora confiável, sem apagar evidência requerida | PostgreSQL, BLOQUEADO |
| IN08-T2 | Autorizar política de retenção física por finalidade/base legal, ciclos de expurgo limitados e auditados, com tratamento de `RESERVED` abandonado, concorrência, replicação de backups e bloqueios de conta | Jurídico + PostgreSQL, BLOQUEADO |
| IN08-T3 | Corridas entre limpeza e validação/consumo, reuso de chaves, restauração de backup, processos concorrentes e falhas parciais não provocam duplicação ou apropriação de identidade | PostgreSQL, BLOQUEADO |

**Retenção jurídica ainda não aprovada:** não inventar prazo de dias ou meses, nem usar TTL de 10/15 minutos como prazo legal para eliminação. HMACs, verificadores e registros pseudonimizados continuam sujeitos à avaliação de privacidade quando reidentificáveis. Nunca apagar documentos, eventos financeiros, evidência de consentimento ou arquivos AGE que devam ser preservados. Nenhum comando `DELETE`, cron ou serviço de limpeza é criado nesta PR.

## 4. Entrega técnica limitada

Arquivos novos nesta PR:
1. `backend/tests/test_g3c4_in07_in08_offline.py` — **11 testes `unittest`** que compilam a minuta Alembic em memória, inspecionam constraints/índices e exercitam expiração sintética. Os casos verdes relativos a perda de dados/ausência de limpeza são **provas das lacunas**, não certificações de segurança operacional.
2. `docs/continuidade/FRcaixinha_2_2_G3C_R12_126_IN07_IN08_Matriz_Risco_Retencao_Offline.md` — esta matriz.

Execução pretendida no executor Python compatível já existente, a partir de `backend/`:

```bash
python -B -m unittest discover -s tests -p 'test_g3c4_in07_in08_offline.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

`unittest` pertence à biblioteca padrão. O CI executará o segundo comando; somente relatório real de CI no SHA exato permite declarar testes executados. Não instalar `pytest`. Não modificar `backend/app/`, `backend/migrations/`, `backend/requirements.txt`, esquemas, ferramentas, segredos ou credenciais.

## 5. Gates de integração e política de backup

A PR será **DRAFT, NOT_MERGED** até auditoria independente PASS, correções de qualquer erro, CI PASS no HEAD exato e autorização expressa do proprietário. Quando #50, #51 e esta PR forem sendo integradas, **atualizar a base da PR seguinte com cuidado e verificar o conjunto cumulativo de testes no novo baseline**. Não extrapolar `318/318` isolado como `338/338` combinado sem executar de fato.

**Política acordada:** adiar **novo backup geral consolidado** até a conclusão validada do ciclo offline IN-01…IN-08; manter backups AGE Git e PostgreSQL anteriores já verificados e checkpoints Git/CI. Não confundir commits com backup de dados. Se algum passo futuro envolver migration, intervenção estrutural, limpeza ou outro risco, a cópia preventiva recuperável permanece obrigatória antes desse passo. Conclusão offline de IN-08 por si só não autoriza nenhum desses atos nem a migração F2P4.

**Resultado documental previsto:** cobertura offline de oito invariantes após integrações e CI cumulativo, ainda com todas as provas SQL reais, política jurídica de retenção e G3-C.5 BLOQUEADAS. Esta entrega não altera o PostgreSQL e não encerra globalmente G3-C.
