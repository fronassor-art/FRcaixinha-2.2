# Fase 2, Pacote 2 — preparação offline de cadastro PF/PJ

Referência: [Issue #37](https://github.com/fronassor-art/FRcaixinha-2.2/issues/37). Entrada: `cd3dc98cd8c40549070440ad4eae578707790a00`.

## Decisão implementada

`identity_registration_offline.py` combina os rascunhos PF/PJ existentes com `identity_document_protection.py`. O chamador fornece, antes da cifra, UUIDs definitivos e distintos para `UserIdentity` e `ContractingParty`, um `DocumentCrypto` configurado externamente e uma porta de consulta de conflitos. O serviço não cria UUID, chave, sessão, usuário, banco ou tenant. CPF permanece somente na identidade global; CNPJ aparece somente na PJ. O representante PJ é uma identidade pendente distinta da pessoa jurídica. A PJ fica `PRELIMINAR`, sem prova de poderes. A PF também fica `PRELIMINAR`; sua identidade fica `PENDENTE`.

As saídas imutáveis contêm bytes protegidos, HMAC e campos cadastrais normalizados. Não contêm CPF/CNPJ em claro, `auth_subject`, fatos de verificação, papéis, aceites ou permissões. A representação textual das saídas é redigida. **Esses objetos não são comandos de inserção e não podem ser serializados para API pública.** Nome, e-mail e telefone continuam dados pessoais em memória e exigem tratamento próprio na integração futura.

`ConflictProbe` é obrigatório e falha fechado em erro, ausência ou resposta ambígua. A ocorrência de CPF, e-mail ou CNPJ já observado rejeita nova preparação. Uma identidade preexistente, inclusive representante PJ, exige fluxo separado de vínculo autenticado e prova de autorização; não há associação silenciosa. A porta é apenas observação offline: ela não comprova origem confiável, consistência temporal, idempotência nem proteção contra corrida. As constraints UNIQUE da base e uma única transação continuam indispensáveis antes de qualquer persistência.

## Gates ainda pendentes

1. **Custódia de chaves:** aprovar origem, acesso mínimo, recuperação e rotação da chave de cifra. A chave HMAC global deve permanecer estável ou ter transição explícita que preserve buscas e unicidade; nenhuma chave operacional foi criada aqui.
2. **Credenciais e sessões:** decidir provedor ou credencial local, origem confiável de `auth_subject` (coluna obrigatória do modelo), digest, revogação e recuperação. Nenhuma identidade pode ser gravada apenas com a saída offline.
3. **Contato e representação:** prova verificável do e-mail antes de ativação; confirmação do telefone para recuperação ou ato sensível; prova documental e validação de poderes antes de PJ `APTO`. Foto segue opcional; endereço deve ser coletado somente por finalidade definida.
4. **Persistência e API:** autorização própria para contrato versionado de API, autenticação, política por recurso, proteção contra abuso, carregamento de fatos confiáveis no servidor, idempotência, UNIQUE e transação única. Revalidar conflitos dentro da transação e testar concorrência/rollback em PostgreSQL autorizado. Nunca aceitar o resultado do probe offline como autorização de escrita.
5. **Isolamento:** identidade CPF/HMAC é global. Associação a tenant/ciclo e acesso a recursos exigem fluxo explícito e política `resource_authorization`; nenhum tenant, membro, licença, pagamento ou capacidade financeira nasce desta preparação.

O projeto permanece sem endpoint de cadastro operacional, sem migração nova e sem escrita PostgreSQL neste pacote. O backup AGE Git do baseline C16-R12.89 tem SHA-256 local registrado `62d3c255ee18573efd91455e3473f4ba19d9f8b3ffc7506021be3076a7bcf4a2`; a confirmação de upload desse arquivo ao Drive ainda era pendente na Issue #37. Não foi repetido backup.
