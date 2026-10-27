# F2-05 / Issue #67 — fluxo PF demonstrativo offline

**Estado em 27/10/2026:** Lote 12 versionado no commit original `9f103b50db29529aa742340e7b3f169744fc4020`; [PR #69](https://github.com/fronassor-art/FRcaixinha-2.2/pull/69) OPEN/DRAFT, sem autorização de merge. A versão auditada 71778a03a8c9bf98b4f0b5bfff2a646442428bfa envolveu cinco arquivos: os três arquivos Flutter, esta nota e o workflow Android. O job temporário pf-demo-debug-apk cumpriu sua finalidade e foi removido nesta correção pré-merge; o job Android padrão foi preservado. A [Issue #67](https://github.com/fronassor-art/FRcaixinha-2.2/issues/67) permanece em andamento. Este registro técnico não aprova política de identidade, cadastro operacional nem tratamento real de dados pessoais.

## Arquitetura e reutilização

- `backend/app/pf_demo_api.py` cria a aplicação FastAPI de demonstração por `create_demo_app()`; `backend/app/main.py` não a monta. A rota de recebimento devolve HTTP 202 e corpo neutro, sem referência de solicitação, CPF, e-mail, token ou estado privado.
- `backend/app/pf_preregistration.py` usa `prepare_person_draft` para validar e normalizar entrada. O armazenamento transitório é injetado por instância, usa HMAC com chave efêmera, lock para duplicidade/idempotência e token simulado com expiração, consumo único e limite de cinco falhas. Não persiste nem autentica.
- `identity_registration_offline.py`, `identity_document_protection.py` e `crypto_documents.py` já preparam CPF cifrado e índice de busca para uma futura etapa autorizada. O fluxo anônimo de demonstração não os chama: a preparação protegida precisa de chaves sob custódia, verificação de conflito e identidade/vínculo adequados.
- `identity_persistence_contract.py` exige `ResolvedAuthSubject` confiável e sessão válida para `PreliminaryWriteIntent`. A alegação anônima não fornece esse sujeito; este lote não fabrica um.
- `mobile/lib/pf_demo.dart` contém uma tela de campos somente leitura com uma ficha sintética fixa e uma porta local injetável. `LocalPfDemoGateway` não faz HTTP, gravação em disco, mensagem ou operação financeira. `mobile/lib/main.dart` mantém o demonstrador desativado por padrão; apenas uma compilação deliberada com `--dart-define=FRC_PF_DEMO=true` ou a injeção explícita em teste mostra a tela. A tela não consulta nem confirma o backend. Seu reconhecimento é uma simulação local, não uma resposta de servidor.

## Contrato da demonstração

A ficha contém nome, CPF formalmente válido, e-mail e telefone sintéticos. A ação local valida apresentação e exibe somente um reconhecimento genérico. Confirmação de contato, autenticação, prova civil, criação de `UserIdentity`/`ContractingParty`, associação a tenant, `Membership`, `RoleGrant`, licença, sessão e acesso financeiro não ocorrem. Validação formal de CPF não atesta titularidade. Nenhum status privado é consultável por referência pública.

A futura integração de transporte requer uma API própria sob G2, com autenticação e autorização proporcionais, custódia de chaves, contratos versionados, proteção contra abuso e observação de enumeração por tempo/cabeçalhos. O demonstrador local não deve ser confundido com essa integração.

## Verificações do lote

- Regressões backend prévias da main integrada: 564/564 no CI da PR #68, conforme checkpoint da Issue #46; não são execução nova deste lote nem do commit documental.
- Novos testes Flutter em `mobile/test/pf_demo_test.dart`: modo padrão ausente, campos fixos somente leitura, estado de processamento, reconhecimento neutro, validação, falha genérica e rejeição de ficha diferente pela porta local.
- `flutter analyze --no-pub`: PASS no Termux, com Flutter 3.44.9 e Dart 3.12.2. Testes de widgets locais: BLOCKED antes da execução pelo carregamento do `flutter_tester`, devido à ausência de `libfontconfig.so`; nenhuma instalação foi feita nesta G2.
- [Flutter CI run 40541360026](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40541360026), no commit original `9f103b50db29529aa742340e7b3f169744fc4020`: PASS; análise sem problemas e 7 testes de widgets PASS no Ubuntu. Esse resultado não representa execução dos widgets no celular.
- [Android APK CI run 40541359960](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40541359960), no mesmo commit: PASS; APK debug compilado e verificado como não vazio, SHA-256 `4db0c70fe43fd72dc5c111afd19f6d8a7444d99aed20f8c5d420f0bde1596df6`. Esse build padrão não publicou APK como artifact e não define `FRC_PF_DEMO=true`, portanto mantém a tela demonstrativa desativada.
- Na versão auditada 71778a03a8c9bf98b4f0b5bfff2a646442428bfa, [Flutter CI run 40558229015](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40558229015) passou com análise sem problemas e sete testes; [Android APK CI run 40558228929](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40558228929) passou nos jobs padrão e demonstrativo. O build demonstrativo usou --dart-define=FRC_PF_DEMO=true; SHA-256 do APK original b6788c0d499ce5355273bb1799709ec3be479c7d13882c4ba282a348252e3390 e do APK cifrado por AGE 9a45afce61d1e8b0eefd537fa8303422de4f2d406dad585944ce8ea9326fe6bc. Somente app-debug.apk.age foi publicado como artifact pf-demo-pr69-71778a03a8c9bf98b4f0b5bfff2a646442428bfa (ID 12758132634); a identidade AGE privada não foi incluída no workflow.
- O Master [registrou na Issue #67](https://github.com/fronassor-art/FRcaixinha-2.2/issues/67#issuecomment-6451274373) instalação e execução do demonstrador no Android real: tela PF exibida, campos somente leitura, ação “Simular envio” com mensagem neutra, rotação horizontal, fechamento e reabertura PASS. Essa evidência visual não equivale a aprovação de cadastro operacional nem a prova dinâmica de ausência de toda comunicação externa.
- A compatibilidade estática do código com Flutter 3.44.9/Dart 3.12.2, os testes de widgets no CI, o build Android e a validação visual no aparelho são evidências distintas. O teste local de widgets no Termux permanece bloqueado por libfontconfig.so ausente.

## Proteção do lote

O Master criou e restaurou no Termux normal o backup preventivo AGE dos quatro arquivos antes do commit: `FRcaixinha_2_2_I67_LOTE12_PRECOMMIT_20261027T162321Z.tar.gz.age`, 6368 bytes, SHA-256 `521eedc60110533147ccc3d0a846909b43f894f010d286cbc843d2d9fe9748fa`. A recuperação e a comparação dos quatro arquivos foram informadas como PASS; existência, tamanho e hash do AGE foram reconferidos pelo Codex. Esse backup antecede os commits e não substitui o backup final do futuro SHA integrado.

Antes da correção pré-merge, o Master criou e restaurou FRcaixinha_2_2_PR69_PREMERGE_PRECHANGE_20261027T213119Z.tar.gz.age, 5021 bytes, SHA-256 068a82097f844a68a96f3cbb13c48e8cc005a43ed18031c69198bd4d8a81fdce. Relatou BACKUP_RESTORE=PASS, comparação dos dois arquivos restaurados com os originais e BACKUP_VERIFY_EXIT_CODE=0. Essa cópia protege o estado anterior à correção, sem substituir o backup final do SHA que vier a ser integrado.

## Pendências para a Issue #67

1. Preservar as evidências da instalação e validação visual já realizadas no aparelho. A distribuição futura de APK demonstrativo e qualquer teste operacional exigem gate próprio; o build Android padrão continua com o modo PF desativado.
2. Executar regressão backend adicional no Python oficial Debian 3.13.5 quando pertinente a uma alteração futura; esta correção documental não altera backend nem acessa PostgreSQL.
3. Para persistência real, decidir sob G2 distinta a transação no PostgreSQL único, unicidade por CPF/e-mail, idempotência entre processos/reinício, autenticação e consulta de estado com controle de acesso. SQL e migrations permanecem NOT_RUN nesta G2.
4. Submeter confirmação real de e-mail, consentimentos e decisões IN06/IN08 às aprovações próprias; não inferir titularidade, retenção ou poderes.
5. Concluir revisão de governança da PR #69 e obter autorização de merge separada. Depois da integração estável, sincronizar o checkout único, validar backup final do novo SHA e registrar o checkpoint aplicável no GitHub.

`ISSUE_67=EM_ANDAMENTO`; `POSTGRESQL=NOT_ACCESSED`; `MIGRATIONS=NOT_RUN`; `CADASTRO_REAL=DISABLED`.
