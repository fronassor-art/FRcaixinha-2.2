# C16-R12.121 — G3-C.3: procedimento de contingência e recuperação, sem ensaio funcional

**Data:** 22/10/2026 (America/Belem). **Issue:** #46. **Escopo:** documentação/revisão somente, sem acesso a PostgreSQL nesta entrega. **Git base:** `2df05b027bd1f4fdf8c8eebea9344d264c5ae0e6`. Esta proposta não substitui o Contrato Técnico Mestre nem altera regras aprovadas.

## 1. Decisão do proprietário e distinção de evidências

O proprietário determinou **priorizar velocidade**, não repetir agora o ensaio de recuperação funcional, **documentar/revisar** um procedimento seguro e continuar o desenvolvimento. A decisão **dispensa temporariamente o ensaio**, não o transforma em prova de recuperação. Um backup validado offline ainda pode falhar ao reconstruir dependências, permissões, extensões, vínculos e dados.

- **G3-C.3-PLANO_DOCUMENTAL:** `DRAFT/EM_REVISAO` até revisão independente e integração autorizada.
- **G3-C.3-RESTAURACAO_FUNCIONAL:** `NOT_RUN / RISCO_RESIDUAL_ACEITO_TEMPORARIAMENTE`; **nunca PASS** sem recuperação de fato e inventário conferido.
- **G3-C.4 DESENVOLVIMENTO OFFLINE:** pode avançar em **PR separada**, com modelos puros, invariantes e testes sem PostgreSQL, desde que não haja erro bloqueante conhecido na etapa.
- **G3-C.4 acesso transacional real, G3-D provas PostgreSQL e G3-E API operacional:** **não liberados** por esta dispensa.
- **G3-C.5 migration `f2p4_20261022`: NÃO AUTORIZADA**; o plano original exigia teste de recuperação e autorização específica para upgrade real. Nenhum gate implícito, inclusive este documento, o contorna.

Não interpretar `FINALIZADO_DOCUMENTALMENTE` como `RECUPERACAO_FUNCIONAL_COMPROVADA`. Antes de operação irreversível ou dados reais, reavaliar o risco e obter autorização explícita para ensaio seguro ou decisão formal de risco compatível com o contrato.

## 2. Evidência congelada no checkpoint

| Componente | Evidência |
| --- | --- |
| Git `main` Termux/GitHub | `2df05b027bd1f4fdf8c8eebea9344d264c5ae0e6`; sincronização C16-R12.114 PASS |
| Git backup AGE | `FRcaixinha_2_2_C16_R12_115_2df05b027bd1.bundle.age`; SHA-256 `9ec8efca1cbebc37b97626243a6ee148b3ca264b96992734e961cff5bf64ec8c`; bare Git/fsck no Termux PASS; Drive ID `1k1eskaCeqdhaxphsZvMVPThBKIi2BacP`; cópia remota idêntica PASS |
| PostgreSQL autoritativo | PostgreSQL 18.2 Termux; `frcaixinha_2_2_dev`, role `frc22_owner`, host `127.0.0.1:5432`; G3-C.1 C16-R12.118 READ ONLY PASS |
| Alembic instalada | `public.alembic_version=c16r5_20261020`; 18 tabelas public incluindo `alembic_version`; F2P4 **não aplicada** |
| PostgreSQL backup AGE | `FRcaixinha_2_2_C16_R12_119_PG18_c16r5_2df05b027bd1.dump.age`; 81166 bytes; SHA-256 `0c44f1bb4f620b25bb81a3311583bf281fe9964ec43dc1cdb5e84c8cdae26545`; Drive ID `1q9OKh7GKxD2Z7x3aArlAz_xTubPqR3fd` |
| PostgreSQL testes do arquivo | C16-R12.119R1 pg_dump -Fc → AGE + validação integral AGE + `pg_restore --list` + geração offline do SQL para `/dev/null` = PASS; Drive C16-R12.120 checksum/bytes PASS |
| Prova **não disponível** | Restauração funcional real, comparação de dados reconstruídos/constraints e prova de RTO/RPO = NOT_RUN |

Esses hashes referem-se ao momento do backup, não a estados futuros. O ensaio Git histórico utilizou `git fsck --full --strict`. Nenhuma senha, chave AGE ou segredo PostgreSQL deve constar neste documento.

## 3. Procedimento de recuperação **para revisão, NÃO EXECUTAR NESTA ETAPA**

**Gatilho:** incidente que comprometa disponibilidade/integridade, perda de dados ou solicitação expressa de ensaio futuro. Qualquer execução exige portão próprio do proprietário. Este documento não autoriza comandos operacionais.

### Fase 0 — contenção e autorização

1. Interromper imediatamente operações financeiras/API e **escritas** na base afetada; impedir novas transações. Não tentar `alembic downgrade`, `stamp`, `pg_restore`, `DROP`, `TRUNCATE` ou `CREATE DATABASE` por impulso.
2. Registrar horário/local da ocorrência, versão dos executáveis, base, commit Git, estado de Git e dispositivos; conservar evidências sem logs de CPF/CNPJ, senha, token ou chave. Se possível, preservar cópia protegida da mídia comprometida sem sobrescrever o último backup íntegro.
3. Nomear operador e revisor; delimitar cenário (**indisponibilidade**, **corrupção**, **perda de chave AGE**, **inconsistência de dados**) e ponto de recuperação; registrar autorização escrita específica para cada operação de escrita, destino e janela.
4. Parar com `BLOCKED` se não houver chave recuperável, backup íntegro, espaço, estratégia de destino ou compatibilidade PostgreSQL demonstrada.

### Fase 1 — seleção dos arquivos e integridade sem alterar banco

1. Identificar a cópia AGE original e a cópia privada Google Drive sem modificar permissões; baixar somente para pasta protegida, fora da raiz ativa e sem sobrescrever arquivos.
2. Conferir **nome, tamanho, SHA-256, data e escopo** comparando a evidência registrada e os arquivos obtidos; verificar cadeia de custódia AGE. Conferir versão de cliente/servidor e o inventário de extensões, roles globais, ACLs, ownership, tablespaces e configurações externos ao dump de uma base.
3. Somente em fluxo efêmero protegido, validar criptografia até EOF, catálogo/TOC e legibilidade de conteúdo. **São provas offline**; não converter estas checagens em status de restauração funcional.
4. Inventariar objetos previstos: schema `public`, `alembic_version`, tabelas, índices, constraints, sequences, FKs, dados, tipos, funções e grants; definir método para comprovar quantidade/consistência pós-restauração. Não divulgar dados pessoais nos relatórios.

### Fase 2 — projeto do destino seguro, sem atalhos

1. Priorizar **destino logicamente e fisicamente isolado do banco autoritativo**, sem acesso aos arquivos `PGDATA` e sem a mesma porta/socket. O requisito de **um banco persistente autoritativo** permanece. Qualquer ambiente efêmero de ensaio, se permitido no futuro, deve ser pré-aprovado, ter escopo/vida útil/limpeza auditáveis e não virar base persistente paralela.
2. **Não restaurar no esquema `public` do banco autoritativo** nem em `postgres`; não executar `pg_restore -d frcaixinha_2_2_dev` em modo de ensaio. O único banco autorizado permanece imutável na etapa documental.
3. `pg_restore --schema` **seleciona** esquema existente no arquivo, **não remapeia** nomes para um esquema de ensaio. `--single-transaction` faz `BEGIN/COMMIT` quando conclui sem erro, não executa `ROLLBACK` preventivo; não usar essas opções como pretensa segurança para a base real.
4. Rever instruções SQL de um arquivo de origem confiável: uma restauração pode executar código do superusuário de origem; evitar `--clean` e `--create` sem aprovação específica. Garantir owner/roles, extensões, encoding, collation e dependências necessárias antes de qualquer restauração autorizada.
5. Se isolamento verificável **não for tecnicamente viável sem novo ambiente** e criação de ambiente não estiver autorizada, o ensaio permanece `BLOCKED`. Não afrouxar a política criando banco/serviço paralelo inadvertidamente.

### Fase 3 — execução futura (somente com autorização específica)

1. Aprovar plano operacional separado com identidade do executor, destino literal verificado, comandos exatos revisados, janela, limiares de parada, rollback/limpeza e backup pré-operação.
2. Exigir revisão independente da segurança do destino e de todos os comandos com conexão. **Este documento deliberadamente não oferece um comando executável de restauração**, prevenindo execução acidental em banco autoritativo.
3. Executar somente no destino aprovado, testar falha/recuperação sem dados reais se for ensaio, registrar saída e encerrar sessão; não promover automaticamente o resultado de um ensaio para produção.

### Fase 4 — provas pós-recuperação e encerramento

1. Comparar `alembic_version`, schema e objetos, número de linhas e agregados não identificadores previamente inventariados, constraints/indexes válidos, FKs, sequences, checksums quando adequados, ACLs/owners/extensões, e trilhas que suportem integridade financeira — nunca apenas `pg_restore --list`.
2. Confirmar que a base autoritativa original **não foi alterada no ensaio** e que nenhuma cópia paralela persistente permaneceu. Registrar RPO, RTO, pontos ausentes e limites; sem evidência, `RESTORE_FUNCTIONAL=NOT_RUN/BLOCKED/FAIL`, conforme caso.
3. Registrar decisão explícita de retorno de serviços após validações e autorização, com responsabilidades e proteção de credenciais. Nenhum dado real poderá ser substituído silenciosamente.

## 4. Limites financeiros, legais e de retenção

- Backups são snapshots: não garantem recuperação de transações posteriores, objetivos RPO/RTO nem arquivo completo de roles globais; definir perda tolerável e guarda/expurgo com responsabilidade legal antes da operação real.
- Não criar recuperação que desbloqueie CPF, e-mail ou CNPJ `PENDENTE/PRELIMINAR` sem prova de titularidade/representação; manter matriz IN-01–IN-08 da PR #47 para G3-C.4.
- Não copiar o AGE para locais públicos, não colocar segredo no Git/Flutter/Issue/console; senha/chave única deve possuir custódia privada e caminho recuperável.
- A restauração em ambiente real é **um evento de alto risco**, exige autorização própria e não é substituída pelo backup Git.

## 5. Critério de conclusão para manter agilidade

**Entrega desta PR:** exatamente um arquivo Markdown documental; sem alterações em backend, migration, tabelas, testes ou ferramentas. Conferência autoral e revisão independente do texto; após `PASS` e autorização de merge, marcar `G3-C.3-PLANO_DOCUMENTAL=PASS`, mantendo `G3-C.3-RESTAURACAO_FUNCIONAL=NOT_RUN (dispensa temporária expressa)`.

**Trilha rápida permitida em paralelo:** iniciar projeto/testes **offline** das invariantes IN-01 a IN-08 em PR separada, reutilizando dependências existentes, com correção imediata de erros e sem aplicar SQL. A aprovação do plano **não libera** migrations, concorrência real, remoção de dados, autenticação pública, emissão de e-mail/PIX, G3-D/E nem novos serviços.

**Condições para retomar ensaio funcional futuro:** (a) incidente real; (b) antes de uma migração destrutiva ou escrita de alto risco; (c) quando houver ambiente efêmero e plano de recuperação aprovados; (d) revisão formal do portão G3-C.5. **Sem a prova funcional, não declarar o banco plenamente recuperável.**

## 6. Referências técnicas

- PostgreSQL 18 `pg_dump`: https://www.postgresql.org/docs/18/app-pgdump.html — snapshot consistente e backup de base única; roles/tablespaces globais fora do dump.
- PostgreSQL 18 `pg_restore`: https://www.postgresql.org/docs/18/app-pgrestore.html — restaurar executa comandos no destino se for fornecido `-d`, opção de esquema como filtro, `--single-transaction`, opções perigosas e riscos de SQL do arquivo.
- PostgreSQL 18 SQL Dump: https://www.postgresql.org/docs/18/backup-dump.html — dependências, permissões e limites de backup lógico.
- Plano G3-C original aprovado na PR #47: `docs/continuidade/FRcaixinha_2_2_G3C_R12_111_Plano_Integridade_Retencao_Recuperacao_PostgreSQL.md`.

**Status ao redigir:** `G3-C.3-PLANO_DOCUMENTAL=EM_REVISAO`; `RESTORE_FUNCTIONAL=NOT_RUN`; `G3-C.4_OFFLINE=PODE_PLANEJAR`; `G3-C.5=NAO_AUTORIZADO`.

---

## 7. Adendo cronológico de reconciliação — 26/10/2026 (C236; revisão documental da PR #48)

**Natureza deste adendo:** atualização temporal posterior à proposta original de 22/10/2026. Os itens 1 a 6 acima ficam **integralmente preservados como fotografia do momento em que foram escritos**. Expressões como `RESTORE_FUNCTIONAL=NOT_RUN`, `F2P4 não aplicada` e `NÃO AUTORIZADA` na fotografia original não constituem o estado vigente e não devem ser reutilizadas sem data e contexto. Este adendo **não autoriza** recuperação, escrita SQL, migration, operação financeira, publicação de API ou merge.

### 7.1. Restaurações funcionais posteriores ao documento original

- **C16-R12.122R1 — 23/10/2026: `FUNCTIONAL_RESTORE=PASS` do backup AGE C119.** A restauração foi realmente executada em cluster PostgreSQL 18 **efêmero e isolado**, com socket privado, TCP desabilitado, inventário da revisão `c16r5_20261020`, **18 tabelas**, índices e constraints válidos, paridade de contagens das 18 tabelas em relação à base autoritativa, descarte e conferência posterior da base principal, sem escrita nela. A tabela Alembic continha 1 linha; as 17 tabelas de negócio continham 0 linhas. A prova **não** demonstra recuperação de informações financeiras populadas nem RPO/RTO real. [Registro probatório C122R1](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6362432633).
- **C16-R12.136 — 23/10/2026: `FUNCTIONAL_RESTORE=PASS` do backup AGE C132.** Segundo restore efetivo em cluster PG18 efêmero isolado, revisão `c16r5_20261020`, 18 tabelas (17 de negócio vazias), conferência de índices, constraints, isolamento, descarte e base principal pós-ensaio. O backup C132 testado tinha SHA-256 `0b64d0009bc7a5e5e32c36a94d5a22e85fe20e224eba20496b2aa0143295ed8f`. Também **não** demonstra recuperação de dados financeiros populados, testes de concorrência ou cumprimento de RPO/RTO. [Registro probatório C136](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6364733470).
- **C16-R12.166/C167:** reconciliações posteriores reconheceram expressamente essas provas e impediram reclassificar os restores concluídos como `NOT_RUN`. [C166](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6377345192) · [C167](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6377564303).

**Alcance do PASS:** refere-se somente à restauração comprovada dos backups C119 e C132 nas condições documentadas. Não se estende automaticamente ao backup posterior C205, à recuperação de dados financeiros reais, às operações dos novos adaptadores ou às provas físicas de concorrência PostgreSQL.

### 7.2. Migration posterior, backup e conferência do banco original

- **C16-R12.203R5 — 24/10/2026:** após autorização G2 específica e preflight, foi aplicada efetivamente a migration Alembic `c16r5_20261020 → f2p4_20261022` no **único banco autoritativo** `frcaixinha_2_2_dev` (PostgreSQL 18). Pós-verificação: revisão `f2p4_20261022`, **22 tabelas** e índices/constraints esperados verificados, `PASS`. [C203R5](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6388195740).
- **C16-R12.204:** regressão **offline** 465/465 PASS e consulta PostgreSQL READ ONLY de revisão, 22 tabelas e integridade estrutural, PASS. Não equivale a ensaio físico de idempotência, locks ou concorrência. [C204](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6388259912).
- **C16-R12.205/C206:** produzido backup pós-F2P4 `FRcaixinha_2_2_C16_R12_205_PG18_f2p4_1685d987_20261024_160549.dump.age` (95.606 bytes, SHA-256 `a10fb867ef77d2a13994cb3e2c253003ced814b28f35026a42c58e78fee17337`). Verificações AGE/TOC/conteúdo offline e cópia privada Google Drive com conferência remota foram registradas como PASS. **Restore funcional específico do backup C205 = NOT_RUN**, não confundir com C122R1/C136. [C205](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6388394790) · [C206 / consolidação pós-F2P4](https://github.com/fronassor-art/FRcaixinha-2.2/pull/55#issuecomment-6388534595).
- **Conferência de continuidade fornecida pelo Administrador Master em 25–26/10/2026:** o cluster original em `$PREFIX/var/lib/frcaixinha_2_2_pg18` foi iniciado de modo controlado após uma interrupção anterior; uma transação `REPEATABLE READ READ ONLY` confirmou **PostgreSQL 18.2**, banco `frcaixinha_2_2_dev`, `alembic_version=f2p4_20261022`, **22 tabelas**, **0 índices inválidos** e **0 constraints não validadas**, com `ROLLBACK` e `conferencia_f2p4=PASS`. O servidor foi depois desligado normalmente (`Database cluster state: shut down`). Não houve execução de migration, restauração ou criação de cluster nesta conferência. As saídas foram fornecidas pelo operador; o redator não executou os comandos no aparelho. [Checkpoint vigente da Issue #46](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46).

### 7.3. Estado vigente e portões preservados

| Controle | Classificação após reconciliação |
| --- | --- |
| Restauração funcional AGE C119 e C132, no escopo ensaiado | **PASS HISTÓRICO** — C122R1/C136 |
| Banco autoritativo PostgreSQL / Alembic F2P4 | **APLICADA e RECONFIRMADA**; não reaplicar nem executar downgrade |
| Backup AGE pós-F2P4 C205, legibilidade e cópia externa | **PASS HISTÓRICO**; restore funcional específico **NOT_RUN** |
| Concorrência de duas conexões, locks, idempotência, revogação e rollback reais | **NOT_RUN / PENDENTE**, não inferir dos testes offline |
| Triggers adicionais IN-05 | **NÃO INSTALADOS** |
| IN-06/IN-08 | Desenhos parcialmente aprovados; decisões e validações operacionais **PENDENTES** |
| G3-C.3 — procedimento documental desta PR #48 | **AGUARDANDO REVISÃO INDEPENDENTE E DECISÃO EXPRESSA DO MASTER** |
| API operacional, e-mail, login, Pix e movimentação financeira | **NÃO AUTORIZADOS** |

**Encerramento desta revisão documental:** o procedimento de contingência original permanece uma referência de planejamento, não um roteiro operacional liberado. O adendo elimina a contradição entre sua fotografia inicial e os fatos posteriores **sem reescrever a história**. A PR #48 permanece Draft; somente após auditoria documental independente e autorização expressa poderão ser decididos o merge ou o encerramento justificado. A regularização da PR #48 deve ser concluída antes de avançar à #54 e à #56, conforme a fila bloqueante do Administrador Master.
