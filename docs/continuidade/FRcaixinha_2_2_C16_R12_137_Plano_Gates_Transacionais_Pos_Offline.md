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
