# C16-R12.25 — Evidencias de backup e restauracao limitada

## Base e escopo
Main/Termux 1386cc3606ade5989a216117115209df60cdd2ef, PR #26.
C16-R12.19 atualizou o plano por ff-only: PASS, exit 0, Git limpo e backend
preservado. Backend segue a correcao PR #25 com 166 testes locais/CI PASS;
nenhuma regressao foi repetida para esta alteracao somente documental.

## Backup Git C16-R12.20 a .23
Arquivo FRcaixinha_2_2_C16_R12_20_1386cc3606ad.bundle.age,
292838 bytes, modo local 600.
SHA256: 0b2062365ba0a2895a811c6c4424c34980c037454b22f10bb71f019b2329304b.
Original: ~/frcaixinha-2.2-backups/. Copia AGE em ~/storage/downloads/.
Criacao R12.20 PASS, exit 0.
Recuperacao independente R12.21 PASS, exit 0: bundle com historia completa,
43 refs anunciadas (incluindo HEAD), referencias Git comparadas, 389 objetos
verificados por fsck --full --strict --no-dangling e sem alternates.
Diretorio bare temporario C16_R12_21_RECUPERACAO_bW0AoB removido em R12.22;
hashes do original e exportacao iguais, Git limpo, exit 0.
Cobre a correcao Alembic e o plano integrado no SHA 1386cc3.
Nao cobre automaticamente registros documentais posteriores; nao repetir backup
por reflexo para cada registro que apenas documente o proprio backup.

R12.23: upload na pasta privada oficial do Drive
1SPEujdnAjbU2IG6YdI1S0Bjb5PgJSNGf; arquivo id
1ddTsd2pYiGWMtxZDDOSkD63mcvm3NwnM.
Link: https://drive.google.com/file/d/1ddTsd2pYiGWMtxZDDOSkD63mcvm3NwnM/view
Metadados: tamanho 292838, pasta correta, shared=false, somente owner.
Download pelo conector seguido de SHA256 e comparacao byte a byte com o anexo:
PASS, processo exit 0. Nenhuma descriptografia no executor ou senha solicitada.

## Autorizacao excepcional C16-R12.24
O proprietario autorizou por "Prossiga" a proposta concreta de criar,
restaurar, auditar e remover exclusivamente frc22_restore_c16r12 no PostgreSQL
existente. Excecao temporaria e especifica a regra de uma base; nao autoriza
novo cluster/instalacao, segundo destino permanente, novo ensaio ou migrations.
A base autoritativa continua frcaixinha_2_2_dev em 127.0.0.1:5432, PG 18.2.

## Execucao e auditorias fornecidas pelo proprietario
| Etapa | Evidencia | Resultado |
|---|---|---|
| R12.24.1 | Criacao de frc22_restore_c16r12 via template0, owner frc22_trial_c16r12, REVOKE ALL FROM PUBLIC somente na temporaria; UTF8/C/C como a autoritativa | PASS, exit 0 |
| R12.24.2 | Preflight READ ONLY validou identidade, papel restrito, dono e destino vazio; age decrypt por pipe para pg_restore 18.2 | PASS, exit 0 |
| R12.24.3 | Conexoes independentes READ ONLY, papel restrito, PG 18.2, read_only on, replica f nas duas bases | PASS, exit 0 |
| R12.24.4 | Preflight de identidade/dono e ausencia de conexoes; DROP DATABASE somente frc22_restore_c16r12, sem FORCE | PASS, exit 0 |

Restore: destino explicito frc22_restore_c16r12, --single-transaction,
--exit-on-error, --no-owner e --no-acl. Sem --create, --clean, migrations
ou reaplicacao de papeis globais. Log: "connecting to database for restore",
"executing SELECT pg_catalog.set_config('search_path', '', false);",
"implied no-schema restore".

R12.24.3 mostrou em ambas as bases somente schema public, dono pg_database_owner;
zero relacoes e constraints de aplicacao nos inventarios consultados;
public.alembic_version ausente e schema de ensaio ausente.
R12.24.4 confirmou BASE_TEMPORARIA_REMOVIDA=PASS e BASE_AUTORITATIVA_PRESENTE=PASS.
Inventario final: frcaixinha_2_2_dev, postgres, template0 e template1.
Git final limpo e main 1386cc3 nos blocos. Nao ficaram bancos temporarios.

## Backup PostgreSQL usado e alcance do resultado
Dump: ~/.local/share/frcaixinha_2_2/backups/C16_R12_4_7_20261021_201558_115mji/frcaixinha_2_2_dev.dump.age.
1281 bytes; SHA256 25e333ab7c117c9e4d1b922c853025aeafd6ad8850a5577894e43e0f09c25112.
Checksum conferido antes/depois do bloco de restore.
Backup de papeis separado, sem senhas, nao foi executado.

Estado anterior "restauracao SQL NOT_RUN" passa a:
RESTAURACAO DO DUMP PRE-MIGRATION SEM OWNER/ACL = PASS NO ESCOPO LIMITADO.
O processo de restore executou com sucesso contra destino temporario real;
o inventario vazio observado e compativel com o backup anterior as tabelas.
Nao havia tabelas/dados de aplicacao a recuperar nesse arquivo. Portanto:
- recuperacao de tabelas, dados, sequencias e constraints de aplicacao NAO TESTADA;
- owner, ACL do banco de origem, senhas e papeis globais NAO RESTAURADOS;
- recuperacao integral do servidor/configuracoes continua NAO VALIDADA.
Nao promover este resultado a recuperacao integral PASS. Nao substituir
o inventario do backup por objetos criados posteriormente por migrations.

## ADR, ERR e proximo gate
ADR: registrar a excecao temporaria autorizada e encerrada; voltar ao inventario
de uma unica base de projeto. Distinguir sucesso do restore limitado de
recuperacao integral. Preservar a evidencia do ensaio C15/C16 com rollback.
ERR: nenhum erro bloqueante nos blocos R12.19 a .24.4; nenhum novo SQL
foi executado pelo conector nesta etapa de documentacao.
Proximo passo: revisar/integrar este registro documental e atualizar Termux.
Depois fazer preflight READ ONLY fresco para preparar proposta concreta de
implantacao, com alvo e riscos explicitos. A limitacao de recuperacao acima deve
constar da proposta; nao presumir satisfacao de requisito de recuperacao integral.
Nenhum upgrade, downgrade ou stamp permanente autorizado.
Fase 2 EM ANDAMENTO, F2-01/F2-02 PARCIAIS; Fase 3 nao iniciada.
