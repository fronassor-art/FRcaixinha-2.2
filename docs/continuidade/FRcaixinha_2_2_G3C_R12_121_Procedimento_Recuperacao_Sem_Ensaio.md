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
