# FRcaixinha 2.2 — C16-R4 — Especificação proposta de `LicenseSubscription`

**Data:** 20/10/2026  
**Estado:** **PROPOSTA TÉCNICA — AGUARDA APROVAÇÃO EXPRESSA**  
**Finalidade:** resolver a lacuna documental e estrutural da entidade `LicenseSubscription` antes de autorizar implementação ou qualquer migration no PostgreSQL.  
**Natureza:** análise, desenho de dados e critérios de teste. **Não contém autorização de programação, SQL, Pix ou ativação comercial.**

## 1. Baseline verificado e hierarquia

- **Repositório único:** `fronassor-art/FRcaixinha-2.2`, diretório local autorizado `~/FRcaixinha_2.2`.
- **`main` oficial conferida:** `01b33a2dce5e57ed2108e58c1ea2975f8220a23d` (PR #18, documentação).
- **Contrato normativo:** `docs/requisitos/FRcaixinha_2_2_Contrato_Tecnico_Mestre_FINAL_APROVADO_2026-10-16.md`, principalmente §§ 3.1, 3.1-A.2, 3.2-A, 3.5–3.11, 9.9, 12.1–12.4, 13.4 e 15.2. O contrato prevalece sobre esta proposta.
- **Auditoria anterior:** `FRcaixinha_2_2_C16_R3_Auditoria_PreMigration_2026-10-20.md` (salva na Biblioteca; **ainda não integrada ao GitHub**).
- **Esquema no Git:** `backend/app/db/models.py` e migration `backend/migrations/versions/c15r2_20261020_initial_schema.py` (**15 tabelas e 18 índices; nenhum `LicenseSubscription`**). A revisão C15 permanece congelada; `down_revision=None`.
- **Banco real:** PostgreSQL Termux 18.2, `frcaixinha_2_2_dev`, `frc22_owner`, `127.0.0.1:5432`; a consulta C16-R1, em transação somente leitura, retornou **zero objetos de aplicação no conjunto pesquisado**, `alembic_version` ausente. Nenhuma migration foi aplicada.
- **Último backup Git:** C16-R2 AGE, SHA-256 `4f3818f1a5065ecfdab2b2034e788ff722831c1b848b5b6b235b7c5ec52ddbd1`, restauração Git independente e cópia no Drive verificadas. Backup PostgreSQL separado com integridade conhecida, mas **restauração SQL NOT_RUN**.
- **Testes de referência:** 89/89 PASS de C15; não foram reexecutados neste C16-R4. **Nenhum teste de DDL real foi feito.**

## 2. Exigências do contrato versus implementação atual

| Fonte | Regra obrigatória, sem mudança | Situação hoje |
|---|---|---|
| § 12.2 (`LicenseSubscription`) | `id`, `tenant_id`, `contracting_party_id`, `plan_id`, `period`, `starts_at`, `ends_at`, `status`, `paid_payment_id` | Modelo e tabela ausentes |
| §§ 3.1, 3.1-A.2 | Identidade, contratante, tenant preliminar, papel e licença são entidades separadas; cadastro/aceite não ativam licença | Estruturas preliminares existentes, sem licença ativável |
| §§ 3.2-A, 3.5, 3.6, 12.2-B(i) | Oferta imutável, preço/versionamento/aceite/pagamento da **mesma operação**, sem ativar com webhook isolado | Cadeia existente `LicenseOffer → TermAcceptance → LicensePaymentObligation → Payment`, todos com bloqueios adequados ao estágio inativo |
| §§ 3.7–3.9 | Vigência `[active_from, active_until)`, fuso `America/Belem`, dia âncora; suspensão imediata sem perder direitos existentes | Sem assinatura/segmentos e sem serviço de vigência |
| § 3.10 e § 12.2-B(vi) | Upgrade proporcional **por segmento não transcorrido**, renovação antecipada separada, downgrade só quando válido, histórico e ampliação gratuita auditados | Exige desenho do histórico de segmentos e operações comerciais |
| § 12.2-B(viii), § 12.4 | Mesma identidade/titularidade e vínculos; proibir relacionamento cruzado entre caixinhas | FKs compostas presentes em partes da cadeia, mas falta o vínculo da licença |
| § 13.4 | Recuperação do banco demonstrável antes da produção; proteção do backup e reconciliação financeira após recuperação | Dump criptografado existe, mas restauração funcional não testada |

**Interpretação:** a ausência da entidade é **lacuna conhecida e bloqueante para declarar licenciamento/Fase 2 completos ou habilitar cobranças**. Não obriga reescrever a revisão C15 nem autoriza aplicá-la agora.

## 3. Opção de modelagem recomendada — pendente de aprovação

### 3.1. Identidade de cada ato comercial

**PROPOSTA:** uma linha de `LicenseSubscription` representa **um ato comercial rastreável por oferta/aceite** (contratação inicial, renovação ou upgrade), e **não** uma licença ativa eterna sobrescrita a cada novo pagamento. Várias linhas históricas podem pertencer ao mesmo tenant, mas a autorização de uso em um instante é calculada pelos **direitos/segmentos efetivamente pagos ou legitimamente concedidos**, nunca pelo último registro alterado por conveniência.

Justificativa técnica: a regra exige que cada assinatura aponte à **mesma oferta imutável** e à **mesma versão de preço aceita** (§ 12.2-B), mesmo após várias renovações e upgrades. Assim os vínculos históricos não são perdidos. **É uma decisão de desenho proposta, não uma convenção já aprovada pelo usuário.**

### 3.2. Campos do cabeçalho `license_subscriptions`

| Campo lógico | Tipo/condição sugeridos | Função e controle |
|---|---|---|
| `id` | UUID, PK, obrigatório | Identificador imutável |
| `tenant_id` | UUID, FK, obrigatório | Caixinha titular do direito |
| `contracting_party_id` | UUID, FK composta com tenant, obrigatório | Contratante da mesma caixinha; não derivar do Master |
| `plan_id` | UUID, obrigatório | Plano efetivamente ofertado |
| `offer_id` | UUID, UNIQUE, obrigatório | Uma oferta imutável por ato comercial |
| `term_acceptance_id` | UUID, UNIQUE, obrigatório | Aceite da mesma oferta, tenant, versão e preço |
| `price_version_id` | UUID, obrigatório | Versão efetivamente aceita (não preço comercial corrente) |
| `period` | `MENSAL` / `ANUAL`, obrigatório | Deve coincidir com a oferta; duração de 1/12 meses respectivamente |
| `duration_months` | SMALLINT, obrigatório | Espelho verificável da periodicidade da oferta |
| `effective_price` | NUMERIC(18,2), obrigatório | Fotografia do valor aceito; operações de ajuste exigem histórico próprio, não cálculo retroativo no ato anterior |
| `action_kind` | Enum/código lógico versionado, a definir | Distinguir contratação, renovação, upgrade; **não inventar política comercial nova** |
| `starts_at`, `ends_at` | TIMESTAMPTZ, **nulos enquanto inativo** | Período legitimamente adquirido, definido somente pela futura confirmação/decisão autorizada; `ends_at > starts_at` se preenchidos |
| `anchor_day` | SMALLINT 1–31, **nulo enquanto inativo** | Dia âncora original preservado durante encadeamento de meses curtos |
| `paid_payment_id` | UUID, **nulo enquanto inativo** | Identifica prova de pagamento conciliado de licença, nunca mero pagamento iniciado; alternativa de concessão gratuita exige autorização formal distinta |
| `environment` | `DEMO` / `HOMOLOGACAO` / `PRODUCAO` ou vínculo de contexto, sujeito a aprovação | Proibir mistura de comprovantes fictícios e pagamentos reais |
| `status` | **somente `RASCUNHO_INATIVO` na primeira revisão** | Não permitir ativação, cobrança ou concessão de uso por esse snapshot |
| `created_at`, `updated_at` | TIMESTAMPTZ | Rastreabilidade técnica; não substituir trilha imutável por mero `updated_at` |

**Campos físicos e nullability da primeira revisão estão propostos, não aprovados.** Campos obrigatórios e sem prova financeira permitem cadastrar apenas o **rascunho inativo**; o banco não pode conceder vigência quando `paid_payment_id` é nulo. O código não deve conferir direitos de uso por simples existência da linha.

### 3.3. Histórico de direitos e segmentos

**PROPOSTA COMPLEMENTAR:** modelar, antes da futura ativação, um registro imutável ou *append-only* de segmentos, eventualmente denominado `LicenseEntitlementSegment` (nome físico sujeito à revisão). Campos semânticos mínimos propostos:

- `subscription_id`, `tenant_id`, `period_start`, `period_end`, `anchor_day`, `plan_id`, `price_version_id`, `offer_id`, `payment_id`/prova de concessão e `amount_allocated`/base contratual do preço;
- relação `origin_segment_id` / `supersedes_segment_id` ou histórico equivalente para upgrade, com trilha de autoria, data de cálculo, versão e valores dos segmentos anteriores;
- registro separado do valor incremental do upgrade, fotografia `calculated_at`, preço de origem e preço de destino e confirmação de pagamento **sem apagar o segmento anterior**;
- intervalo futuro pré-pago de renovação registrado como segmento próprio; concessão gratuita apenas com autorização, oferta, aceite e auditoria, **sem Pix fictício R$ 0**.

**Aprovação ainda necessária:** delimitar se a tabela de segmentos nasce já no primeiro incremento estrutural (inteiramente inativa) ou em migration posterior, sempre **antes** de implementar o serviço de ativação/renovação/upgrade. **Não implementar `status=ATIVA` e nem materializar vigência pagável sem histórico por segmento.**

## 4. Restrições propostas e dependências reais do schema C15

1. **Inatividade permanente da primeira revisão:** `CHECK status = 'RASCUNHO_INATIVO'`; `paid_payment_id IS NULL`; `starts_at IS NULL`; `ends_at IS NULL`; `anchor_day IS NULL` enquanto esta revisão estiver vigente. Esses limites só podem mudar em migration/serviço posterior expressamente autorizados e testados.
2. **Integridade de contexto:** FK composta `(tenant_id, contracting_party_id) → tenants(id, contracting_party_id)` já encontra chave única na C15. Um FK isolado para cada coluna **não basta**.
3. **Mesma oferta e preço:** recomendam-se FKs compostas com as colunas estáveis da oferta; isso exige **analisar a adição de uma chave UNIQUE compatível em `license_offers`** na futura revisão, pois a chave composta existente não tem exatamente todos os campos de contratante, plano e período. Não presumir que o índice atual aceita qualquer subconjunto como FK.
4. **Mesmo aceite:** a C15 já possui `term_acceptances(id, offer_id, tenant_id, price_version_id, effective_price)` sob UNIQUE, que pode ser alvo de FK composta para a assinatura proposta. Não confiar somente no `id` do aceite.
5. **Mesmo pagamento:** na C15 `payments` possui chave composta `(id, tenant_id, expected_amount, environment)`, mas **não** a chave completa com `offer_id` e `price_version_id`; para um vínculo garantido pelo banco será necessário avaliar nova chave única composta e FK compatível, ou um caminho de prova relacional equivalente sem perder o tenant/valor/oferta. Não basta FK simples de `paid_payment_id` para comprovar a titularidade.
6. **Idempotência:** `UNIQUE(offer_id)`, `UNIQUE(term_acceptance_id)` e unicidade parcial do `paid_payment_id` quando não nulo (sujeita à futura política de ajustes). Não definir `UNIQUE(tenant_id)`: renovação e histórico exigem múltiplos atos da mesma caixinha.
7. **Períodos:** `CHECK (ends_at IS NULL AND starts_at IS NULL) OR (ends_at > starts_at)` na etapa futura; nunca interpretar vazio como licença ativa. Validações de **sobreposição de direitos**, renovações e upgrades exigem concorrência transacional e semântica de segmentos; não impor exclusão simplista de intervalos que impediria upgrades legítimos.
8. **Imutabilidade/auditoria:** contratos, preço, oferta e segmentação não devem ser alterados silenciosamente. Atualização de estado operacional (quando futura e aprovada) precisa de evento auditável; proibir `ON DELETE CASCADE` em vínculos financeiros/contratuais.
9. **Sem credenciais:** referências a comprovantes/segredos são opacas; não gravar senha, token ou CPF/CNPJ em texto claro nessa tabela.

**Atenção:** adicionar a tabela proposta também cria índices e possivelmente novas chaves UNIQUE nas tabelas existentes; os **18 índices da C15 deixam de ser a contagem total futura**. A especificação não afirma contagem final de índices/constraints antes da geração/revisão do DDL.

## 5. Regras de negócio a preservar (desenho, não implementação agora)

- **Ativação:** somente confirmação íntegra e conciliada de Pix pertencente à plataforma, quantia exata, oferta/aceite/vendedor/ambiente corretos e registro idempotente. Webhook, print, clique e data de cadastro isoladamente **não ativam** licença.
- **Licença mensal/anual:** 1 ou 12 meses a partir da confirmação do pagamento inicial. Armazenar instantes com timezone, fazer cálculo de calendário com `America/Belem` e intervalo semiaberto; anual comercial = `10 × mensal` conforme versão, não preço editável independente.
- **Renovação antecipada:** acrescentar o novo segmento depois do término efetivo de direitos pagos, sem perda de dias e sem mudar a âncora; renovação vencida começa na confirmação, sem retroatividade.
- **Mês curto:** preservar `anchor_day` da origem — caso de dia 31 não deve virar perpetuamente dia 28/29.
- **Término:** negar imediatamente **novos** compromissos após `active_until`; direitos e obrigações existentes continuam acessíveis/quitáveis. Um job noturno NÃO é único mecanismo de suspensão; cada operação sensível verifica a vigência atual.
- **Upgrade:** diferença calculada separadamente por segmento elegível e tempo restante, `Decimal`/`ROUND_HALF_UP`, fotografia `calculated_at`; não somar tempo nem cobrar período adquirido pela segunda vez; oferta expirada exige recálculo e novo aceite.
- **Downgrade:** apenas na próxima renovação e se ambas as capacidades efetivamente usadas couberem na faixa, sem apagar dados e obrigações.
- **Cancelamento/reembolso/reversão:** preservar vigência paga até limite legal e contratual; reversão só por conciliação/evidência, preservando transações e direitos legítimos de terceiros.
- **Ampliado:** sem checkout/ativação enquanto o teto não for aprovado. **DEMO/HOMOLOGAÇÃO:** dados/credenciais fictícios, sem operações reais, nunca promovidos automaticamente a PRODUÇÃO.

**Nenhuma dessas operações de negócio entra na primeira migration inativa por esta proposta.**

## 6. Plano de implementação proposto para autorização posterior

**Passo A — decisão documental (este checkpoint):** aprovar ou ajustar identidade por ato comercial, esquema de campos, caminho de integridade composta e estratégia do histórico de segmentos. Registar decisão na documentação canônica.

**Passo B — nova tarefa de código, com autorização própria:** em branch própria e no diretório único, adicionar modelo SQLAlchemy **somente inativo** e nova migration Alembic dependente de `c15r2_20261020`. **Preservar o conteúdo da migration C15**. Incluir constraints/chaves complementares estritamente necessárias, testes estáticos e de regressão. Não instalar dependências nem fazer DDL no banco.

**Passo C — revisão técnica/CI:** validar `pip check`/testes no Python 3.13.5 do Debian PRoot independente ou GitHub Actions, sem mascarar falhas; revisar DDL compilado, diferenças Git, segurança, risco e contrato; PR e merge só após aceites. A CI estática não equivale a prova DDL no servidor.

**Passo D — pré-execução PostgreSQL em gate separado:** inspeção read-only, backup PostgreSQL fresco cifrado com recuperação verificável e plano de ensaio isolado/autorizado; teste real de `upgrade`/`downgrade` somente em cenário seguro, efêmero e autorizado. **Jamais testar `downgrade` apagando as tabelas da única base autoritativa.** Se não houver estratégia segura, status BLOCKED e retorno ao proprietário.

**Passo E — eventual aplicação real:** somente ordem específica do proprietário, com revisão-alvo, identidade do banco, backup recente, plano de reversão e evidência; ainda sem habilitar dinheiro real ou licenças ativas.

## 7. Matriz mínima de testes e aceites futuros

| Teste proposto | Critério objetivo | Estágio |
|---|---|---|
| LS-01 | Revisão C15 preservada; nova revisão possui `down_revision=c15r2_20261020` | Código, após autorização |
| LS-02 | Modelo/tabela de assinatura não permitem estado `ATIVA`, `paid_payment_id` ou vigência ativa no snapshot inicial | Código/teste de restrição |
| LS-03 | Tenant/contratante distintos, oferta/versão/preço/aceite incompatíveis são negados por FKs ou por validação comprovada sem brecha | Testes de integridade PostgreSQL autorizados |
| LS-04 | Mesmo aceite/oferta não cria duas assinaturas; callbacks duplicados não duplicam o direito | Estrutural primeiro, serviço depois |
| LS-05 | Nenhum Pix ou licença ativa é concedido em ambiente `DEMO`/`HOMOLOGACAO` | Implementação financeira futura |
| LS-06 | Vencimento suspende imediatamente novos compromissos, mantendo pagamentos e direitos existentes | Serviço futuro; AT-04 |
| LS-07 | Renovação antecipada/atrasada, ano bissexto e âncora 31 preservam os intervalos corretos | Serviço futuro; AT-19 |
| LS-08 | Upgrade calcula segmentos antigos/futuros separadamente; não cobra novamente preço já quitado | Serviço futuro; AT-20 |
| LS-09 | Downgrade com capacidade excedente é recusado sem remover participações | Serviço futuro; AT-20 |
| LS-10 | Reversão de pagamento não apaga obrigações e não ativa licença fictícia | Serviço futuro; AT-16/23 |
| LS-11 | Ensaio real da migration e reversão segura demonstrados fora da base principal | Gate PostgreSQL posterior |
| LS-12 | Dump PostgreSQL tem estratégia de restauração testada, sem fonte de verdade paralela persistente | Gate de recuperação posterior |

**Importante:** LS-01 a LS-12 são **critérios propostos, não testes PASS**. A Fase 2 continua **EM ANDAMENTO**.

## 8. Decisões explícitas a obter antes de editar código

1. **D-R4-01 — Registro por ato comercial:** aprovar a recomendação de uma assinatura por oferta/aceite, preservando múltiplos históricos por tenant; ou optar formalmente por cabeçalho único de vigência com eventos imutáveis.
2. **D-R4-02 — Segmentação:** aprovar histórico `append-only` obrigatório antes de ativação e decidir se a estrutura inativa de segmentos entra na **mesma futura revisão** ou somente em uma revisão posterior, antes dos serviços de licença.
3. **D-R4-03 — Restrição inicial:** aprovar que a primeira implementação de `LicenseSubscription` seja **inteiramente inativa** (sem vigência, pagamento conciliado, privilégios ou operações reais), sem mudar o contrato financeiro.
4. **D-R4-04 — Integridade:** autorizar que o desenho técnico acrescente chaves/índices compostos nas tabelas preexistentes, quando estritamente necessários à coerência tenant→oferta→aceite→pagamento, com testes explícitos.
5. **D-R4-05 — Execução:** após aprovação do desenho, solicitar **nova autorização específica** para arquivos, branch, PR e testes; migração no banco, restauração e operações financeiras exigem **gates independentes**.

**Recomendação global:** aprovar D-R4-01/03/04 e a obrigatoriedade conceitual da segmentação; para D-R4-02, preferir **schema de segmentos inativos na mesma futura revisão** se os testes estáticos mostrarem coerência, mantendo toda ativação fora do escopo. Isso evita fixar um desenho insuficiente já conhecido, sem multiplicar repositórios ou bancos.

## 9. Checkpoint de governança

| Campo | Resultado |
|---|---|
| `C16_R4_CONTRACT_REVIEW` | PASS — §§ do contrato identificados e mapeados |
| `C16_R4_CURRENT_SCHEMA_REVIEW` | PASS — modelos C15 e chaves existentes conferidos |
| `C16_R4_SPECIFICATION` | **PROPOSTA CONCLUÍDA — NÃO APROVADA AINDA** |
| `C16_R4_CODE_CHANGES` | ZERO |
| `C16_R4_POSTGRES_WRITES` | ZERO |
| `C16_R4_NEW_MIGRATION` | NOT_CREATED |
| `C16_R4_PYTHON_TESTS` | NOT_RUN — nenhum teste novo invocado |
| `C16_R4_BACKUP` | C16-R2 PASS — backup Git existente, sem novo backup nesta etapa |
| `C16_R4_GIT_PUBLISH` | NOT_RUN — documento fora do repositório até autorização/revisão |
| `C16_R4_NEXT_GATE` | Aprovação de desenho D-R4-01 a D-R4-05; depois escopo mínimo de implementação |

**Regra de continuidade:** preservar este documento na Biblioteca e publicar no repositório por procedimento documental controlado quando aprovado, sem substituí-lo por lembranças informais de chat. Não alterar C15, PostgreSQL ou as regras financeiras por inferência.
