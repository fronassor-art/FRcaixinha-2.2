# C16-R12.46 — Preparacao PF/PJ sem persistencia (22/10/2026)

## Contrato e escopo autorizado

O proprietario determinou "Prossiga" apos C16-R12.45 com backup Git
`894e74d8fd6a3b2a3c17c25c4a31d9f83cd3ae96` criptografado,
recuperado em ambiente temporario e confirmado por download/SHA na pasta
Google Drive `FRcaixinha_2.2_Backups` (acesso apenas do proprietario).

Contrato Tecnico Mestre aprovado de 16/10/2026, clausulas 3.1-A,
3.1-A.1, 3.1-A.2, 6.1-A, 6.1-A.1/6.1-A.2 e 13.1-13.2: identificacao
PF/PJ, CPF/CNPJ, nome, e-mail confirmado, telefone com DDD, representante
PJ e verificacao de poderes; identidade unica/tenant isolado; credenciais,
documentos e autorizacoes devem permanecer protegidos.
Esta fase nao autoriza novo status de conta, contratacao PJ funcional,
emissao de Pix, concessao de papel ou alteracao das politicas financeiras.

Ponto de partida: commit da `main`
`894e74d8fd6a3b2a3c17c25c4a31d9f83cd3ae96`, aplicacao FastAPI
expondo apenas `/health`, modelos SQLAlchemy e migrations C15/C16
ja aplicadas na base autoritativa. O modulo de CPF/CNPJ C16-R12.41
possui 176/176 testes no CI e continua reutilizado, sem duplicacao.

## Implementacao restrita

Arquivo novo `backend/app/identity_draft.py`:

- `normalize_email`: validacao sintatica ASCII deliberadamente conservadora,
  caixa de correio nao verificada; respeita limites de 64 (local) e 254
  caracteres do endereco, rejeita pontos/labels incorretos, normaliza caixa;
  enderecos internacionais Unicode nao sao cobertos nesta etapa.
- `normalize_phone`: entrada nacional com DDD e 8 digitos de fixo ou
  9 digitos de celular; permite formato compacto ou mascara usual, compara
  DDDs oficiais da Anatel e rejeita prefixos invalidos. Nao implementa
  formato `+55`, verificacao de posse nem consulta a operadora.
- Preparacao de `PersonDraft` com nome Unicode NFC, nao-vazio e limite
  200 caracteres, proibicao de controles invisiveis; sem impor requisito
  artificial de pelo menos duas palavras (nome legal de um termo pode existir).
  Nome declarado nao equivale a identidade real verificada.
- `prepare_pf_contractor_draft` faz CPF pertencer a identidade pessoal,
  sem criar `ContractingParty.tax_id` para PF.
- `prepare_pj_contractor_draft` verifica CNPJ numerico/alfanumerico e
  exige dados pessoais de representante para rascunho; NAO habilita PJ,
  nao confirma poderes, nao define status APTO nem registra documentos.
- `PersonDraft`/`ContractingPartyDraft`: objetos imutaveis e sem campos
  de autenticacao, ativacao, permissao, tenant, aceite ou licenca.
  `repr` nao expoe PII; erros possuem codigos estaveis sem refletir entrada.

Fonte externa consultada em 22/10/2026 para DDD e prefixo telefonico:
https://www.gov.br/anatel/pt-br/regulado/numeracao/plano-de-numeracao-brasileiro
https://www.gov.br/anatel/pt-br/regulado/numeracao/perguntas-frequentes
https://www.gov.br/anatel/pt-br/assuntos/noticias/anatel-implementa-novas-areas-locais-da-telefonia-fixa-na-bahia-e-sergipe-a-partir-de-domingo-dia-11-01

Teste novo `backend/tests/test_identity_draft.py`: cenarios positivos,
negativos e limites de nome, e-mail, telefone, DDD, CPF, CNPJ, PJ com
representante, erros sem PII e objetos imutaveis. Dados sinteticos;
sem dados reais de membros ou contratantes.

## Gate e riscos residuais

PR #31: https://github.com/fronassor-art/FRcaixinha-2.2/pull/31
Exigir CI no HEAD FINAL: `python -m pip check` e
`python -B -m unittest discover -s tests -p 'test_*.py' -v`.
Nao declarar PASS antes de verificar logs/resultados e SHA final.

Validar sintaxe de e-mail/telefone/CPF/CNPJ NAO autentica pessoa,
NAO confirma posse do contato, NAO comprova poderes da PJ,
NAO bloqueia duplicidades no banco nem e seguro armazenar CPF em claro.
Nenhum endpoint, persistencia, cifra/HMAC, segredo ou papel foi criado.
A implementacao posterior da API exigira verificacao de origem e escopo,
armazenamento protegido, auditabilidade, controles de duplicidade,
aceite, rate limit, transacoes e revisao de autorizacoes.

Neste checkpoint: nenhum SQL, migration, banco temporario, ferramenta ou
dependencia nova. Recuperacao/backup PostgreSQL C16-R12.37 NAO repetidos;
backup Git C16-R12.43 a C16-R12.45 ja verificado permanece preservado.
Fase 2 EM ANDAMENTO, funcionalidades de cadastro/autenticacao/integracao
AINDA INCOMPLETAS; Fase 3 NAO INICIADA.

Proxima acao apos PASS: integrar PR, atualizar Termux por fast-forward
protegido, validar estado e planejar camada de protecao de CPF/CNPJ
e confirmacao de identidade sem comprometer o banco autoritativo.
