# C16-R12.37 — Restauracao estrutural do dump pos-migration (21/10/2026)

## Escopo, autorizacao e fontes da evidencia

Projeto FRcaixinha 2.2, Fase 2 EM ANDAMENTO. Baseline Git no Termux:
`main` `e755218b7a5764b834bdc99ddb62042c1fae15bd` (PR #28,
documental; codigo/backend preservados). Raiz unica `~/FRcaixinha_2.2`.
PostgreSQL Termux 18.2, 127.0.0.1:5432. Banco autoritativo unico
`frcaixinha_2_2_dev`, owner `frc22_owner`. Nenhuma nova migration autorizada
ou executada neste ensaio.

O proprietario recebeu a explicacao sobre o ensaio anterior C16-R12.24
(backup pre-migration, sem tabelas de aplicacao) e respondeu "Ok, prossiga"
ao escopo especificamente proposto para C16-R12.37: criar exclusivamente
base temporaria de recuperacao, restaurar, auditar e remover. A excecao
temporaria nao autoriza nova base persistente, clone, cluster ou repeticao
automatica do ensaio.

Fonte das evidencias: saidas de comandos executados pelo proprietario no
Termux e transcritas na conversa. Nao houve conexao direta do agente ao
PostgreSQL para executar ou confirmar SQL nesta documentacao.

## Artefato recuperado e preflight

- Arquivo AGE: `FRcaixinha_2_2_C16_R12_30_67adc6eda5b9.dump.age`.
- Local: `~/.local/share/frcaixinha_2_2/backups/`.
- Tamanho: 81.166 bytes; modo 600; SHA-256:
  `702849367d765f27f44eac71cd51445efc8410c935afd048b4d3af9149217a4e`.
- Copia externa Drive, privada/somente proprietario e previamente comparada
  byte a byte: ID `1EVq7CAa6LM3IU82aFxcMqYJ1caIw0HB5` (C16-R12.33).
- C16-R12.34 sincronizacao ff-only para `e755218`: PASS, exit 0, Git limpo.
- C16-R12.35 auditoria autoritativa READ ONLY: PASS, exit 0.
- C16-R12.36 preflight de recuperacao READ ONLY: PASS, exit 0;
  backup/SHA, PG 18.2, ferramentas, espaco disponivel, existencia do
  papel restrito e ausencia inicial da base temporaria.

## Execucao autorizada C16-R12.37

| Etapa | Evidencia observada no Termux | Resultado |
|---|---|---|
| R12.37.1 | Baseline e backup conferidos; preflight imediato; `CREATE DATABASE` (template0, UTF8/C/C, owner `frc22_trial_c16r12`, inicialmente sem conexoes); `REVOKE` de PUBLIC; conexoes habilitadas; auditoria independente confirmou exatamente duas bases nao-sistema e destino temporario restrito | PASS, `CRIACAO_TEMPORARIA_EXIT_CODE=0` |
| R12.37.2 | Preflight de identidade; restauracao somente na base `frc22_restore_c16r12` pelo papel restrito; retorno do `pg_restore` sem erro | PASS, `RESTAURACAO_EXIT_CODE=0` |
| R12.37.3 | Nova consulta READ ONLY independente na temporaria e na autoritativa; tabelas, owner esperado em cada base, indice/revisao/constraints e contagens verificadas | PASS, `AUDITORIA_INDEPENDENTE_EXIT_CODE=0` |
| R12.37.4 | Preflight sem sessoes na temporaria; `DROP DATABASE frc22_restore_c16r12` sem FORCE; auditorias READ ONLY de inventario e da autoritativa; Git limpo | PASS, `REMOCAO_EXIT_CODE=0` |

Restore do R12.37.2: `age -d` por pipe para `pg_restore` com destino
explicitamente temporario, `--format=custom`, `--single-transaction`,
`--exit-on-error`, `--no-owner`, `--no-acl`, `--no-tablespaces`,
`--no-publications` e `--no-subscriptions`. Nao foram usados
`--create`, `--clean`, `--jobs` ou SQL de migration.
As senhas foram fornecidas no proprio terminal; nenhuma senha registrada
nesta documentacao. O resultado exit 0 e os controles de integridade
atestam o sucesso deste ensaio nos limites definidos, nao recuperacao
completa de um servidor.

## Auditoria independente e cobertura efetiva

As duas conexoes READ ONLY de R12.37.3 relataram `PASS` e comparacao exata
do resumo de contagens:

`PASS|ccafc9d030261abf3ac595008ad27a19ce860ed015f464a1e0b2be3df04bc599|LINHAS=1`

O hash acima e SHA-256 da representacao textual das **contagens por tabela**,
nao hash do conteudo de todas as linhas. Como o total e 1 e
`alembic_version` tem uma linha, as 17 tabelas de aplicacao estavam
vazias nas duas bases no momento dessas consultas.

Controles verificados em cada base:

- Nomes exatos de 18 tabelas no schema `public`: 17 da aplicacao e
  `alembic_version`; nenhuma outra tabela `public`.
- Uma linha em `public.alembic_version`: `c16r5_20261020`.
- 70 indices `public`; nenhum invalido/não pronto entre os verificados.
- Constraints do schema `public`: 95 CHECK, 28 FOREIGN KEY,
  176 NOT NULL, 18 PRIMARY KEY e 32 UNIQUE; nenhuma nao validada.
- Tabelas pertencem ao papel conectado na respectiva base; ausencia
  dos schemas adicionais verificados.
- Contagens por tabela iguais entre temporaria e autoritativa.

A auditoria de estrutura/contagens **nao equivale** a comparacao integral
de todas as definicoes de coluna, indicialidade, regras de permissoes,
conteudos de linhas ou comportamento funcional da aplicacao. Os controles
nao demonstram isolamento de tenants, fluxos de PF/PJ, autorizacao de API,
operacoes financeiras nem recuperacao de registros que nao estavam no dump.

## Pos-remocao, limites e continuidade

R12.37.4 confirmou exclusivamente uma base nao-sistema no PostgreSQL,
`frcaixinha_2_2_dev`; `frc22_restore_c16r12` removida sem FORCE;
autoritativa acessivel com 18 tabelas, 70 indices, revisao
`c16r5_20261020` e nenhuma constraint nao validada. Git continuou
limpo em `e755218` durante os checkpoints executados.

**Veredito:** recuperacao estrutural desse dump pos-migration = PASS NO
ESCOPO TESTADO. Recuperacao de linhas de aplicacao = NAO TESTADA, pois
nenhuma linha de aplicacao existia. Identidades globais, senhas, ACL de
origem, configuracoes PostgreSQL e recuperacao integral do servidor =
NAO VALIDADAS. As verificacoes finais nao fazem comparacao byte a byte
do banco original; nao houve comando de restauracao apontado a ele.

ADR: reutilizar o mecanismo de ensaio temporario ja exercitado em
C16-R12.24, evitando duplicacao de ferramentas e bases persistentes.
Nao repetir este ensaio estrutural por rotina a cada adendo documental;
eventual teste de recuperacao de dados deve usar dados controlados e
autorizacao propria, sem contaminar a base autoritativa.

ERR: nenhuma falha bloqueante observada nas quatro saidas do ensaio.
Nenhuma nova migration, instalacao, backup ou acao financeira foi feita
para este registro. Backup anterior e copia privada preservados.

**Status de fase:** F2-01/F2-02 ainda PARCIAIS no criterio integral,
apesar da aplicacao C15/C16 e recuperacao estrutural comprovadas.
Demais fluxos funcionais pendentes; Fase 2 EM ANDAMENTO; Fase 3 NAO INICIADA.

**Proximo gate:** integrar este registro documental por PR, atualizar
Termux apenas por fast-forward seguro e selecionar o proximo requisito
funcional da Fase 2 mediante consulta ao contrato e checklist. Nao
criar DB de recuperacao novamente nem repetir migrations por reflexo.
