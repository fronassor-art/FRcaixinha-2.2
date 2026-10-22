# C16-R12.56 — Manifesto criptográfico

Baseline: `95f19686e397fe04b103301897386b511d08146c`.

A auditoria C16-R12.56B identificou reutilização da mesma mensagem HMAC entre
CPF e CNPJ. A correção C16-R12.56C adiciona o domínio versionado
`FRCAIXINHA/LOOKUP/v1/<kind>` ao HMAC, sem adicionar tenant ou identificador de
registro à busca global. A chave de cifragem permanece separada da chave HMAC.

A implementação mantém `cryptography==50.0.2`, `cffi==2.0.0` e
`pycparser==2.22`, AES-256-GCM, envelope versionado, `key_id`, nonce aleatório
de 12 bytes e AAD canônico. A normalização CPF/CNPJ reutiliza
`app.document_validation`.

Os testes passaram a cobrir CPF com zero inicial, CNPJ alfanumérico, domínios
HMAC, entradas inválidas, envelope truncado, versão e chave desconhecidas,
contexto inválido e ausência de PII em erros e representações.

A rotação de chaves, persistência, integração API e validação real no
PostgreSQL continuam pendentes. Esta etapa não cria chaves, não acessa banco e
não executa migrations.


## C16-R12.56E — correção após execução oficial

A execução Python 3.13.5 identificou um CPF sintético inválido no teste de
zero inicial (`042.236.650-51`). O caso foi corrigido para
`042.236.650-14`, confirmado pelo `normalize_cpf()`, com resultado
`04223665014`.

Também foi corrigida a fronteira de exceção de `decrypt()`: o AAD agora é
construído antes da chamada AES-GCM. Assim, `CONTEXT_INVALID` permanece
identificável, enquanto adulteração ou divergência criptográfica continua
resultando em `DOCUMENT_AUTHENTICATION_FAILED`, sem expor PII ou segredos.

A correção H preserva os 12 testes criptográficos anteriores e acrescenta
um teste de autenticação do `key_id`, totalizando 13 testes criptográficos.
Com os 196 testes anteriores, o total esperado passa a 209 testes. A rotação de chaves, persistência e
validação real no PostgreSQL continuam pendentes.


## C16-R12.56H — autenticação do `key_id`

A auditoria G identificou que o `key_id` do envelope ainda não participava do
AAD. A correção H inclui o identificador validado no AAD versionado durante
cifragem e decifragem. Foi acrescentado teste que troca o identificador por
outro que reutiliza o mesmo material de cifragem; a autenticação falha
obrigatoriamente.
