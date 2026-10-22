# C16-R12.14 — ensaio real e auditoria independente após rollback

Registro da sessão de 21/10/2026 (America/Belem).
Base e checkout Termux: main 13a87726491f55fe20dfa04a6d5b754979fc6355, PR #23.
Fase 2 EM ANDAMENTO; Fase 3 NÃO INICIADA.
Esta atualização é somente documental: não autoriza repetição do ensaio,
migrations permanentes, restauração, merge ou ativação operacional.

## Resultado consolidado

| Controle | Resultado e limite |
|---|---|
| Correção FK C16-R12.7R1 | Teste original 1/1 PASS; regressão 159/159 PASS em Debian PRoot Python 3.13.5; CI PASS |
| Integração | PR #23 merged; atualização main local exit 0; backend idêntico ao commit eb57ce9 testado |
| Git local após ensaio | main 13a87726491f55fe20dfa04a6d5b754979fc6355, árvore limpa, conforme bloco concluído |
| C16-R12.12 | Autenticação e consulta READ ONLY como frc22_trial_c16r12 PASS, exit 0 |
| C16-R12.13 inicial | FAIL, exit 1: ModuleNotFoundError: No module named migrations, antes de conexão |
| Diagnóstico de importação | Revisões C15/C16 e hashes PASS com raiz backend no PYTHONPATH; consulta independente sem resíduos, exit 0 |
| C16-R12.13R1 | Ensaio REAL das funções congeladas de C15/C16 PASS, exit 0 |
| C16-R12.14 | Nova conexão psql READ ONLY: sem schema de ensaio, relações/constraints de aplicação ou public.alembic_version, exit 0 |
| Aplicação permanente C15/C16 | NÃO EXECUTADA e NÃO AUTORIZADA |
| Restauração funcional SQL | NOT_RUN |

## Autorização e destino do ensaio concluído

O proprietário aprovou expressamente a proposta do ensaio transacional nesta
sessão. O escopo foi um único banco autoritativo, sem banco paralelo:
- PostgreSQL Termux 18.2, 127.0.0.1:5432, frcaixinha_2_2_dev.
- Papel frc22_trial_c16r12; schema frc22_c16_trial_c16r12.
- Checkpoint fixado no acionador: C16-R12.3-SCHEMA-20261021.
- Credencial digitada somente no celular; nenhuma senha registrada.
- Python Debian PRoot 3.13.5, backend/.venv existente.
- Parâmetros do processo: connect timeout 10s, statement timeout 15000ms,
  lock timeout 3000ms, idle-in-transaction timeout 60000ms.
- Sem instalação, edição de fontes ou migration permanente durante a execução.

A execução bem-sucedida foi a sequência do executor auditado:
C15 upgrade (15 tabelas), C16 upgrade (17 tabelas), C16 downgrade (15 tabelas),
C15 downgrade (0 tabelas), rollback e comparação interna de catálogos.
Saída do proprietário:
C16_R12_3_SCHEMA_TRIAL=PASS
C16_R12_13R1_ENSAIO_TRANSACIONAL=PASS
ENSAIO_TRANSACIONAL_EXIT_CODE=0

A sequência e as verificações são inferidas do caminho de sucesso do executor
nesse commit; não houve log individual de cada DDL fornecido no chat.
O ensaio chama as funções congeladas de revisões, não o fluxo completo de
alembic/env.py; não cria nem atualiza a tabela de versionamento Alembic.
Não prova inserções de dados, todos os cenários de enforcement das constraints,
APIs, autenticação da aplicação, isolamento financeiro por tenant ou recuperação SQL.
A autorização foi consumida pelo ensaio descrito; não repetir automaticamente.

## C16-R12.14 — evidência independente

Consulta em NOVA conexão psql, PGOPTIONS default_transaction_read_only=on,
BEGIN READ ONLY, ON_ERROR_STOP=1, usuário frc22_trial_c16r12:
- banco frcaixinha_2_2_dev; transaction_read_only on.
- schemas com prefixo frc22_c16_trial: 0 linhas.
- relações em pg_class fora dos schemas sistêmicos consultados: 0 linhas.
- constraints em pg_constraint fora dos schemas sistêmicos consultados: 0 linhas.
- to_regclass('public.alembic_version') IS NOT NULL: false.
- COMMIT; C16_R12_14_CONSULTA_POS_ENSAIO=PASS; POS_ENSAIO_EXIT_CODE=0.
O resultado comprova ausência de resíduos nesses inventários consultados,
não auditoria universal de todos os tipos de objetos ou instalações do celular.

## ERR-C16-R12.13 — importação na chamada direta

Sintoma reproduzido: executar tests/c16_r12_3_schema_trial_launcher.py diretamente
não tornou a raiz backend importável; _frozen_revisions falhou ao importar migrations.
Ponto da falha anterior a create_engine/connect, conforme código e traceback.
A primeira tentativa não chegou à conexão/DDL do executor.
Causa operacional: comando de execução sem caminho de importação explícito.
Correção mínima: a partir de backend, prefixar a chamada com PYTHONPATH="$PWD".
Não editar migrations, reinstalar dependências ou tornar aprovações permanentes.
Diagnóstico sem escrita: simular sys.path[0]="tests" com backend no PYTHONPATH
e executar _frozen_revisions(); retornou c15r2_20261020 e c16r5_20261020.
Reexecução do mesmo ensaio autorizado: PASS; auditoria pós-ensaio independente PASS.
Prevenção: preservar a chamada correta para sessões Termux/PRoot e não confundir
sucesso de unittest (que tinha raiz importável) com chamada direta operacional.

## Backups Git C16-R12.8 a C16-R12.11

Nome: FRcaixinha_2_2_C16_R12_7R1_FINAL_13a87726491f.bundle.age.
Local original: ~/frcaixinha-2.2-backups/.
Bytes: 269748; permissão 600.
SHA256: fffe247fedb91871d4e3222f3d5cccfcfe30c4409a8219d22e70dac758755f7f.
Criação quiet/AGE em pipe, exit 0; sem arquivo bundle intermediário desprotegido.
Recuperação independente em bare temporário: bundle verify em repositório vazio
PASS, histórico completo; bundle unbundle importou 344 objetos; 41 refs no índice
(inclui HEAD); referências restauradas iguais às originais; fsck --full --strict
--no-dangling PASS; main recuperada no SHA esperado; nenhum alternates.
Bare temporário C16_R12_9_RECUPERACAO_Vn2xDD removido seletivamente em R12.10,
com confirmações dos arquivos protegidos .pack/.rev/.idx. Exit 0; original e
cópia criptografada em Downloads mantiveram o SHA; checkout preservado.
Não recriar esse bare nem tratar branches históricas como clones ativos.

Cópia externa privada via integração Drive, somente proprietário, pasta oficial:
https://drive.google.com/file/d/1P7ThstLeE-hw2sFiouDUuPHQuOcHZCjp/view
Download remoto: 269748 bytes, SHA esperado e comparação byte a byte PASS, exit 0.
Esse backup contém o Git em 13a8772, NÃO contém esta atualização documental futura,
banco PostgreSQL, arquivos não versionados, senhas, .env ou configurações externas.

## Backups PostgreSQL e papéis preservados

Diretório: ~/.local/share/frcaixinha_2_2/backups/C16_R12_4_7_20261021_201558_115mji.
- DB: 1281 bytes; SHA 25e333ab7c117c9e4d1b922c853025aeafd6ad8850a5577894e43e0f09c25112.
- Papéis sem senhas: 858 bytes; SHA 89b15b2027433bbbf506423f88161249653e982f8248693ca5282cb4a7f43c72.
Leitura/descriptografia e cópias externas com bytes iguais já PASS em R12.4.8/.10.
Os três backups foram conferidos por SHA no preflight da primeira tentativa
R12.13, sem mudança Git posterior; reexecução corrigiu somente PYTHONPATH.
Detalhes e links DB/papéis no checkpoint C16-R12.5.
Restauração funcional SQL continua NOT_RUN; o rollback do ensaio não a substitui.

## ADR-C16-R12.14 e próxima passagem

Decisão factual: encerrar o ensaio transacional específico como PASS, sem
transformá-lo em autorização de migration permanente ou encerramento da Fase 2.
F2-01 permanece PARCIAL: ensaio específico seguro comprovado, não todos os testes.
F2-02 permanece PARCIAL: funções de upgrade/downgrade ensaiadas no PG real;
fluxo completo Alembic, implantação e recuperação funcional ainda pendentes.
Demais requisitos da Fase 2 não recebem PASS por consequência deste ensaio.
Não iniciar Fase 3, pagamentos, Pix ou operações financeiras reais.

Próximo gate: revisar/integrar este registro documental mediante autorização;
depois preparar plano de implantação Alembic e recuperação com riscos e limites,
sem executar upgrade/downgrade/stamp ou restaurar a base por presunção.
Não repetir os 159 testes por reflexo para esta mudança somente documental.
O backup recuperável 13a8772 cobre o código ensaiado. Distinguir o estado
documental posterior e a cobertura de cada backup ao planejar o próximo checkpoint.
