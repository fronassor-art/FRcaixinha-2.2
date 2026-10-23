# C16-R12.111 — G3-C: plano de integridade, retenção e recuperação PostgreSQL

**Estado:** DOCUMENTAÇÃO PARA REVISÃO. **G3-C (operações no banco) NÃO AUTORIZADO.** Data: 22/10/2026, America/Belem. Issue #46. Baseline Git: **ec44a4752ebab7a68468a43f68ed422705b9fc52** (Pacotes 1–5 integrados). Escopo: apenas análise do código, matriz de riscos e planejamento. Nenhuma consulta PG, dump novo, recuperação, migration, chave, serviço, login ou pagamento foi executado.

## 1. Evidências e fonte de verdade

- Uma raiz ativa: **~/FRcaixinha_2.2**, Termux. Backups externos não são cópias ativas de desenvolvimento.
- Banco único: PostgreSQL Termux 18.2, **frcaixinha_2_2_dev**, **frc22_owner**, **127.0.0.1:5432**. Último inventário **READ ONLY C16-R12.99**: **public.alembic_version=c16r5_20261020**, 18 tabelas em public **incluindo alembic_version**, zero índices inválidos, zero constraints não validadas. Evidência datada; não houve consulta PG nesta etapa.
- **Head de código Alembic f2p4_20261022** contém uma minuta de quatro tabelas a partir da revisão c16r5_20261020; estar versionada no Git **não significa aplicada**. Os 21 modelos ORM em Base.metadata incluem 17 tabelas antigas e 4 propostas; não correspondem por si a tabelas instaladas.
- **CI do P5:** 305/305 PASS; verifica paridade offline, não DDL/concorrência no PostgreSQL.
- **Backup Git atual:** FRcaixinha_2_2_C16_R12_109_ec44a4752eba.bundle.age, 419084 bytes, SHA256 **0f4ac11cc3cfc9ecd35abc809e75cdc423ab1d1af7091b0e4decd43c587c31bf**, cópia AGE privada Drive ID **1LVK8A7xOVHqsh00QCSBos3Jtu0YFVSA6**, recuperado como Git no Termux e comparado após download.
- **Backup SQL histórico:** C16-R12.30 **FRcaixinha_2_2_C16_R12_30_67adc6eda5b9.dump.age**, 81166 bytes, SHA256 **702849367d765f27f44eac71cd51445efc8410c935afd048b4d3af9149217a4e**. Um ensaio estrutural histórico limitado não comprova recuperação funcional dos dados correntes. É necessário backup PostgreSQL **específico e atualizado** antes de uma migration real.
- **Executor protegido existente:** backend/tests/pg_migration_trial_executor.py prepara ensaios C15/C16 com destinos explicitamente travados, desabilitados por padrão. **Não** cobre automaticamente a minuta P4. Reuso exige projeto, revisão e autorização separados; não desabilitar gates para obter PASS.
- Registros antigos de 20–21/10 que dizem C15/C16 não aplicadas estão superados pelo read-only C16-R12.99. Conferir o estado real em novo preflight; não escolher a evidência conveniente.

## 2. Matriz de integridade e riscos

| ID | Evidência | Lacuna de segurança/integridade | Tratamento proposto (não autorizado) |
| --- | --- | --- | --- |
| IN-01 | registration_idempotency tem FKs individuais para identidade e contratante | PF pode referir outro pf_user_id; PJ pode referir outro representative_user_id; ambas FKs válidas isoladamente | Provar identidade–parte em transação, avaliar restrição composta/trigger ou validação serializável/locking com testes de races e troca de representante |
| IN-02 | InitialAttemptLookup.find_completed é porta abstrata e bootstrap é offline | Lookup negativo e criação concorrente podem conflitar; UNIQUE e CHECK TTL não garantem replay seguro | Reserva transacional, tratamento de conflitos UNIQUE e reconsulta do mesmo fingerprint sob guarda atômica e antiapropriação |
| IN-03 | EmailChallengeRecord carrega email mas a tabela email_confirmation_challenges não grava snapshot do contato | Mudança de e-mail, reuso de desafio e consumo simultâneo | Vincular identidade, e-mail atual, finalidade, expiração e token em transação única com consumo condicional; PJ nunca APTO pela confirmação |
| IN-04 | identity_sessions e SessionStore ainda abstratos | Suspensão, revogação e alteração de senha podem não invalidar sessão na prática | Estado e revogação consultados do servidor em cada uso, TTL <=15 min, sem claims cliente/RoleGrant implícito |
| IN-05 | identity_credentials.updated_at tem onupdate ORM, não trigger; UUIDs gerados em Python | Operações SQL diretas não recebem onupdate/UUID | Definir caminho único de escrita ou mecanismo PostgreSQL comprovável e auditado |
| IN-06 | user_identities possui unicidade de lower(email) e CPF HMAC mesmo com identidade PENDENTE; contracting_parties.tax_id_lookup_hmac é UNIQUE mesmo quando a PJ está PRELIMINAR (C15) | Pré-reserva indevida de CPF, e-mail **ou CNPJ** pode impedir que o titular legítimo cadastre uma PF ou PJ | Aprovar controle de tentativas/rate-limit, verificação de titularidade e representação, contestação da reserva de CNPJ, recuperação segura de PF/PJ e política para inscrições PENDENTE/PRELIMINAR abandonadas, sem apropriação de identidade ou liberação automática de CNPJ |
| IN-07 | downgrade f2p4 executa DROP TABLE em quatro tabelas | Perda de todos os dados posteriores à migration | Vetar downgrade destrutivo automático; plano de correção forward e recuperação real autorizada |
| IN-08 | CHECK limita TTL dos três artefatos | CHECK não apaga linhas expiradas; UNIQUE pode continuar ocupada | Limpeza segura limitada, retenção e relógio confiável, com races e idempotência testados |

A paridade ORM/DDLs foi confirmada por compilação em memória, **não** por INSERTs reais. Não alterar migrations sem nova PR e gate.

## 3. Retenção de dados — proposta sujeita a decisão jurídica e técnica

### Prazo para uso, já definido no código offline
- Desafio de e-mail: até **10 minutos** para validação.
- Sessão opaca: até **15 minutos**, podendo ser revogada antes.
- Replay de cadastro inicial: até **15 minutos**, desde que registro COMPLETED confiável e fingerprint idêntico.

### Retenção física, ainda NÃO aprovada
Validade não equivale à eliminação das linhas. CHECK e UNIQUE não são agendadores; idempotência RESERVED expirada pode bloquear reutilização. Não inventar prazos legais de guarda nem eliminar registros financeiros ou evidência sob obrigação de conservação.

**Decisões necessárias:** retenção mínima de hashes/pseudônimos por finalidade e base legal; tratamento de desafios e sessões expirados; cancelamento e disputa de cadastro PENDENTE e de PJ PRELIMINAR, inclusive quando CPF, e-mail ou CNPJ legítimo estiver pré-reservado; recuperação de cadastro PF/PJ com prova de titularidade/representação e rate-limit, sem tomada de conta de terceiro; auditoria minimizada, trilha de consentimento e preservação por obrigação legal; retenção de AGE backups e efeito de eventual eliminação. Consultar responsabilidade LGPD e regras aplicáveis antes de fixar dias, job ou cron.

**Segurança:** CPF/CNPJ em cifra autenticada; HMAC de busca, digests de tentativa e verificadores são protegidos como dados pessoais/pseudonimizados quando reidentificáveis. Nunca enviar ou registrar senha, token, segredo de e-mail, material criptográfico ou fingerprint. Custódia AGE/keyring fora de Git, banco e Flutter. Nenhum expurgo operacional neste pacote.

## 4. Plano futuro do backup PostgreSQL — NÃO EXECUTAR NESTE GATE

1. **G3-C.1 — preflight READ ONLY autorizado:** identificar versão do servidor/cliente, role, db, schema, alembic_version, tabelas, constraints, índices e espaço atual; conferir main e trabalho limpos. Se houver divergência, interromper.
2. **G3-C.2 — arquivo lógico consistente autorizado:** verificar ferramentas existentes antes de instalar; **pg_dump formato custom** da base única, leitura consistente em snapshot, anotando escopo de owners, ACLs, extensions, roles globais, que não são automaticamente todos contemplados por um dump da base. Definir documento de inventário de objetos e dados esperados.
3. **AGE streaming e integridade:** só com aprovação: senha interativa protegida, umask 077, pipefail, arquivo .partial fora do projeto, criptografia sem dump em claro persistente, promoção atômica ao final, SHA256 e permissões. Jamais passar senha por parâmetro, logs, ambiente persistente ou chat. Não sobrescrever backups anteriores.
4. **Checagem offline do arquivo:** descriptografar por fluxo protegido e conferir catálogo/TOC via **pg_restore --list**. A listagem do TOC não comprova leitura integral de dados nem autenticação do fluxo AGE até o fim: exigir também verificação separada de consumo integral do ciphertext/AGE até EOF, com códigos de saída controlados e sem armazenar dump em claro. Mesmo um arquivo integralmente legível **não comprova restauração funcional**. Registrar separadamente AGE_INTEGRITY, ARCHIVE_TOC_READABLE, ARCHIVE_CONTENT_CHECKED (se houver prova efetiva) e RESTORE_FUNCTIONAL.
5. **Cópia externa:** exportar somente .dump.age para local protegido e Drive privado **FRcaixinha_2.2_Backups**. Verificar nome, tamanho, SHA256, proprietário sem exposição pública; baixar a cópia e comparar byte a byte. Proteger metadados e segredos da base.
6. **G3-C.3 — restauração real:** exigir estratégia de ensaio com segurança e autorização separada. Não criar uma base persistente paralela nem restaurar inadvertidamente sobre public. **pg_restore --schema apenas filtra objetos do esquema nomeado; não remapeia os objetos do dump para outro esquema.** **pg_restore --single-transaction encapsula comandos em BEGIN/COMMIT e, se concluir com sucesso, CONFIRMA as alterações; não executa rollback preventivo.** Logo, nenhum desses parâmetros isoladamente oferece ensaio reversível na base autoritativa. Avaliar e revisar técnica de isolamento efetivo, nomes qualificados, FKs, extensões, ownership e forma explícita e verificável de desfazer qualquer escrita, antes de executar DDL/DML. Sem desenho seguro aprovado, registrar **BLOCKED**. Referência: [pg_restore PostgreSQL 18](https://www.postgresql.org/docs/18/app-pgrestore.html).
7. **G3-C.4 — correção de invariantes:** decisões PF/PJ, replay, consumo único, cleanup, revogação, timestamp e possíveis alterações da minuta em **outra PR**, com teste e revisão independente. Preservar arquivos históricos congelados.
8. **G3-C.5 — upgrade real:** autorização expressa adicional após backup PG recuperável, revisão de rollback, teste funcional e rechecagem de schemas, hashes e configuração. Planejar janela, condições de parada e pós-checkpoint. Nenhuma chamada a alembic upgrade/downgrade/stamp é autorizada aqui.

### Evidências mínimas de backup recuperável
SHA256 local e externo igual; localização e acessos; tamanho; escopo e ferramenta; revisão do PostgreSQL, commit Git e data; inventário restaurado em ambiente isolado autorizado e comparação de dados/constraints; verificação de não alteração do banco principal. **Um bundle Git não é dump PostgreSQL; pg_restore --list não é restauração funcional.**

## 5. Estados de portões

| Portão | Status neste checkpoint |
| --- | --- |
| G3-A — arquitetura G3-A | **PASS histórico** C16-R12.100 |
| G3-B — PostgreSQL read-only | **PASS datado** C16-R12.99; atualizar antes do risco |
| G3-C.0 — plano offline de segurança e backups | **PREPARADO PARA REVISÃO** |
| G3-C.1 — preflight SQL read-only novo | **NOT_RUN** |
| G3-C.2 — backup PostgreSQL atualizado | **NOT_RUN**, necessita autorização |
| G3-C.3 — ensaio de recuperação funcional SQL | **BLOCKED**, necessita desenho e autorização |
| G3-C.4 — invariantes e serviços transacionais | **BLOCKED** até revisão/implementação separada |
| G3-C.5 — aplicar migration f2p4 | **NÃO AUTORIZADO** |
| G3-D — concorrência, rollback e provas PostgreSQL | **NOT_RUN / BLOCKED** |
| G3-E — API, login e entrega real de e-mail | **BLOCKED** |

## 6. Critérios de encerramento do documento

- Esta entrega possui apenas um arquivo documental novo, em **uma branch e uma PR DRAFT sem merge**. Não modifica banco, migrations, test runner, ambiente ou contratos aprovados.
- GitHub Actions, caso disparado, valida código existente; relatório deve dizer explicitamente o SHA, sucesso/falha e limites.
- Governança: um diretório, uma base, nenhuma instalação duplicada, nenhum erro bloqueante mascarado, backups distintos, acesso mínimo e aprovações por risco.
- Espaço livre no Termux reportado após o backup anterior: aproximadamente **19 GB (82% de uso)**; confirmar de novo antes de uma futura geração de artefatos SQL.
- O plano não altera o Contrato Técnico Mestre, não concede autorização de operação e **não encerra G3-C**.

**Decisão futura exigida do proprietário:** autorizar **separadamente** preflight read-only; backup PG novo criptografado; ensaio funcional de restore; alterações de esquema/transações; e, por último, upgrade real. A execução de uma etapa não autoriza as demais.
