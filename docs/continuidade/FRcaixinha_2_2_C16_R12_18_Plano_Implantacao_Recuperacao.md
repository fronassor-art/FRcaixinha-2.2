# C16-R12.18 — Plano de implantacao Alembic e recuperacao

Status: PLANO EM REVISAO. Nao e autorizacao de execucao.
Fase 2 EM ANDAMENTO; Fase 3 nao iniciada.

## Base comprovada
- Main/Termux: e6a66da640a865d51d86296144270e928b12374c, PR #25 integrada.
- C16-R12.17: BASELINE, BACKEND_IDENTICO_AO_TESTADO, atualizacao ff-only e
  Git final limpo PASS; ATUALIZACAO_EXIT_CODE=0, conforme saida do proprietario.
- Backend identico ao commit local testado d50efa49e2ef09e77f662aa09c6802ba0c88ba33.
- Regressao Debian Python 3.13.5: 166/166 em 0.689s, pip check PASS.
- CI final da PR #25, HEAD dd855edf31bfbb4e0ab91e23c949dce92e92b7ff:
  run 39701679673, conclusion success. CI inicial e testes detalhados no
  checkpoint C16-R12.16R1.
- Ensaio REAL com rollback C16-R12.13R1 PASS; auditoria independente R12.14
  PASS: nenhum schema de ensaio, relacao ou constraint de aplicacao nos
  inventarios consultados; public.alembic_version ausente.
- A ultima auditoria SQL e historica: nao foi repetida nesta etapa documental.
- Correcao env.py usa engine.begin() envolvendo identidade e migrations.
  Controle commit/rollback validado offline, ainda sem commit real no PostgreSQL.

## Escopo exato proposto
Uma unica raiz ~/FRcaixinha_2.2, unico PostgreSQL Termux 18.2 em
127.0.0.1:5432, unica base autoritativa frcaixinha_2_2_dev.
Alembic roda no Debian PRoot independente, backend/.venv Python 3.13.5.
O destino atualmente exigido pelo env.py e frc22_owner; este papel e superusuario.
O papel frc22_trial_c16r12 permanece exclusivo do ensaio autorizado; nao
aumentar seus privilegios para executar o fluxo permanente.

Revisoes propostas: c15r2_20261020 -> c16r5_20261020, destino explicito
c16r5_20261020, sem usar head como alvo variavel e sem stamp.
Resultado esperado da implantacao: 17 tabelas de aplicacao mais a tabela de
controle public.alembic_version; a contagem nao inclui esta ultima como modelo.
Validar tambem nomes, colunas, indices e constraints contra as revisoes,
e a unica versao esperada c16r5_20261020. Contagem isolada nao basta.

Nenhuma ativacao de assinatura, cobranca, Pix, pagamento, credito, API de
negocio ou Fase 3 decorre da criacao do schema.

## Sequencia e gates
1. Revisar e integrar este plano; atualizar o Termux. A revisao e documental,
   sem repetir regressao ou ensaio ja comprovados.
2. Consolidar um backup Git AGE do estado final que inclua a correcao da PR #25
   e os registros. Verificar recuperacao Git independente e copia externa.
   Nao repetir backups de codigo identico a cada adendo documental.
3. Resolver a pendencia de recuperacao SQL: definir procedimento e destino
   exatos compativeis com a regra de uma base autoritativa, e submeter qualquer
   restauracao/escrita ou excecao de ambiente a autorizacao especifica.
   Nao criar segundo banco, cluster, clone ou instalacao por iniciativa propria.
   Esta etapa nao aprova restauracao sobre a base atual.
4. Antes da implantacao, conferir integridade e cobertura do backup PostgreSQL
   e papeis. Se a auditoria mostrar mudanca desde o dump, produzir e verificar
   novo backup coerente antes de qualquer escrita autorizada.
5. Executar preflight READ ONLY fresco imediatamente antes da janela proposta:
   Git/SHA e arvore limpa, banco/host/porta/versao, usuario, ausencia de replica,
   inventario de objetos e versao Alembic, fontes C15/C16 e seus hashes.
   Qualquer divergencia suspende a implantacao para diagnostico.
6. Apresentar bloco exato de implantacao ao proprietario, com SHA consolidado,
   revisoes e destino fixos, limites de tempo, credenciais somente no celular
   e efeitos persistentes descritos. Aguardar autorizacao especifica.
7. Apenas apos essa autorizacao, abrir a janela sem escritores concorrentes,
   executar um unico upgrade pelo ambiente validado e fechar o gate/credenciais
   efemeros ao terminar. Nao editar env.py ou aplicar DDL manual como atalho.
8. Fazer auditoria independente em nova conexao READ ONLY para comprovar commit,
   versao, inventario e ausencia de residuos do ensaio. Registrar saida, exit code,
   SHA e limites. Se houver discrepancia, nao declarar PASS.
9. Somente com implantacao e pos-auditoria aprovadas, produzir backup PostgreSQL
   do estado novo e registrar proximo requisito da Fase 2. Nao iniciar Fase 3
   por consequencia desta implantacao.

## Inventario de recuperacao disponivel
| Artefato | Evidencia | Limite |
|---|---|---|
| Bundle Git AGE do SHA 13a87726491f55fe20dfa04a6d5b754979fc6355 | Recuperacao bare, referencias e fsck PASS; copia privada Drive comparada | Nao cobre a correcao posterior env.py da PR #25 |
| Dump PostgreSQL AGE de 21/10, 1281 bytes | SHA, descriptografia e geracao SQL sem executar PASS; copia externa verificada | Restauracao funcional NOT_RUN |
| Papeis sem senhas AGE, 858 bytes | Dois papeis esperados presentes, token PASSWORD ausente; copia externa verificada | Nao recupera senhas; nao equivale a configuracao completa do servidor |

Checksums:
- Git: fffe247fedb91871d4e3222f3d5cccfcfe30c4409a8219d22e70dac758755f7f.
- DB: 25e333ab7c117c9e4d1b922c853025aeafd6ad8850a5577894e43e0f09c25112.
- Papeis: 89b15b2027433bbbf506423f88161249653e982f8248693ca5282cb4a7f43c72.

Local DB/papeis: ~/.local/share/frcaixinha_2_2/backups/C16_R12_4_7_20261021_201558_115mji.
Bundle: ~/frcaixinha-2.2-backups/FRcaixinha_2_2_C16_R12_7R1_FINAL_13a87726491f.bundle.age.
Links e evidencias anteriores nos checkpoints R12.5 e R12.14.

Chaves AGE e senhas ficam com o proprietario; jamais no chat ou repositorio.
Nao foi demonstrada cobertura de pg_hba.conf, postgresql.conf ou segredos
operacionais. Registrar como serao recuperados antes de aprovar recuperacao
de servidor; dump logico nao e copia fisica do cluster.
Gerar SQL para /dev/null nao e ensaio de restauracao. O estado pre-migration
sem tabelas tambem limita o que esse backup demonstra sobre dados futuros.

## Resposta a falhas
| Momento | Conduta |
|---|---|
| Antes de conectar ou validar identidade | Interromper, registrar erro, manter gate fechado e diagnosticar |
| Excecao de migration com conexao integra | Esperar rollback do escopo engine.begin(); verificar estado por nova conexao antes de concluir |
| Conexao perdida ou resultado de commit incerto | Tratar resultado como desconhecido; nao repetir upgrade automaticamente; auditar catalogo e versao |
| Upgrade termina mas pos-auditoria diverge | Interromper avanço e preservar evidencias; nenhum downgrade, drop ou stamp automatico |
| Falha depois de commit comprovado | Avaliar dados/escritores e apresentar plano especifico; downtime, perda e autorizacao explicitos |

Downgrade nao equivale a restauracao. C15/C16 incluem remocao de estruturas;
com dados posteriores pode haver perda. Nao usar downgrade base, DROP SCHEMA
CASCADE, DROP DATABASE ou restauracao com --clean como recuperacao automatica.
A eventual recuperacao precisa de alvo, backup, efeito nos dados e autorizacao
especificos. Nao reaplicar exportacao de papeis indiscriminadamente sobre papeis
existentes e nao recriar senhas a partir do arquivo sem senhas.

## ADR e ERR
ADR: separar ensaio das funcoes de revisao, controle transacional do env.py,
implantacao persistente e recuperacao funcional. Cada evidencia tem alcance
proprio; nenhum PASS substitui o seguinte.
ERR: importacao direta do launcher corrigida por PYTHONPATH (R12.13);
autobegin sem commit externo corrigido por engine.begin() (R12.16R1).
Nao repetir esses diagnosticos sem divergencia de versao ou circunstancia.

## Decisao pendente
O plano esta preparado para revisao; a implantacao continua NAO AUTORIZADA.
Recuperacao funcional SQL continua NOT_RUN e requer definicao/autorizacao
concreta antes de ser declarada validada. Nenhuma escrita ou nova instalacao
foi feita nesta etapa.
F2-01/F2-02 PARCIAIS; demais requisitos nao mudam de status.
Proximo passo imediato: integrar o plano documental e atualizar o Termux;
depois consolidar backup Git e tratar o gate de recuperacao SQL.
