# FRcaixinha 2.2 — C16-R5A — Adendo de autorização para testes históricos

**Data:** 20/10/2026. **Natureza:** autorização de escopo **estritamente adicional**, concedida pelo proprietário com “Prossiga” após a apresentação do bloqueio e solicitação explícita para incluir três testes existentes.

**Estado:** autorização documental registrada; implementação e testes **ainda não executados nesta etapa**. Este adendo integra, sem substituir, a autorização C16-R5 e a especificação C16-R4. A fonte normativa permanece o Contrato Técnico Mestre aprovado de 16/10/2026.

## 1. Diagnóstico de bloqueio confirmado

O Codex parou antes da primeira edição: a branch `feat/f2-c16-license-subscription-inactive` estava limpa e no commit `365ed0475ca0306327564c559682c546c01005e0`. A suite histórica fixa a metadata a **15 tabelas** e a C15 como **única** revisão Alembic, embora a C16-R5 aprovada acrescente duas entidades e uma revisão derivada.

Auditoria complementar do GitHub confirmou **três** testes históricos afetados por expansão da metadata:

1. `backend/tests/test_db_initial_migration_schema.py`: pressupõe `len(Base.metadata.tables)==15`, compara todo o DDL da revisão congelada C15 com todos os modelos ORM atuais e exige `scripts.get_heads()==[c15r2_20261020]`.
2. `backend/tests/test_db_identity_schema.py`: fixa o conjunto integral `Base.metadata.tables` nas 15 tabelas C15.
3. `backend/tests/test_db_tenant_rolegrant_schema.py`: fixa o mesmo conjunto integral de 15 tabelas.

## 2. Autorização adicional e limite exato

**AUTORIZADO:** modificar **exclusivamente esses três arquivos de testes adicionais** para compatibilizar suas expectativas com os **17 modelos/tabelas totais previstos** e a nova revisão Alembic, **sem retirar, desativar nem enfraquecer a proteção histórica**.

- A C15 `c15r2_20261020_initial_schema.py` permanece **intocada e congelada**, contendo **15 tabelas e 18 índices declarados**, com sequência, constraints e DDL originais preservados. A adaptação de `test_db_initial_migration_schema.py` deve comprovar sua integridade contra referência histórica independente — por exemplo, fingerprint conhecido do blob Git inicial e validações abrangentes de DDL — e **não** equivaler a comparar a revisão consigo mesma; preservar testes de dependências, indexes, SQL PostgreSQL, upgrade/downgrade interceptados e ausência de CASCADE.
- `ScriptDirectory.get_base()` deve continuar apontando para `c15r2_20261020` e `get_heads()` apontar à nova revisão C16; sem criar outro ramo de migrations.
- Os testes de identidade e Tenant/RoleGrant devem continuar afirmando o **conjunto exato** de tabelas ORM atualizado (15+2 = 17), além das regras de segurança anteriores; não substituir conjuntos exatos por `assertIn` genéricos.
- A comparação do DDL atual dos modelos não pode ser confundida com o snapshot congelado da migration C15 se forem acrescentadas constraints/índices a modelos antigos por nova revisão.
- A inclusão de constraints compostas suplementares poderá impactar testes estritos de `LicenseOffer`, `Payment` ou outras entidades existentes. **Tais testes não estão autorizados a ser editados por este adendo**. Em caso de necessidade comprovada de ampliar a lista de arquivos, Codex deve parar, apresentar os testes, linhas e a correção mínima, e pedir novo aceite.

**Nenhum outro arquivo é automaticamente autorizado** além dos já enumerados na C16-R5 e desses três. Não criar outro banco, clone, ambiente ou instalação. Não alterar contrato, dependências, CI, frontend ou a C15.

## 3. Retomada segura pelo Codex

1. No diretório local único `~/FRcaixinha_2.2`, confirmar identidade Git e árvore limpa, buscar a branch oficial, executar atualização `--ff-only` sem reset/force. **A branch remota terá um commit documental adicional para este adendo; sincronize-o antes de editar.**
2. Ler contrato, Documento Mestre v1.1, C16-R3, C16-R4, C16-R5 e este C16-R5A.
3. Aplicar as alterações de código/migration e os testes **dentro das listas já autorizadas**, com escopo mínimo e sem ativações financeiras.
4. No Python 3.13.5 do Debian PRoot independente, fazer `python -B -m pip check`, testes novos e regressão total; validar Alembic heads **sem abrir ambiente de migrations** e DDL compilado/offline no mecanismo de mocks, sem conectar ao banco.
5. Se surgir outro bloqueio, **PARAR imediatamente**, demonstrar causa e propor mínima ampliação específica. Não deletar testes, mascarar erros nem instalar dependências por tentativa.
6. Entregar SHA, diff, novos testes, regressão, dados de ambiente, migrações e quaisquer status BLOCKED/FAIL/NOT_RUN. Não abrir PR ou fazer merge além dos limites vigentes sem aceite do responsável.

## 4. Invariantes não revogados

- PostgreSQL Termux 18.2 `frcaixinha_2_2_dev`, `frc22_owner`, `127.0.0.1:5432`: **ZERO ESCRITAS**; `alembic upgrade/downgrade/stamp/current` e SQL DDL **não autorizados**.
- A migration C15 não foi aplicada, e uma C16 criada em código também **não** fica autorizada para aplicação por este adendo.
- Primeira versão de `LicenseSubscription` e `LicenseEntitlementSegment`: estrutura apenas INATIVA, sem Pix, cobrança, confirmação financeira ou concessão de vigência.
- Backup Git C16-R2 AGE SHA-256 `4f3818f1a5065ecfdab2b2034e788ff722831c1b848b5b6b235b7c5ec52ddbd1`, cópia externa validada. Dump PostgreSQL de recuperação SQL ainda **não ensaiado**.
- `main` oficial de referência: `01b33a2dce5e57ed2108e58c1ea2975f8220a23d`. Branch de trabalho não implica merge.

**Situação do checkpoint:** C16-R5A AUTORIZAÇÃO COMPLEMENTAR APROVADA; C16-R5 IMPLEMENTAÇÃO PENDENTE. Nenhum teste ou alteração PostgreSQL efetuados pelo registro desta autorização.
