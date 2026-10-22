# C16-R12.16R1 — Transacao explicita no Alembic

## Estado e evidencias
Base main e Termux: 14ae65f9524e2e38bd8cf48585c7e80f8b7b314c (PR #24).
Atualizacao Termux C16-R12.15 PASS, exit 0, Git limpo e backend preservado.
Inspecao offline C16-R12.16 PASS, exit 0, no Debian Python 3.13.5:
SQLAlchemy 2.0.55, Alembic 1.20.0, psycopg 3.3.6.

PASS da inspecao significa coleta concluida; o fluxo inspecionado possui defeito.
Nao houve nova conexao ou operacao PostgreSQL nesta etapa.

## ERR — transacao sem proprietario de commit
A consulta SELECT de identidade em engine.connect() dispara autobegin.
MigrationContext detecta connection.in_transaction() como transacao externa;
begin_transaction() retorna nullcontext. Nao existe commit externo no env.py.
Ao fechar a conexao, a transacao pendente e revertida: uma execucao poderia
terminar sem persistir o DDL nem alembic_version.

Causa comprovada pelo env.py e trechos das bibliotecas instaladas fornecidos
pelo proprietario. Nao e falha das revisoes C15/C16 ou do ensaio com rollback.
Nao se afirma que houve tentativa de upgrade permanente: continua NOT_RUN.

## ADR — transacao externa explicita
Trocar engine.connect() por engine.begin(), mantendo consulta de identidade e
context.run_migrations() dentro do mesmo escopo. Engine confirma no termino
normal e reverte em excecao. Alembic continua reconhecendo a transacao externa,
agora com responsavel explicito. Nao adicionar commit isolado depois do SELECT.

Preservar gates, validacao de URL/servidor, bloqueio offline, NullPool,
models, requirements, revisoes congeladas e executor/launcher do ensaio.

## Validacao proposta
Novo teste executa env.py com SQLAlchemy e MigrationContext reais, dialeto
PostgreSQL e DBAPI gravador em memoria. O DBAPI nao possui servidor, sockets,
arquivos de banco ou execucao SQL. Comandos sinteticos representam DDL e
versionamento; nao sao as migrations reais.

Verificar commit unico apos os dois comandos, rollback na falha, recusa de
identidade divergente antes do DDL, descarte de recursos e gates antes da
construcao do engine. Teste de sucesso deve falhar com env.py anterior
(ausencia de commit). Regressao completa e teste negativo pendentes de CI/local.
O runtime desta conversa nao possui SQLAlchemy/Alembic; nao instalar pacotes
para contornar a limitacao. Sintaxe pode ser verificada sem importar bibliotecas.

## Limites e proximo gate
Correcao em branch/PR; merge nao realizado nesta etapa.
Validacao local Debian Python 3.13.5 ainda PENDENTE.
Nenhum teste real de commit no PostgreSQL ou restauracao funcional foi executado.
Ensaio real C16-R12.13R1 e auditoria independente C16-R12.14 seguem PASS.
Backups existentes permanecem validos para os seus respectivos conteudos; nao
cobrem automaticamente commits posteriores.
F2-01/F2-02 PARCIAIS. Fase 2 EM ANDAMENTO; Fase 3 nao iniciada.
Migrations permanentes, novo ensaio e restauracao SQL nao autorizados aqui.
Antes de implantacao: integrar correcao validada, concluir plano de recuperacao
e obter autorizacao especifica para o comando e revisoes exatos.
