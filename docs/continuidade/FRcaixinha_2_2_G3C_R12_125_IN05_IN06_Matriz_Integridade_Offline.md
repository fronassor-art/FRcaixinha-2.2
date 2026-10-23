# C16-R12.125 — G3-C.4 / IN-05 e IN-06: provas e lacunas OFFLINE

**Data:** 23/10/2026, America/Belem. **Issue:** #46. **Base:** `main@b1ff819eed23788b3e56df1da284bd458d3f55a3` (PR #49 integrada). **Estado:** minuta de teste/documentação para revisão independente. Não há autorização de merge, consulta SQL, migration, novo banco ou implantação.

## 1. Limite do escopo

IN-05 verifica a diferença entre metadados do ORM e imposição real pelo PostgreSQL de identificadores e `updated_at`. IN-06 examina as restrições globais de CPF HMAC, `lower(email)` e CNPJ HMAC quando um cadastro já está `PENDENTE` ou `PRELIMINAR`. As regras aprovadas não permitem criar outra identidade, assumir conta existente nem liberar CNPJ por expiração presumida. Esta entrega **não implementa** política de recuperação ou alteração estrutural.

O código auditado foi `backend/app/db/models.py`, `backend/app/identity_registration_offline.py` e a migration histórica congelada `c15r2_20261020_initial_schema.py`; `f2p4_20261022_auth_bootstrap_draft.py` segue apenas minuta. Os objetos `Base.metadata` e a compilação `CreateTable`/`CreateIndex` não provam o estado atual de triggers, dados e concorrência da instância real. O checkpoint PostgreSQL G3-C.3 é prova de recuperação em outro escopo.

## 2. IN-05 — timestamp e identificadores

| Caso | Prova offline | Limite |
| --- | --- | --- |
| IN05-O1 | `UserIdentity`, `ContractingParty` e `IdentityCredential` definem `updated_at` com `server_default` e `onupdate` do SQLAlchemy, mas sem `server_onupdate` declarado | Isso não é trigger PostgreSQL; não prova atualização automática por escritas externas |
| IN05-O2 | Os três modelos usam geração Python de `id` e não declaram `server_default` de UUID | Inserção SQL direta sem UUID não recebe automaticamente o mesmo default Python |
| IN05-O3 | Fragmentos `CreateTable` compilados offline não incluem trigger de atualização | Só descreve o DDL compilado, não comprova ausência de trigger aplicado fora da migration |
| IN05-T1 | PostgreSQL rejeita escrita sem ID quando for a política aprovada e mantém `updated_at` confiável em INSERT/UPDATE/ROLLBACK conforme caminho de escrita único ou mecanismo de banco escolhido | **BLOCKED**: nenhuma operação SQL autorizada |
| IN05-T2 | Em atualização concorrente, `updated_at` não pode mascarar mudança de estado, regressão temporal ou autoria; log minimizado e imutabilidade exigem desenho específico | **BLOCKED** |

**Decisão técnica pendente:** escolher o caminho único de escrita com enforcement verificável ou trigger/controle equivalente, com testes de SQL direto e concorrência em ensaio seguro separado. Não modificar o histórico congelado; eventual DDL deve constar de migration nova revisada e autorizada.

## 3. IN-06 — reservas indevidas de identidade

| Caso | Prova offline | Limite |
| --- | --- | --- |
| IN06-O1 | CPF HMAC é `UNIQUE` em `user_identities`, inclusive para o status `PENDENTE`; e-mail é único globalmente via índice `lower(email)` sem predicado parcial | Ausência de filtro por estado não resolve legitimidade do primeiro cadastro |
| IN06-O2 | CNPJ HMAC é `UNIQUE` em `contracting_parties`, inclusive quando a PJ está `PRELIMINAR` | Não autoriza liberação de reserva, tomada de CNPJ ou mudança automática de representante |
| IN06-O3 | Dois rascunhos PF com mesmo CPF geram HMAC de busca igual e ciphertext diferente por vínculo ao UUID; o estado continua pendente | Não é ensaio de duas transações reais |
| IN06-O4 | Um `ConflictProbe` sintético que acusa CPF existente faz o preparador rejeitar outro candidato com erro genérico | Não prova que o titular novo pode recuperar uma pré-reserva ilegítima |
| IN06-O5 | Um `ConflictProbe` que acusa CNPJ existente rejeita nova PJ, inclusive sem prova de representação concluída | Não distingue reserva legítima de abuso/abandono |
| IN06-T1 | Tentar apropriar-se de CPF/e-mail/CNPJ de terceiro sempre falha fechado, sem vazamento sobre existência, mesmo sob concorrência | **BLOCKED** |
| IN06-T2 | Fluxos PF/PJ de contestação, recuperação e expiração exigem verificação de titularidade e, para PJ, poderes de representação, rate limit, trilha mínima e política jurídica aprovada | **BLOCKED** |
| IN06-T3 | Cadastro preliminar abandonado não pode bloquear indefinidamente titular comprovado, mas exclusão/reuso deve preservar obrigações legais, auditoria e bloqueio antifraude | **BLOCKED** |

**Lacuna aberta intencional:** não existe no escopo atual um serviço confiável de prova de titularidade, contestação ou recuperação. `UNIQUE` previne duplicidade, mas pode ser explorada para reservar CPF/e-mail/CNPJ; remover ou relaxar UNIQUE seria uma correção **insegura**, proibida sem desenho aprovado.

## 4. Execução e interpretação

Arquivo novo: `backend/tests/test_g3c4_in05_in06_offline.py`, contendo **10 testes** usando documentos sintéticos, `DocumentCrypto` de teste e metadados SQLAlchemy em memória. Alguns casos verdes documentam **lacunas** de proteção futura; não significam conformidade transacional. Nenhum acesso, edição ou backup PostgreSQL faz parte desses testes.

A partir do diretório `backend/`, com o Python compatível já disponível:

```bash
python -B -m unittest discover -s tests -p 'test_g3c4_in05_in06_offline.py' -v
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

O segundo comando segue `.github/workflows/backend-ci.yml`. A CI precisa comprovar HEAD exato, `pip check`, casos individuais, total e sucesso. Não instalar `pytest` ou dependências adicionais. Não atribuir testes executados localmente ao Termux sem log correspondente.

## 5. Gates, sequenciamento e backups

- **PR #50 (IN-03/04):** DRAFT, `main` ainda não contém seus arquivos. CI 318/318 PASS em `3da90f2d3da0ad0b5bd355d6212e1efdda4d33b3`, mas aguarda auditoria independente e autorização de integração.
- **Este pacote (IN-05/06):** PR separada e DRAFT baseada em `main@b1ff819...`, deliberadamente sem depender dos arquivos da PR #50. CI e parecer independente obrigatórios antes de considerar PASS final. Somente documentação e testes offline; não alterar aplicações ou migrations.
- **IN-01/02:** pacote offline integrado na PR #49; provas PostgreSQL transacionais continuam `BLOCKED`.
- **IN-07/08:** últimos dois itens da matriz G3-C.4, ainda pendentes. Sua conclusão **offline** não conclui G3-D/E nem autoriza `f2p4`.
- **Backup geral:** adiado por decisão do proprietário até terminar o ciclo de testes offline IN-01…IN-08. Preservar backups Git/PG AGE existentes; continuar Git e registros CI como checkpoints, sem confundir commit local com backup recuperável. Antes de qualquer migration/alteração estrutural/ação de risco, backup preventivo recuperável permanece obrigatório.
- **Governança:** uma raiz Termux `~/FRcaixinha_2.2`, um PostgreSQL autoritativo `frcaixinha_2_2_dev`, sem banco paralelo persistente, nenhuma instalação duplicada, sem SQL real nem desvio de regras para obter testes verdes. Nenhum merge sem autorização expressa do proprietário.

**Situação de aceite desta PR:** testes e matriz **propostos para revisão**; IN-05/06 transacionais, `G3-C.5` e implantação seguem **BLOCKED**.
