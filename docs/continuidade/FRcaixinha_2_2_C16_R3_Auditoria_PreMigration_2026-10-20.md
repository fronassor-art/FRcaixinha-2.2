# FRcaixinha 2.2 — C16-R3 — AUDITORIA PRÉ-MIGRATION

**Emissão:** 20/10/2026. **Natureza:** relatório técnico e contratual de análise; **não é ordem de execução**.  
**Escopo:** conferência de requisitos de licenciamento, schema inicial C15, recuperação de PostgreSQL e critérios de gate; nenhuma modificação de repositório ou banco foi realizada nesta auditoria.

## 1. Identificação e evidências verificadas

- **Repositório:** `fronassor-art/FRcaixinha-2.2`.
- **`main` de referência:** `01b33a2dce5e57ed2108e58c1ea2975f8220a23d` (merge da PR #18, somente documentação). Não confundir com o SHA histórico `0316c3cc29aa` do código C15.
- **Migração inicial:** `backend/migrations/versions/c15r2_20261020_initial_schema.py`; `revision='c15r2_20261020'`; `down_revision=None`; 15 tabelas e 18 índices declarados. DDL congelado e ordenado por dependências, `upgrade()` executa SQL `CREATE`; `downgrade()` ordena `DROP TABLE` em sentido inverso sem `CASCADE`. Não houve demonstração de execução dessa migration em PostgreSQL real.
- **Alembic:** `backend/migrations/env.py`, exige alvo fixo `postgresql+psycopg`, banco `frcaixinha_2_2_dev`, papel `frc22_owner`, `127.0.0.1:5432`, PostgreSQL 18.x e gate explícito de escrita; modo offline está bloqueado. A análise desse controle não equivale à autorização para abri-lo.
- **Estado confirmado do banco pelo proprietário na C16-R1 (somente leitura):** PostgreSQL 18.2 (server_version_num `180002`), banco/usuário/host/porta corretos, `transaction_read_only=on`; consulta a classes de relação selecionadas em schemas não sistêmicos retornou 0 linhas; `to_regclass('public.alembic_version')` retornou NULL; transação encerrada com `ROLLBACK`. Não equiparar esse inventário a auditoria integral de extensões, funções, privilégios ou ao teste de instalação da migration.
- **Verificações anteriores:** CI C15 89/89 PASS e inspeções estáticas C16-R1 PASS; Python do PRoot não foi reexecutado neste checkpoint. Não inventar novos resultados de teste.
- **Backup Git C16-R2:** `FRcaixinha_2_2_C16_R2_FINAL_01b33a2dce5e.bundle.age`; SHA-256 `4f3818f1a5065ecfdab2b2034e788ff722831c1b848b5b6b235b7c5ec52ddbd1`; AGE e restauração independente de Git, cópia privada no Drive e comparação remota: PASS conforme checkpoints anteriores.
- **Backup PostgreSQL existente:** `frcaixinha_2_2_dev_20261018_173109_8123.dump.age`; SHA-256 `95991140611c029d923e62baa05bcae3a4c0e8341fa5b1ac6ab11f5e7503b027`; integridade criptográfica/remota anteriormente conferida; **restauração SQL: NOT_RUN**.

## 2. Autoridade e rastreabilidade contratual

**Fonte normativa principal:** [Contrato Técnico Mestre FINAL_APROVADO de 16/10/2026](https://github.com/fronassor-art/FRcaixinha-2.2/blob/01b33a2dce5e57ed2108e58c1ea2975f8220a23d/docs/requisitos/FRcaixinha_2_2_Contrato_Tecnico_Mestre_FINAL_APROVADO_2026-10-16.md); as instruções operacionais v1.1 são subordinadas ao contrato. O documento de 16/10 contém passagens históricas prospectivas sobre G2; os fatos posteriores são comprovados pelos merges e checkpoints. Não interpretar uma revisão operacional como autorização para DDL ou dinheiro real.

| Fonte contratual | Exigência | Situação na C16-R3 |
|---|---|---|
| §§ 3.1, 3.1-A.2 | Identidade, contratante, licença, tenant e papel distintos; tenant preliminar inativo; ativação somente após Pix conciliado | Estruturas preparatórias existentes; fluxo comercial e licença ativa não implementados |
| §§ 3.2-A, 3.5–3.6 | Oferta, preço aceito, versão e evidências imutáveis; pagamento para recebedor correto, conciliado e idempotente | Entidades de oferta/aceite/obrigação/pagamento inativo modeladas; fluxo real NOT_RUN |
| §§ 3.7–3.10 | Vigência no fuso `America/Belem`, dia âncora, renovação antecipada, zero carência, suspensão com direitos preservados, upgrades segmentados e downgrade condicionado | Sem modelo/fluxo completo de assinatura, NOT_RUN |
| §§ 12.1–12.2, sobretudo linha `LicenseSubscription` | No mínimo `id`, `tenant_id`, `contracting_party_id`, `plan_id`, `period`, `starts_at`, `ends_at`, `status`, `paid_payment_id` | **AUSENTE** dos 15 modelos/migration C15 |
| § 12.2-B (i, vi, viii) | Mesma oferta imutável e versão de preço em `LicenseOffer/LicensePriceVersion/TermAcceptance/LicenseSubscription/Payment`; segmentos de vigência e âncora recuperáveis; identidade/contratante/tenant/licença distintos | Necessita desenho de vínculos de assinatura e validação de constraints antes de habilitar licença |
| § 12.4 | `ContractingParty 1:N Tenant/LicenseSubscription` e vínculos semânticos exigidos | Ausência da assinatura mantém relação incompleta |
| § 13.4 | Backup criptografado, recuperação demonstrável, retenção e metas em infraestrutura homologada; teste de restauração antes da produção | Backup lógico protegido existente, sem prova de restauração SQL; política de WAL/RPO/RTO não comprovada |
| § 15.2, Fase 2 | Migrations com prova de subida/descida e controles de acesso | A Fase 2 continua **EM ANDAMENTO** |

## 3. Achados e diagnóstico — PASS / PARCIAL / BLOCKED

**C16-R3-A01 (PASS estático):** a migração C15 declara um primeiro subconjunto de **15 tabelas inativas**, com ordem de criação e reversão coerente com os testes e a inspeção anterior. A correspondência sintática e com metadata não demonstra execução DDL no servidor PostgreSQL 18 real.

**C16-R3-A02 (PARCIAL / lacuna funcional conhecida):** `LicenseSubscription` é **obrigatória** no contrato, mas não existe no modelo SQLAlchemy nem no snapshot C15. Isso não torna automaticamente inválido um checkpoint incremental de esquema *inativo*; torna inválida qualquer alegação de que o licenciamento, a Fase 2 ou o MVP já estejam completos.

**C16-R3-A03 (BLOCKED para operação):** não existe demonstração da vinculação persistente e segura de uma assinatura à **mesma** oferta, versão, contratante e pagamento conciliado. Sem isso, ficam bloqueadas licença ATIVA, renovação, mudança de plano, suspensão automática e cobrança real. É necessário também proteger idempotência, unicidade comercial aplicável, concorrência e vínculo intertenant.

**C16-R3-A04 (PARCIAL):** várias constraints dos modelos atuais restringem estados a `INATIVO`, `RASCUNHO_INATIVO`, `NAO_INICIADO_INATIVO` ou equivalentes. Isto preserva a segurança do esqueleto, mas exigirá migrações/regras **separadas e autorizadas** quando se habilitarem transições legítimas; não afrouxar constraints prematuramente para obter testes verdes.

**C16-R3-A05 (BLOCKED para implantação sem gate):** `upgrade` e `downgrade` estão escritos, mas ainda sem ensaio efetivo em PostgreSQL 18 isolado. O `downgrade` apaga tabelas e **não** pode ser aplicado em uma base real com conteúdo por mera rotina de teste. A base autoritativa continua intocada.

**C16-R3-A06 (PARCIAL recuperação):** SHA-256 do backup lógico do PostgreSQL demonstra identidade dos bytes, **não recuperação funcional do banco**. A listagem do conteúdo do arquivo `pg_dump` por `pg_restore --list`, se feita depois sob autorização, é inspeção estrutural e **não substitui** restauração independente. A estratégia de teste deverá ser isolada, descartável e sem promover segunda base autoritativa ou duplicar ferramentas persistentes.

**C16-R3-A07 (não exigência imediata no Termux, exigência de produção):** a política contratual de backup diário, WAL em até 15 min quando suportado, retenção de 35 dias, RPO/RTO e reconciliação após recuperação **não está comprovada como implantada** neste ambiente. O `pg_dump` lógico **não é** um backup físico base e não habilita recuperação pontual por WAL. Referência oficial: [PostgreSQL 18 — PITR](https://www.postgresql.org/docs/18/continuous-archiving.html).

**C16-R3-A08 (limite de abrangência):** autenticação, aceites efetivos, isolamento por API de tenants e Master, adesões e fluxos de pagamento ainda não receberam prova de ponta a ponta; não serão declarados PASS pela mera presença de modelos e índices.

## 4. Proposta de menor caminho seguro — AINDA NÃO APROVADA PARA CODIFICAÇÃO

**4.1. Preservar a revisão C15 como baseline histórico.** Evitar alterar in-place a migration inicial já mergeada. Recomendar **nova revisão dependente de `c15r2_20261020`** para o futuro modelo `LicenseSubscription` e suas constraints, após revisar contrato, sem tocar o banco. Se a análise identificar uma incompatibilidade real que impede criar o baseline C15, **parar, reproduzir e propor correção mínima**, sem editar a revisão por reflexo.

**4.2. Definir a especificação de `LicenseSubscription` antes do código.** O desenho deve, no mínimo, rastrear `tenant_id`, `contracting_party_id`, `plan_id`, periodicidade, intervalo de vigência, status e `paid_payment_id`; registrar também vínculos à **oferta imutável**, **versão de preço**, **aceite** e histórico de segmentos/dia âncora conforme § 12.2-B. A forma física exata, constraints, políticas de transição e segmentação devem ser submetidas à aprovação técnica; não inventar cobrança ou exceção ao contrato.

**4.3. Fazer testes de regressão e contratos em ambiente de código já existente.** Planejar testes para: oferta/versão/aceite coerentes; negação de ativação antes de confirmação íntegra; duplicação e reversão de pagamento; intertenant; vencimento sem carência preservando direitos; renovação antecipada e mês curto preservando âncora; upgrades por segmentos; downgrade acima da capacidade; impossibilidade de Pix real em DEMO/HOMOLOGAÇÃO. Sem alterar status para ATIVA até autorização pertinente.

**4.4. Preparar plano de ensaio PostgreSQL.** Antes da primeira escrita autorizada: confirmar SHA/local, árvore limpa, requisitos e dependências; backup fresco cifrado do banco único e cópia externa; conferir lista/integridade do dump sem segredo em logs; ensaio de `upgrade/downgrade` **somente** em ambiente de teste efêmero, isolado e autorizado, sem duplicar base persistente e sem operar na base autoritativa; relatório de objetos, constraints e regressões. Se esta estratégia não for viável no Android/Termux, deixar **BLOCKED** e propor alternativa segura ao proprietário, sem forçar execução.

**4.5. Novo gate independente para PostgreSQL autoritativo.** Apenas após relatório e aceite expresso do responsável poderá ser considerada uma aplicação SQL de verdade; exigir validação de DB, versão, backup recuperável, revisão-alvo, transações e plano de recuperação. **Não executar `upgrade`, `downgrade`, `stamp`, DROP, CREATE ou manipulação de WAL agora.**

## 5. Próximo checkpoint recomendado

**C16-R4 — desenho contratual e técnico de `LicenseSubscription` SOMENTE LEITURA / PROPOSTA**: produzir contrato de dados (campos, dependências, índices, triggers/constraints se realmente necessários, transições inativas, evidências e testes), com comparação aos modelos existentes e riscos de migration, para aprovação do proprietário **antes de editar código**. Em paralelo, elaborar a sequência de verificação do dump PostgreSQL sem tocar a base. Sem reinstalar Python/PostgreSQL/Flutter; executor Codex para trabalho em repo e Termux pelo proprietário quando houver limitações de acesso interativo.

## 6. Checkpoint e decisões

| Campo | Status |
|---|---|
| C16_R3_CONTRACT_REVIEW | PASS — fontes localizadas e comparadas |
| C16_R3_C15_SCHEMA_STATIC | PASS — histórico da C16-R1, sem reexecução de CI |
| C16_R3_LICENSE_SUBSCRIPTION_IMPLEMENTED | NO |
| C16_R3_LICENSE_SUBSCRIPTION_DESIGN | PENDING APPROVAL |
| C16_R3_PG18_DDL_EXECUTION | NOT_RUN |
| C16_R3_PG_RESTORE_TEST | NOT_RUN |
| C16_R3_CODE_CHANGES | ZERO |
| C16_R3_DB_WRITES | ZERO |
| C16_R3_GIT_BACKUP | PASS — C16-R2 local e remoto |
| C16_R3_AUDIT | PASS — avaliação concluída |
| C16_R3_MIGRATION_AUTHORIZATION | BLOCKED — requer gate separado |
| FASE_2_COMPLETA | NÃO |

**Regra de continuidade:** registrar este parecer na documentação do projeto após revisão e aprovação; não reduzir as pendências a “já testado” nem reabrir incidentes anteriores sem causa nova identificada. Nenhuma decisão de implementação desta proposta está aprovada automaticamente pela simples emissão do relatório.

## 7. Referências técnicas adicionais

- [PostgreSQL 18 — Backup and Restore](https://www.postgresql.org/docs/18/backup.html).
- [PostgreSQL 18 — pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html).
- [PostgreSQL 18 — pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html).
- [PostgreSQL 18 — Continuous Archiving / PITR](https://www.postgresql.org/docs/18/continuous-archiving.html).
