# F2-05 / Issue #67 — fluxo PF demonstrativo offline

**Estado em 27/10/2026:** Lote 12 versionado no commit original `9f103b50db29529aa742340e7b3f169744fc4020`; [PR #69](https://github.com/fronassor-art/FRcaixinha-2.2/pull/69) OPEN/DRAFT, sem autorização de merge. A [Issue #67](https://github.com/fronassor-art/FRcaixinha-2.2/issues/67) permanece em andamento. Este registro técnico não aprova política de identidade, cadastro operacional nem tratamento real de dados pessoais.

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
- [Android APK CI run 40541359960](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/40541359960), no mesmo commit: PASS; APK debug compilado e verificado como não vazio, SHA-256 `4db0c70fe43fd72dc5c111afd19f6d8a7444d99aed20f8c5d420f0bde1596df6`. O workflow não publica o APK como artifact; instalação e execução no aparelho Android estão NOT_VERIFIED. O build padrão não define `FRC_PF_DEMO=true`, portanto mantém a tela demonstrativa desativada.
- A compatibilidade estática do código com Flutter 3.44.9/Dart 3.12.2 e o build Android passaram na mesma base de código usada no Termux. CI em Ubuntu não comprova comportamento no dispositivo Android real.

## Proteção do lote

O Master criou e restaurou no Termux normal o backup preventivo AGE dos quatro arquivos antes do commit: `FRcaixinha_2_2_I67_LOTE12_PRECOMMIT_20261027T162321Z.tar.gz.age`, 6368 bytes, SHA-256 `521eedc60110533147ccc3d0a846909b43f894f010d286cbc843d2d9fe9748fa`. A recuperação e a comparação dos quatro arquivos foram informadas como PASS; existência, tamanho e hash do AGE foram reconferidos pelo Codex. Esse backup antecede os commits e não substitui o backup final do futuro SHA integrado.

## Pendências para a Issue #67

1. Validar instalação e execução em aparelho Android real sob G2 própria. Um eventual APK com `FRC_PF_DEMO=true` exige build demonstrativo explicitamente autorizado; o APK debug atual mantém o modo desativado.
2. Executar regressão backend adicional no Python oficial Debian 3.13.5 quando pertinente a uma alteração futura; esta correção documental não altera backend nem acessa PostgreSQL.
3. Para persistência real, decidir sob G2 distinta a transação no PostgreSQL único, unicidade por CPF/e-mail, idempotência entre processos/reinício, autenticação e consulta de estado com controle de acesso. SQL e migrations permanecem NOT_RUN nesta G2.
4. Submeter confirmação real de e-mail, consentimentos e decisões IN06/IN08 às aprovações próprias; não inferir titularidade, retenção ou poderes.
5. Concluir revisão de governança da PR #69 e obter autorização de merge separada. Depois da integração estável, sincronizar o checkout único, validar backup final do novo SHA e registrar o checkpoint aplicável no GitHub.

`ISSUE_67=EM_ANDAMENTO`; `POSTGRESQL=NOT_ACCESSED`; `MIGRATIONS=NOT_RUN`; `CADASTRO_REAL=DISABLED`.
