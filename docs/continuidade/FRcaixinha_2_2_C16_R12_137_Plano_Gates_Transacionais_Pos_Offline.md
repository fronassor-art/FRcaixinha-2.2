# C16-R12.137 — Portões de implementação e provas transacionais G3-C (PROPOSTA)

**Data:** 23/10/2026 (America/Belem)  
**Rastreamento:** Issue #46  
**Base:** `main@751da8f8f380fc45d58de68cf707a3c2f9149777`  
**Situação:** DRAFT, SOMENTE DOCUMENTAÇÃO; não é autorização para implementar regras indecisas, aplicar migration ou usar dados reais em testes.

## 1. Fronteira de conclusão: preservar o trabalho aprovado

- **G3-C.4 IN-01…IN-08 OFFLINE:** concluído, auditado e integrado pelas PRs #49–#52; regressão conjunta **339/339 PASS** no snapshot de árvore correspondente à `main`. Os testes positivos e os *contraexemplos* documentados são igualmente válidos dentro do escopo offline. Não os refazer para simular progresso.
- **C16-R12.130–136:** Git local/PG read-only PASS; Git AGE recuperado integralmente via bare+fsck; PG18.2 AGE restaurado funcionalmente em **cluster efêmero isolado**, com 18 tabelas, Alembic `c16r5_20261020` e 17 tabelas de negócio vazias. Backups Git/PG enviados à pasta privada do Drive, baixados novamente, SHA-256 e comparação binária PASS.
- **Provas ainda não dadas:** execução de operações transacionais reais sob concorrência no PostgreSQL, validação de política de retenção/contestação PF-PJ e prontidão da minuta `f2p4_20261022`.
- **Não permitidos neste pacote:** DDL/DML no PostgreSQL autoritativo, `alembic upgrade/downgrade/stamp`, criação de banco persistente paralelo, ativação de login/e-mail/Pix/financeiro, mudanças em quotas/rateios/contratos, envio/registro de segredos.
- **Regra de aprovação:** uma PR DRAFT não é aprovação, GitHub CI não substitui auditoria técnica independente, um teste offline não substitui PostgreSQL, merge remoto não equivale à sincronização Termux.

## 2. Resultado pretendido da próxima tarefa

Desenvolver o **adaptador transacional de identidade/registro** e seus mecanismos de integridade em pacotes revisáveis, fazendo toda a programação e regressão **offline no GitHub antes da sincronização única posterior no Termux**. Só integrar após cobertura positiva de cada invariante, CI cumulativo, revisão independente e autorização do proprietário. Em seguida, executar no Termux somente verificações e ensaios SQL expressamente autorizados; após conclusão estável, gerar o backup consolidado AGE Git+PostgreSQL e conferir restauro/cópia externa.

**Exceção não negociável:** se alguma alteração estrutural ou operação de risco no banco for especificamente autorizada antes do fechamento, continua obrigatório um backup preventivo recuperável **antes** da operação; o adiamento do backup consolidado final não elimina essa salvaguarda.

## 3. Critérios de aceitação transacional — implementação ainda pendente

| Prova | Requisito de código e comportamento | Prova independente necessária |
| --- | --- | --- |
| IN01-T1…T4 | `registration_idempotency` COMPLETED sempre vinculada à identidade **da mesma parte** PF/PJ, mesmo contra FKs cruzadas e troca concorrente de representante; nenhuma PJ APTA implícita | Inserts sintéticos em transação isolada, violações rejeitadas, concorrência com locks, rollback completo |
| IN02-T1…T6 | Reserva+escrita+conclusão atômicas, UNIQUE arbitra corrida, replay só para mesma origem/fingerprint e IDs persistidos, sem novo segredo; estados expiração/conflito falham fechados | Corridas 2+ sessões reais, fingerprint divergente, falhas forçadas, timeout/deadlock e reconsulta confiável |
| IN03-T1…T3 | Consumo de desafio por UPDATE condicional único, verificando propósito, e-mail atual, TTL no relógio do servidor, identidade e atomicidade da ativação; representação PJ separada | 2 confirmações concorrentes, alteração de e-mail, revogação, expirado, rollback/erro de transporte |
| IN04-T1…T3 | Consulta por requisição da sessão e estados atuais de identidade/credencial/tenant; senha trocada ou identidade suspensa invalida imediatamente; nenhum RoleGrant implícito | Corrida suspensão/login, revogação, mudança credencial, negação de acesso cross-tenant |
| IN05-T1…T2 | Política definida de UUID e `updated_at` para escrita ORM versus SQL; sem confiar em `onupdate` Python como trigger PG | INSERT/UPDATE direto, corrida, rollback e relógio, comportamento documentado |
| IN06-T1…T3 | Proteger `UNIQUE` CPF/e-mail/CNPJ e impedir reserva abusiva e apropriação; recuperação apenas com legitimidade provada, sem vazamento de existência | Conflitos PF/PJ sintéticos, dois candidatos concorrentes, contestação/abuso negados, auditoria mínima |
| IN07-T1…T2 | **Proibir downgrade destrutivo** da minuta: quatro DROP TABLE apagariam dados. Planejar correção forward/recuperação autorizada, com reconciliação pós-backup | Inspeção do DDL e prova de falha controlada com dados sintéticos isolados; nenhuma perda no banco principal |
| IN08-T1…T3 | TTL de 10 min desafio e 15 min sessão/idempotência distinto de retenção física; limpeza com base legal aprovada e corridas seguras, sem apagar histórico protegido | Expiração no limite, UNIQUE após TTL, concorrência cleanup/consumo/replay, auditoria LGPD e guarda de evidências |

**Política de CI:** usar Python e dependências existentes, `python -B -m pip check` e `python -B -m unittest discover -s tests -p 'test_*.py' -v`; não instalar pytest nem mover, apagar ou adaptar teste para mascarar lacuna. Cada novo pacote exige regressões e uma revisão independente do diff, incluindo casos negativos e contraexemplos que se convertam em proteções reais.

## 4. Decisões normativas ainda NÃO aprovadas (não inventar padrões)

1. **Retenção, expurgo e contestação:** prazo físico por finalidade e base legal de desafios, sessões, tentativas PENDENTE/PRELIMINAR, e efeito nos backups AGE. TTL de sessão não é prazo de exclusão.
2. **Identidade PF/PJ:** prova de titularidade e poderes de representante, disputa/recuperação de CPF/e-mail/CNPJ pré-reservados; rate-limit, proteção antifraude e auditoria que não revele se a identidade existe. NÃO afrouxar UNIQUE automaticamente.
3. **Mecanismo de enforcement real:** opção entre constraint/trigger/locking/isolamento adequada a IN-01/02 e estratégia de versão/suspensão de IN-04 e atualização de timestamps IN-05. Documentar e revisar ordem de bloqueios, deadlocks, retries e modelo de falha antes de alterações de migration.
4. **Migração/rollback:** revisão separada da F2P4, sem declarar seguro seu `downgrade` com quatro DROP TABLE; eventual substituição ou nova migration com reversão segura deve ser expressamente aprovada.
5. **Ensaio PostgreSQL real:** configuração de cluster **descartável e isolado**, com dados sintéticos, sem TCP público, autorização específica, prova do descarte e verificação read-only do banco principal antes/depois. Evitar segundo banco persistente.
6. **Implantação G3-C.5 e G3-D/E:** autorização expressa adicional; não deduzir da aprovação de testes offline, backup, Git sync ou do presente documento.

Enquanto alguma decisão bloquear o comportamento seguro, a implementação afetada deve permanecer **BLOCKED**, com provas limitadas rotuladas corretamente. Não falsificar PASS.

## 5. Sequência operacional acordada

| Portão | Critério de entrada/saída | Status nesta PR |
| --- | --- | --- |
| A — levantamento e contrato | Lacunas de IN01–08 inventariadas, requisitos e limites conhecidos | DOCUMENTADO |
| B — desenvolvimento offline | Adaptadores de persistência e migrations propostas em branches/PRs distintas, nenhum SQL principal | **NOT_RUN** |
| C — testes offline completos | Casos positivos/negativos novos, regressão total no SHA exato e correções sem testes removidos | **NOT_RUN** |
| D — validação independente | Auditor técnico/Codex revisa comportamento, diff, falhas, concorrência e evidências; CI PASS | **NOT_RUN** |
| E — aprovação de integração | Aprovação expressa sobre PRs, sem decisões jurídicas/financeiras presumidas | **BLOCKED** até C/D |
| F — integração remoto/Termux | Merge autorizado, fast-forward seguro de `main`, árvore limpa, checkup | **NOT_RUN** |
| G — testes PG isolados | Somente se especificamente autorizados, com baseline e restauração/discard seguros | **NÃO AUTORIZADO** |
| H — backups consolidados | Git AGE e PG18 AGE somente no fechamento estável, SHA/restore/Drive privado/download conferidos | **NOT_RUN; BACKUPS C16-R12.131/132 preservados** |

**Não seguir do portão com FAIL/BLOCKED.** A execução do portão H não autoriza implantação G3-C.5. Registrar ao final commit SHA, CI, parecer independente, banco/revisão e hashes dos backups válidos.

## 6. Evidências e decisão sobre esta PR

Este documento não modifica `backend/app`, `backend/migrations`, `backend/tests`, workflows, dependências, banco ou backups. Branch e PR DRAFT são preparação para revisão. **Concluir este documento não equivale a concluir a tarefa transacional.** Mudanças de regra e cada gate de risco seguem sujeitos às aprovações especificadas.

## 7. Adendo cronológico de reconciliação — 26/10/2026 (revisão documental da PR #54)

**Natureza e precedência temporal.** As seções 1–6 acima, datadas de 23/10/2026, foram preservadas literalmente como **fotografia histórica** do momento da proposta. Este adendo registra fatos comprovados depois daquela data. Expressões originais como `F2P4 não aplicada`, `NOT_RUN`, `NÃO AUTORIZADO` e `base main@751da8f8...` continuam corretas **somente em seus contextos históricos**; não descrevem integralmente o estado de 26/10/2026. O adendo não substitui o Contrato Técnico Mestre, não amplia nenhuma G2 e **não autoriza** DDL/DML, novo cluster/banco, testes físicos, login, Pix, operações financeiras ou merge.

### 7.1. Fatos posteriores, com evidência e limites

1. **Preparação offline IN-01…IN-08:** as PRs #49–#52 já integravam a base descrita em 23/10, com referência histórica a 339/339 testes naquele snapshot. Posteriormente, a [PR #55](https://github.com/fronassor-art/FRcaixinha-2.2/pull/55) foi integrada em `main@98526e2ae96bc270c4b45c026354c342cabeb966` (25/10/2026). O pacote alcançou **508/508 testes backend offline PASS** na suíte histórica da integração, com [job unittest e passos de dependências/testes SUCCESS](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40161734178). Esses resultados não testam concorrência PostgreSQL, locks, sessões simultâneas, triggers nem políticas jurídicas reais. Não repetir ou recontar como trabalho novo.
2. **Migration F2P4 no único PostgreSQL autoritativo:** C16-R12.203R5 executou, mediante G2 própria, Alembic `c16r5_20261020 → f2p4_20261022` no banco `frcaixinha_2_2_dev`, PostgreSQL 18.2. [Evidência de execução e pós-verificação](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6388195740) confirmou a revisão `f2p4_20261022`, **22 tabelas**, quatro tabelas novas, coluna e constraints previstas. Nova conferência READ ONLY no Termux em 25–26/10 confirmou 22 tabelas e **nenhum índice inválido nem constraint não validada**; `ROLLBACK` e desligamento controlado `shut down`. **Não executar novo upgrade, downgrade ou stamp.**
3. **Downgrade destrutivo IN-07:** o código de migration integrado na `main` contém `downgrade(): raise RuntimeError("F2P4_DOWNGRADE_NOT_AUTHORIZED")`. Isso corrige o perigo de quatro `DROP TABLE` presente na minuta histórica, **mas não cria procedimento autorizado de reversão/recuperação operacional**. A decisão de rollback/recuperação permanece restrita a plano e G2 próprios.
4. **Backup e recuperação:** restaurações reais C16-R12.122R1 (AGE C119) e C16-R12.136 (AGE C132), em cluster PG18 efêmero isolado, foram `PASS` no escopo de 18 tabelas (`alembic_version` + 17 tabelas de negócio vazias). C16-R12.205 produziu backup PostgreSQL **pós-F2P4** `FRcaixinha_2_2_C16_R12_205_PG18_f2p4_1685d987_20261024_160549.dump.age`, **95.606 bytes**, SHA-256 `a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337`, com AGE/TOC/conteúdo legíveis, cópia externa privada e readback SHA/`cmp` PASS, conforme [registro de reconciliação](https://github.com/fronassor-art/FRcaixinha-2.2/pull/55#issuecomment-6388534595). **Restauração funcional específica do C205 = NOT_RUN**; testes dos backups antigos não se transferem automaticamente a este.
5. **Git e preservação recente:** a [PR #48](https://github.com/fronassor-art/FRcaixinha-2.2/pull/48) foi revisada, integrada por squash e encerrada integralmente na `main@6990642ab8b337a9b234c2576309bed503f31171`. O Termux sincronizou `main` e `origin/main`, mantendo C236-R14 e quatro arquivos R22 intactos, `git fsck` PASS. Um backup Git+R22 AGE recuperável foi comprovado local e remotamente no Drive privado, [checkpoint de conclusão](https://github.com/fronassor-art/FRcaixinha-2.2/pull/48#issuecomment-6407683959). **Isto não é backup final de uma implementação física transacional ainda não realizada.**
6. **Diretrizes IN-06/IN-08:** a [G2 C16-R12.172](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6378494008) aprovou **desenho e preparação de testes offline** (incluindo distinção TTL versus retenção física), não prova final de titularidade/representação, prazos físicos de expurgo, base legal operacional, rotinas de limpeza ou tratamento de disputas. Esses itens continuam pendentes de decisões separadas.
7. **IN-05 e ensaios reais:** os triggers PostgreSQL adicionais **não foram instalados**. As provas físicas com duas conexões, atomicidade real, conflitos concorrentes, revogação, idempotência sob corrida e limpeza concorrente **continuam NOT_RUN/BLOCKED**. A execução de F2P4 estrutural não os conclui.

### 7.2. Reconciliação de A–H sem transformar progresso offline em conclusão física

| Portão original | Prova posterior verificada | Status por escopo em 26/10/2026 |
| --- | --- | --- |
| **A — levantamento e contrato** | Inventário IN-01…IN-08 e critérios originais documentados; esta reconciliação incorpora fatos novos | **DOCUMENTADO**, decisões operacionais e jurídicas ainda pendentes |
| **B — desenvolvimento offline** | Pacote preparatório IN-01…IN-08 da PR #55 integrado | **PASS APENAS PREPARAÇÃO OFFLINE**; adaptadores transacionais PostgreSQL reais/novas DDL não comprovados |
| **C — testes offline completos** | Suíte backend histórica 508/508 PASS após #55, com CI específica | **PASS OFFLINE NO SHA HISTÓRICO**; testes físicos de concorrência NOT_RUN |
| **D — validação independente** | Pareceres e CI do pacote offline já registrados; este novo documento ainda precisa de revisão própria | **PARCIAL POR ESCOPO**; `PR54_REVISAO_ADENDO=NOT_RUN` |
| **E — aprovação de integração** | G2 separadas foram concedidas para a PR #55, F2P4 e PR #48 | **PR54_MERGE=SEM_AUTORIZAÇÃO**; aprovações históricas não se estendem a esta PR |
| **F — integração remoto/Termux** | PRs #55/#48 integradas; último `main` Termux/GitHub `6990642ab8...` sincronizado e íntegro | **PASS PARA INTEGRAÇÕES HISTÓRICAS**; PR #54 ainda Draft/não integrada |
| **G — testes PG isolados** | Restores de backups antigos e pós-DDL READ ONLY, ambos em escopos distintos | **NOT_RUN/BLOCKED PARA TESTES FÍSICOS TRANSACIONAIS** |
| **H — backups consolidados** | AGE PostgreSQL pós-F2P4 C205 e Git+R22 pós-PR48 com cópia remota verificável | **PASS PARA BACKUPS CITADOS**; não é encerramento/backup final de testes físicos futuros |

**Regra de parada:** todo FAIL/BLOCKED de um gate técnico afetado continua impedindo a etapa operacional dependente. Não renomear evidência offline como teste PostgreSQL real nem declarar G3-C.5/G3-D/E operacionais.

### 7.3. Condição de integração original e decisão ainda reservada ao Master

A seção 2 e a descrição originais da PR #54 condicionam o merge à aprovação de testes da implementação transacional futura. **Esta condição histórica não foi silenciosamente revogada.** Ela deve ser tratada expressamente em decisão posterior e separada do Administrador Master, com duas alternativas a avaliar:

- **Conservar a condição original:** manter a PR #54 Draft/BLOCKED até os testes físicos, decisões de segurança e revisão necessários; não declarar o documento encerrado.
- **Autorizar expressamente a integração exclusiva do plano documental atualizado:** reconhecer que o documento funciona como planejamento, com **todos os gates físicos e jurídicos ainda em aberto** e rastreados; somente após revisão independente do adendo e G2 específica, sem tratar a integração documental como aceite da implementação.

A presente G2 autorizou **somente acrescentar este adendo na branch da PR #54**. Não escolheu nenhuma das alternativas de merge, não aprovou testes SQL e não liberou PR #56/C236. A PR #54 permanece **DRAFT / MERGE BLOCKED** até avaliação independente deste novo HEAD e nova decisão explícita.
