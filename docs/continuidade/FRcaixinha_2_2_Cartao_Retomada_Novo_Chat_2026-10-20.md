# FRCAIXINHA 2.2 — CARTÃO OBRIGATÓRIO DE RETOMADA DE CHAT

**Data-base:** 20/10/2026 — C15-R7. **Consultar atualização posterior antes de agir.**

> **Escopo exclusivo FRcaixinha 2.2**. Não começar do zero. Não criar ambiente, banco ou clone extra. Nunca reabrir incidente corrigido antes de consultar o Documento Mestre v1.1 (ADR/ERR) e a auditoria Fase1–C15. Não misturar projetos.

**Autoridade:** Contrato Técnico Mestre FINAL_APROVADO de 16/10/2026; Documento Mestre de Instruções v1.1 (20/10), subordinado ao contrato; Caderno de 17/10 como plano histórico. **Este cartão não concede autorização.**

**Repositório/raiz:** `fronassor-art/FRcaixinha-2.2` em `~/FRcaixinha_2.2`; `main` = `0316c3cc29aa6966033e52d5d21d5f378683ba97` (PR #17 merged). PRs #1–#4 fundação FastAPI/Flutter/CI/APK. PRs #5–#17 Fase 2 até C15.

**Código e testes:** primeira migration `revision=c15r2_20261020`, `down_revision=None`, 15 modelos/tabelas e 18 índices, integrada à `main`; **89/89 PASS** em Python 3.13.5 Debian PRoot + GitHub Actions (PR #17). `LicenseSubscription` **ainda ausente**. Cadastro PF/PJ, autenticação/convites e isolamento efetivo NÃO concluidos. Fase 2 NÃO concluída.

**Única base:** PG Termux 18.2, `frcaixinha_2_2_dev`, `frc22_owner`, `127.0.0.1:5432`, data dir `$PREFIX/var/lib/frcaixinha_2_2_pg18`. Conexão READ ONLY PASS; inspeção anterior encontrou 0 tabelas de aplicação regulares/particionadas, `alembic_version` ausente. **MIGRATION NÃO APLICADA; NÃO EXECUTAR SQL DE ESCRITA sem gate específico.**

**Backup Git C15:** AGE/scrypt com senha apenas em Termux; `FRcaixinha_2_2_C15_FINAL_0316c3cc29aa.bundle.age`, SHA256 `d77fc40bbedd54c98e04e5d92d87cc493c514dcfffe01340be3af6732a274919`; recuperação independente Git PASS; Drive privado file id `1KiryYKBrG4muW6VYE9f3wQEAS72obMeI`; byte-a-byte remoto PASS.

**Backup PG separado:** `frcaixinha_2_2_dev_20261018_173109_8123.dump.age`, SHA256 `95991140611c029d923e62baa05bcae3a4c0e8341fa5b1ac6ab11f5e7503b027`; integridade local/remota verificada, mas **restauração SQL NOT_RUN**.

**Falhas antigas com soluções:**

- PRoot aninhado → executar Debian `.venv` em sessão independente do Termux; Python 3.13.5 (não Python 3.14 auxiliar); não reinstalar pacotes.
- Alembic host mismatch → `host(inet_server_addr())`, guard PG18 estrito; escrita bloqueada por padrão.
- PostgreSQL antes não respondia → cluster original iniciado com preflight, agora acesso validado; **não criar novo cluster**.
- AGE prompt confuso → `git bundle create --quiet`; senha interativa privada.
- AGE `git bundle verify -` SIGPIPE 141 → `age -d "$PART" | { git bundle verify -; cat >/dev/null; }`.
- AGE `.partial` → apagar apenas parcial verificado, após consentimento; teste de recuperação Git bare e checksum Drive.
- Codex Cloud proxy `proxy:8080` falhava em 18/10; **ponte Cloud NÃO comprovada**; não burlar proxy, fallback Termux.

**Fluxo obrigatório:** Codex trabalha no escopo, PARA e relata falta de acesso; ChatGPT consulta ADR/ERR, prepara comando para Termux; proprietário executa em Termux/PRoot independente e envia saída; ChatGPT valida; Codex só retoma com resultado e gate vigentes. Erro resolvido vira ADR/ERR versionado, não memória informal.

**Próxima pendência IMEDIATA:** versionar **a atualização documental v1.1 e este cartão** por revisão Git própria no mesmo repositório (nenhum código/SQL); ainda não publicado na `main`. Só então discutir C16 auditoria pré-migration PostgreSQL somente leitura; upgrade/downgrade e qualquer DDL requerem autorização separada.

**Protocolo no novo chat:** confirmar acesso aos três documentos, citar último SHA, checar se houve checkpoint posterior e **não oferecer reinstalação, nova base, recuperação ou pesquisa repetida sem causa nova documentada**. Validar contratualmente qualquer nova proposta.


## Atualização de continuidade — C16-R12.5 (21/10/2026)

Este adendo prevalece sobre a fotografia de status de 20/10 acima, preservada
como histórico. A base main desta revisão é 499f9f1bfd891def8bf11596538db367f7a7ee19
(PR #21); Fase 2 em andamento, Fase 3 não iniciada. Auditorias READ ONLY
C16-R12.4.1/.2 PASS; 52 testes offline C16-R12.4.6 PASS. Backups PostgreSQL e papéis
atualizados, criptografados, lidos e copiados ao Drive privado com comparação de
bytes/SHA PASS. Restauração funcional e ensaio real PostgreSQL continuam NOT_RUN.
C16-R12.5 implementa apenas habilitação temporária e testes, em revisão/CI;
não autoriza DDL, merge ou aplicação permanente das migrations.
ADR, ERR corrigido, hashes, evidências, limites e próximo gate estão em
[checkpoint C16-R12.5](FRcaixinha_2_2_C16_R12_5_Habilitacao_Controlada_2026-10-21.md).
Resultado do CI desta alteração deve ser lido no job do HEAD da PR, não presumido.


## Bloqueio posterior — C16-R12.7 e correção C16-R12.7R1

PR #22 integrada; main 0155808916b352cde6f718835df0ab2cdfb10cb5 e atualização
Termux C16-R12.6 PASS. Regressão local C16-R12.7 FAIL (1/159), exit 1,
Python 3.13.5 e pip check PASS: seleção ambígua da FK de plan_id no teste de
catálogo. A causa foi identificada no teste; modelo e migrations preservados.
Correção em revisão no checkpoint [C16-R12.7R1](FRcaixinha_2_2_C16_R12_7R1_Correcao_Teste_FK.md).
CI anterior verde não substitui correção e revalidação local. Interromper avanço
para backup Git/ensaio até corrigir e verificar regressão. Fase 2 em andamento.
SQL/papéis protegidos preservados; restauração e ensaio real NOT_RUN.


## Estado posterior — C16-R12.14, ensaio real concluído

Base main/Termux 13a87726491f55fe20dfa04a6d5b754979fc6355, PR #23.
Correção FK validada: teste original e regressão local/CI 159/159 PASS.
Backup Git recuperado independentemente e cópia privada Drive com bytes iguais:
fffe247fedb91871d4e3222f3d5cccfcfe30c4409a8219d22e70dac758755f7f.
Ensaio transacional REAL C15/C16 C16-R12.13R1 PASS, exit 0. Chamada direta exige
PYTHONPATH apontando a backend; falha inicial de importação corrigida sem editar fontes.
Auditoria independente pós-ensaio C16-R12.14 READ ONLY PASS, exit 0: zero schemas
de ensaio, relações e constraints de aplicação nos inventários consultados;
public.alembic_version ausente. DDL revertido, sem migrations permanentes.
Restauração funcional SQL NOT_RUN; F2-01/F2-02 continuam PARCIAIS; Fase 2 EM ANDAMENTO.
Fonte atual de evidências, ADR/ERR, backups e próximo gate:
[checkpoint C16-R12.14](FRcaixinha_2_2_C16_R12_14_Ensaio_Real_e_PosAuditoria.md).
Esta atualização documental não autoriza novo ensaio, implantação ou Fase 3.


## C16-R12.16R1 — Correcao da transacao Alembic em revisao

Main/Termux 14ae65f9524e2e38bd8cf48585c7e80f8b7b314c, PR #24, atualizacao
C16-R12.15 PASS. Inspecao offline C16-R12.16 PASS identificou autobegin da
consulta de identidade sem commit externo no env.py. Correcao proposta:
engine.begin() envolvendo identidade e migrations; nenhuma revisao alterada.
Novo teste usa SQLAlchemy/Alembic reais com DBAPI gravador, sem banco ou sockets.
CI e validacao Debian pendentes; nao presumir PASS. Fonte ADR/ERR e gates:
FRcaixinha_2_2_C16_R12_16R1_Transacao_Alembic.md.
Ensaio real anterior e pos-auditoria seguem PASS. Aplicacao permanente e
restauracao funcional NOT_RUN. Fase 2 em andamento; Fase 3 nao iniciada.


## C16-R12.18 — Plano de implantacao e recuperacao em revisao

PR #25 integrada; main/Termux e6a66da640a865d51d86296144270e928b12374c.
C16-R12.17 PASS, exit 0; Git limpo e backend identico ao testado localmente.
Correcao transacional validada: Debian 3.13.5 166/166 e pip check PASS;
CI final do HEAD dd855edf, run 39701679673, success.
Plano versionado em FRcaixinha_2_2_C16_R12_18_Plano_Implantacao_Recuperacao.md:
revisoes explicitas C15 -> C16, preflight, autorizacao, pos-auditoria e falhas.
Backup Git anterior cobre 13a8772; consolidar copia com correcao integrada.
Restauracao funcional SQL NOT_RUN: definir procedimento/destino e autorizacao,
sem criar segunda base/instalacao ou restaurar a autoritativa por presuncao.
Nao repetir regressao/ensaio para mudanca somente documental.
Fase 2 em andamento; F2-01/F2-02 PARCIAIS. Implantacao permanente nao autorizada;
Fase 3 nao iniciada. Proximo passo: revisar/integrar este plano e atualizar Termux.


## C16-R12.25 — Backup atual e restauracao limitada comprovados

Main/Termux 1386cc3606ade5989a216117115209df60cdd2ef (PR #26), R12.19 PASS.
Backup Git R12.20-.23: recuperacao independente, 389 objetos/fsck, referencias
comparadas e Drive privado com download/bytes iguais PASS. SHA256:
0b2062365ba0a2895a811c6c4424c34980c037454b22f10bb71f019b2329304b.
Excecao temporaria autorizada: frc22_restore_c16r12 criada, restore executado
pelo papel restrito, auditorias independentes READ ONLY e remocao final PASS,
todos exit 0. Inventario voltou a frcaixinha_2_2_dev e tres bases de sistema.
Restauracao do dump pre-migration sem owner/ACL PASS NO ESCOPO LIMITADO;
sem tabelas/dados de aplicacao no backup, sua recuperacao continua NAO TESTADA.
Papeis/senhas/ACL de origem e recuperacao integral NAO VALIDADOS pelo ensaio.
Evidencias, ADR/ERR e limites: FRcaixinha_2_2_C16_R12_25_Backup_Restore_Limitado.md.
Fase 2 em andamento; F2-01/F2-02 PARCIAIS; migrations permanentes nao autorizadas.
Proximo gate: integrar registro, atualizar Termux e preflight READ ONLY fresco;
proposta de implantacao deve explicitar a limitacao de recuperacao. Fase 3 nao iniciada.


## C16-R12.29 — C15/C16 aplicadas permanentemente e auditadas

Base de execucao main/Termux 67adc6eda5b93ad0c84d15862b48b8fba4ff53ee.
Autorizacao especifica recebida para C15/C16 e COMMIT. R12.27 READ ONLY PASS;
R12.28 Alembic upgrade c16r5_20261020 PASS, exit 0. Nova conexao psql R12.29
confirmou 17 tabelas de aplicacao + alembic_version, unica revisao c16r5_20261020,
owner frc22_owner, 70 indices validos/prontos e zero constraints nao validadas.
R12.29 PASS, exit 0; Git limpo. Estado historico "migrations nao aplicadas"
superado SOMENTE para C15/C16. Nao repetir upgrade, downgrade ou stamp.
Fonte: FRcaixinha_2_2_C16_R12_29_Implantacao_e_Auditoria.md.
Backup PostgreSQL pos-migration PENDENTE (R12.30); dump anterior nao cobre tabelas.
Regressao local/CI anterior 166/166 PASS; nao repetida para documentacao.
Testes funcionais de dados e recuperacao de dados de aplicacao NAO TESTADOS.
Fase 2 em andamento; F2-01/F2-02 PARCIAIS; Fase 3 nao iniciada.
Proximo passo: backup SQL AGE do estado implantado, verificar e guardar copia externa.


## C16-R12.33 — Backup pos-migration verificado e externo

Pendencia de backup R12.30 acima superada: dump AGE de 81166 bytes, modo local
600, 18 TABLE/18 TABLE DATA e revisao c16r5_20261020 conferidos, leitura SQL
completa sem execucao PASS; R12.30/.31/.32 exit 0. SHA256:
702849367d765f27f44eac71cd51445efc8410c935afd048b4d3af9149217a4e.
Copia Drive privada, somente owner, id 1EVq7CAa6LM3IU82aFxcMqYJ1caIw0HB5;
download, SHA e comparacao byte a byte PASS. Evidencias no checkpoint R12.29.
Restauracao funcional DESTE dump ainda NOT_RUN; ensaio anterior cobriu dump
pre-migration sem tabelas. Nenhuma nova migration ou Fase 3 por consequencia.
Proximo passo: integrar registro documental e atualizar Termux; Fase 2 em andamento.

## C16-R12.37 — Restauracao estrutural pos-migration validada (21/10/2026)

Este adendo supera somente o estado historico "restauracao do novo dump NOT_RUN".
R12.34 sincronizacao Git ff-only PASS; R12.35 auditoria da autoritativa READ ONLY
PASS; R12.36 preflight de recuperacao PASS. Com autorizacao especifica do
proprietario, R12.37.1/.2/.3/.4 criaram, restauraram, auditaram e removeram
a base TEMPORARIA `frc22_restore_c16r12`, todos PASS/exit 0. Banco original
`frcaixinha_2_2_dev` preservado e unico banco nao-sistema no inventario final.
Restore usou backup C16-R12.30 (81166 bytes, SHA256
702849367d765f27f44eac71cd51445efc8410c935afd048b4d3af9149217a4e).
Auditoria READ ONLY encontrou 18 tabelas, 70 indices, constraints validadas
e revisao `c16r5_20261020` em ambas as bases; contagens iguais,
`LINHAS=1` (apenas alembic_version). **Recuperacao estrutural PASS no
escopo; recuperacao de dados de aplicacao NAO TESTADA** por ausencia de linhas;
owner/ACL/senhas/configuracao de servidor nao recuperados. F2-01/F2-02
PARCIAIS, Fase 2 em andamento; Fase 3 nao iniciada.
Fonte detalhada, evidencias, ADR/ERR e limites:
[checkpoint C16-R12.37](FRcaixinha_2_2_C16_R12_37_Restauracao_Estrutural_Pos_Migration.md).
Proximo gate: integrar documento, sincronizar Termux e retomar requisitos
funcionais da Fase 2 sem repetir restauracao ou migration.

## C16-R12.41 — Validacao de documentos implementada (21/10/2026)

Checkpoint posterior a R12.39: baseline `37088dec`, PR #30 para criar
`app/document_validation.py` e 10 testes offline para CPF e CNPJ numerico
ou alfanumerico, com mascara integral aceita e DV correto. Nenhum endpoint,
cadastro real, login, migration, escrita no PostgreSQL ou dependencia nova.
Run Backend CI `39712992632` do codigo `7e8b953f`: 176/176 e pip check
PASS; novo HEAD documental exige conferencia do CI final antes do merge.
Fonte: [C16-R12.41](FRcaixinha_2_2_C16_R12_41_Validacao_CPF_CNPJ.md).
F2-05/F2-06/F2-07 continuam incompletos; Fase 2 em andamento, Fase 3
nao iniciada. Proximo gate: integrar PR apos CI do HEAD final e sincronizar
Termux por fast-forward. Nao repetir migrations ou recuperacao estrutural.

## C16-R12.46 — Preparacao de rascunho de identidade PF/PJ (22/10/2026)

Apos R12.45, backup Git da versao 894e74d8 foi recuperado em teste bare
R12.44 PASS e copiado ao Drive privado com SHA de download identico
R12.45 PASS; mantidos backups anteriores. C16-R12.46: modulo puro
`backend/app/identity_draft.py` de normalizacao de nome, e-mail e telefone
nacional com DDD valido, reunindo CPF/CNPJ de C16-R12.41 para preparar
rascunhos PF/PJ sem efeitos colaterais. Testes separados em
`backend/tests/test_identity_draft.py`. Nao ha autenticacao, API,
persistencia de dados pessoais, concessao de papeis, prova de representacao
PJ, ativacao de licencas, migration, banco extra ou dependencias novas.
PR #31 deve ter CI final PASS antes de integrar e atualizar Termux.
Registro detalhado: [C16-R12.46](FRcaixinha_2_2_C16_R12_46_Preparacao_Identidade_PF_PJ.md).
Fase 2 em andamento e funcionalidades PF/PJ/tenant ainda incompletas;
Fase 3 nao iniciada.
