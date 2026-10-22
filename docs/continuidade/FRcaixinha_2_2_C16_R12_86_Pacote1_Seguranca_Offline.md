# C16-R12.86 — Pacote 1 da Fase 2: fundação offline de segurança

Referências: Issue #35; Contrato Técnico Mestre aprovado, cláusulas 2.3,
2.8–2.9, 3.1-A.1–A.2, 6.1-A, 12.3 e 13.1–13.2; Caderno Mestre F2-07,
F2-10 e F2-13. Baseline de entrada: `1a4e9d6cf6cd8d91f5a9e2f67663ebfd4217ab2d`.

## Escopo implementado

- `resource_authorization.py`: avaliador puro de uma ação, um papel selecionado
  e um recurso cujo tenant/ciclo/proprietário devem vir de fonte confiável.
  Identidade ativa, grant vigente não revogado, licença ativa e vínculos são
  exigidos. Master só recebe leituras de plataforma delimitadas. Ações
  financeiras e Pix são sempre negadas neste pacote. Estados ativos dos testes
  são fatos sintéticos futuros: os modelos atuais continuam inativos.
- `document_key_rotation.py`: acrescenta uma chave de **cifragem** e conserva
  todas as chaves antigas para decifrar envelopes históricos. Exige o mesmo
  `lookup_key` em todos os IDs, preservando os HMACs persistidos e a unicidade.
  Chaves entram apenas por injeção; este módulo não cria nem carrega segredos.
- `offline_credentials.py`: hash scrypt versionado (`N=16384, r=8, p=1`,
  salt aleatório de 16 bytes e saída de 32 bytes), limite de senha em bytes,
  comparação constante e trabalho de KDF também para usuário desconhecido.
  Verificação de sessão de até 15 minutos, sujeita a revogação e ao mesmo
  sujeito, sem emissão de token, login ou armazenamento.

## Decisões e gates operacionais

**Custódia de chaves.** Separar material de cifra e de busca; fornecer por
interface controlada com privilégio mínimo. Manter IDs de cifra antigos enquanto
existirem envelopes correspondentes; remover apenas após inventário,
recifragem verificada e backup recuperável. Não registrar segredo em Git, log,
exceção, backup desprotegido ou configuração de cliente. A escolha de KMS,
controle de acesso, carregamento, auditoria e recuperação exige decisão própria.

**Rotação do HMAC de busca: BLOQUEADA neste pacote.** Trocar `lookup_key`
diretamente quebraria consultas e unicidade entre HMACs antigos e novos. Uma
transição futura precisa: (1) inventário e leitura dos documentos históricos
com chaves autorizadas; (2) suspensão coordenada de escritas; (3) cálculo sob
novo domínio/chave e verificação global de duplicidades em CPF e CNPJ,
separadamente; (4) plano transacional de coluna/índice ou equivalente para
reindexação atômica, com rollback e backup PostgreSQL atual; (5) prova de
consistência antes de permitir novas escritas; (6) retirada gradual da chave
antiga apenas após recuperação ensaiada. Nenhuma migration ou SQL foi
autorizada pelo Issue #35.

**Autorização.** `TrustedFacts` é uma interface de dados, não prova de origem.
Uma API futura deve autenticar o `auth_subject`, carregar actor/grant/resource,
membership, licença e tenant/ciclo diretamente de armazenamento confiável,
aplicar a decisão em cada objeto e auditar negados sem PII. Não confiar em
headers de papel, IDs ou status enviados pelo cliente. A escolha do contexto
é explícita por `grant_id`; o Master não herda permissões do tenant. Atos
financeiros exigem gates e implementação posteriores.

**Credenciais e sessões.** O hash offline não cria autenticação operacional.
Ainda requer decisão sobre credenciais internas versus provedor, armazenamento
do digest, confirmação de e-mail e telefone quando aplicável, recuperação,
revogação persistida, rate limiting, proteção contra automação, TLS,
identificação de dispositivo, auditoria minimizada e política de rehash quando
uma versão nova for aprovada. `auth_subject` não é papel nem membership. O
verificador de sessão aceita fatos apenas de um futuro armazenamento confiável;
não é um formato de token nem substitui checagem de revogação em cada acesso.

## Limites de evidência

Os testes deste pacote usam fatos e chaves sintéticos; não demonstram
autenticação, controle por endpoint, enforcement PostgreSQL, integração
financeira nem operação em produção. Os resultados efetivos de CI e o SHA do
commit pertencem ao relatório do PR. Nenhuma mudança em models, migrations,
requirements, `env.py`, `main.py`, banco ou regras financeiras integra o pacote.
