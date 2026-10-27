# F2-05 / Issue #67 — fluxo PF demonstrativo offline

**Escopo deste lote:** implementação local sem commit. Este registro técnico não aprova política de identidade, cadastro operacional nem tratamento real de dados pessoais.

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

- Regressões backend prévias da main integrada: 564/564 no CI da PR #68, conforme checkpoint da Issue #46; não são execução nova deste lote.
- Novos testes Flutter em `mobile/test/pf_demo_test.dart`: modo padrão ausente, campos fixos somente leitura, estado de processamento, reconhecimento neutro, validação, falha genérica e rejeição de ficha diferente pela porta local.
- `flutter analyze --no-pub`: execução deste lote; resultado e limitações constam no relatório ao Master. `flutter test --no-pub` depende do `flutter_tester` funcional no ambiente existente.

## Pendências para a Issue #67

1. Revisar e executar os testes de widgets no toolchain autorizado antes de versionar a interface.
2. Executar regressão backend no Python oficial Debian 3.13.5; esta G2 não acessa PostgreSQL.
3. Para persistência real, decidir sob G2 distinta a transação no PostgreSQL único, unicidade por CPF/e-mail, idempotência entre processos/reinício, autenticação e consulta de estado com controle de acesso.
4. Submeter confirmação real de e-mail, consentimentos e decisões IN06/IN08 às aprovações próprias; não inferir titularidade, retenção ou poderes.
5. Revisar a diferença local, versionar em gate específico, integrar somente depois de checks e revisão, então validar backup recuperável e checkpoint GitHub.

`ISSUE_67=EM_ANDAMENTO`; `POSTGRESQL=NOT_ACCESSED`; `MIGRATIONS=NOT_RUN`; `CADASTRO_REAL=DISABLED`.
