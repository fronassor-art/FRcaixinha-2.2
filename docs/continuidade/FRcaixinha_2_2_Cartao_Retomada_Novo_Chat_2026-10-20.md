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
