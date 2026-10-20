# FRcaixinha 2.2 — C16-R5 — Autorização e escopo da implementação estrutural INATIVA

**Registro:** 20/10/2026. **Responsável:** autorização do proprietário no chat, por “Prossiga”, em resposta direta à pergunta de aprovação da especificação C16-R4 para iniciar implementação controlada.

**Estado:** DESENHO C16-R4 APROVADO PARA DESENVOLVIMENTO E TESTES ESTÁTICOS; IMPLEMENTAÇÃO AINDA NÃO CONCLUÍDA. **Não é autorização para migration real, operação financeira ou merge automático.**

## 1. Fontes e baseline imutáveis

1. O Contrato Técnico Mestre FINAL APROVADO de 16/10/2026 prevalece, especialmente §§ 3.1, 3.2-A, 3.5–3.11, 12.1–12.4, 13.4 e 15.2.
2. Ler os dois documentos ao lado deste registro: C16-R3 (auditoria) e C16-R4 (especificação), e as ADR/ERR do Documento Mestre v1.1.
3. Diretório local único: `~/FRcaixinha_2.2`; GitHub `fronassor-art/FRcaixinha-2.2`.
4. Base Git: `01b33a2dce5e57ed2108e58c1ea2975f8220a23d` (PR #18). Branch autorizada: `feat/f2-c16-license-subscription-inactive`.
5. Migration C15 `c15r2_20261020`: NÃO EDITAR, NEM REESCREVER; está versionada, **não aplicada** ao único PostgreSQL 18.2 Termux. Preserve `down_revision=None` na C15.
6. Backup Git C16-R2 externo/local comprovado: AGE SHA-256 `4f3818f1a5065ecfdab2b2034e788ff722831c1b848b5b6b235b7c5ec52ddbd1`. Backup PostgreSQL lógico existe, mas restauração SQL ainda NOT_RUN.

## 2. Decisões C16-R4 aprovadas neste checkpoint

- **D-R4-01: APROVADO.** Uma linha `LicenseSubscription` por ato comercial identificado por oferta/aceite, não sobrescrever histórico e não impor `UNIQUE(tenant_id)`. Cadastro/aceite não concedem uso.
- **D-R4-02: APROVADO conforme recomendação global.** Histórico `LicenseEntitlementSegment` (nome físico sujeito à revisão) append-only e seus vínculos estruturais na **mesma futura revisão**, sempre totalmente INATIVOS. Não habilitar a vigência antes de aprovar serviços e integridade temporal/financeira completa.
- **D-R4-03: APROVADO.** Primeira implementação só `RASCUNHO_INATIVO`, sem pagamento confirmado, `starts_at`, `ends_at`, `anchor_day`, ativação ou cobranças.
- **D-R4-04: APROVADO COM LIMITES.** FKs compostas e UNIQUE suplementares em tabelas C15 somente quando necessárias para eliminar vínculos cruzados; nenhuma alteração destrutiva, financeira ou de status.
- **D-R4-05: AUTORIZADA APENAS ETAPA DE CÓDIGO/TESTES E PREPARAÇÃO DE PR.** Implantação SQL no PostgreSQL, restauração de dump, habilitação de estados, merge definitivo, custos ou dinheiro real requerem gates separados. É proibido alterar o banco nesta etapa.

## 3. Limites da tarefa de Codex — IMPLEMENTAÇÃO C16-R5

### Arquivos autorizados

- `backend/app/db/models.py` — dois modelos INATIVOS, FKs/UNIQUE existentes estritamente necessários e nomes consistentes.
- `backend/migrations/versions/<nova_revision>_license_subscription_inactive.py` — revisão **nova**, `down_revision = "c15r2_20261020"`, DDL reversível sem tocar dados; esquema base permanece congelado.
- `backend/tests/test_db_license_subscription_schema.py` — testes estruturais de modelos, FKs compostas, nullabilidade, inatividade e equivalência SQLAlchemy/Alembic.
- `backend/tests/test_db_license_entitlement_segment_schema.py` — testes estruturais da tabela de segmentos, inatividade, integridade com subscription e auditoria prevista.
- `docs/continuidade/` — apenas acréscimo de relatório de checkpoint e anotações de testes comprovados, se necessário; não reescrever contrato.

**Não alterar** `backend/migrations/versions/c15r2_20261020_initial_schema.py`, requirements, CI, frontend, credenciais ou banco; expansão de escopo exige novo gate.

### Integridade mínima a demonstrar

1. FK composta `(tenant_id, contracting_party_id) → tenants(id, contracting_party_id)`.
2. Vínculos compostos que provem `LicenseSubscription` com a **mesma** `LicenseOffer`, `TermAcceptance`, tenant, plano, versão, periodicidade e valor aceito. Respeitar que o PostgreSQL exige UNIQUE/PK exatamente adequado ao conjunto referenciado; não usar FKs fracas com IDs isolados.
3. Pagamento `paid_payment_id` NULO obrigatório nesta revisão; não fabricar chave/estado de pagamento conciliado. Preparar o campo como futuro elo e registrar as futuras dependências do pagamento para auditoria.
4. `period` só MENSAL/ANUAL, `duration_months` coerente 1/12; `effective_price` `NUMERIC(18,2)`; timestamps timezone-aware; `starts_at`, `ends_at`, `anchor_day` obrigatoriamente NULL no snapshot inicial.
5. `UNIQUE(offer_id)` e `UNIQUE(term_acceptance_id)` para não duplicar ato comercial. Não impor unicidade global à licença do tenant.
6. Segmentos na mesma revisão, com vínculo ao tenant e à assinatura e campos preparados para futuras provas; nesta etapa `status` INATIVO, sem intervalo/valor financeiro/entitlement concedido.
7. Nenhum endpoint, serviço, cron, Pix, ledger ou permissão nova; `ACTIVE`, `ATIVA`, status pago e qualquer escrita financeira proibidos.
8. Ordem de tabelas/constraints/índices e reversão sem `CASCADE`, na revisão nova. Não fazer downgrade na base autoritativa.
9. Se identificada impossibilidade de cumprir integridade com modelo inativo sem alterar contratos/cadeia C15 de forma significativa: **PARAR, descrever causa, propor solução mínima e pedir aceite**, não inventar regra.

### Processo e testes

- Antes de editar, confirmar `main/origin/main`, branch e árvore limpa. Branch remota acima já foi criada a partir do baseline.
- Codex executa em `~/FRcaixinha_2.2` somente se tiver acesso; identificar Termux normal versus Debian PRoot.
- Reutilizar Python 3.13.5 + `backend/.venv` **no Debian PRoot independente**; não reinstalar ferramentas, não aninhar PRoot, não usar Python 3.14 auxiliar como prova.
- Comandos permitidos, quando disponíveis: `python -B -m pip check`; `python -B -m unittest discover -s tests -v`; `python -B -m alembic heads` (sem conexão de banco e sem `env.py`, desde que verificado). Não rodar `alembic current/upgrade/downgrade/stamp`.
- Checar regressões C15, revisar DDL offline/compilado, ausência de segredos e limites da revisão, `git diff --check`.
- Corrigir FAIL pelo protocolo oficial reproduzir → causa → correção mínima → reteste → regressão → registro. Qualquer BLOCKED impede conclusão.
- Nenhuma declaração de PASS sem comando, ambiente, data e saída real. `NOT_RUN` e `BLOCKED` não são PASS.
- Com CI e revisão aprovadas, solicitar autorização separada para merge, checkpoint de backup e planejamento de prova PostgreSQL real. **Nenhum merge automático**.

## 4. Critérios de saída C16-R5

- [ ] Código e migration nova com integridade estrutural demonstrada; C15 byte idêntico ao baseline.
- [ ] Dois modelos e segmentos somente inativos, sem Pix nem autorização de uso.
- [ ] `down_revision` correto e `alembic heads` aponta somente nova revisão.
- [ ] Testes novos, regressões e `pip check` PASS em ambiente oficialmente suportado; CI conferida se PR for aberta.
- [ ] Diff limitado, testes de DDL compilado e riscos residuais documentados.
- [ ] Banco único `frcaixinha_2_2_dev`: **ZERO ESCRITAS; migration NÃO APLICADA**.
- [ ] SHA, branch, PR/CI se aplicável, bloqueios e backup C16-R2 preservados; próximo gate explicitado.

**Protocolo Codex/Termux:** o Codex para ao encontrar limitação de ambiente; relata o comando/falha sem repetir investigação; ChatGPT consulta ADR/ERR e fornece os procedimentos do Termux ao proprietário. Nenhum Codex, chat ou relatório recebe senha/segredos.
