# C16-R12.124 — G3-C.4 / IN-03 e IN-04: matriz de segurança OFFLINE

**Data:** 23/10/2026 (America/Belem). **Questão de rastreio:** #46. **Base da proposta:** `main@b1ff819eed23788b3e56df1da284bd458d3f55a3` (PR #49, IN-01/02 offline, integrada após aprovação expressa). **Estado:** PROPOSTO PARA AUDITORIA INDEPENDENTE; nenhuma autorização de merge/SQL/DDL/migration ou autenticação operacional nesta entrega.

## 1. Escopo, fronteira e evidência

- IN-03: confirmação de e-mail, finalidade `INITIAL_EMAIL`, contato atual, desafio de 10 minutos, revogação e consumo **exatamente uma vez**. `backend/app/email_confirmation_offline.py` define `EmailChallengeRecord` (com `email`, mas sem campo `purpose`) e `ChallengeConsumption.consume_once`, porta abstrata. `verify_and_consume_email_challenge` compara a entrada de e-mail ao registro injetado, mas **não carrega o e-mail atual da tabela de identidade** e não comprova que o registro veio de storage confiável. A minuta F2P4 contém `purpose`, porém não contém snapshot persistido do contato.
- IN-04: `backend/app/opaque_sessions_offline.py` prepara token opaco de 32 bytes somente a partir de fatos de identidade `ATIVA`, contato confirmado e senha verificada fornecidos pelo chamador. `resolve_opaque_session` consulta `SessionStore.find_by_verifier` por uso e valida revogação, TTL de 15 minutos e hash; **não recebe os estados atuais de `user_identities` ou `identity_credentials`**, logo não comprova suspensão nem revogação após troca de senha. `SessionStore` segue protocolo abstrato.
- O banco autoritativo `frcaixinha_2_2_dev` no Termux continua no Alembic `c16r5_20261020`, conforme último checkpoint confirmado. Quatro tabelas `f2p4_20261022` **não aplicadas e não autorizadas**. Esta proposta não acessa nem modifica PostgreSQL. O restore funcional G3-C.3 foi aprovado no C16-R12.122R1, mas isso não valida IN-03/04 transacionais.
- IN-01/02 offline foram integrados no squash merge da PR #49 `b1ff819eed23788b3e56df1da284bd458d3f55a3`, com 308/308 testes do HEAD anterior e auditoria independente. IN-01/02 transacionais continuam BLOCKED.

## 2. IN-03: critérios por nível de prova

| ID | Evidência e resultado esperado | Natureza |
| --- | --- | --- |
| IN03-O1 | Desafio com identidade, contato e token corretos passa uma vez e recusa repetição com *stub que implementa consumo único sequencial*; somente verificador SHA-256 em registro | OFFLINE |
| IN03-O2 | Entrada de e-mail atualizada (diferente do snapshot antigo) ou desafio expirado não alcança consumo; validade é menor que 10 min | OFFLINE |
| IN03-L1 | Se a identidade tiver novo e-mail mas o chamador passar o e-mail antigo, função offline ainda aceita o desafio: demonstra ausência de comparação com contato **atual de fonte confiável** | CONTRAEXEMPLO, segurança real NÃO PROVADA |
| IN03-L2 | Um `consume_once` inseguro que sempre retorna `True` possibilita dois sucessos para o mesmo desafio: a função não arbitra concorrência nem atomicidade | CONTRAEXEMPLO, segurança real NÃO PROVADA |
| IN03-L3 | `EmailChallengeRecord` não representa `purpose`; não se pode afirmar prova de finalidade apenas por um campo de migration ainda não aplicada | CONTRAEXEMPLO, modelo incompleto |
| IN03-T1 | Confirmação sob uma única transação valida identidade, contato atual, finalidade e TTL pelo relógio confiável do banco; consumo condicional único + atualização de `email_verified_at` e estado aprovado são atômicos | PostgreSQL / BLOQUEADO |
| IN03-T2 | Duas confirmações simultâneas do mesmo token: uma só efetiva; outra retorna erro genérico. Mudança de contato, suspensão, revogação, erro de transporte e rollback jamais ativam identidade indevida | PostgreSQL / BLOQUEADO |
| IN03-T3 | PJ não vira `APTO` apenas por confirmar e-mail do representante; comprovação de representação permanece separada | PostgreSQL / BLOQUEADO |

**Projeto futuro a revisar, não implementado:** carregar registros e contato atual **do servidor** dentro do limite transacional, associar finalidade explícita, expiração e verificador sem registrar tokens em logs, empregar condição `consumed_at IS NULL` / `revoked_at IS NULL` e validar linhas efetivamente alteradas antes de atualizar identidade na mesma transação. Avaliar contato pseudonimizado/snapshot cifrado, finalidade e política de retenção à luz da LGPD, sem fixar prazo arbitrário. A senha/token não deve transitar em logs, Git ou ChatGPT.

## 3. IN-04: critérios por nível de prova

| ID | Evidência e resultado esperado | Natureza |
| --- | --- | --- |
| IN04-O1 | Reconsulta a porta a cada uso e rejeição imediata de `revoked_at` presente no instante observado | OFFLINE |
| IN04-O2 | Token divergente e instante igual a `expires_at` recusados; validade não ultrapassa 15 minutos | OFFLINE |
| IN04-L1 | Com registro de sessão ainda válido, alterar estado sintético `ATIVA` → `SUSPENSA` fora do registro não impede `resolve_opaque_session`: estado atual da identidade não é parte do contrato de leitura | CONTRAEXEMPLO, segurança real NÃO PROVADA |
| IN04-L2 | Com registro intacto, trocar revisão sintética da credencial não invalida token antigo: não há prova de invalidação após atualização/revogação da senha | CONTRAEXEMPLO, segurança real NÃO PROVADA |
| IN04-T1 | Por requisição, confirmar sessão + status atual de identidade + estado/versão de credencial confiáveis; suspensão/revogação/mudança de senha resultam em negação imediata e auditável | PostgreSQL / BLOQUEADO |
| IN04-T2 | Concorrência entre autenticação e suspensão/troca de senha sem janela indevida de autorização; teste de rollback e race em isolamento aprovado | PostgreSQL / BLOQUEADO |
| IN04-T3 | Nenhuma sessão concede `RoleGrant`, tenant, ciclo, Pix ou autorização financeira implicitamente. Contexto de recurso continua exigido e segregado | PostgreSQL + API / BLOQUEADO |

**Projeto futuro a revisar, não implementado:** revalidar fatos de identidade/credencial em fonte servidor no limite de cada operação, preferindo versão/revogação monotônica com transação adequada; definir como propagar mudanças de senha e suspensão para todas as sessões, com critérios de invalidação imediata, não confiar em claims do Flutter ou somente em cache. Não abrir login, endpoint de e-mail ou envio real.

## 4. Testes sintéticos no pacote

**Arquivo novo:** `backend/tests/test_g3c4_in03_in04_offline.py` — 10 casos `unittest`:

- IN-03: proteção sequencial do stub, e-mail divergente/TTL, e três **contraexemplos** explícitos (e-mail antigo passado pelo chamador, consumidor `True` não atômico e ausência de `purpose` no contrato).
- IN-04: reconsulta/revogação, dois **contraexemplos** (suspensão e troca de senha ausentes do registro), token adulterado/TTL.
- Verificação de que os caminhos testados não chamam diretamente arquivo, rede nem `psycopg.connect`.

**ATENÇÃO:** testes de contraexemplo devem passar enquanto demonstram o **limite da segurança atual**, não representam PASS de IN-03/04 transacionais. Em implementação futura, substituir os contraexemplos pelos testes de garantia positiva apropriados; não mascarar falhas para obter verde.

**Comandos padronizados com `unittest` (diretório `backend/`, ambiente Python existente compatível):**

```bash
python -B -m unittest discover -s tests -p 'test_g3c4_in03_in04_offline.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

O workflow `.github/workflows/backend-ci.yml` usa a segunda linha; CI deve comprovar SHA do HEAD, número de testes, `pip check` e código de saída. Não instalar `pytest` ou dependências no Termux para rodar essa proposta. Aguardar CI real; criar PR não prova testes executados.

## 5. Portões e consolidação de backup

- **G3-C.4 IN-03/04 offline:** pode ser submetido para auditoria por PR **DRAFT** separada. Merge só após CI PASS, revisão independente PASS e aprovação expressa do proprietário.
- **IN-03/04 PostgreSQL:** BLOCKED; sem contrato de escrita, mudança de migration, transação, autenticação pública ou envio de e-mail. G3-C.5 (f2p4) permanece NÃO AUTORIZADO.
- **Sequência de oito invariantes:** IN-01, IN-02, IN-03, IN-04, IN-05, IN-06, IN-07 e IN-08. **IN-08 encerra a lista de invariantes**, não todos os testes/portões do aplicativo; os testes SQL/concorrência/integração exigem fases posteriores.
- **Decisão do proprietário:** adiar **novo backup geral consolidado** até concluir o pacote offline IN-01…IN-08 e as verificações correspondentes. Continuam válidos os backups Git AGE e PG AGE anteriores, versionamento Git por checkpoint e rechecagens de integridade. Este adiamento não dispensa backup preventivo **antes de migrations, alterações estruturais ou ações arriscadas**, caso sejam posteriormente autorizadas. Não criar duplicações ou arquivos de backup desnecessários neste pacote.
- Não confundir CI do GitHub com teste no Termux, nem merge remoto com sincronização local. Um diretório raiz `~/FRcaixinha_2.2`, um PostgreSQL autoritativo e auditoria contínua.

**Status desta entrega:** documentação e testes **propostos**; sem operação SQL, sem migration, sem aplicação real de quatro tabelas, sem dados financeiros e sem backup geral novo.
