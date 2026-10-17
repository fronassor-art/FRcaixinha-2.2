
# FRCAIXINHA 2.2 — CADERNO MESTRE DE CONTROLE MANUAL DO DESENVOLVIMENTO

**Edição de acompanhamento: 17/10/2026 — Documento derivado para impressão; não altera o Contrato Técnico Mestre.**  
**FONTE AUTORITATIVA:** Contrato Técnico Mestre FINAL_APROVADO de 16/10/2026.  
**FONTES COMPLEMENTARES:** Documento Mestre de Instruções de Desenvolvimento (17 seções e quatro anexos); Minutas dos membros (não aprovadas para uso real).  
**G1:** aprovado em 16/10/2026. **G2:** ordem separada de início ainda não autorizada.  
**USO:** imprimir, marcar com caneta, registrar data, evidência, commit, testes, erro e aprovação manual. Papel marcado não substitui evidência técnica.  
**ESTADOS:** N/I = não iniciado; AND = em andamento; PASS = validado com evidência; FAIL = falha; BLOQ = bloqueado; N/A = não aplicável com justificativa. **Somente PASS com evidências ou N/A justificado permite encerramento de item.**  
**IMPORTANTE:** todas as normas dos 147 itens numerados do contrato e os cenários AT-01 a AT-50 são reproduzidos adiante, além do Documento Mestre de Instruções integral. Não houve execução de código, banco, Pix ou infraestrutura para produzir este caderno.

## SUMÁRIO DO CADERNO

**Parte I:** Como utilizar, autorizações e checklist obrigatório por tarefa.  
**Parte II:** Linha do tempo, da Fase 0 ao final das sete etapas de D1 a D60.  
**Parte III:** Vinte exemplos práticos detalhados e formas de fiscalização.  
**Parte IV:** Reprodução, por seção, das 147 cláusulas numeradas do contrato aprovado, com caixa para assinatura e evidência.  
**Parte V:** Testes individuais AT-01 a AT-50, com status e resultados esperados.  
**Parte VI:** Transcrição completa do Documento Mestre de Instruções e Governança (17 seções e anexos).  
**Parte VII:** Registro de fontes e hashes, pendências condicionadas e minutas dos membros.  
**Parte VIII:** Fichas imprimíveis de desenvolvimento, erro, backup e passagem de fase.  

---


# PARTE I — COMO USAR ESTE CADERNO IMPRESSO


## 1. Identificação do acompanhamento

| Campo | Preenchimento manual |
|---|---|
| Responsável pela fiscalização | __________________________________________ |
| Data da abertura | ____/____/________ |
| Documento do contrato (versão) | FINAL_APROVADO_2026-10-16 |
| Hash da cópia contratual | Conferir no registro de fontes (Parte VII) |
| Sessão Termux / host | __________________________________________ |
| Repositório (após G2) | __________________________________________ |
| Diretório (após G2) | `~/FRcaixinha_2.2` |
| PostgreSQL autoritativo | __________________________________________ |
| Último backup restaurável | Data ______  Local ______  Prova ______ |

## 2. Passos obrigatórios em TODA tarefa

- ☐ Identificar requisito e cláusula contratual; se não encontrar, PARAR e submeter dúvida em vez de inventar.
- ☐ Confirmar que G2 e a etapa específica foram expressamente autorizados antes de escrever código/infraestrutura.
- ☐ Registrar situação anterior: branch, commit SHA, banco/schema/Alembic, testes existentes, recursos livres no celular.
- ☐ Listar o menor conjunto de arquivos permitido e identificar dependências, riscos e critério de reversão.
- ☐ Quando alteração estrutural ou arriscada, fazer backup protegido antes da escrita; verificar integridade.
- ☐ Implementar somente o escopo autorizado; nenhuma cópia paralela de projeto, banco persistente ou instalações redundantes.
- ☐ Rodar teste de unidade, integração e regressões afetadas; conferir saída real e evidências.
- ☐ Em qualquer FAIL/BLOQ, reproduzir, investigar causa, aplicar correção mínima, retestar e registrar antes de continuar.
- ☐ Conferir diferença Git, ausência de segredos, compatibilidade das migrations e documentação correspondente.
- ☐ Guardar evidência, concluir checkpoint, identificar backup válido e solicitar aceite manual antes de passar de fase.

**Ficha curta por tarefa:** ID ______  Cláusulas ______  Data ______  Commit SHA ______  Banco/migration ______  Teste/comando ______  Resultado ______  Backup ______  Assinatura ______

## 3. Regras que nunca podem ser presumidas

- ☐ Plano Ampliado: teto de membros/cotas não decidido; venda, checkout e ativação bloqueados.
- ☐ Taxa adicional do Master sobre lucros de caixinhas de terceiros: EM ESTUDO; não cobrar, não gerar obrigação nem fazer split.
- ☐ Operações reais de Pix, empréstimos, liquidação e bolões: somente depois dos gates jurídicos/provedor/produção pertinentes.
- ☐ Minutas jurídicas dos membros: ainda sujeitas a preenchimento, conferência jurídica e aceite individual; não têm aprovação automática.
- ☐ Bolões: somente demonstrador com dinheiro/dados fictícios em pacote separado, após autorização específica; não integram os 60 dias.
- ☐ Desenvolvimento: projeto novo independente, nada de código, bancos, credenciais ou migrations de projeto anterior.
- ☐ Banco: uma base de desenvolvimento PostgreSQL autoritativa; segregação de tenants dentro do esquema, não uma base por caixinha.
- ☐ Não suprimir etapas de testes nem declarar PASS quando uma ferramenta, endpoint ou ambiente não foi efetivamente testado.

# PARTE II — CRONOGRAMA DE IMPLEMENTAÇÃO E FISCALIZAÇÃO

**Estimativa do Contrato, §15.2:** sete janelas consecutivas, **3 + 8 + 14 + 9 + 13 + 7 + 6 = 60 dias úteis**. Os dias contam somente após G2 e não são promessa de conclusão. Etapas com erro bloqueante não avançam. Cada fase possui escopo próprio; as verificações transversais do contrato permanecem em todas elas.

## FASE 0 — PRÉ-INÍCIO: G1/G2, autorização e salvaguardas

**Janela:** ANTES DE D1 | **Duração:** 0 dias de codificação | **Cláusulas-chave:** 1.8; 15.1; 15.2; 15.4; 15.5; 16.1–16.5 | **Testes de referência:** AT-18.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Conferir posse da íntegra do contrato FINAL_APROVADO e instruções; preservar a versão aprovada e hash.
- ☐ **02.** Conferir se consta ordem expressa G2 específica para criar diretório/repositório e iniciar programação; sem ela, não executar.
- ☐ **03.** Conferir que nenhuma contratação, hospedagem, recurso pago, operação real ou credencial foi autorizada por inferência.
- ☐ **04.** Identificar ferramentas já instaladas no Android/Termux e possíveis incompatibilidades sem instalar nada ainda.
- ☐ **05.** Exigir plano da primeira etapa com arquivos permitidos, testes, salvaguardas e orçamento zero ou custo expressamente aprovado.
- ☐ **06.** Identificar as pendências condicionadas: Plano Ampliado, taxa extra em estudo, conformidade legal, provedores e loteria.
- ☐ **07.** Conferir separação de funções G1–G7 e do demonstrador lotérico fora do núcleo.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 1 — BASE DO PROJETO

**Janela:** D1–D3 | **Duração:** 3 dias úteis | **Cláusulas-chave:** 1.1–1.12; 15.2; 15.3; 15.5; 13.7; Instruções 4–7/17 | **Testes de referência:** AT-18; AT-32; AT-33.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Somente após G2, confirmar existência de UM diretório raiz `~/FRcaixinha_2.2` sem clone concorrente.
- ☐ **02.** Criar a estrutura autorizada `mobile/`, `backend/`, documentação e `.github/` dentro da mesma raiz.
- ☐ **03.** Criar repositório GitHub NOVO e próprio; não reaproveitar código, banco ou histórico anterior.
- ☐ **04.** Inspecionar requisitos técnicos de Flutter/Dart, Python/FastAPI, PostgreSQL, SDK Android e CI para ARM64/Termux/PRoot.
- ☐ **05.** Reutilizar ferramentas compatíveis já instaladas; não fazer múltiplas instalações por tentativa e erro.
- ☐ **06.** Configurar Git, .gitignore, secrets protegidos, branches e CI mínimo sem chaves ou dados pessoais.
- ☐ **07.** Confirmar comandos que inicializam Flutter e API mínima no ambiente disponível sem exigir computador.
- ☐ **08.** Validar fluxo GitHub Actions para build APK quando previsto, distinguindo teste local de runner GitHub.
- ☐ **09.** Registrar commit SHA, resultado CI, backup inicial e uso de memória/armazenamento.
- ☐ **10.** Não declarar fase concluída sem app/API mínimos inicializarem e sem aceite do responsável.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 2 — BANCO POSTGRESQL, IDENTIDADE E SEGURANÇA

**Janela:** D4–D11 | **Duração:** 8 dias úteis | **Cláusulas-chave:** 2.1–2.9; 3.1-A; 6.1-A; 12.1–12.5; 13.1–13.2; Instruções 8/11/17 | **Testes de referência:** AT-09; AT-10; AT-47; AT-49.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Configurar UMA base PostgreSQL de desenvolvimento como única fonte de verdade, com teste transacional isolado.
- ☐ **02.** Criar migrations Alembic reversíveis e verificar upgrade/downgrade na base autorizada sem perda de dados.
- ☐ **03.** Modelar `UserIdentity` única, `ContractingParty`, `Tenant`, `RoleGrant`, `Membership`, `Cycle`, `Quota`, `LicenseSubscription`, `TermAcceptance` e entidades do contrato.
- ☐ **04.** Garantir isolamento lógico por `tenant_id` e `cycle_id`, unicidade, chaves estrangeiras e índices compostos.
- ☐ **05.** Cadastrar PF: nome/CPF/e-mail confirmado/telefone DDD; foto opcional; endereço só quando necessário.
- ☐ **06.** Preparar PJ somente quando habilitada: razão social/CNPJ, representante e comprovação de poderes quando exigida.
- ☐ **07.** Validar CPF/CNPJ, e-mail, sessões, senha com hash, confirmação de posse de telefone quando utilizada.
- ☐ **08.** Modelar membro por convite nominal, identidade existente ou nova, contratos e aceite por ciclo.
- ☐ **09.** Conferir convite pendente sem acesso financeiro; nenhuma alteração no outro tenant ao trocar contexto.
- ☐ **10.** Negar consultas cruzadas por ID/URL entre caixinhas; Master não recebe poderes financeiros.
- ☐ **11.** Versionar contratos, políticas e consentimentos; guardar hash/identidade/evidência/data de aceite.
- ☐ **12.** Fixar o calendário global e negar alteração de datas centrais pelo administrador.
- ☐ **13.** Verificar proteção de dados pessoais, logs mínimos e ausência de segredos.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 3 — NÚCLEO DE AUTOMAÇÃO E CÁLCULOS

**Janela:** D12–D25 | **Duração:** 14 dias úteis | **Cláusulas-chave:** 3.1–3.11; 4.1–4.8; 6.1–6.6; 7.1–7.6; 8.1–8.9; 10.1–10.8 | **Testes de referência:** AT-01–08; AT-12–14; AT-19–22; AT-24–25; AT-34–35; AT-41–44; AT-45–50.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Implementar planos Essencial (20/40; 89,90 mensal), Intermediário (50/50; 109,90 mensal) e Ampliado SEM checkout até teto decidido.
- ☐ **02.** Garantir preço anual = mensal × 10, editando só mensal e gerando `LicensePriceVersion`; preço pago não muda retroativamente.
- ☐ **03.** Ofertar licença e aceite antes de cobrar; ativar apenas após confirmação/conciliacão legítima.
- ☐ **04.** Vigência preserva dia âncora; renovação antecipada soma tempo; expirada fica suspensa com zero carência.
- ☐ **05.** Em licença suspensa, impedir novos compromissos e preservar pagamentos de obrigações, consultas, conciliação e fechamento.
- ☐ **06.** Contar membro ativo uma vez e cada cota separadamente; convites não gastam capacidade.
- ☐ **07.** Permitir configurações próprias por tenant, nunca copiar taxa/percentual do proprietário a outros.
- ☐ **08.** Congelar percentuais de distribuição por tenant/ciclo; mudança só no ciclo seguinte após aceites.
- ☐ **09.** Ciclo anual 01/01–31/12, vencimento mensal dia 10, liquidação elegível dia 10/01 seguinte; fuso America/Belem.
- ☐ **10.** Reconhecer somente contribuições confirmadas e conciliadas, inclusive parciais, mantendo status financeiro separado do temporal.
- ☐ **11.** Ledger em centavos exatos com partidas dobradas, estornos rastreáveis e caixa livre sem dupla dedução.
- ☐ **12.** Empréstimos SOMENTE para membros, taxa/prazo próprios por tenant e motor Price 1–12 parcelas dentro do ciclo.
- ☐ **13.** Na caixinha do proprietário: 20% ao mês, máximo 6 parcelas, multa única R$ 10, mora simples diária 20%/30 sobre principal vencido.
- ☐ **14.** Primeiro vencimento dia 10 mês seguinte ao Pix confirmado; juros iniciais proporcionais dias reais/30; Price ajustada.
- ☐ **15.** Pagamentos parciais: parcela vencida mais antiga e componentes juros→mora→multa→principal; sem juros futuros na antecipação.
- ☐ **16.** Bloquear empréstimos próprios do admin sem unanimidade anual válida e revalidar antes da autorização, reserva e Pix.
- ☐ **17.** Na caixinha própria, conferir gatilho de três contribuições consecutivas não quitadas e perda integral do lucro do ciclo SOMENTE se juridicamente validada; principal devolvível preservado.
- ☐ **18.** Calcular lucro líquido realizado, rateio Capital-Dias fim de dia e percentuais do ciclo fixos.
- ☐ **19.** Distribuir resíduos pelo método maiores restos/desempate membership_id, sem Pix isolado de centavos.
- ☐ **20.** Fechamento separa principal, lucro, remuneração, reserva, resultado contestado e obrigações remanescentes.
- ☐ **21.** Testar lotes com dinheiro fictício, casos de mês curto e limites de virada anual, sem tocar dinheiro real.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 4 — PIX, RESERVAS E CONCILIAÇÃO

**Janela:** D26–D34 | **Duração:** 9 dias úteis | **Cláusulas-chave:** 3.6; 7.4–7.6; 9.1–9.9; 10.6; 12.2; 13.6 | **Testes de referência:** AT-11; AT-16; AT-23; AT-28–29; AT-37; AT-41.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Separar conta legítima da plataforma (licenças) das contas conectadas legítimas das caixinhas.
- ☐ **02.** Conferir capacidades reais e contrato do Mercado Pago; não inventar APIs Pix OUT ou Connect.
- ☐ **03.** Implementar adaptadores `PaymentCollectionPort`, `PaymentDisbursementPort`, `ProviderReconciliationPort`, `ExternalAccountPort` e `EvidenceStorePort`.
- ☐ **04.** Proteger tokens por tenant e ambiente; não expor credenciais no Flutter/CI/logs.
- ☐ **05.** Gerar QR e Copia e Cola vinculados à obrigação e ao recebedor certo, com idempotência estável.
- ☐ **06.** Confirmar pagamentos apenas por fonte autoritativa conciliada, nunca por print, botão ou webhook isolado.
- ☐ **07.** Testar webhook inválido, duplicado, fora de ordem, valores e comerciante divergentes, conexão revogada.
- ☐ **08.** Reservar saldo atomicamente na aprovação de crédito; impedir gasto duplo e Pix OUT duplicado.
- ☐ **09.** Timeout/ambiguidade: manter PENDENTE_CONCILIACAO e consultar provedor antes de repetir.
- ☐ **10.** Pix de encerramento: destinatário, valor, comprovação e distribuição vinculada; nada antes de autorizações.
- ☐ **11.** Simular reembolso/estorno com eventos compensatórios sem apagar histórico.
- ☐ **12.** DEMO/HOMOLOGACAO não podem enviar/receber dinheiro real. Operação real bloqueada sem G5/G6 e demais autorizações.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 5 — FLUTTER, JORNADAS E PAINÉIS

**Janela:** D35–D47 | **Duração:** 13 dias úteis | **Cláusulas-chave:** 2.7–2.9; 3.1-A; 6.1-A; 11.0-A–11.5; 13.1–13.2 | **Testes de referência:** AT-01–10; AT-33; AT-39; AT-45–50.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Implementar telas reais por papel (Master, Administrador e Membro) sem navegação financeira transversal.
- ☐ **02.** Tela “Quero administrar uma caixinha”: PF/PJ autorizada, foto opcional, oferta, preço, aceite e Pix confirmado.
- ☐ **03.** Jornada de membro por convite nominal, cadastro/CPF/e-mail confirmado, aceite e cotas no tenant/ciclo correto.
- ☐ **04.** Mostrar capacidades e contagem exata; impedir exceder plano e bloquear Ampliado.
- ☐ **05.** Painel Master: licenças, métricas comerciais e suporte, sem dados financeiros íntimos de terceiros.
- ☐ **06.** Painel administrador: políticas por tenant, membros, cobranças, empréstimos, relatórios e fechamento.
- ☐ **07.** Painel membro: apenas suas cotas, seu capital, contribuições, empréstimos e resultados.
- ☐ **08.** Exibir calendário global em modo leitura: nenhum botão de edição de datas centrais.
- ☐ **09.** Apresentar simulação de crédito e contrato financeiro completo antes do pedido.
- ☐ **10.** Exibir estados PENDENTE/PARCIAL/VENCIDO/EM CONCILIAÇÃO com textos acessíveis, não apenas cor.
- ☐ **11.** Telas de suspensão distinguem proibição de novos compromissos e preservação de obrigações antigas.
- ☐ **12.** Exibir anuência anual do admin-membro como instrumento específico, verificável e revogável.
- ☐ **13.** Manual de administrador deve reproduzir exatamente telas e caminhos reais, sem inventar funções.
- ☐ **14.** Testes ponta a ponta: erro de conexão, rotação, tamanho de tela, sem clique repetido que gera duplicata.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 6 — SUPORTE, SEGURANÇA E RECUPERAÇÃO

**Janela:** D48–D54 | **Duração:** 7 dias úteis | **Cláusulas-chave:** 5.1–5.5; 13.1–13.6; Instruções 5–7/12/15/17 | **Testes de referência:** AT-16–17; AT-21; AT-23.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Suporte normal utiliza logs minimizados e métricas sem navegar por dados pessoais/financeiros de terceiros.
- ☐ **02.** Acesso excepcional exige consentimento com tenant, recurso, finalidade, autoria, escopo e prazo.
- ☐ **03.** Acesso normal de suporte: até 60 minutos, sem renovação automática; acesso emergencial: até 30 minutos e somente gatilho crítico comprovado.
- ☐ **04.** Revogação e expiração devem invalidar sessões ativas e negar novas chamadas.
- ☐ **05.** Suporte excepcional jamais autoriza Master a aprovar empréstimo, realizar Pix ou alterar patrimônio.
- ☐ **06.** Rotinas de backup: completo criptografado diariamente, WAL no intervalo até 15 min, retenção 35 dias quando homologado.
- ☐ **07.** Manter cópia recuperável fora do diretório ativo, sem outra árvore ativa do projeto e sem segredos expostos.
- ☐ **08.** Verificar capacidade RPO ≤1 hora e RTO ≤8 horas na infraestrutura homologada; testes de restauração antes de produção e trimestrais depois.
- ☐ **09.** Restaurar base em ambiente autorizado e reconciliar Pix para impedir reenvio de transações já concluídas.
- ☐ **10.** Monitorar armazenamento, memória, certificados, saúde API/banco/CI e evitar caches/builds redundantes.
- ☐ **11.** Testar resposta a incidentes, alertas e recuperação com evidências e checkpoint.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


## FASE 7 — HOMOLOGAÇÃO TÉCNICA E ENTREGA

**Janela:** D55–D60 | **Duração:** 6 dias úteis | **Cláusulas-chave:** 15.2–15.7; 16.1–16.5; 13.6; 9.9 | **Testes de referência:** AT-01–AT-50.

**Abertura da fase** — data ____/____/______ | autorizado por __________________ | baseline SHA __________________ | PostgreSQL/Alembic __________________ | backup de entrada __________________
- ☐ **01.** Executar a matriz completa AT-01 a AT-50 e testes de regressão; registrar PASS/FAIL/BLOQ/NOT_RUN reais.
- ☐ **02.** Qualquer FAIL/BLOQ que afete a etapa é corrigido e reexecutado antes de conclusão.
- ☐ **03.** Conferir todas as 147 cláusulas numeradas e as tabelas/legendas/vetos transversais contra o código entregue.
- ☐ **04.** Conferir migração Alembic e único banco PostgreSQL autoritativo, sem dados financeiros divergentes.
- ☐ **05.** Validar backups e restauração, ausência de segredos, segurança/tenant, idempotência financeira e logs.
- ☐ **06.** Empacotar APK Android reproduzível pelo GitHub Actions, com commit/hash e artefato verificável.
- ☐ **07.** Entregar manual do administrador baseado nas telas efetivas, documentação e registro de requisitos.
- ☐ **08.** Concluir núcleo como NUCLEO_HOMOLOGADO somente se houver provas e aceite formal; não alegar produção ou Pix real.
- ☐ **09.** Manter separadas autorizações G5 (provedor), G6 (jurídica/tributária), G7 (publicação), infraestrutura e recursos lotéricos.
- ☐ **10.** Registrar checkpoint final, resultados, limitações, backup válido e aprovação manual expressa.

**ENCERRAMENTO / PORTÃO MANUAL**
- ☐ Sem falha bloqueante conhecida
- ☐ Testes reexecutados e provas anexadas
- ☐ Git e migration verificados
- ☐ Backup íntegro e restaurável
- ☐ Regras aprovadas preservadas
- ☐ Aprovação do responsável antes da fase seguinte
**Resultado da fase:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ N/A justificado  |  Data ____/____/______  |  Evidências (IDs/caminhos): __________________________  |  Assinatura: __________________________

---


# PARTE III — EXEMPLOS DETALHADOS PARA CONFERÊNCIA MANUAL

**Os exemplos desta parte reproduzem dados, parâmetros ou resultados ilustrativos previstos no Contrato Técnico Mestre. Não autorizam testes com dinheiro real.** Quando indicado “fictício”, trata-se de teste sintético e não de obrigação a impor a um tenant.

### E01 — Capacidade e escolha do plano

**Fonte:** 3.2; 3.3; 3.4; AT-01–03.
**Exemplo para simulação/manual:** Um solicitante pede 20 membros e 40 cotas: Essencial, R$ 89,90/mês ou R$ 899,00/ano. Para 21 membros e 40 cotas, ou 15 membros e 45 cotas: Intermediário, R$ 109,90/mês ou R$ 1.099,00/ano. O pedido de 40 membros e 60 cotas exige Ampliado, que fica bloqueado enquanto não houver teto aprovado.
**O que o fiscal deve exigir:** Comprovar que as duas capacidades são verificadas simultaneamente e que não se gera Pix nem licença de Ampliado.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E02 — Uma pessoa, várias cotas

**Fonte:** 3.4; 6.2; AT-48–49.
**Exemplo para simulação/manual:** Uma identidade com três cotas ativas em uma caixinha consome uma vaga de membro e três cotas. Um convite pendente consome zero vagas. A mesma identidade pode participar de outra caixinha por vínculo independente, sem enxergar os dados da primeira.
**O que o fiscal deve exigir:** Registrar contadores antes/depois, memberships separados e negação de consulta cruzada.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E03 — Preço comercial e histórico

**Fonte:** 3.2-A; AT-24–25.
**Exemplo para simulação/manual:** Ao alterar a mensalidade Essencial de R$ 89,90 para R$ 99,90, o anual passa automaticamente de R$ 899,00 a R$ 999,00. Licença já paga e oferta previamente aceita conservam o preço/versão original; renovação exige nova oferta/aceite.
**O que o fiscal deve exigir:** Comprovar que o campo anual não é editável, o cálculo usa ×10 e que há LicensePriceVersion.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E04 — Carência zero sem lesar direitos

**Fonte:** 3.7–3.9; AT-04; AT-19.
**Exemplo para simulação/manual:** No instante final da licença paga, sem renovação conciliada, o tenant entra em SUSPENSA; não admite novo membro, cota ou novo empréstimo, mas preserva extratos, pagamentos já devidos, conciliação e fechamento.
**O que o fiscal deve exigir:** Tentar ação nova e ação de quitação legítima no mesmo cenário; a primeira deve falhar e a segunda prosseguir sob controles.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E05 — Calendário e ciclo

**Fonte:** 4.5; 4.6; AT-06.
**Exemplo para simulação/manual:** Para o primeiro ciclo, período 01/01/2027–31/12/2027; contribuição mensal dia 10 quando aplicável; liquidação elegível prevista em 10/01/2028. O administrador não pode alterar datas globais.
**O que o fiscal deve exigir:** Conferir data/fuso America/Belem, bloqueio por backend e fechamento condicionado à conciliação.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E06 — Políticas independentes

**Fonte:** 4.1–4.4; 10.2; AT-05; AT-35; AT-44.
**Exemplo para simulação/manual:** Na caixinha do proprietário, 20% ao mês, Price e máximo seis parcelas; divisão 85% membros/15% admin. Um outro cliente pode, após aceite e validação, escolher 20/80 ou 30/70 sem alterar a caixinha do proprietário. Percentual 15% de 2027 não muda retroativamente para 30%; possível novo valor só vale em 2028 após aceites.
**O que o fiscal deve exigir:** Comparar configurações e o rateio final de dois tenants e testar edição no meio do ciclo.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E07 — Contribuição parcial vencida

**Fonte:** 6.3–6.4; AT-12.
**Exemplo para simulação/manual:** Uma contribuição de teste é parcialmente paga e confirmada, mas o saldo continua aberto após dia 10. Exibir estado financeiro PARCIAL e temporal VENCIDA simultaneamente. Cobrança pendente ou QR gerado não é capital confirmado.
**O que o fiscal deve exigir:** Conferir ledger, comprovantes e que a parte não paga não aumentou o saldo disponível.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E08 — Inadimplência particular da caixinha do proprietário

**Fonte:** 6.5–6.6; 10.3.
**Exemplo para simulação/manual:** Três contribuições mensais consecutivas vencidas e não integralmente quitadas fazem, se a cláusula for juridicamente válida, o peso de lucro do membro zerar em todo o ciclo, mas não fazem desaparecer o principal que ele realmente pagou nem sua dívida documentada.
**O que o fiscal deve exigir:** Executar teste apenas fictício e marcar dependência de validação jurídica antes de operação real.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E09 — Primeiro intervalo Price

**Fonte:** 8.4–8.5; AT-43.
**Exemplo para simulação/manual:** Desembolso confirmado em 28/02; primeiro vencimento em 10/03. O intervalo para juros da primeira prestação usa os dias civis efetivos entre as datas, divididos por 30, e não presume um mês completo. Parcelas seguintes vencem todo dia 10, e a última deve caber até 31/12.
**O que o fiscal deve exigir:** Conferir contagem de dias, fórmula variável do primeiro período, prestações estáveis e ajuste apenas na última parcela.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E10 — Imputação de pagamento parcial

**Fonte:** 8.6; AT-41.
**Exemplo para simulação/manual:** Diante de uma parcela vencida com juros remuneratórios, mora acumulada, multa única e principal, um pagamento pequeno é imputado primeiro aos juros. Se sobra, passa à mora; só depois à multa e ao principal. Enquanto nada for imputado ao principal, sua base de mora futura não diminui.
**O que o fiscal deve exigir:** Exigir lançamentos separados por componente e simular pagamentos posteriores até amortizar o principal.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E11 — Mora simples, sem anatocismo

**Fonte:** 4.2; 8.6.
**Exemplo para simulação/manual:** Teste fictício: se houver R$ 100,00 de principal vencido não pago durante 3 dias civis, a mora nominal simples a 20%/30 ao dia totaliza R$ 2,00 (100 × 0,20/30 × 3), antes de verificar regras monetárias do contrato e incidência legítima. Não calcular mora sobre juros, multa ou sobre a própria mora.
**O que o fiscal deve exigir:** Conferir data efetiva de confirmação de pagamentos e arredondamentos; simulação não representa legalidade automática de 20%.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E12 — Pré-pagamento sem juros futuros

**Fonte:** 8.5–8.6.
**Exemplo para simulação/manual:** Membro antecipa quitação após ter parcelas futuras ainda não vencidas: cobrar somente saldo de principal e encargos já incorridos legitimamente exigíveis; juros futuros não entram na quitação. Atualização de ledger deve ser conciliada.
**O que o fiscal deve exigir:** Comparar cronograma antes/depois e comprovar ausência de juros de períodos futuros.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E13 — Empréstimo do administrador-membro

**Fonte:** 2.5–2.6; 8.8; AT-07–08.
**Exemplo para simulação/manual:** Todos os outros membros ativos assinam individualmente a autorização específica para 2027. Novo membro entra sem aderir ou signatário exerce revogação eficaz antes do Pix: bloquear novo desembolso mesmo se o empréstimo havia sido aprovado. Para 2028 é exigido novo consentimento.
**O que o fiscal deve exigir:** Conferir unanimidade na decisão, reserva e imediatamente antes do envio Pix; ausência de membros adicionais não libera operação.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E14 — Pix duplicado e timeout

**Fonte:** 9.3–9.5; AT-11; AT-16.
**Exemplo para simulação/manual:** O provedor confirma uma transação e a notificação chega 10 vezes, ou o primeiro retorno dá timeout. O sistema deve guardar uma operação econômica, esperar conciliação no timeout e jamais repetir cobrança/desembolso como se fosse novo.
**O que o fiscal deve exigir:** Comparar idempotency_key, external_id, reservas e ledger; um único efeito econômico.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E15 — Rateio pelo Capital-Dias

**Fonte:** 10.1–10.4; AT-13.
**Exemplo para simulação/manual:** O peso de cada membro é W_i = Σ_d(C_i,d × E_i,d), a partir de capital comprovadamente recebido/conciliado e elegibilidade no fechamento de cada dia em America/Belem. O total distribuível exclui principal e dinheiro de outros tenants.
**O que o fiscal deve exigir:** Recalcular com entradas de capital em dias distintos e verificar que dias anteriores não ganham peso retroativo.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E16 — Centavos e maiores restos

**Fonte:** 10.4; AT-14; AT-42.
**Exemplo para simulação/manual:** Após truncar o direito de cada membro ao centavo, o resíduo não pertence ao administrador. Distribuir R$ 0,01 por vez aos maiores restos fracionários, desempate por membership_id ascendente; registrar e zerar a carteira técnica dos resíduos atribuídos, sem Pix individual de centavos.
**O que o fiscal deve exigir:** Verificar igualdade centavo a centavo entre total dos direitos e das distribuições, inclusive empate.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E17 — Restaurar backup sem novo pagamento

**Fonte:** 13.4; 9.4; AT-16; AT-23.
**Exemplo para simulação/manual:** Após restauração de um snapshot anterior à confirmação externa de um Pix, reconciliar novamente junto ao provedor antes de qualquer retry. Um pagamento já executado não pode sair novamente só porque o backup é anterior ao webhook.
**O que o fiscal deve exigir:** Anexar restauração, consulta autoritativa ao provedor, idempotência, RPO/RTO medidos.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E18 — Suporte 60/30 minutos

**Fonte:** 5.2–5.4; AT-17; AT-21.
**Exemplo para simulação/manual:** Acesso técnico normal expira em até 60 min, emergencial em até 30 min e com incidente crítico real comprovado. Revogação no meio da sessão corta chamadas imediatamente; nunca atribuir botão de aprovar empréstimo ao Master.
**O que o fiscal deve exigir:** Testar expiração/revogação no backend, logs e ausência de acesso financeiro.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E19 — Demonstrador lotérico somente fictício

**Fonte:** 14.1–14.6; AT-15; AT-26–27.
**Exemplo para simulação/manual:** Simulação do próprio contrato: 20 cotas a R$ 25,00 = R$ 500,00 totais; custo oficial fictício R$ 150,00, R$ 7,50 por cota; margem bruta R$ 350,00. Não existe aposta real, bilhete oficial ou Pix verdadeiro; demo pertence a pacote adicional autorizado separadamente.
**O que o fiscal deve exigir:** Conferir diferenciação entre margem e prêmios e bloqueio técnico de dinheiro real.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

### E20 — Membro/cadastro e privacidade

**Fonte:** 3.1-A; 6.1-A; AT-45–50.
**Exemplo para simulação/manual:** PF administrador ou membro deve ter nome, CPF, e-mail confirmado e telefone DDD; endereço apenas quando necessário; foto opcional. Convite pendente não libera extrato. Um CPF legítimo com dois memberships não cria dois logins concorrentes nem expõe outra caixinha.
**O que o fiscal deve exigir:** Testar CPF inválido, e-mail não confirmado, foto removida, troca de contexto, permissões de backend e minimização.
☐ Teste demonstrado  ☐ Cálculo conferido  ☐ Cláusula respeitada  ☐ Evidência arquivada  |  Teste/arquivo __________  Resultado __________  Data __________

# PARTE IV — CONFERÊNCIA LITERAL DE CADA CLÁUSULA DO CONTRATO APROVADO

**Atenção:** a redação contratual abaixo foi retirada do arquivo oficial aprovado, por cláusula e com suas tabelas. Não alterar percentuais, datas, condições, texto ou status por analogia. A transcrição conserva a redação em Markdown e acrescenta apenas o quadro de fiscalização após cada item. Em caso de divergência de renderização ou interpretação, conferir o arquivo oficial cujo SHA-256 está na Parte VII. A organização das fases está na Parte II.**

## Norma de abertura do contrato (íntegra do cabeçalho, finalidade e bloqueios)

**FRCAIXINHA 2.2 — texto de abertura original**

**CONTRATO TÉCNICO MESTRE — VERSÃO FINAL APROVADA PARA DESENVOLVIMENTO**

**Versão documental final:** 16/10/2026 — consolidação integral após auditoria do Codex, quatro convenções financeiras aprovadas, complementos cadastrais 3.1-A e 6.1-A e aprovação expressa do proprietário para servir como especificação de desenvolvimento. **G1 (aprovação documental) CONCLUÍDO. G2 (ordem separada de criação e programação) NÃO AUTORIZADO.**  
**Titular e responsável pela aprovação:** Administrador Master do FRcaixinha 2.2.  
**Objeto:** uma plataforma SaaS privada de automação de caixinhas, com administração independente por contratante e transparência aos membros.  
**Natureza do documento:** especificação funcional, arquitetural, de dados e de aceite; **não substitui contrato jurídico de adesão, parecer regulatório ou autorização de operação financeira**.

> **MARCO ZERO.** O aplicativo, a pasta futura `~/FRcaixinha_2.2`, o repositório novo, o banco de produção, as credenciais e a hospedagem **ainda não foram criados**. Não procurar ou reutilizar projeto anterior. A aprovação documental deste contrato está concluída; somente **após ordem separada e expressa do proprietário** será permitido criar o projeto e programar. Nenhum Pix real ou atividade financeira é autorizado por esta minuta.

**Legenda:** **DEFINIDO** = decisão expressa anterior do proprietário; **APROVADO COMO REQUISITO DOCUMENTAL** = definição técnica de escopo ou comportamento que passou a integrar esta aprovação final, sem implicar início de código ou operação com dinheiro real; **EM ESTUDO** = hipótese não aprovada para cobrança nem desenvolvimento; **CONDICIONADO** = atividade sujeita a validação jurídica, regulatória, contratual ou do provedor para operação real; **ADIADO** = funcionalidade fora da primeira entrega. Não converter condição externa, parâmetro inexistente ou hipótese em estudo em liberação presumida.

---



## SEÇÃO 1 — Identidade comercial, finalidade e limites do produto


### Cláusula 1.1 | Fases de verificação: 0/1

**1.1. Visão — DEFINIDO.** O FRcaixinha 2.2 é uma solução de **automação de uma atividade já realizada manualmente** por administradores de caixinhas privadas. Em vez de cadernos e planilhas, entrega cadastro, cálculos, contribuições, crédito, cobranças, prestação de contas, relatórios e encerramento. O desenvolvedor/proprietário aufere **receita comercial de licenciamento**; o contratante conduz sua própria caixinha; cada membro visualiza sua participação e direitos. O aplicativo **não é o dono do dinheiro** nem se torna administrador financeiro das caixinhas de terceiros.

**CONTROLE MANUAL 1.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.2 | Fases de verificação: 0/1

**1.2. Público e modelo.** Contratante = pessoa responsável por organizar uma caixinha de grupo fechado; membro = pessoa convidada e admitida segundo regras contratuais; convidado externo não se torna membro por abrir material de divulgação. A oferta comercial de licença pode ser acessada por novos administradores mediante cadastro restrito, sem abrir os dados dos grupos ao público. Uma única base técnica suporta caixinhas logicamente separadas.

**CONTROLE MANUAL 1.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.3 | Fases de verificação: 0/1

**1.3. Princípios não negociáveis — DEFINIDO.** Autonomia legítima do administrador contratante; transparência aos membros; calendário financeiro uniforme e imutável pelo contratante; regras financeiras **parametrizadas por caixinha**; controle técnico/comercial do Master, **sem interferência arbitrária na operação financeira de terceiros**; Pix real apenas integrado e confirmado; trilha de auditoria; simplicidade visual; proteção do patrimônio individual; nenhum recurso pago ou uso de credenciais sem autorização.

**CONTROLE MANUAL 1.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.4 | Fases de verificação: 0/1

**1.4. Diferença essencial entre software e operação.** A plataforma fornece meios técnicos, simulações e registros. A legitimidade jurídica da organização financeira, taxa de juros, remuneração dos administradores, distribuição de resultados, cobrança e eventuais bolões depende de avaliação própria, não da mera existência da ferramenta. Administrador não pode obter do software autorização para violar lei, acordo de membros ou direito adquirido.

**CONTROLE MANUAL 1.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.5 | Fases de verificação: 0/1

**1.5. Primeira entrega — DEFINIDO.** Uma solução Android com autenticação; contratação/licenças; acesso por papel; cadastro e cotas; políticas de caixinha; calendário fixo; contribuições; extratos; caixa e ledger; simulação, pedidos e decisão de empréstimos internos; desembolso exclusivamente Pix integrado; recebimentos confirmados; cálculo do resultado; rateio; fechamento; central Master comercial/técnica; backup/restauração e suporte excepcional.

**CONTROLE MANUAL 1.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.6 | Fases de verificação: 0/1

**1.6. Escopo por prontidão, sem circularidade — APROVADO COMO REQUISITO DOCUMENTAL.** (A) **Núcleo inicial funcional e homologável**: recursos do item 1.5. (B) **Função sujeita a enquadramento setorial**: bolões oficiais; desenvolver integralmente a experiência, motor de cotas, mandato, preço, prestação de contas e verificações em **modo demonstração/homologação sem dinheiro real**, com ativação comercial impedida até liberação de conformidade; o pacote demonstrável não é promessa de permissão legal. (C) **Evolução institucional remota**: arquitetura com pontos de extensão para eventual carteira/contas de pagamento, liquidação, controles prudenciais e acesso a redes financeiras, **sem emitir contas, guardar dinheiro ou atuar como banco agora**. Eventos digitais, vendas de produtos, sorteios privados, consórcios, empréstimos a não membros, garantias de joias/leilões e marketplace não são funções aprovadas; não entram escondidos no escopo. O desenvolvimento do demonstrador do item (B) precisa ter esforço e aceite formal estimados; não cabe prometer concluí-lo dentro dos 60 dias destinados ao núcleo sem replanejamento.

**CONTROLE MANUAL 1.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.7 | Fases de verificação: 0/1

**1.7. Dinheiro real e fronteira de responsabilidade — DEFINIDO.** O dinheiro movimentado em produção por um cliente no Mercado Pago **já é dinheiro real**. O FRcaixinha atual não é detentor/custodiante de depósitos nem emissor de conta própria: automatiza instruções, confirma operações por APIs e mantém contabilidade e direitos, com os recursos efetivos na instituição provedora. Não representar saldo de ledger como depósito próprio do FRcaixinha; nunca permitir transferência sem autorização conforme a função e o provedor.

**CONTROLE MANUAL 1.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.8 | Fases de verificação: 0/1

**1.8. Ambiente técnico oficialmente escolhido — DEFINIDO.** O proprietário desenvolverá pelo **smartphone Android, sem computador**, auxiliado por **ChatGPT + Codex**, utilizando **Termux**, Git, **GitHub** e **GitHub Actions**; tecnologias do produto: **Flutter/Dart** (Android), **FastAPI/Python** (backend), **PostgreSQL/Alembic** e integração Mercado Pago exclusivamente conforme capacidades autorizadas pelo provedor. O código ficará em **repositório GitHub próprio, novo e preferencialmente privado**, a ser criado somente após ordem de início. GitHub Actions terá verificações de segurança, testes, migrações e compilação do APK por CI; arquivos de configuração de exemplo podem ser versionados, mas credenciais, keystores, tokens e dados pessoais jamais serão publicados. Segredos via armazenamento protegido/Secrets, permissões mínimas, autenticação forte e rotação. Escolher ferramentas e infraestrutura gratuitas quando viáveis, sem assumir que os limites gratuitos sejam suficientes ou que qualquer conta de nuvem já exista. O backend implementa regras financeiras; o aplicativo não é fonte de verdade de saldos ou autorizações.

**Exemplo de conferência (sem substituir o contrato):** Verificar Termux + GitHub Actions Android sem notebook; jamais instalar SDK duplicado sem razão.

**CONTROLE MANUAL 1.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.9 | Fases de verificação: 0/1

**1.9. Desenvolvimento independente e orçamento inicial — DEFINIDO.** O idealizador realizará pessoalmente planejamento, desenvolvimento, publicação, formalização, requerimentos e atendimento inicial, com assistência das ferramentas citadas; **sem contratação planejada de advogado, contador, programador, consultoria ou servidor pago**. Priorizar documentação própria, tutoriais e canais gratuitos oficiais (Redesim, Sebrae, Receita/NAF, INPI, órgãos competentes). Esta é uma **política de custo mínimo**, não dispensa de tributo, taxa legal, assinatura profissional obrigatória em alguma hipótese, proteção de dados ou exigência de autorização. Qualquer custo obrigatório identificado será apresentado antes de assumir despesa; se inviável, o recurso correspondente não será explorado até solução.

**CONTROLE MANUAL 1.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.10 | Fases de verificação: 0/1

**1.10. Titularidade e estratégia comercial.** O proprietário pretende manter controle da empresa e da propriedade intelectual do código, comercializando **licenças SaaS** aos administradores, com receitas de assinaturas separadas dos recursos dos membros. O posicionamento comercial inicial é “automatizar a caixinha que o administrador já opera manualmente”, sem promessa de rendimentos, segurança regulatória automática ou status bancário. O FRcaixinha é inicialmente empresa/projeto de tecnologia, não “Big Tech” por definição jurídica ou licença.

**CONTROLE MANUAL 1.10:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.11 | Fases de verificação: 0/1

**1.11. Documentos empresariais por estágio.** Antes da exploração comercial efetiva: verificar natureza empresarial elegível (pessoa física para desenvolvimento, Inova Simples experimental se adequado, ou LTDA unipessoal para operação estável), CNAE real, tributos, obrigações contábeis, nota fiscal, eventual licenciamento municipal, CNPJ e conta PJ quando exigidos por lei/fornecedor/contrato. Não escolher MEI por CNAE fictício; não prometer isenção tributária nem supor que CNPJ autorize atividade lotérica ou financeira. Proteção intelectual: pesquisa de disponibilidade e pedido de **marca FRcaixinha**; registro de **software** quando houver versão concreta; patente somente se houver invenção técnica patenteável, nunca por possuir uma ideia abstrata. Os atos serão realizados pelo proprietário quando o serviço oficial aceitar solicitação direta, mantendo lista de requisitos, custos, protocolos e comprovantes.

**CONTROLE MANUAL 1.11:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 1.12 | Fases de verificação: 0/1

**1.12. Plano econômico enxuto.** Fontes de receita aprovadas: licenças mensais/anuais; **possível taxa adicional da plataforma sobre lucros de terceiros permanece EM ESTUDO e desativada**, sem consentimento ou cobrança implícitos. Reservar plano de negócios (custos reais, receitas recorrentes, capacidade, impostos, indicadores, reinvestimento), material de demonstração e marketing honesto e manual passo a passo. Esses entregáveis são documentação comercial, **não** novos módulos bancários ou financeiros.

**CONTROLE MANUAL 1.12:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 2 — Papéis, autonomia, autorização e privacidade


### Cláusula 2.1 | Fases de verificação: 2/5

**2.1. Perfis funcionais — DEFINIDO.** (a) **Master da plataforma:** comercial, licenças, catálogo de funcionalidades, parâmetros **globais de calendário**, disponibilidade, suporte e manutenção; (b) **Administrador contratante:** gestão operacional e financeira **somente de sua caixinha**; (c) **Membro:** consulta e interação com seus direitos e obrigações; (d) **identidade simultânea:** a mesma pessoa pode exercer papéis distintos e ter cotas/membership por tenant e ciclo.

**CONTROLE MANUAL 2.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.2 | Fases de verificação: 2/5

**2.2. Direitos do administrador contratante — DEFINIDO.** Configurar contribuição por membro/cota, juros, limites e condições de crédito, encargos juridicamente permitidos, número de parcelas dentro do horizonte válido, remuneração administrativa sobre resultado elegível, política de entrada e participação, aprovar/rejeitar operações, liberar pagamentos legitimamente autorizados, organizar arrecadação habilitada, fechar o ciclo. Isso é **autonomia administrativa efetiva**, e não permissão para burlar validação financeira ou acessar recursos de outros grupos.

**CONTROLE MANUAL 2.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.3 | Fases de verificação: 2/5

**2.3. Papéis simultâneos e troca de contexto.** A identidade é única, mas a atuação é contextual: `MASTER`, `TENANT_ADMIN`, `TENANT_MEMBER`. Cada ação financeira traz `tenant_id` e `cycle_id` explícitos e exige o papel correspondente. Se o Master for membro ou administrador de sua própria caixinha, atua como **contratante/membro daquele tenant**, com exatamente as mesmas restrições que os demais. O Master não recebe acesso financeiro ampliado aos tenants dos clientes.

**CONTROLE MANUAL 2.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.4 | Fases de verificação: 2/5

**2.4. Administrador também é membro — DEFINIDO.** Pode aderir, adquirir cotas, contribuir, consultar extratos, receber resultados e solicitar empréstimos como qualquer membro. A remuneração de administrador é apurada **separadamente** de sua eventual participação como membro. A participação como membro não justifica tratamento privilegiado de juros, prazo, principal ou priorização patrimonial.

**CONTROLE MANUAL 2.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.5 | Fases de verificação: 2/5

**2.5. Autorização coletiva anual para crédito próprio — DEFINIDO COMO MODELO CONTRATUAL.** No início de cada ciclo anual, todos os demais membros ativos assinam individualmente cláusula específica, expressa e destacada, com validade apenas naquele ciclo, permitindo ao administrador-membro identificado aprovar seus pedidos próprios sem nova coleta por operação. A assinatura do beneficiário não substitui a unanimidade dos demais; ingressantes devem aderir antes de novas operações. O backend verifica a eficácia, unanimidade e versão das assinaturas **na aprovação, na reserva e imediatamente antes do envio Pix**. Se sobrevier revogação eficaz ou ingresso sem anuência depois da aprovação, **não desembolsar**: registrar suspensão/cancelamento motivado da autorização pendente, impedir Pix e liberar reserva apenas após prova de não envio; dívida já efetivamente desembolsada permanece válida conforme o contrato. Nenhuma autorização atravessa o ano. São indispensáveis simulação, contrato, saldo, liquidez e avaliação jurídica de sua eficácia (CC arts. 117 e 119, quando aplicáveis); Master nunca é aprovador substituto.

**Exemplo de conferência (sem substituir o contrato):** Revogação eficaz antes do Pix bloqueia empréstimo próprio ainda não pago.

**CONTROLE MANUAL 2.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.6 | Fases de verificação: 2/5

**2.6. Ausência de outros membros ou falta de unanimidade.** **Não autoriza autoempréstimo**. Não se cria um novo aprovador artificial nem se transfere essa decisão ao Master. Os empréstimos de **outros** membros seguem a decisão do administrador com os controles normais.

**CONTROLE MANUAL 2.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.7 | Fases de verificação: 2/5

**2.7. Transparência aos membros.** Cada membro visualiza **somente seu** contrato, aceite, quantidade de cotas, capital confirmado, contribuições, parcelas/encargos, solicitações, pagamentos, direitos a resultado e comprovantes; pode acompanhar status e questionar divergências por canal de suporte. Demonstrativos coletivos só podem mostrar dados agregados ou de terceiros na extensão contratualmente permitida.

**CONTROLE MANUAL 2.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.8 | Fases de verificação: 2/5

**2.8. Acesso de Master.** Master consulta empresa/conta contratante, identificação de caixinha, quantidade **agregada** de membros/cotas contratados e usados, vigência/licença, arrecadação **própria da plataforma**, saúde técnica e evidências mínimas de conformidade. Não recebe por padrão CPF de membros, contas bancárias, saldo individual, extrato individual, dívida ou poder para fazer Pix de terceiros. Supervisão/fiscalização é **comercial, técnica e de conformidade**, não ingerência patrimonial. Qualquer dado adicional exige hipótese legal e fluxo excepcional da seção 5.

**Exemplo de conferência (sem substituir o contrato):** Master tenta abrir extrato de terceiro: requisição negada no backend.

**CONTROLE MANUAL 2.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 2.9 | Fases de verificação: 2/5

**2.9. Matriz básica de permissões.** Para cada endpoint, combinar identidade ativa + papel + `tenant_id` + `cycle_id` + situação da licença + autorização específica + estado financeiro. Proibir acesso direto por URL/ID de objeto alheio; o backend impõe a regra, independente do que a tela exiba.

| Ação | Master | Admin do tenant | Membro do tenant |
|---|---|---|---|
| Definir preços de licenças/calendário global | Sim | Não | Não |
| Ver totais agregados de capacidade contratada | Sim | Seu tenant | Não |
| Configurar política financeira do tenant | Não | Sim, conforme aceite | Não |
| Ver extratos individuais | Não por padrão | Seu tenant, legitimamente | Somente o próprio |
| Solicitar empréstimo | Se membro, nesse contexto | Se membro, nesse contexto | Sim |
| Aprovar pedido de membro alheio | Não | Sim | Não |
| Aprovar crédito próprio do administrador | Não | Só com autorização coletiva anual eficaz | Não |
| Autorizar Pix financeiro da caixinha | Não | Sim, dentro dos controles | Somente os atos permitidos ao membro |
| Suporte excepcional | Sim, na seção 5 | Conceder/revogar | Não concede acesso geral |

**CONTROLE MANUAL 2.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 3 — Licenciamento, precificação, aceite, renovação e suspensão


### Cláusula 3.1 | Fases de verificação: 3/5

**3.1. Início da contratação e tenant preliminar — APROVADO COMO REQUISITO DOCUMENTAL.** Tela **Quero administrar uma caixinha** → identidade/cadastro comercial restrito → **registro preliminar de oferta/capacidade ou tenant em estado RASCUNHO_INATIVO** → seleção de plano/quantidade de membros e cotas → preço e termos → aceite → Pix da plataforma → confirmação conciliada → licença ATIVA e apenas então permissão para ativar/gerenciar a caixinha. O identificador preliminar pode referenciar `LicenseSubscription.tenant_id`, mas **não** concede visibilidade financeira, capacidade operacional ou acesso de membros antes do pagamento confirmado.

**CONTROLE MANUAL 3.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.1-A | Fases de verificação: 3/5

**3.1-A. Cadastro e identificação do Administrador Contratante — DEFINIDO E APROVADO em 16/10/2026.** O ingresso comercial pela tela **Quero administrar uma caixinha** terá etapas objetivas e acessíveis pelo smartphone, sem exigir informações desnecessárias ou fotografia obrigatória. **Pessoa física:** nome completo e CPF são obrigatórios; e-mail válido e confirmado e telefone com DDD válido são obrigatórios. Endereço de faturamento será coletado quando necessário à contratação, às exigências fiscais ou às condições efetivamente aplicáveis do provedor. **Foto de perfil é opcional** e poderá ser enviada, modificada ou removida posteriormente. **Pessoa jurídica, quando esta modalidade estiver habilitada:** razão social, CNPJ e dados de faturamento necessários, com identificação do representante autorizado (nome completo, CPF, e-mail e telefone), declaração de poderes e comprovação quando exigível. O cadastro pode ser criado em estado preliminar sem licença ativa.

**Exemplo de conferência (sem substituir o contrato):** PF com CPF/e-mail/DDD e foto opcional; endereço fiscal somente quando necessário.

**CONTROLE MANUAL 3.1-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.1-A.1 | Fases de verificação: 3/5

**3.1-A.1. Verificação e segurança.** Backend valida formato e dígitos verificadores de CPF/CNPJ, duplicidades incompatíveis com identidade única, consistência de e-mail/telefone e confirmação do e-mail por fluxo verificável; validação formal de documento **não equivale a prova de titularidade ou poderes de representação**. O telefone será validado e sua posse confirmada quando for usado para autenticação, recuperação ou ato sensível. Credenciais nunca serão armazenadas em texto puro; aplicar hash de senha adequado, autenticação e recuperação controladas, sessões e permissões com escopo, proteção contra automação abusiva, TLS em produção e auditoria minimizada. Uma opção de confirmação não deve presumir contratação de SMS pago sem aprovação de custo.

**CONTROLE MANUAL 3.1-A.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.1-A.2 | Fases de verificação: 3/5

**3.1-A.2. Aceite, identidade e privacidade.** Antes da cobrança, apresentar titular contratante, plano, limites, periodicidade, preço e versão dos documentos, e registrar o aceite eletrônico individual com identidade do signatário, evidência, data/hora, versão e integridade do instrumento conforme 3.5; a validade jurídica e nível de assinatura eletrônica dependem do ato e da lei aplicável. Informação de privacidade deverá explicar finalidade, bases legais, acesso, compartilhamentos necessários, retenção e direitos dos titulares; marketing opcional não poderá ser aceito por presunção. Separar **identidade pessoal (`UserIdentity`)**, **titular/contratante comercial (`ContractingParty`)**, **licença (`LicenseSubscription`)**, **caixinha (`Tenant`)**, **papel administrativo (`RoleGrant`)** e eventual **adesão como membro (`Membership`)**, sem criar privilégios financeiros nem compartilhar dados de terceiros por inferência. O Pix confirmado e conciliado continua sendo indispensável para a ativação da licença; completar cadastro ou aceitar termos não ativa o tenant.

**CONTROLE MANUAL 3.1-A.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.2 | Fases de verificação: 3/5

**3.2. Tabela comercial — DEFINIDA E APROVADA.** Planos com **as mesmas funcionalidades habilitadas**; diferenças somente de limite simultâneo e período. A opção anual equivale a **12 meses de uso pelo preço de 10**, aproximadamente 16,67% de desconto.

| Plano | Capacidade máxima de membros | Capacidade máxima de cotas | Mensal | Anual |
|---|---:|---:|---:|---:|
| Essencial | 20 | 40 | R$ 89,90 | R$ 899,00 |
| Intermediário | 50 | 50 | R$ 109,90 | R$ 1.099,00 |
| Ampliado | Acima de 50 se necessário; **teto pendente** | Acima de 50 se necessário; **teto pendente** | R$ 129,90 | R$ 1.299,00 |

**Exemplo de conferência (sem substituir o contrato):** Plano Essencial 20/40 e Intermediário 50/50; Ampliado não contratável.

**CONTROLE MANUAL 3.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.2-A | Fases de verificação: 3/5

**3.2-A. Preço comercial dinâmico e anual automático — DEFINIDO.** No Painel Master, **somente o valor mensal** de cada plano pode ser editado pelo proprietário da plataforma, sem alteração de código e com registro no banco. O valor anual é **campo calculado de leitura** pela fórmula `preco_anual = 10 × preco_mensal` (12 meses de licença pelo preço de 10). Cada mudança cria `LicensePriceVersion` com valor anterior/novo, autor, data/hora, início de vigência e motivo; nunca sobrescreve oferta aceita nem altera assinatura já paga. Oferta/aceite/Pix armazenam `price_version_id` e preço efetivo imutável. Renovação apresenta tabela vigente e requer novo aceite/pagamento confirmado; não se presume concordância automática com reajuste. Plano Ampliado continua sem checkout até definir teto. Os R$ 899,00 / 1.099,00 / 1.299,00 são resultados iniciais derivados das três mensalidades, não campos editáveis isoladamente.

**Exemplo de conferência (sem substituir o contrato):** De R$ 89,90 para R$ 99,90, anuidade de R$ 899,00 para R$ 999,00; preço antigo intacto.

**CONTROLE MANUAL 3.2-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.2-B | Fases de verificação: 3/5

**3.2-B. Cobrança por resultado das caixinhas — EM ESTUDO, não aprovada.** O proprietário cogitou uma **remuneração adicional pequena sobre o lucro líquido elegível de cada caixinha**, além da assinatura, inspirada no preço de serviços de pagamento. **Não existe percentual, fato gerador, vencimento, base contratual ou débito automático aprovados**. A primeira versão **NÃO COBRA** tal tarifa nem a desconta do dinheiro dos membros. Se futuramente adotada, exigirá desenho contratual aceito previamente, avaliação jurídica/fiscal/financeira e decisão separada sobre faturar ao administrador; **split Pix de uma transação não equivale a calcular percentagem de lucro de ciclo**. Não misturar com os 15%, 20% etc. que cada administrador contrata como remuneração da sua caixinha nem com sua assinatura.

**CONTROLE MANUAL 3.2-B:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.3 | Fases de verificação: 3/5

**3.3. Enquadramento sem lacunas.** Selecionar a **menor faixa que atenda simultaneamente ambos os limites**. Ex.: 20/40 = Essencial; 21/40 ou 15/45 = Intermediário; 50/50 = Intermediário; 40/60 = Ampliado **apenas quando seu teto estiver definido**. O Ampliado **não é ilimitado e não pode ser vendido/ativado** até aprovação expressa de limites máximos de membros e cotas. Nada é contratado acima de capacidade validamente ofertada.

**Exemplo de conferência (sem substituir o contrato):** 40 membros/60 cotas: oferecer apenas se capacidade do Ampliado for futuramente aprovada.

**CONTROLE MANUAL 3.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.4 | Fases de verificação: 3/5

**3.4. Contagem de capacidade — APROVADO COMO REQUISITO DOCUMENTAL.** `membros_em_uso` = pessoas com adesão `ATIVA` no ciclo, contadas uma vez por identidade e tenant; `cotas_em_uso` = cotas `ATIVAS` atribuídas a adesões ativas. Convites pendentes não consomem vaga. Uma pessoa com três cotas utiliza uma vaga de membro e três cotas. Saída regular preserva registros e obrigações; a vaga/cota só se libera após status de saída eficaz, sem permitir apagamento de direitos ainda pendentes. Usuário inadimplente ou com créditos/dívidas não desaparece da contagem por simples comando de exclusão. Entrada/reativação só é aceita se houver capacidade simultânea para ambas as dimensões. Esta é a convenção única da primeira versão.

**Exemplo de conferência (sem substituir o contrato):** 3 cotas da mesma pessoa = 1 membro e 3 cotas.

**CONTROLE MANUAL 3.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.5 | Fases de verificação: 3/5

**3.5. Aceite de licença.** Guardar oferta exibida (identificador, faixa, limites, valor, moeda BRL, duração, versão dos termos, validade e hash do documento), identidade do contratante, data/hora, IP e evidências tecnicamente adequadas, sem supor que simples toque valha como assinatura qualificada para todos os fins. **Não aceitar uma oferta alterada durante o pagamento.**

**CONTROLE MANUAL 3.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.6 | Fases de verificação: 3/5

**3.6. Pagamento de licença.** Criar cobrança Pix na conta legítima da **plataforma**, mostrar QR e Copia e Cola; preço total/valor esperado são imutáveis por tentativa; `PAGO_CONFIRMADO` depende da reconciliação com o provedor, da titularidade/comerciante correto e da correspondência de valor. Webhook isolado ou print do pagador não ativam nada. Idempotência de cobrança e de ativação obrigatória.

**CONTROLE MANUAL 3.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.7 | Fases de verificação: 3/5

**3.7. Vigência mensal/anual — APROVADO COMO REQUISITO DOCUMENTAL.** Licença inicia na confirmação financeira íntegra e vale por 1 ou 12 meses consecutivos, independentemente do ciclo da caixinha; intervalo de validade `[active_from,active_until)`, no fuso `America/Belem`. O sistema conserva o **dia âncora** do início: quando o mês final não tiver esse dia, usa-se o último dia do mês, sem provocar deriva permanente da âncora. Ex.: início dia 31, vencimento em fevereiro no último dia, próxima renovação mantém a âncora 31. Pagamento de renovação confirmado **antes** do vencimento acrescenta o período ao `active_until` vigente, sem eliminar dias pagos. Renovação confirmada **após** o vencimento inicia nova vigência na confirmação; intervalo vencido não é retroativamente autorizado. Sem cobrança recorrente automática na primeira versão; toda renovação exige oferta, aceite e Pix autorizado.

**Exemplo de conferência (sem substituir o contrato):** Pagamento antecipado renova sem perder dias; pagamento após vencimento não autoriza tempo vencido.

**CONTROLE MANUAL 3.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.8 | Fases de verificação: 3/5

**3.8. Tolerância = ZERO DIAS — DEFINIDO.** No exato término da licença paga, se não houver renovação integralmente confirmada, estado `SUSPENSA` **sem prazo de carência**. Suspensão impede **novos** compromissos opcionais (novas adesões/cotas, novos empréstimos/desembolsos, novas ações) e preserva o necessário para **direitos adquiridos e obrigações existentes**: consultar extratos, contribuir/pagar parcelas já devidas, regularizar, concluir operações já legitimamente irreversíveis, conciliar, quitar, apurar e realizar fechamento e pagamentos devidos sob autorização do administrador e controles normais. O modo de contingência não vira licença grátis para atividades novas.

**Exemplo de conferência (sem substituir o contrato):** SUSPENSA sem carência; quitar dívidas antigas continua permitido.

**CONTROLE MANUAL 3.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.9 | Fases de verificação: 3/5

**3.9. Reativação e cobranças revertidas.** Pix confirmado e aceite aplicável reativam o serviço com estado auditável, sem botão de ativação comercial que substitua pagamento. Confirmação posterior ou reversão financeira produz revisão/reconciliação do direito comercial, notificação, oportunidade de regularização e suspensão de **novas** operações se a licença ficar descoberta; jamais apagar obrigações, dados ou Pix legítimos dos membros. A correção de erro do provedor exige provas, e não ajuste manual silencioso. Master pode corrigir falha **técnica comprovada** de reconhecimento de um pagamento já ocorrido, sem criar pagamento fictício.

**CONTROLE MANUAL 3.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.10 | Fases de verificação: 3/5

**3.10. Alteração, cancelamento e reembolso — APROVADO COMO REQUISITO DOCUMENTAL.** (a) Upgrade de mesma periodicidade exige oferta/aceite e Pix da diferença proporcional, com `Decimal` e `ROUND_HALF_UP`. O cálculo usa **cada segmento de vigência já adquirido e não transcorrido**, identificado por `period_start`, `period_end`, preço do plano original pago e versão, na fotografia de tempo (`calculated_at`) que fica gravada na oferta; para cada segmento afetado: `max(0, novo_preco_do_segmento − antigo_preco_pago_do_segmento) × segundos_restantes_do_segmento / segundos_totais_do_segmento`. Somar somente os segmentos elegíveis, evitando cobrar de novo um upgrade já quitado; comparar capacidade já adquirida e manter `active_until` e dia âncora. Renovação antecipada cria segmento futuro próprio: sua diferença, quando houver, é apresentada separadamente e **nunca** calculada como se todo o tempo pré-pago fosse um único mês. A oferta tem validade finita e deve ser recalculada e aceita novamente se expirar antes do pagamento. (b) Downgrade só na próxima renovação e quando membros/cotas couberem na faixa, sem apagar obrigações. (c) Cancelamento impede renovação futura e preserva o acesso pago até o término, salvo resolução legal. (d) Arrependimento, cobrança indevida, reembolso e estorno observam direitos legais e conciliação, sem cláusula de não reembolso absoluto. (e) Ampliação gratuita legítima precisa de autorização comercial registrada, nova oferta/aceite e auditoria, **sem** simular Pix R$ 0.

**CONTROLE MANUAL 3.10:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 3.11 | Fases de verificação: 3/5

**3.11. Separação de receitas.** Licença = receita do Master/plataforma. Capital de membros, recebimentos de empréstimos e remuneração administrativa do administrador contratante = universos distintos. O pagamento da licença **não pode ser tomado do caixa coletivo automaticamente** nem confundido com percentuais de lucros de tenants.

**CONTROLE MANUAL 3.11:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 4 — Autonomia configurável por caixinha e calendário central imutável


### Cláusula 4.1 | Fases de verificação: 2/3

**4.1. Política financeira por tenant — DEFINIDO.** Cada administrador decide, para sua própria caixinha e com ciência/aceite dos integrantes, valor da contribuição/cota, políticas de cobrança, taxa remuneratória, limites de empréstimo, número de parcelas, encargos permitidos, política de aprovação, critérios de adesão, percentuais de divisão de lucro e outras regras legítimas **realmente suportadas pelo software**. Não forçar 20% a.m. ou 85/15 em caixinhas de terceiros.

**CONTROLE MANUAL 4.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.2 | Fases de verificação: 2/3

**4.2. Configuração inaugural da caixinha do proprietário — DEFINIDO.** Modelo próprio do responsável: taxa de **20% a.m.**, amortização **Price**, até **6 parcelas**, multa **R$ 10,00**, mora simples diária de **20%/30** sobre principal vencido e não pago, critérios de elegibilidade/atraso e rateio **85% membros / 15% administrador** nos termos aprovados; obrigações legais sempre prevalecem. Essas configurações não são automaticamente copiadas nem vendidas como imposição global a outros administradores.

**Exemplo de conferência (sem substituir o contrato):** 20% a.m., Price, 6 parcelas e 85/15 apenas para a caixinha do proprietário.

**CONTROLE MANUAL 4.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.3 | Fases de verificação: 2/3

**4.3. Percentual administrativo — DEFINIDO.** Cada contratante escolhe o percentual de remuneração sobre o **lucro líquido realizado e juridicamente elegível**, com exibição prévia aos membros e aceite contratual (exemplos: 15/85, 20/80, 30/70). A soma `percentual_admin + percentual_membros = 100%`. Um percentual não aprovado/ilegal não é aplicável, mesmo que o administrador tente cadastrá-lo. O Master não é beneficiário automático dos percentuais alheios.

**CONTROLE MANUAL 4.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.4 | Fases de verificação: 2/3

**4.4. Vigência das políticas e dos percentuais — DEFINIDO.** Cada caixinha mantém política por tenant/ciclo com autor, versão, aceite, data e motivo. **O percentual de remuneração administrativa (`admin_pct`) e o percentual complementar dos membros (`member_pct`) ficam fixos durante TODO o ciclo financeiro anual.** Mudança solicitada no curso do ano poderá ser formalizada e aceita, mas **somente terá efeitos no ciclo anual seguinte**, sem recalcular resultados nem reduzir direitos constituídos no ciclo atual. Na caixinha do proprietário, permanecem 15% administrador e 85% membros; outros contratantes configuram os próprios percentuais para o ciclo seguinte. Taxas, encargos e condições de novos empréstimos podem ter vigência prospectiva após aceite, sem modificar obrigações já contratadas. Toda mudança mantém trilha auditável; o Master não altera políticas de terceiros.

**Exemplo de conferência (sem substituir o contrato):** Percentual 15% em 2027 não muda para 30% dentro de 2027.

**CONTROLE MANUAL 4.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.5 | Fases de verificação: 2/3

**4.5. CALENDÁRIO FINANCEIRO CENTRAL — DEFINIDO E NÃO EDITÁVEL PELO TENANT.** Para todas as caixinhas, fuso **America/Belem**; início anual **01/01**; término do ciclo e data de referência do fechamento **31/12**; vencimento mensal das contribuições **dia 10**, quando houver obrigação mensal; data central para liquidação elegível do encerramento **10/01 do ano seguinte**, após conciliação. Primeiro ciclo planejado **01/01/2027–31/12/2027**, pagamento final elegível previsto **10/01/2028**. Administrador não altera início, fim, fechamento, vencimento central ou data-alvo final.

**Exemplo de conferência (sem substituir o contrato):** Ciclo 01/01/2027–31/12/2027; vencimentos dia 10; encerramento elegível 10/01/2028.

**CONTROLE MANUAL 4.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.6 | Fases de verificação: 2/3

**4.6. Fases do fechamento sem mudar datas.** Em 31/12 é congelada a base temporal; de 01 a 09/01 seguinte ocorrem conferência, ajustes documentados, auditoria e autorização; 10/01 é a data-alvo de pagamento **se** o valor estiver devido, conciliado e líquido. Operação tecnicamente pendente ou litigiosa **não é marcada como paga**, nem a data-fixa permite antecipar obrigação indevida. Atrasos são exceções formalmente auditadas, não livre alteração de calendário.

**CONTROLE MANUAL 4.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.7 | Fases de verificação: 2/3

**4.7. Entrada após 01/01 e lançamento futuro.** Contratações no meio do ano não deslocam o ciclo global; a participação começa na data real de adesão, sem contribuições anteriores presumidas como pagas, e segue a política aceita. Se o sistema só ficar pronto após uma data planejada, **não gerar eventos retroativos fictícios**: entrada em produção e eventual transição requerem autorização expressa, mantendo a regra de calendário anual central.

**CONTROLE MANUAL 4.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 4.8 | Fases de verificação: 2/3

**4.8. Separação do ciclo e da licença.** O mesmo administrador pode ter licença mensal renovada várias vezes no ciclo financeiro; sua expiração gera a restrição comercial da seção 3 e **não altera a data do fechamento nem os direitos e obrigações dos membros**.

**CONTROLE MANUAL 4.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 5 — Suporte, manutenção e acesso excepcional sem ingerência


### Cláusula 5.1 | Fases de verificação: 6

**5.1. Atendimento normal.** Master presta suporte por métricas técnicas, status de licenças, identificadores de falha e logs minimizados, sem navegar pelos cadastros, extratos e dados pessoais dos membros de outra caixinha.

**CONTROLE MANUAL 5.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 5.2 | Fases de verificação: 6

**5.2. Acesso excepcional consentido.** Apenas diante de incidente específico e autorização expressa do administrador contratante: `tenant_id`, finalidade, motivo, recurso permitido, identidade do técnico, prazo finito, autorização, início e expiração. Acesso se encerra por término, revogação ou expiração — **o que ocorrer primeiro**. Revogação deve invalidar sessões em andamento e impedir novas chamadas.

**CONTROLE MANUAL 5.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 5.3 | Fases de verificação: 6

**5.3. Prazo e gatilhos de suporte — APROVADO COMO REQUISITO DOCUMENTAL.** Acesso excepcional normal: **até 60 minutos por autorização**, apenas aos recursos essenciais ao chamado, com renovação somente por novo consentimento expresso. Acesso de contingência (*break-glass*): **até 30 minutos**, exclusivamente diante de incidente crítico comprovado que impeça a autorização normal, como comprometimento ativo de segurança, risco imediato de perda de dados, falha de integridade financeira ou indisponibilidade grave que ameace continuidade. Exigir justificativa, autenticação forte, elevação mínima, auditoria inviolável, aviso ao administrador assim que viável e revogação imediata após a solução; nenhuma elevação concede permissão para Pix ou aprovação financeira. Novas emergências exigem justificativa independente; a duração não se renova automaticamente.

**Exemplo de conferência (sem substituir o contrato):** Suporte excepcional 60 min / emergencial 30 min, expira e revoga imediatamente.

**CONTROLE MANUAL 5.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 5.4 | Fases de verificação: 6

**5.4. Vedações invariáveis.** Nenhum acesso técnico autoriza Master a aprovar empréstimo, escolher mutuário, liberar Pix, alterar arbitrariamente saldo, mudar rateio ou recolher patrimônio de terceiro. Correção financeira exige trilha contábil de compensação, prova, justificativa, autorização do legítimo responsável e conciliação; alteração silenciosa de linha original é proibida.

**CONTROLE MANUAL 5.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 5.5 | Fases de verificação: 6

**5.5. Operação da manutenção.** Monitorar disponibilidade da API, banco, confirmação Pix, alertas de segurança e status de backup; registrar incidente → diagnosticar sem dados pessoais sempre que possível → autorizar acesso pontual se necessário → corrigir a causa → testar → publicar versão autorizada e reversível → confirmar recuperação → encerrar com evidências. Custos de nova infraestrutura ou serviços pagos exigem autorização específica.

**CONTROLE MANUAL 5.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 6 — Membros, cotas, contribuições e inadimplência


### Cláusula 6.1 | Fases de verificação: 2/3/5

**6.1. Adesão.** Administrador cria convite nominal, disponibiliza contrato/política do ciclo e aceite, identifica membro e associa cotas respeitando simultaneamente capacidade contratada. Convidado não tem acesso financeiro enquanto não aceito/autenticado. Mudança de papel não modifica titularidade de cotas. A adesão deve informar contribuição, juros, remuneração do administrador e direitos de encerramento conforme a política vigente.

**CONTROLE MANUAL 6.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.1-A | Fases de verificação: 2/3/5

**6.1-A. Cadastro e identificação do Membro — DEFINIDO E APROVADO em 16/10/2026.** A adesão é feita **somente por convite nominal do administrador legítimo daquela caixinha**. O convidado pode criar identidade pessoal única ou autenticar-se com identidade existente na plataforma, sem ganhar acesso a outros grupos. Campos obrigatórios do membro pessoa física: **nome completo, CPF, e-mail válido com confirmação e telefone com DDD válido**; CPF com verificação de dígitos e tratamento seguro de duplicidade, e telefone validado com confirmação de posse quando utilizado para recuperação/autenticação ou ato sensível. **Foto de perfil é opcional**, alterável/removível; **endereço será solicitado apenas quando exigido para a operação, documentação, identificação legal ou provedor**, sem presumir obrigatoriedade de endereço residencial. Chave Pix e dados bancários não serão exigidos antecipadamente: somente quando necessários a operação legitimamente habilitada, com confirmação de titularidade/destinatário conforme regras financeiras e de provedor. A validação cadastral formal não comprova sozinha a identidade real de uma pessoa.

**Exemplo de conferência (sem substituir o contrato):** Convidado sem aceite não acessa extrato; CPF único e foto removível.

**CONTROLE MANUAL 6.1-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.1-A.1 | Fases de verificação: 2/3/5

**6.1-A.1. Aceite e liberação de acesso.** O membro deverá visualizar a caixinha específica, responsável, ciclo, quantidade/valor de cotas e contribuições, taxas e sistema de empréstimo aplicáveis, percentuais administrativos e dos membros, regras de inadimplência, direitos de encerramento, política de privacidade e instrumentos pertinentes **na versão vigente**. Somente após autenticação, aceite eletrônico individual verificável e aprovação/ativação da adesão conforme política aceita poderá acessar o próprio painel financeiro. Convite pendente não concede visibilidade financeira nem ocupa capacidade até adesão ativa conforme 3.4. Conservar versão/hash do instrumento, prova do aceite, autor, instante, escopo `tenant_id/cycle_id` e histórico de revogação/correção conforme o ato.

**CONTROLE MANUAL 6.1-A.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.1-A.2 | Fases de verificação: 2/3/5

**6.1-A.2. Identidade única, cotas, privacidade e isolamento.** Uma mesma pessoa pode ser membro de mais de uma caixinha, ou também administradora, mediante papéis explícitos e vínculos `Membership` independentes por caixinha e ciclo. É proibida a duplicação de identidade para contornar limites, bloqueios ou direitos, e a troca de contexto jamais expõe contratos, documentos, dívidas, saldo, CPF ou extratos de outro tenant. O administrador visualiza apenas os dados necessários dos membros de sua caixinha para sua gestão legítima; o Master não acessa cadastros pessoais de membros por padrão. Aplicar LGPD, autenticação segura, minimização, permissões de backend e proteção contra edição/exclusão que destrua histórico financeiro. O cadastro não altera os requisitos da autorização coletiva anual para eventual crédito próprio do administrador-membro.

**CONTROLE MANUAL 6.1-A.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.2 | Fases de verificação: 2/3/5

**6.2. Capital e cotas.** Cada cota tem titular e ciclo; membro pode deter múltiplas cotas. Capital próprio reconhecido = **pagamentos efetivamente confirmados e conciliados**, ajustados por restituições e reversões comprovadas. Boleto/QR gerado, transferência alegada, prazo vencido ou promessa não equivalem a capital recebido.

**CONTROLE MANUAL 6.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.3 | Fases de verificação: 2/3/5

**6.3. Contribuições.** Valor/quantidade são definidos pelo administrador nos termos aceitos; quando contribuição for mensal, vencerá no **dia 10 central**. Backend gera obrigação e cobrança identificável; suporta pagamento parcial; confirma Pix com vínculo a obrigação; emite comprovante, saldo aberto e extrato. Manter status do pagamento **separado** do status temporal: um débito pode estar `PARCIAL` e `VENCIDO` ao mesmo tempo.

**Exemplo de conferência (sem substituir o contrato):** Pagamento parcial e vencido tem dois estados simultâneos.

**CONTROLE MANUAL 6.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.4 | Fases de verificação: 2/3/5

**6.4. Estados.** Financeiro: `PENDENTE`, `PARCIAL`, `QUITADA`, `REVERTIDA`, `CANCELADA_JUSTIFICADA`; temporal: `A_VENCER`, `VENCIDA`, `REGULARIZADA`. A sequência de eventos conserva pagamentos parciais, estornos e comprovantes sem apagar histórico. Uma obrigação quitada depois do vencimento continua com histórico do atraso.

**CONTROLE MANUAL 6.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.5 | Fases de verificação: 2/3/5

**6.5. Regra específica da caixinha do proprietário — DEFINIDO, sujeita à validação jurídica antes da execução real.** **Três contribuições mensais consecutivas vencidas e não quitadas** ocasionam bloqueio definitivo do membro **para participação no lucro daquele ciclo completo**: o peso Capital-Dias V2 do ciclo passa a **zero integralmente**, não apenas nos dias posteriores ao gatilho, e a parcela é redistribuída aos demais elegíveis. A prova do gatilho preserva as três obrigações, datas, conciliações e eventual regularização posterior; esta não restabelece automaticamente o rateio naquele ciclo. O principal comprovadamente pago continua apurável para restituição no encerramento, abatidas exclusivamente obrigações legitimamente devidas e documentadas. Saída regular de membro adimplente preserva os direitos adquiridos. **Esta consequência não é regra universal dos tenants contratantes**; cada administrador define sua política juridicamente permitida, versionada e aceita.

**Exemplo de conferência (sem substituir o contrato):** Após três contribuições consecutivas não quitadas, efeito particular no lucro só se juridicamente permitido; principal continua devolvível.

**CONTROLE MANUAL 6.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 6.6 | Fases de verificação: 2/3/5

**6.6. Proibição de confisco e exclusão indevida.** Bloquear novas operações por inadimplência não autoriza apagar pagamentos, recolher principal sem base, alterar retroativamente direitos ou exibir lucro não realizado. Se a regra da caixinha for juridicamente questionável, ela não deve ser executada automaticamente enquanto a questão necessária não estiver resolvida.

**CONTROLE MANUAL 6.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 7 — Caixa da Caixinha, ledger, saldo disponível e conciliação


### Cláusula 7.1 | Fases de verificação: 3/4

**7.1. Segregação.** Conta/caixa lógico separado por `tenant_id + cycle_id`; contratos, cotas, capital, empréstimos, resultados e contas bancárias associadas não se misturam entre caixinhas nem com a conta de receita da plataforma. Caso a conexão financeira de um cliente não permita segregação adequada, a funcionalidade financeira permanece indisponível até correção.

**CONTROLE MANUAL 7.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 7.2 | Fases de verificação: 3/4

**7.2. Ledger autoritativo.** Contabilidade em **centavos exatos**, contas e partidas dobradas equilibradas (`Σ débitos = Σ créditos` por transação), com ligação ao evento de negócio (`payment_id`, `loan_id`, `distribution_id`, etc.) e conciliação ao provedor externo. Não editar/apagar lançamento confirmado: utilizar estorno ou ajuste compensatório rastreável. Saldo exibido deriva de eventos conciliados, não de campo manual independente que possa divergir.

**Exemplo de conferência (sem substituir o contrato):** Toda entrada/saída confirma partidas dobradas e não admite “editar saldo” manualmente.

**CONTROLE MANUAL 7.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 7.3 | Fases de verificação: 3/4

**7.3. Diferenciar saldos e evitar dupla dedução.** `capital_confirmado` = contribuições reconciliadas menos restituições/reversões; `caixa_financeiro` = dinheiro conciliado na conta legítima do tenant; `saldo_devedor` = principal de empréstimos e encargos exigíveis discriminados. `caixa_livre = caixa_financeiro − soma(obrigações financeiras comprometidas e ainda não liquidadas)`; cada compromisso tem `obligation_id`/`reservation_id` lógico único e é abatido **uma única vez**, mesmo quando aparece simultaneamente como RESERVA e PAGAMENTO_EXIGIVEL. Desembolso confirmado consome a reserva e a baixa corretamente; falha comprovada libera a reserva. **Caixa total nunca equivale ao dinheiro livre para novos empréstimos.**

**CONTROLE MANUAL 7.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 7.4 | Fases de verificação: 3/4

**7.4. Concorrência.** Ao aprovar e tentar desembolsar, registrar reserva atômica com identificador estável; duas solicitações simultâneas não podem gastar a mesma disponibilidade. Pix com resposta ambígua fica `PENDENTE_CONCILIACAO`; consultar o provedor antes de qualquer nova tentativa. Reserva só se libera por cancelamento comprovado ou resolução conciliante.

**Exemplo de conferência (sem substituir o contrato):** Duas aprovações simultâneas não comprometem a mesma disponibilidade.

**CONTROLE MANUAL 7.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 7.5 | Fases de verificação: 3/4

**7.5. Controle de integridade.** Reconciliar obrigatoriamente saldos do banco, contas internas, pagamentos confirmados e estado de Pix. Eventos ausentes geram fila controlada de conferência/reprocessamento idempotente; não criar saldo fictício nem marcar operação concluída antes da prova externa.

**CONTROLE MANUAL 7.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 7.6 | Fases de verificação: 3/4

**7.6. Fronteira regulatória entre livro e custódia — CONSOLIDADO.** `LedgerAccount` é conta contábil interna e **não** conta de depósito ou de pagamento emitida pelo FRcaixinha. Registrar: instituição custodiante, identificador da conta externa autorizada, titulares legítimos, contrato/mandato quando cabível, conciliação com extrato do provedor e tratamento de transações pendentes. Direitos dos membros nunca nascem apenas de saldo mostrado na interface sem lastro e prova. Para evolução futura, nenhum campo de negócio deve assumir `mercado_pago` como única instituição possível; a ligação com o provedor ocorre via adaptador e IDs externos versionados.

**CONTROLE MANUAL 7.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 8 — Empréstimos internos parametrizados, autorização e recebimento


### Cláusula 8.1 | Fases de verificação: 3/4/5

**8.1. Exclusividade interna.** Somente membros regulares daquela caixinha podem pedir crédito interno. **Não há empréstimos a terceiros não membros no escopo inicial.** O administrador decide se empresta, a quem empresta e em que termos configurados, sem pedir autorização financeira ao Master e sem poder ultrapassar os limites legais e a liquidez real.

**CONTROLE MANUAL 8.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.2 | Fases de verificação: 3/4/5

**8.2. Parametrização financeira na primeira entrega — APROVADO COMO REQUISITO DOCUMENTAL.** Cada administrador fixa a taxa periódica contratual, número de parcelas, valores, limites e encargos juridicamente admitidos, dentro das capacidades documentadas do motor. O **único sistema de amortização implementado na primeira entrega será Price**, com taxa decimal contratada e de **1 a 12 parcelas mensais**, desde que todos os vencimentos caibam no ciclo anual e que o contrato aceito não imponha número inferior. Assim, a caixinha particular do proprietário continua com **máximo de 6 parcelas e 20% a.m.**, sem criar obrigação igual para outros clientes. Se a data de adesão deixar menos vencimentos mensais no ciclo, o aplicativo oferecerá somente as parcelas compatíveis. Outros regimes de amortização ou prazos que ultrapassem o ciclo são extensões futuras, não mudanças silenciosas do motor. Taxas/encargos ilegais não devem ser habilitados.

**CONTROLE MANUAL 8.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.3 | Fases de verificação: 3/4/5

**8.3. Elegibilidade e limites verificáveis.** Conferir membro ativo, política e aceite vigentes, principal e destinatário, simulação obrigatória, impedimentos, exposição, conta externa e caixa livre. Na caixinha do proprietário, o pedido de empréstimo é condicionado ao **saldo próprio disponível confirmado** e à inexistência de outro empréstimo impeditivo, respeitando as regras específicas pactuadas; contribuições prometidas ou não conciliadas não geram garantia de saldo. Demais tenants podem parametrizar limites juridicamente permitidos. **Não criar limite numérico ou multiplicador que não esteja documentado e aceito; qualquer regra de cálculo individual sem redação recuperável deverá ser explicitada antes da implementação do respectivo crédito real ou simulado como contrato de negócio.**

**CONTROLE MANUAL 8.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.4 | Fases de verificação: 3/4/5

**8.4. Simulação obrigatória e datas.** Antes do pedido, exibir principal, taxa (unidade mensal), número de parcelas, amortização Price, cronograma, juros e principal por prestação, encargos, total, versão da política e consentimento. **DEFINIDO: o primeiro vencimento será no dia 10 do mês seguinte à efetiva liberação CONFIRMADA do empréstimo; os demais vencimentos ocorrerão todo dia 10 dos meses seguintes.** Empréstimo cujo primeiro vencimento ou última parcela ultrapasse 31/12 do ciclo será recusado ou terá prazo ajustado em nova simulação, com aceite. **O primeiro intervalo é de dias corridos efetivos entre a data local da liberação confirmada e a primeira data de vencimento**, sem contar duas vezes qualquer dia. Somente o primeiro período receberá proporcionalidade de `dias_corridos/30`; cada período mensal posterior aplica a taxa mensal pactuada. A simulação e a obrigação conservam todas as datas e a versão de taxa aceita; nenhuma modificação posterior as altera retroativamente.

**Exemplo de conferência (sem substituir o contrato):** Pix confirmado 28/02: vencimento 10/03 com juros proporcionais aos dias reais/30.

**CONTROLE MANUAL 8.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.5 | Fases de verificação: 3/4/5

**8.5. Price com primeiro período irregular — DEFINIDO.** Para principal `PV`, taxa contratual mensal decimal `i` e `n` parcelas, a taxa do primeiro período é `i_1 = i × dias_corridos_primeiro_periodo/30`; para `k = 2,...,n`, `i_k = i`. Calcular prestação uniforme pela equivalência financeira: `PMT = PV / Σ_{j=1..n}[1 / Π_{k=1..j}(1+i_k)]`; em primeiro intervalo convencional de 30 dias, equivale a `PV × i/(1−(1+i)^(-n))`, ou `PV/n` quando taxa zero. Em cada vencimento: `juros_k = saldo_anterior × i_k`, `amortizacao_k = prestacao_k − juros_k`, `saldo_novo = saldo_anterior − amortizacao_k`. Calcular internamente com Decimal, arredondar valores monetários por `ROUND_HALF_UP` conforme a política e corrigir **apenas a última parcela** por centavos para zerar o saldo devido. A prestação inicial e as intermediárias terão valores iguais no centavo, salvo o ajuste final. Se o calendário produzir prestação inferior aos juros ou amortização negativa, bloquear e exigir nova simulação/condições válidas; nenhuma parcela vence após o fim do ciclo.

**Exemplo de conferência (sem substituir o contrato):** A primeira taxa usa dias reais, outras taxa mensal; última parcela ajusta centavos.

**CONTROLE MANUAL 8.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.6 | Fases de verificação: 3/4/5

**8.6. Atrasos, imputação parcial e quitação — DEFINIDO.** Cada caixinha define apenas encargos legalmente admitidos, previamente contratados e auditáveis. Na caixinha do proprietário, **multa única de R$ 10 por parcela/obrigação vencida não quitada**, lançada uma vez no primeiro dia de atraso, sem reaplicação por dia; mora **simples diária de `20%/30` sobre o principal vencido ainda não pago**, sem capitalização, contando dias civis a partir do dia seguinte ao vencimento. **Ordem obrigatória para pagamentos parciais confirmados e conciliados:** primeiro a **parcela vencida mais antiga**; dentro dela, (1) **juros remuneratórios vencidos**, (2) **mora simples já acumulada**, (3) **multa única exigível**, (4) **principal vencido**; avançar às próximas obrigações somente quando os componentes exigíveis anteriores estiverem quitados. Cada recebimento discrimina e grava `paid_interest`, `paid_mora`, `paid_fine`, `paid_principal` ou lançamentos tipificados equivalentes. A base da mora futura diminui **somente no valor efetivamente imputado ao principal**, a partir da data de confirmação/efetividade aplicável, preservando os encargos vencidos. Não cobrar mora sobre multa, mora ou juros vencidos. Quitação antecipada paga principal aberto e encargos já vencidos legitimamente exigíveis, **sem juros futuros não incorridos**, com demonstrativo e conciliação obrigatórios; efeitos de pagamento/reversão são não destrutivos.

**Exemplo de conferência (sem substituir o contrato):** Pagamento parcial: juros → mora → multa → principal da parcela vencida mais antiga.

**CONTROLE MANUAL 8.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.7 | Fases de verificação: 3/4/5

**8.7. Aprovação.** Membro pede → backend simula e valida → administrador recebe e decide (`APROVADO`/`REJEITADO`) → empréstimo aprovado reserva disponibilidade → administrador aciona **Liberar empréstimo via Pix** → confirmação externa → `DESEMBOLSADO`. Decisão comercial do administrador não substitui integridade, existência de dinheiro ou aceites. O Master não figura como aprovador.

**CONTROLE MANUAL 8.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.8 | Fases de verificação: 3/4/5

**8.8. Empréstimo do administrador-membro.** Uma autorização coletiva anual unânime, registrada por ciclo e identificando o administrador, permite autoaprovação sob os mesmos parâmetros dos demais membros, sem consulta ao Master ou votos por parcela. Revalidar unanimidade e revogação **antes de aprovar, reservar e executar o Pix**; um pedido aprovado, mas ainda não desembolsado, **perde autorização executiva** diante de revogação eficaz ou novo membro não anuente. Registrar motivo e sustar liberação; não enviar Pix nem conceder direito financeiro com base em consentimento inválido. Empréstimo já desembolsado mantém direitos e obrigações originalmente constituídos. A avaliação jurídica específica é condição de operação real.

**Exemplo de conferência (sem substituir o contrato):** Novo membro sem anuência bloqueia crédito próprio do administrador antes do Pix.

**CONTROLE MANUAL 8.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 8.9 | Fases de verificação: 3/4/5

**8.9. Proibição de fechamento indevido.** Empréstimos não quitados no encerramento entram na apuração de obrigações e direitos conforme políticas e lei; não apagar dívida, forçar lucro com juro futuro ou gerar Pix de resultado sem liquidez. Parcelamento deve respeitar limites do ciclo e a regra de inadimplência aplicável àquele contrato.

**CONTROLE MANUAL 8.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 9 — Pix integrado, estados transacionais e pagamentos do ciclo


### Cláusula 9.1 | Fases de verificação: 4

**9.1. Contas e finalidade.** Há pelo menos dois domínios financeiros completamente separados: (i) **plataforma Master**, que cobra licenças; (ii) **conta conectada da caixinha**, usada para contribuições, cobranças internas, empréstimos e liquidação de resultados autorizada. Conta MP de um tenant nunca substitui conta de outro; identificadores do pagador/destinatário são validados na operação.

**CONTROLE MANUAL 9.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.2 | Fases de verificação: 4

**9.2. Integração escolhida.** Backend FastAPI → Mercado Pago, com conexão autorizada dos administradores (OAuth/Connect, quando disponível e homologado), notificações autenticadas, identificação durável de cobrança, consulta autoritativa de status e Pix de saída integrado. A viabilidade de cada endpoint/capacidade deve ser testada **na nova implementação** antes de promessa comercial. Acesso e tokens nunca são colocados em código Flutter ou logs.

**CONTROLE MANUAL 9.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.3 | Fases de verificação: 4

**9.3. Recebimento.** Gerar Pix associado à obrigação exata (`type`, `tenant_id`, `member_id`, `payment_id`, valor esperado, vencimento, versão dos termos). Exibir QR Code e Pix Copia e Cola. Pagamento só produz capital, quitação ou licença ativa depois de **confirmação confiável do provedor + conciliação com a obrigação e o recebedor corretos**; webhook isolado/print não bastam. Não contabilizar valor em duplicidade se chegarem notificações repetidas, atrasadas ou fora de ordem.

**CONTROLE MANUAL 9.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.4 | Fases de verificação: 4

**9.4. Saída, autorização e idempotência.** Aprovação legítima gera **uma só obrigação de desembolso e uma única reserva lógica** vinculada ao `loan_id` e `tenant_id`. Antes do envio, revalidar consentimentos aplicáveis, autorização, reserva, disponibilidade e estado da operação. Acionar **Liberar empréstimo via Pix** gera `business_operation_id` estável; todas as tentativas/consultas e chaves técnicas se vinculam a essa mesma operação econômica. Novo identificador técnico jamais autoriza novo desembolso do mesmo direito. Estado `PENDENTE_CONCILIACAO` diante de timeout/ambiguidade, até consulta autoritativa; estados `SOLICITADO`, `RESERVADO`, `ENVIADO`, `PENDENTE_CONCILIACAO`, `CONFIRMADO`, `FALHOU`, `CANCELADO_COMPROVADO`, mapeados ao provedor e auditados.

**Exemplo de conferência (sem substituir o contrato):** Timeout não gera segundo Pix; confirmar status externo primeiro.

**CONTROLE MANUAL 9.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.5 | Fases de verificação: 4

**9.5. Reversão ou falha.** Pagamento confirmado revertido exige contrapartida financeira, atualização de obrigação e trilha de razão, nunca exclusão do evento original. Em operação de saída ambígua, primeiro consultar o provedor e os identificadores externos; somente após comprovação de não execução admitir nova tentativa com protocolo correto.

**CONTROLE MANUAL 9.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.6 | Fases de verificação: 4

**9.6. Fechamento.** O administrador legítimo da caixinha verifica relatório, despesas elegíveis, capital a devolver, resultados a distribuir e conta dos beneficiários; autoriza Pix pelo aplicativo. Cada pagamento tem destinatário, valor, `distribution_id`, `external_id`, prova e estado. Regra central do dia 10/01 não dispensa confirmação nem pagamento regular já exigível durante eventual suspensão comercial da licença.

**CONTROLE MANUAL 9.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.7 | Fases de verificação: 4

**9.7. Bolões.** Cobranças relacionadas a apostas/cotas **NÃO estão habilitadas**; mesmo a documentação da categoria lotérica em um provedor não equivale a autorização comercial. A seção 14 define os pré-requisitos legais e a aprovação escrita do processador antes de introduzir qualquer Pix nessa finalidade.

**CONTROLE MANUAL 9.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.8 | Fases de verificação: 4

**9.8. Verificações mínimas.** Testar mesmo webhook 10 vezes, entrega fora de ordem, valor divergente, ID de comerciante alheio, conta desconectada, duas aprovações concorrentes, timeout após provedor aceitar, saldo insuficiente e restauração de banco anterior ao pagamento. Resultado esperado: **um único efeito econômico real**, com reconciliação verificável.

**Exemplo de conferência (sem substituir o contrato):** Repetir webhook dez vezes: um único efeito econômico.

**CONTROLE MANUAL 9.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.8-A | Fases de verificação: 4

**9.8-A. Interfaces estáveis de integração para futura migração — CONSOLIDADO.** O backend terá contratos internos mínimos `PaymentCollectionPort` (cobrança), `PaymentDisbursementPort` (ordem de saída), `ProviderReconciliationPort` (consulta e eventos), `ExternalAccountPort` (conta/titularidade) e `EvidenceStorePort` (comprovantes). Implementação inicial: adaptadores autorizados do Mercado Pago e simuladores locais determinísticos com **bloqueio absoluto de dinheiro real em ambiente DEMO/TEST**. As regras de negócio de dívida, cotas, resultado e licença não dependem de payload particular do provedor; converter estados externos em eventos de domínio auditáveis. Novos provedores/banking-as-a-service futuros dependem de contrato, homologação e segurança próprios; não há troca automática de banco por alteração de configuração.

**CONTROLE MANUAL 9.8-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 9.9 | Fases de verificação: 4

**9.9. Ambientes e liberação por finalidade — APROVADO COMO REQUISITO DOCUMENTAL.** `DEMO`, `HOMOLOGACAO` e `PRODUCAO` possuem dados, credenciais, contas e permissões isolados; backend barra irrevogavelmente dinheiro real em DEMO/HOMOLOGACAO. Toda capacidade regulada progride por `ESPECIFICADA`, `IMPLEMENTADA_DEMO`, `TESTADA`, `DOSSIÊ_PRONTO`, `AUTORIZADA_PARA_PRODUCAO` e `ATIVA`, **sem pular validações**. `RegulatedCapability` conserva prova, autoridade/contraparte, versão, **finalidade exata**, ambiente, titular da conta/tenant, limites, período de vigência, revogação e condições técnicas. A cada transação verificar se a autorização continua válida, tem escopo correspondente e o provedor está apto; **expiração/revogação suspende novas operações da finalidade afetada**, preservando reconciliação, direitos adquiridos e saneamento. Simulador não conta como homologação técnica externa.

**CONTROLE MANUAL 9.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 10 — Resultado realizado, rateio variável e encerramento anual


### Cláusula 10.1 | Fases de verificação: 3/4/7

**10.1. Formação da base e corte de realização.** Distribuível = receitas **efetivamente recebidas e conciliadas** com fato gerador e competência comprovados dentro do ciclo, menos despesas legitimamente reconhecidas, comprovadas e aceitas, perdas e ajustes admitidos, excluídos principal, cobranças ainda não pagas, juros futuros, valores de outros tenants e prêmios lotéricos alheios. **O instante contábil de reconhecimento, o instante financeiro de confirmação e a data de competência são preservados separadamente.** Valor recebido após 31/12 não será silenciosamente acrescido a snapshot já aprovado: se comprovar correção de evento anterior, abrir revisão auditada e excepcional antes do fechamento definitivo; se for evento novo, atribuir ao período próprio. Resultado não positivo gera parcela de lucro distribuível **zero**, sem distribuir principal como lucro nem presumir cobertura de perda por terceiros.

**CONTROLE MANUAL 10.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.2 | Fases de verificação: 3/4/7

**10.2. Percentuais por caixinha — DEFINIDO.** `admin_pct` é ajustado pelo administrador e aceito pelos membros; `member_pct = 100 − admin_pct`. Na caixinha do proprietário `admin_pct = 15`, `member_pct = 85`. Em outros tenants 20/80 ou 30/70 são **exemplos**, não valores impostos. Todos os percentuais incidem sobre **o mesmo lucro líquido elegível**, e não sobre capital total ou dinheiro de empréstimo.

**CONTROLE MANUAL 10.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.3 | Fases de verificação: 3/4/7

**10.3. Rateio Capital-Dias V2 — motor comum, com corte diário aprovado.** Para membro `i`, `W_i = Σ_d(C_i,d × E_i,d)`; `C_i,d` = capital próprio confirmado, corrigido por restituições/reversões e reconhecido no dia local `d`; `E_i,d ∈ {0,1}` = elegibilidade do ciclo conforme regras aceitas; período anual `[01/01,01/01 seguinte)` em `America/Belem`. A **convenção técnica aprovada** é usar o estado conciliado ao **fim do dia civil local**; eventos de confirmação, reversão ou saída que ocorram no próprio dia afetam o capital a partir desse fechamento diário, e não criam peso em dias anteriores. O histórico de efetividade de cada evento permite recomposição verificável; correções tardias exigem revisão documentada antes de snapshot definitivo. **Exceção da caixinha do proprietário:** três contribuições consecutivas não quitadas ocasionam `E_i,d = 0` para **todos** os dias do ciclo, em conformidade com 6.5, se juridicamente válida. `R_i = R_membros × W_i/ΣW`; se `ΣW=0`, bloquear distribuição e registrar apuração pendente. Algoritmo comum, percentuais e elegibilidade específicos por tenant. **Corte diário aprovado, sem modificar a fórmula contratual do Capital-Dias V2.**

**Exemplo de conferência (sem substituir o contrato):** Capital-Dias conta capital conciliado ao fim do dia em America/Belem.

**CONTROLE MANUAL 10.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.4 | Fases de verificação: 3/4/7

**10.4. Rateio, precisão e destino definitivo dos centavos — DEFINIDO.** Apurar o lucro líquido elegível e dividir primeiro os montantes devidos ao administrador e ao conjunto dos membros segundo os percentuais **fixos para o ciclo** (soma 100%). Calcular os direitos individuais dos membros pelo Capital-Dias V2 com `Decimal`, **truncar cada quota ao centavo** e registrar provisoriamente a diferença na **Carteira Administrativa TÉCNICA e segregada**, sem reconhecê-la como remuneração do administrador, do Master ou lucro adicional. **Distribuir integralmente os centavos residuais aos membros elegíveis pelo método dos maiores restos:** ordenar as frações decimais descartadas do direito exato, atribuir um centavo adicional por vez aos maiores restos até esgotar a diferença; empates são resolvidos por identificador estável de participação (`membership_id`) em ordem ascendente, com trilha auditável. O ajuste integra o **pagamento normal de fechamento**, não gera Pix separado de centavos, e a carteira técnica é baixada integralmente após as atribuições. Total dos valores distribuídos e dos direitos/obrigações reconhecidos deve fechar ao centavo, sem transferência indevida de resíduos a quem não tem direito. Se não houver membros elegíveis (`ΣW = 0`), suspender a distribuição e manter o montante segregado como obrigação pendente, sem apropriá-lo ao administrador.

**Exemplo de conferência (sem substituir o contrato):** Resíduo por maiores restos, desempate membership_id; nunca vira receita do administrador.

**CONTROLE MANUAL 10.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.5 | Fases de verificação: 3/4/7

**10.5. Distinguir administrador como beneficiário duplo.** Se for membro elegível, recebe **sua participação proporcional como membro** e, em conta contábil/linha separada, a remuneração administrativa configurada para sua caixinha. É proibido contar duas vezes a mesma parcela. Master só recebe remuneração de administração se ele próprio for administrador legítimo daquela caixinha; sua receita de licenças sempre é outra conta.

**CONTROLE MANUAL 10.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.6 | Fases de verificação: 3/4/7

**10.6. Fechamento anual e obrigações remanescentes.** Na referência de 31/12 congelar a base temporal e guardar movimentos com trilha própria; de 01 a 09/01 conferir contribuições, principal devolvível, encargos, recibos, recursos reservados, perdas, despesas elegíveis, percentuais do tenant, Capital-Dias e centavos. Gerar snapshot que classifica separadamente **principal a devolver, lucro de membros, remuneração do administrador, resíduo técnico, valores contestados e reservas**. Em 10/01 iniciar Pix idempotente **somente dos itens líquidos, conciliados e legitimamente autorizados**. Estado `EM_APURACAO` enquanto faltam documentos; `APROVADO_PARA_LIQUIDACAO` após reconciliação; `PENDENTE_LIQUIDACAO` quando ainda existirem reservas, obrigações exigíveis ou Pix não conclusos; **`FECHADO` somente quando todos os direitos e débitos estiverem pagos, compensados, reservados com destinação legal expressa ou formalmente solucionados e conciliados**. Recursos ainda comprometidos com o ciclo encerrado permanecem **segregados por seu `cycle_id`**, mesmo quando o próximo ciclo já estiver aberto; proibir dupla contagem no caixa livre. Receitas após 31/12 seguem 10.1, sem reconhecimento retroativo silencioso. Resultado líquido não positivo **não gera rateio de lucros**. Nenhuma pendência altera a data global.

**CONTROLE MANUAL 10.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.7 | Fases de verificação: 3/4/7

**10.7. Documentos e conferência.** Demonstrativo individual com capital confirmado, cotas, aportes/devoluções, obrigações, amortizações, juros realizados, encargos, peso Capital-Dias, participação do lucro, resíduos técnicos divulgáveis, resultado autorizado e pagamento efetivamente concluído. Resumo da caixinha mostra totais reconciliados e evita exposição desnecessária de informações de terceiros.

**CONTROLE MANUAL 10.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 10.8 | Fases de verificação: 3/4/7

**10.8. Imutabilidade e versões de resultado — DEFINIDO.** Datas centrais, identidade de tenant/ciclo, contratos aceitos, movimentos financeiros confirmados e histórico de parcelas são imutáveis, ressalvados lançamentos compensatórios comprovados. A remuneração do administrador e a participação dos membros são **congeladas como percentuais contratuais para cada ciclo**; mudanças assinadas no decorrer do ano só entram em vigor no ciclo seguinte. `CycleClosing` guarda versão aplicável, pesos, rateios exatos, truncamentos, centavos redistribuídos, comprovantes de pagamento e eventuais pendências, sem repartir lucro futuro a partir de versão inexistente no ciclo encerrado.

**CONTROLE MANUAL 10.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 11 — Inventário de telas, componentes, colunas e ações


### Cláusula 11.0-A | Fases de verificação: 5

**11.0-A. Telas de demonstrador regulatório e evolução — CONSOLIDADO.** A área Master exibirá o status documental/homologação das capacidades específicas sem conceder poderes de abrir conta bancária ou aprovar operações de terceiros. A futura função bolões terá, **somente em DEMO/HOMOLOGAÇÃO**, fluxo completo de criar campanha, publicar composição do preço, coletar aceite simulado do mandato, reservar/atribuir cotas, processar pagamento fictício, simular lançamento de registro oficial identificado como fictício, conferir resultados de teste, ratear prêmio simulado aos titulares e produzir relatório comprobatório; jamais rotular um registro fictício como bilhete válido da Caixa.

**CONTROLE MANUAL 11.0-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 11.1 | Fases de verificação: 5

**11.1. Design simples.** Uma navegação inferior ou menu por papel: `Início`, `Minha Caixinha`/`Membros`, `Financeiro`, `Relatórios` e `Perfil/Ajuda`, ajustada às permissões. Na tela do Master, `Licenças`, `Operação Técnica` e `Suporte`, sem navegação para finanças dos tenants.

**CONTROLE MANUAL 11.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 11.2 | Fases de verificação: 5

**11.2. Estados visuais.** `Pendente` = ainda sem comprovação; `Confirmado` = prova conciliada; `Vencido` = obrigação temporal; `Parcial` = algum valor recebido; `Em conciliação` = não repetir operação; `Bloqueado` = motivo e procedimento legítimo de regularização. Não usar apenas cor para estado.

**Exemplo de conferência (sem substituir o contrato):** Pendente/confirmado/vencido/parcial explicados também com texto, não só cores.

**CONTROLE MANUAL 11.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 11.3 | Fases de verificação: 5

**11.3. Textos de transparência.** Antes de qualquer pagamento ou empréstimo mostrar preço, juros, prazo, nome do recebedor, termos, valor total e etapa real; **não** usar a mensagem “pago” para Pix apenas solicitado. Se um novo parâmetro for diferente do contrato aceito, exigir novo aceite quando aplicável.

**CONTROLE MANUAL 11.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 11.4 | Fases de verificação: 5

**11.4. Manual oficial para administradores — ENTREGÁVEL DO MVP.** Manual em linguagem simples, acessível no aplicativo e disponibilizado em PDF: (1) criar conta; (2) selecionar plano/capacidade; (3) aceitar e pagar licença; (4) ativar caixinha; (5) configurar políticas e percentuais; (6) convidar/admitir membros; (7) registrar cotas e acompanhar contribuições; (8) simular/analisar/liberar crédito conforme permissões; (9) consultar extratos/ledger; (10) autorizações anuais do administrador-membro; (11) conciliar Pix; (12) gerar relatórios e fechamento; (13) renovar licença; (14) suspender/reativar sem lesar membros; (15) solicitar suporte/revogar; (16) verificar incidentes. Cada passo terá objetivo, tela, campos, confirmação e solução de erro; as capturas reais só podem ser incluídas **depois** da criação do app.

**CONTROLE MANUAL 11.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 11.5 | Fases de verificação: 5

**11.5. Apoio comercial e demonstração — ENTREGÁVEL NÃO TRANSACIONAL.** Kit de apresentação com descrição clara dos três planos, preço vigente parametrizado, limites de membros/cotas, desconto anual, demonstração com dados fictícios e roteiro de vídeo curto gravado no celular. Marketing inicial por apresentação direta aos administradores de caixinhas, WhatsApp, indicação voluntária e página informativa, **sem revelar dados de membros**, prometer rentabilidade ou simular autorização do Banco Central/CAIXA. O público conhece a oferta de licença; dados dos grupos continuam fechados. Testes com clientes-piloto não dispensam os requisitos legais de operação real.

**CONTROLE MANUAL 11.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 12 — Modelo de dados, chaves, colunas e restrições


### Cláusula 12.1 | Fases de verificação: 2/3/4

**12.1. Padrões de todas as tabelas.** Chaves `id` imutáveis (UUID ou outro identificador único estável), `tenant_id` obrigatório em registros de caixinha, `cycle_id` quando houver vínculo ao ciclo, `created_at`/`updated_at` timezone-aware, autoria e eventos críticos em trilha de auditoria. Valores monetários como `NUMERIC(18,2)` ou centavos inteiros conforme decisão de implementação única; **não usar float para dinheiro**. Taxas em tipo decimal de precisão apropriada, unidade explícita (por mês, por dia), datas `DATE`, instante `TIMESTAMPTZ`. `UNIQUE` por chave de negócio e referências externas necessárias; `FOREIGN KEY` para evitar registros órfãos.

**CONTROLE MANUAL 12.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.2 | Fases de verificação: 2/3/4

**12.2. Entidades fundamentais (tabelas e colunas mínimas).** A nomenclatura física exata poderá ser padronizada pelo Codex na futura etapa 2, mas **a semântica, as ligações e os invariantes abaixo são contratuais**. Campos `status`, `source`, `external_id`, `policy_version_id` e `consent_version_id` devem apontar para valores/relacionamentos válidos; campos sensíveis minimizados e protegidos.

**Dicionário de entidades — tabela contratual reformatada por linha para impressão; conteúdo de cada célula preservado:**

**Entidade:** **UserIdentity**
**Colunas mínimas / tipo lógico:** `id`, `name`, `cpf`, `email`, `email_verified_at`, `phone`, `phone_verified_at?`, `profile_photo_ref?`, `auth_subject`, `status`, `created_at`
**Restrições e finalidade:** Identidade pessoal única; CPF validado, contatos controlados; foto opcional; acesso restrito; confirmação de titularidade conforme função

**Entidade:** **ContractingParty**
**Colunas mínimas / tipo lógico:** `id`, `party_type` (PF/PJ), `legal_name`, `cpf_or_cnpj`, `billing_address?`, `representative_user_id?`, `fiscal_data?`, `status`, `created_at`
**Restrições e finalidade:** Titular comercial da licença, distinto do papel de administrador; PJ com representante verificado quando aplicável; dados fiscais mínimos

**Entidade:** **Tenant**
**Colunas mínimas / tipo lógico:** `id`, `admin_user_id`, `contracting_party_id`, `display_name`, `status`, `created_at`
**Restrições e finalidade:** Caixinha isolada; contratante comercial distinguido do administrador operacional; sem dados financeiros no painel Master

**Entidade:** **RoleGrant**
**Colunas mínimas / tipo lógico:** `id`, `user_id`, `tenant_id?`, `role`, `active_from`, `active_until`, `revoked_at`
**Restrições e finalidade:** Master global, admin/membro por tenant; proibir permissão implícita

**Entidade:** **Cycle**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `year`, `start_date`, `end_date`, `settlement_date`, `status`
**Restrições e finalidade:** Datas herdadas do calendário **global**, não editáveis pelo admin

**Entidade:** **TenantPolicyVersion**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `version`, `values_json`, `effective_at`, `author_id`, `status`
**Restrições e finalidade:** Juros, contribuições, limites, multas, admin_pct; versões não destrutivas

**Entidade:** **TermAcceptance**
**Colunas mínimas / tipo lógico:** `id`, `user_id`, `tenant_id?`, `cycle_id?`, `document_version`, `document_hash`, `accepted_at`, `evidence_ref`, `scope`
**Restrições e finalidade:** Aceite individual de licença, adesão, política, empréstimo ou mandato

**Entidade:** **Membership**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `user_id`, `joined_at`, `left_at`, `status`
**Restrições e finalidade:** Unicidade de associação ativa no ciclo; protege histórico

**Entidade:** **Quota**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `membership_id`, `quota_number`, `status`, `effective_from/to`
**Restrições e finalidade:** Identificação e quantidade de cotas; capacidade licenciada

**Entidade:** **Contribution**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `membership_id`, `quota_id?`, `competence`, `due_date`, `amount_due`, `amount_paid`, `payment_status`, `due_status`
**Restrições e finalidade:** Nunca marcar quitada sem conciliação; parcial + vencida coexistem

**Entidade:** **Payment**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id?`, `purpose`, `obligation_id`, `expected_amount`, `confirmed_amount`, `provider`, `external_id`, `status`, `confirmed_at`
**Restrições e finalidade:** Licença, contribuição, prestação e outros pagamentos tipificados; idempotência

**Entidade:** **Loan**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `borrower_membership_id`, `policy_version_id`, `principal`, `rate`, `term`, `schedule_type`, `decision_by`, `status`, `pix_transfer_id?`
**Restrições e finalidade:** Política congelada no contrato; aprovação e desembolso separados

**Entidade:** **LoanInstallment**
**Colunas mínimas / tipo lógico:** `id`, `loan_id`, `sequence`, `due_date`, `principal_due`, `interest_due`, `penalties_due`, `paid_amount`, `status`
**Restrições e finalidade:** Identificar componentes e ajustar última parcela; sem juros futuros na quitação

**Entidade:** **AnnualSelfLoanConsent**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `beneficiary_admin_id`, `document_version`, `status`, `valid_from/to`
**Restrições e finalidade:** Autoriza **somente o ciclo**, sob unanimidade dos demais membros

**Entidade:** **ConsentSignature**
**Colunas mínimas / tipo lógico:** `id`, `consent_id`, `signer_membership_id`, `signed_at`, `evidence_ref`, `revoked_at?`
**Restrições e finalidade:** Uma assinatura por signatário legítimo; ingresso posterior exige adesão

**Entidade:** **LedgerAccount**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `account_code`, `kind`, `status`
**Restrições e finalidade:** Conta contábil de principal, receita, despesa, reserva, obrigação e ajuste

**Entidade:** **LedgerTransaction**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `business_type`, `business_id`, `posted_at`, `reversal_of_id?`, `status`
**Restrições e finalidade:** Evento contábil indivisível, idempotente e auditável

**Entidade:** **LedgerEntry**
**Colunas mínimas / tipo lógico:** `id`, `transaction_id`, `account_id`, `direction`, `amount`, `currency`
**Restrições e finalidade:** Lançamentos dobrados, soma de débitos/créditos equilibrada

**Entidade:** **PixTransfer**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `purpose`, `beneficiary_id`, `amount`, `idempotency_key`, `provider_external_id`, `status`, `confirmed_at?`
**Restrições e finalidade:** Desembolso ou liquidação; nunca duplicar transferência

**Entidade:** **CycleClosing**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `cycle_id`, `snapshot_at`, `policy_version_id`, `member_pool`, `admin_pool`, `residual`, `status`, `approved_by`
**Restrições e finalidade:** Foto contábil auditável; fechamento só com provas

**Entidade:** **Distribution**
**Colunas mínimas / tipo lógico:** `id`, `closing_id`, `beneficiary_type`, `beneficiary_id`, `amount_due`, `amount_paid`, `pix_transfer_id?`, `status`
**Restrições e finalidade:** Separar principal devolvido, lucro-membro, remuneração admin, pendências

**Entidade:** **LicensePlan**
**Colunas mínimas / tipo lógico:** `id`, `name`, `member_limit`, `quota_limit`, `status`
**Restrições e finalidade:** Identidade/capacidade do plano; valores ficam em LicensePriceVersion; anual = mensal × 10, só leitura; Ampliado indisponível sem limites

**Entidade:** **LicensePriceVersion**
**Colunas mínimas / tipo lógico:** `id`, `plan_id`, `monthly_price`, `annual_price_computed`, `effective_from`, `effective_to`, `changed_by`, `reason`, `created_at`
**Restrições e finalidade:** Histórico imutável de preços comerciais; cálculo anual determinístico, oferta congela versão

**Entidade:** **LicenseSubscription**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `contracting_party_id`, `plan_id`, `period`, `starts_at`, `ends_at`, `status`, `paid_payment_id`
**Restrições e finalidade:** Contratante e tenant vinculados; renovação sem carência e ativação somente por Pix conciliado

**Entidade:** **SupportAccessGrant**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id`, `granted_by`, `granted_to`, `scope`, `reason`, `issued_at`, `expires_at`, `revoked_at`
**Restrições e finalidade:** Acesso mínimo, temporário, revogável e auditado

**Entidade:** **Incident**
**Colunas mínimas / tipo lógico:** `id`, `tenant_id?`, `severity`, `reason`, `opened_at`, `owner`, `resolution`, `closed_at`
**Restrições e finalidade:** Manutenção preventiva/corretiva/emergencial

**Entidade:** **AuditEvent**
**Colunas mínimas / tipo lógico:** `id`, `actor_id`, `tenant_id?`, `object_type`, `object_id`, `action`, `timestamp`, `reason`, `evidence_ref`
**Restrições e finalidade:** Trilha imutável lógica para decisões, suporte, Pix, políticas e aceites

**Exemplo de conferência (sem substituir o contrato):** Verificar entidades UserIdentity/ContractingParty/Membership/Tenant/License, FKs e unicidade.

**CONTROLE MANUAL 12.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.2-B | Fases de verificação: 2/3/4

**12.2-B. Vínculos semânticos obrigatórios identificados na auditoria.** (i) `LicenseOffer/LicensePriceVersion/TermAcceptance/LicenseSubscription/Payment` referenciam **a mesma oferta imutável e a mesma versão de preço aceita**; assinatura pode apontar ao tenant preliminar inativo, sem ativação antes do Pix; (ii) `Payment.obligation_id` deve referenciar uma obrigação tipificada **existente no mesmo tenant/ciclo ou no domínio da plataforma**, conforme o tipo, impedindo ligações cruzadas; (iii) `LoanInstallment` e pagamentos discriminam de modo recuperável **principal, juros remuneratórios, multa, mora, reversões e valor pago por componente**; (iv) ledger, capital, conta externa e reservas mantêm titularidade individual do membro quando aplicável, sem depender somente de `account_code`; (v) `CycleClosing` preserva snapshot, todos os pesos, bases, percentuais e **versões efetivamente aplicáveis**, além da natureza de cada distribuição; (vi) assinatura registra segmentos de vigência, dia âncora, oferta histórica e upgrades anteriores; (vii) capacidades reguladas mantêm finalidade, conta/titular, ambiente, validade e evidência, com revogação; (viii) `UserIdentity`, `ContractingParty`, `Tenant`, `RoleGrant`, `Membership` e `LicenseSubscription` são vínculos diferentes; documentos pessoais, contatos e fotografia obedecem aos itens 3.1-A/6.1-A, sem visibilidade intertenant nem concessão implícita de licença. A estrutura física/nomes exatos continuam livres na etapa 2 desde que nenhum desses vínculos possa ser perdido.

**CONTROLE MANUAL 12.2-B:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.2-A | Fases de verificação: 2/3/4

**12.2-A. Campos de preparação para novos provedores, sem código bancário — CONSOLIDADO.** `ExternalProviderConnection(tenant_id?, provider_code, account_owner_ref, environment, status, capabilities_json, token_secret_ref, consent_ref)` guarda metadados necessários sem segredos em claro; `ExternalAccountBinding(tenant_id, membership_id?, provider_connection_id, masked_external_account_ref, ownership_verified_at)` referencia contas legítimas; `RegulatedCapability(id, code, environment, status, evidence_ref, permitted_from, approved_by)` controla liberação por escopo. Esses campos não são licença nem criam contas reais. Os identificadores de ativos, passivos e prova financeira serão independentes de fornecedor. Novas tabelas prudenciais, saldo custodial próprio, cadastro KYC completo e relatórios regulatórios **não** são implementados antes de definição da figura autorizada e de seus requisitos.

**CONTROLE MANUAL 12.2-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.3 | Fases de verificação: 2/3/4

**12.3. Regras de chaves e índices.** `UserIdentity`: prevenir CPF duplicado entre identidades ativas incompatíveis e tratar fusão/correção de conta com verificação e auditoria; `ContractingParty`: CPF/CNPJ consistente e representante autorizado quando PJ, sem reutilizar registro contratual para contornar licenças; `Membership`: restrição de uma associação ativa por usuário/tenant/ciclo; `Quota`: número único por tenant/ciclo; `Contribution`: única obrigação por membro/cota/competência de acordo com política; `Payment`/`PixTransfer`: unicidade de identificadores externos e de idempotência no escopo; `TenantPolicyVersion`: versão única por tenant/ciclo; `ConsentSignature`: um registro vigente por consentimento/signatário; `LedgerEntry`: débitos/créditos equilibrados na operação. Índices compostos começam por `tenant_id` em consultas de dados privados para reduzir risco de vazamento e suportar segregação.

**CONTROLE MANUAL 12.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.4 | Fases de verificação: 2/3/4

**12.4. Relações de negócio.** `Tenant 1:N Cycle`; `User N:M Tenant` via `Membership/RoleGrant`; `ContractingParty 1:N Tenant/LicenseSubscription` conforme titularidade contratual efetiva; `Cycle 1:N Membership, Quota, Contribution, Loan, CycleClosing`; `Loan 1:N LoanInstallment`; `Contribution/LoanInstallment 1:N Payment`; `LedgerTransaction 1:N LedgerEntry`; `CycleClosing 1:N Distribution`; `AnnualSelfLoanConsent 1:N ConsentSignature`; `PixTransfer 1:1` com tentativa lógica autorizada, mantendo histórico das consultas ao provedor em eventos separados. A implementação não pode duplicar dívida ou distribuir principal como lucro.

**CONTROLE MANUAL 12.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 12.5 | Fases de verificação: 2/3/4

**12.5. Entidades futuras de bolões — não migrar na primeira entrega.** Após aprovação de escopo: `LotteryCampaign(tenant,cycle,modality,contest,status)`, `LotteryQuota(campaign,holder,official_cost,final_price)`, `LotteryMandate(acceptance,evidence)`, `OfficialTicket(campaign,receipt,registered_at,custodian)`, `LotterySettlement(campaign,official_cost,gross_margin,expenses,eligible_net)`, `LotteryPrize(ticket,holder,amount,status)`. Premiações pertencem aos titulares, não ao `CycleClosing.member_pool`. **Não criar tabelas operacionais lotéricas no MVP enquanto bloqueado.**

**CONTROLE MANUAL 12.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 13 — Segurança, disponibilidade, privacidade e continuidade


### Cláusula 13.1 | Fases de verificação: 2/6/7

**13.1. Defesa em camadas.** Autenticação segura, senhas protegidas por hash adequado, sessões limitadas, recuperação de conta, autorização por recurso no backend, segregação de tokens por comerciante, HTTPS em produção, criptografia de segredos, princípio de menor privilégio e proteção de logs. Interface não pode disponibilizar tokens privados nem operações protegidas apenas por esconder botões.

**CONTROLE MANUAL 13.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.2 | Fases de verificação: 2/6/7

**13.2. LGPD e minimização.** Coletar somente dados necessários à identidade, ao contrato e à operação autorizada; avisar finalidade, acesso, direitos de titulares, canal de atendimento e retenção legítima. Não permitir que licença suspensa apague prova financeira. Logs técnicos devem mascarar dados sensíveis. O administrador contratante só recebe dados dos membros de sua caixinha necessários à sua gestão legítima.

**CONTROLE MANUAL 13.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.3 | Fases de verificação: 2/6/7

**13.3. Controle fiscal e conformidade da plataforma.** Master vê receita de **suas licenças**, contratos comerciais, pagamentos e notas/relatórios próprios; dos tenants vê capacidade, estado de licença e métricas técnicas minimizadas. Relatórios tributários de cada caixinha e obrigações de seus gestores exigem responsabilidade e fundamento próprios; **não prometer fiscalização fiscal irrestrita de terceiros** nem equiparar Painel Master a autoridade tributária.

**CONTROLE MANUAL 13.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.4 | Fases de verificação: 2/6/7

**13.4. Política mínima de backup e recuperação — APROVADO COMO REQUISITO DOCUMENTAL.** Backup completo **criptografado diariamente** e arquivamento de registros de transações do PostgreSQL (*WAL*) **a cada até 15 minutos**, para recuperação pontual quando suportada pela infraestrutura homologada; cópia externa isolada do servidor principal, acesso mínimo e alertas de falha. **Retenção de backup: 35 dias**, sem confundir o período de backup com o prazo legal de preservação de contratos, lançamentos e provas financeiras, que pode ser maior. Meta de recuperação em produção: **RPO de até 1 hora** (máximo de perda de dados recuperáveis antes da conciliação) e **RTO de até 8 horas**, ambos sujeitos a ensaio real documentado e custo aprovado. Teste de restauração antes de entrar em produção e depois **trimestralmente**; reconciliar Pix com o provedor para não repetir pagamentos após a restauração. Se a hospedagem/armazenamento escolhido não sustentar esses requisitos, **não ativar operação financeira real** até ajustar infraestrutura e demonstrar conformidade.

**Exemplo de conferência (sem substituir o contrato):** Backup diário+WAL até 15 min, 35 dias, restauração, RPO 1h e RTO 8h.

**CONTROLE MANUAL 13.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.5 | Fases de verificação: 2/6/7

**13.5. Monitoramento enxuto.** Saúde API, banco, pagamentos/webhooks, tarefas de conciliação, backups e incidentes. Alertas por indisponibilidade prolongada, confirmação duplicada, divergência monetária, falha de backup ou acesso indevido. Não exigir microserviços, infraestrutura paga ou múltiplas ferramentas desde o início.

**CONTROLE MANUAL 13.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.6 | Fases de verificação: 2/6/7

**13.6. Homologação.** Dados fictícios e testes controlados até cumprir critérios jurídicos, de fornecedor e do responsável. Sem execução Pix real, integração lotérica, hospedagem paga ou publicação de aplicativo sem autorização explícita.

**CONTROLE MANUAL 13.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.7 | Fases de verificação: 2/6/7

**13.7. Projeto preparado para evolução institucional — CONSOLIDADO.** O código novo deve ser organizado como **monólito modular**, com domínios isoláveis `identidade/permissões`, `licenciamento`, `caixinha/políticas`, `obrigações e crédito`, `ledger/conciliação`, `pagamentos/adaptadores`, `evidências/auditoria` e `capacidades reguladas`. O backend fornece contratos estáveis às telas. Versionamento de APIs, migrações reversíveis, testes de contrato dos adaptadores, trilha imutável lógica, exportação integral e reconciliação permitem evolução progressiva. Não implantar microsserviços, core bancário, contas de pagamento próprias, contas de depósito, Pix direto, módulo prudencial ou motores de compliance bancário **na primeira entrega**: isso seria outro produto, com novos requisitos e custos.

**CONTROLE MANUAL 13.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.8 | Fases de verificação: 2/6/7

**13.8. Possível instituição financeira ou de pagamento no futuro — CONDICIONADO.** A intenção de operar sob licença própria deve ser avaliada com escolha **posterior** do enquadramento correto (por exemplo instituição de pagamento ou instituição financeira, conforme produtos concretos), estrutura societária, capital, governança, gestão de riscos, prevenção à lavagem de dinheiro, políticas de segurança, proteção ao cliente, relatórios e requisitos de conexão ao sistema de pagamentos. Ser "banco digital" não é uma permissão adquirida por ter aplicativo pronto. Uma instituição de pagamento não equivale a banco e não recebe automaticamente poderes de intermediação financeira. Nenhum contrato técnico pode garantir evolução para banco real **sem novos módulos, auditorias, investimentos e autorização**; nosso compromisso é minimizar a reescrita do núcleo e tornar claros os pontos de substituição.

**CONTROLE MANUAL 13.8:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.9 | Fases de verificação: 2/6/7

**13.9. Linha de licenciamento/homologação — CONSOLIDADO.** Ao identificar uma função que possa precisar de autorização: (i) classificar exatamente a atividade e órgão competente; (ii) verificar **antes da implementação** os requisitos para requerimento (há processos que admitem projeto/plano sem app pronto e processos que demandam sistema demonstrável); (iii) desenvolver e testar no ambiente apropriado conforme escopo aprovado pelo responsável, com simulações não monetárias; (iv) produzir dossiê técnico com telas, regras, riscos, dados, logs, fluxos e testes reproduzíveis; (v) protocolar o pedido na etapa juridicamente correta, sem pressupor que código completo é requisito universal; (vi) atender diligências e homologações; (vii) liberar operação real **apenas após as autorizações, aprovações comerciais e requisitos efetivamente exigidos**. Não é válido o ciclo circular "só programo se autorizado" / "só peço autorização depois de operar"; a prontidão documental/demonstrável é distinta da autorização operacional.

**CONTROLE MANUAL 13.9:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.10 | Fases de verificação: 2/6/7

**13.10. Formalização empresarial digital — ROTEIRO PARA O PROPRIETÁRIO.** Etapa A: pesquisar atividades econômicas reais, enquadramento e emissão fiscal pela Receita Federal/Redesim, portal de empreendedorismo, Junta Comercial/município conforme aplicável; etapa B: verificar se **Inova Simples** é compatível com a comercialização pretendida e seu estágio experimental, sem equiparar esse cadastro à blindagem patrimonial de uma LTDA; etapa C: se necessário, abrir **LTDA unipessoal** por canais oficiais, verificando custos obrigatórios, contador quando legalmente exigido e elegibilidade a regimes tributários; etapa D: abrir **conta PJ** apenas quando houver CNPJ/necessidade real, observando regras do banco e separação patrimonial. O protocolo dos pedidos será feito pessoalmente onde permitido. **Nenhuma forma empresarial exime automaticamente impostos** nem autoriza receber depósitos de terceiros como instituição financeira.

**CONTROLE MANUAL 13.10:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.11 | Fases de verificação: 2/6/7

**13.11. Propriedade intelectual e documentos de titularidade.** Antes do lançamento, pesquisar e, se estrategicamente oportuno, protocolar marca **FRcaixinha** no INPI, após definir titular legítimo e classes de software/SaaS compatíveis. Manter documentação de autoria do código, commits GitHub, versões, contratos de contribuição e comprovantes de desenvolvimento; após existir versão material, avaliar pedido eletrônico de registro de programa de computador no INPI, com exigências de assinatura/certificado vigentes. **Patente não protege automaticamente algoritmo genérico, método de negócio ou ideia de aplicativo**; analisar somente possível solução técnica patenteável e necessidade de sigilo prévio. Não usar marcas de terceiros para sugerir vínculo institucional.

**CONTROLE MANUAL 13.11:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.12 | Fases de verificação: 2/6/7

**13.12. Assistência gratuita e autonomia nos requerimentos.** Priorizar Gov.br, Receita/NAF, Sebrae, INPI, Ouvidorias/portais de consulta de órgãos reguladores, serviços públicos e atendimento jurídico gratuito **sujeito a elegibilidade e objeto**. A Defensoria Pública não deve ser presumida como consultoria gratuita irrestrita para empresa comercial; procedimentos que exigirem profissional habilitado, parecer técnico ou representação especializada deverão ser classificados com custo e risco conhecidos, sem fingir emissão de laudo pelo ChatGPT.

**CONTROLE MANUAL 13.12:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.13 | Fases de verificação: 2/6/7

**13.13. Matriz documental de conformidade por função — PARA CONSTRUÇÃO E AUDITORIA.** (a) **Software, cadastro, adesões e extratos:** documentos de termos, privacidade, segurança e fiscalização de dados pessoais; órgão de referência LGPD/ANPD, sem “licença geral da ANPD” presumida. (b) **Assinaturas da plataforma:** CNPJ/tributação/documentos comerciais quando aplicáveis, conta/contrato do Mercado Pago e teste da cobrança. (c) **Crédito interno e remuneração dos administradores:** exame da atividade econômica concreta e de possível enquadramento no BC/legislação civil, inclusive taxas e autoaprovação; pode exigir avaliação formal antes do uso com recursos reais. (d) **Pix IN/OUT:** homologação técnica e aceitação comercial do Mercado Pago para **todas as finalidades** e contas envolvidas, não apenas geração de QR. (e) **Bolões oficiais com margem incorporada ao preço:** contrato de mandato, consulta regulatória sobre comercialização/intermediação independente, requisitos operacionais da CAIXA, tratamento de prêmios, prova de aposta, prevenção a fraude, tributação e aprovação explícita do provedor. (f) **Futura instituição de pagamento ou banco:** processo próprio junto ao Banco Central conforme modelo e autorização requerida; nenhum pedido/solução bancária presente é presumido. Para cada item, conservar órgão/canal, pergunta, versão do produto, documentos anexos, protocolo, resposta, eventuais condicionantes e status `NAO_SOLICITADO / CONSULTA / EM_ANALISE / APROVADO / NEGADO / NAO_APLICAVEL` mediante evidência.

**CONTROLE MANUAL 13.13:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 13.14 | Fases de verificação: 2/6/7

**13.14. Regra de licenciamento sem impasse circular.** O aplicativo pode ser **desenvolvido e demonstrado com dados fictícios antes de uma licença operacional** quando a lei/procedimento permitir; alguns pedidos podem ser feitos com plano de negócios e arquitetura, outros requerem sistema demonstrável. O proprietário verificará os requisitos **antes de assumir gasto**, montará dossiê com fluxos/testes/prints e protocolará no momento determinado pelo órgão. A operação com dinheiro real e a publicação comercial de função regulada só serão liberadas após exigências efetivas; não afirmar que **todo órgão exige produto pronto** nem que a simples existência de código produz autorização.

**CONTROLE MANUAL 13.14:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 14 — Bolões oficiais próprios e demais ações futuras — condicionado


### Cláusula 14.1 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.1. Modelo escolhido — CONDICIONADO.** Até quatro campanhas anuais por caixinha de bolões das Loterias CAIXA, **organizadas na interface tecnológica do FRcaixinha, sob responsabilidade do administrador contratante/organizador expressamente identificado** (pessoa/entidade legitimamente apta e mandatária de cada aderente conforme instrumento próprio, quando juridicamente permitido). O **Master fornece software e suporte**, não é mandatário, titular de bilhete ou recebedor automático dos valores de terceiros. Cada oferta identifica organizador, responsáveis por receber pagamentos, efetivar registro em canal oficial, custodiar comprovantes, conferir sorteios, prestar contas e responder por restituições, observados os requisitos legais. Participação voluntária de membros maiores de 18 anos; contrato de mandato individual, registro e sorteios exclusivamente pelos canais oficiais CAIXA, sem presumir API pública ou autorização automática.

**CONTROLE MANUAL 14.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 14.2 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.2. Preço final e margem — DEFINIDO COMO MODELO ECONÔMICO.** O administrador propõe o preço **total** de cada cota; esse preço pode ser superior ao custo oficial por participação. Mostrar ambos **antes da compra** e separar a margem de organização incluída. Não há cobrança extra após o preço final. **Exemplo ilustrativo:** bolão oficial R$ 150,00 dividido em 20 cotas = custo oficial **R$ 7,50 por cota**; preço final proposto **R$ 25,00/cota**, arrecadação **R$ 500,00**, custo oficial **R$ 150,00**, **margem bruta R$ 350,00** (R$ 17,50/cota). É remuneração econômica embutida, mesmo que não seja rotulada como taxa à parte.

**Exemplo de conferência (sem substituir o contrato):** 20 × R$ 25 = R$ 500; custo R$ 150; margem bruta R$ 350; apenas demonstração.

**CONTROLE MANUAL 14.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 14.3 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.3. Destinação e risco.** Apenas margem **efetivamente realizada, permitida por lei, confirmada e líquida** de despesas, tributos, tarifas e reembolsos pode entrar no resultado da respectiva caixinha. Exemplo na caixinha do proprietário, **se** os R$ 350 fossem integralmente líquidos/elegíveis: R$ 297,50 para membros (85%) e R$ 52,50 para administrador (15%). Em outros tenants, aplicar percentuais **daquele** grupo, não 85/15 universais. Os R$ 350 vieram do dinheiro dos próprios compradores e **não são riqueza nova garantida ao conjunto**. Prêmios lotéricos pertencem aos titulares reais das cotas, proporcionalmente, e não são lucro do grupo.

**CONTROLE MANUAL 14.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 14.4 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.4. Fluxo de demonstrador completo e futura operação condicionada.** Administrador configura concurso/modalidade, custo oficial, quantidade de cotas, preço final e data-limite → o sistema apresenta decomposição e mandato específico → membro adere e paga via canal autorizado → backend comprova pagamento → mandatário registra efetivamente apostas em canal oficial CAIXA → associa comprovante oficial e titularidades → confere resultado oficial → presta contas, garante resgates legítimos, reembolsa se não houve registro e encerra. **Pagamento não é comprovante de aposta.** Sem registro oficial tempestivo, restituir integralmente o preço pago, incluindo margem embutida, conforme condições legais; não reter lucro por serviço não prestado.

**CONTROLE MANUAL 14.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 14.5 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.5. Barreiras de operação, NÃO de desenvolvimento demonstrável.** **NÃO OPERAR OU COBRAR COM DINHEIRO REAL, registrar apostas efetivas, vender cotas nem pagar prêmios reais** antes de (a) parecer jurídico brasileiro específico sobre mandato oneroso, atividade de intermediação independente, comercialização de cotas e margem pretendida; (b) verificação do Manual CAIXA vigente, registro, limites, custódia e direito a prêmios; (c) aprovação **por escrito** do Mercado Pago para esse ramo e suas movimentações; (d) validação fiscal, proteção de dados, fraude e consumidores; (e) ordem separada do Master para escopo, prazo, custos e homologação. O Código Civil (arts. 653 e seguintes) reconhece mandato, mas **não dispensa automaticamente normas setoriais**. A existência de outras empresas com contratos de mandato não equivale a licença para qualquer terceiro.

**CONTROLE MANUAL 14.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 14.6 | Fases de verificação: PACOTE SEPARADO, CONDICIONADO

**14.6. Demonstração e prova regulatória.** A preparação de arquitetura e evidências **observará o regime aplicável, sem constituir autorização para operação**. Após autorização técnica separada e análise do procedimento aplicável, elaborar e testar a experiência com **dados fictícios**, contrato/mandato, cota, custo oficial, preço final e margem destacada, comprovação e prestação de contas. Nada gera aposta oficial ou direito a prêmio, nem cobra dinheiro real antes dos requisitos de 14.5. O demonstrador tem **escopo, orçamento e cronograma adicionais aos 60 dias do núcleo**, com aceite próprio; não condicionar a homologação do núcleo à conclusão dos bolões. Documentos fictícios trazem `DADOS FICTÍCIOS` de modo permanente. Não adicionar rifa privada, jogo próprio, consórcio ou evento digital como substituto.

**CONTROLE MANUAL 14.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 15 — Cronograma executivo fechado, dependências e critérios de aceite


### Cláusula 15.1 | Fases de verificação: 0/1–7

**15.1. Ordem de trabalho.** **Fase documental concluída:** auditoria do texto disponível, consolidação das convenções, inclusão dos cadastros 3.1-A/6.1-A e **aprovação documental final expressa do proprietário em 16/10/2026 (G1)**. **Fase futura separada e ainda não autorizada:** ordem expressa para criar novo diretório/repositório e iniciar desenvolvimento (G2) → implementação por etapas → testes com dados fictícios → homologação e aceites → eventual liberação jurídica/comercial específica para operações reais. Não existe projeto novo no Termux neste marco.

**CONTROLE MANUAL 15.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.2 | Fases de verificação: 0/1–7

**15.2. Estimativa inicial, sem promessa de entrega.** **60 dias úteis de execução estimada**, sem promessa de data de produção. Janelas consecutivas: **3 + 8 + 14 + 9 + 13 + 7 + 6 = 60**. As sete etapas só começam quando o responsável ordenar a criação e o desenvolvimento; infraestrutura/custos reais e a capacidade do ambiente ainda precisam ser confirmados. A previsão de ciclo em 01/01/2027 **não prova** que a entrega terminará antes dessa data.

| Ordem | Janela e duração | Desenvolvimento concreto | Teste objetivo e entregável para aceite |
|---|---|---|---|
| **1. Base do projeto** | D1–D3 • 3 úteis | Criar **somente após ordem** um repositório novo, estrutura `mobile/`, `backend/`, documentação de configuração, autenticação de ambiente de testes e CI básico | App/API mínimos inicializam; comandos reproduzíveis; nenhum segredo no Git; responsável aprova estrutura |
| **2. Banco e segurança** | D4–D11 • 8 úteis | Modelar User/Tenant/Cycle/Membership/Quota/Policy/Consent/License, migrations, papéis e autenticação; calendário fixo no backend | Migration sobe/volta; chamadas cruzadas entre tenants e acessos Master financeiros **negados**; ciclo imutável |
| **3. Núcleo de automação** | D12–D25 • 14 úteis | Licenciamento/precificação e aceites; políticas por caixinha; contribuições/ledger; motor de empréstimos Price parametrizado; anuência coletiva anual; Capital-Dias e fechamento | Testes de preços 89,90/109,90/129,90; licença zero carência; 20/40 e 50/50; juros próprios vs de terceiros; 85/15 vs 80/20; cálculos, inadimplência e fechamento determinísticos |
| **4. Pix e conciliação** | D26–D34 • 9 úteis | Conexão e configuração conforme homologação do provedor; cobranças de licença e contribuição; pagamentos de parcelas, reserva e Pix OUT; distribuição e recuperação idempotente | Webhook inválido/duplicado/fora de ordem, timeout, concorrência, reversão; nenhuma ativação/saída sem confirmação; ambiente de teste |
| **5. Flutter e painéis** | D35–D47 • 13 úteis | Telas de contratação, membro, administrador e Master; dados por papel; painel de políticas e calendário travado; autorizações anuais; suspensão com direitos preservados | Jornadas ponta a ponta do usuário; acessibilidade; sem visualização de dados alheios; telas completas para regras definidas |
| **6. Operação e continuidade** | D48–D54 • 7 úteis | Central de manutenção, métricas mínimas, suporte temporário/revogável, proteção de dados, backup, teste de restauração e reprocessamento Pix | Revogação durante sessão; ausência de acesso financeiro Master; restauração sem duplicar Pix; evidências auditáveis |
| **7. Homologação e entrega** | D55–D60 • 6 úteis | Corrigir erros de aceite, testar todas as regras, empacotar APK para homologação, entregar documentação operacional e matriz de testes | Relatório final PASS/FAIL por função; APK íntegro; sem Pix real não autorizado; aceite formal ou bloqueio justificado |

**Exemplo de conferência (sem substituir o contrato):** Sete janelas de 3,8,14,9,13,7,6 dias úteis, condicionadas a G2.

**CONTROLE MANUAL 15.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.2-A | Fases de verificação: 0/1–7

**15.2-A. Condição de prontidão do escopo.** A etapa de base pode iniciar após aprovação deste contrato e ordem separada, **sem** exigir contratação de OCI, ativação de Pix real ou liberação de bolões. O primeiro pacote entregável contém Essencial e Intermediário; o Ampliado terá estrutura prevista, mas checkout bloqueado até aprovação da capacidade. Pareceres e homologações são gates para operação real, não justificativa para Codex inventar regras ou alterar autonomamente o escopo.

**CONTROLE MANUAL 15.2-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.2-B | Fases de verificação: 0/1–7

**15.2-B. Pacotes independentes, sem circularidade.** **Pacote NÚCLEO (D1–D60):** construir o SaaS, licenças, dados, motor de regras, Pix simulado/homologável, telas e **manual do administrador baseado nas telas efetivas**, com seus próprios testes e aceite `NUCLEO_HOMOLOGADO`. O kit comercial de apresentação acompanha preparação para lançamento, mas sua campanha publicitária não é requisito para homologação técnica do núcleo. **Pacote DEMONSTRADOR LOTÉRICO (fora de D1–D60):** dimensionar/autorizar separadamente, implementar com dados fictícios, testar, apresentar evidências, corrigir exigências, com aceite próprio `DEMONSTRADOR_LOTERICO_HOMOLOGADO`; a ausência de aprovação lotérica **não bloqueia** o aceite do núcleo. **Ações empresariais/regulatórias:** consultas e documentação podem correr em paralelo conforme procedimento concreto; a liberação de cada funcionalidade real é independente e depende de seus respectivos requisitos técnicos e jurídicos. Evolução para banco é possibilidade futura, sem implementação prudencial no MVP.

**CONTROLE MANUAL 15.2-B:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.2-C | Fases de verificação: 0/1–7

**15.2-C. Prazo e conclusão honesta.** O quadro de **60 dias úteis** é estimativa apenas do **núcleo do aplicativo**, não do demonstrador lotérico, processo regulatório, integração bancária própria nem banco digital. Antes de prometer a conclusão de "todas as funcionalidades", apresentar e aprovar uma previsão adicional para bolões e homologação técnica. Tramitação em órgãos externos não tem prazo controlado pelo Codex e não integra aceites de codificação. A primeira entrega tecnológica poderá ter status `NUCLEO_HOMOLOGADO`; o produto completo com bolões terá status separado `DEMONSTRADOR_LOTERICO_HOMOLOGADO` e `OPERACAO_LOTERICA_LIBERADA`, que não são equivalentes. O módulo de evolução bancária é apenas possibilidade arquitetural, sem prazo nem promessa de autorização.

**CONTROLE MANUAL 15.2-C:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.3 | Fases de verificação: 0/1–7

**15.3. Gestão do cronograma por etapa.** Para cada tarefa: ID, objetivo verificável, responsáveis de execução (Codex/operador técnico) e de aprovação (Master), arquivos permitidos, pré-requisitos, D-início/D-fim, teste reproduzível e resultado. Não iniciar etapa dependente com falha crítica; não multiplicar etapas por correção repetitiva. `BLOCKED` é impedimento documentado, **não entrega concluída**. Uma modificação de prazo/escopo exige decisão expressa e não nasce da vontade do Codex.

**CONTROLE MANUAL 15.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.3-A | Fases de verificação: 0/1–7

**15.3-A. Evidências técnicas obrigatórias para apresentar a terceiros.** Inventário de telas e APIs; descrição ponta a ponta das funções; diagramas de dados e provedores; exemplos de contrato/mandato e precificação; documentação de separação patrimonial; segurança, autenticação, logs e reconciliação; testes com cenários válidos/inválidos e evidência audiovisual; versão da aplicação e do esquema de dados; matriz de riscos com responsabilização. Documento fiscal ou autorização de operação não é inferido do funcionamento do app. Não fornecer ao órgão um protótipo que exija transação monetária real para demonstrar sua interface.

**CONTROLE MANUAL 15.3-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.4 | Fases de verificação: 0/1–7

**15.4. Gates independentes.** **G1** contrato auditado e aprovado **(CONCLUÍDO em 16/10/2026)**; **G2** ordem de criar/repositório; **G3** disponibilidade de ambiente e dependências; **G4** rotinas testadas; **G5** provedor Pix com autorização e capacidade homologadas; **G6** avaliação jurídica/tributária para **operação real**; **G7** aprovação de publicação. Bolões exigem ainda gates separados na seção 14. A passagem de G1 para G2 não é automática.

**Exemplo de conferência (sem substituir o contrato):** G1 aprovado não libera G2; Pix real depende de gates próprios.

**CONTROLE MANUAL 15.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.5 | Fases de verificação: 0/1–7

**15.5. Execução técnica.** Codex não decidirá taxa do cliente, assinatura jurídica, custo pago, alteração de calendário, reembolso ou novo módulo. Não copiar arquivos de projetos anteriores, não procurar diretórios inexistentes antes da ordem, não criar infra paga, não movimentar fundos reais ou credenciais por presunção. A auditoria desta minuta é **documental** e não implica inspeção técnica de código inexistente.

**CONTROLE MANUAL 15.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.6 | Fases de verificação: 0/1–7

**15.6. Plano de negócios e chegada ao mercado — FORA DOS 60 DIAS DE CODIFICAÇÃO.** **Preparação (já, sem custo):** pesquisar 10–20 administradores potenciais e entrevistas sobre controles manuais; validar disposição de pagamento sem coletar dados bancários de terceiros; listar despesas inevitáveis e critérios de preço. **Durante o MVP:** preparar protótipo demonstrável, fluxos de cadastro/aceite, manuais, indicadores de conversão, modelo comercial e documentação de marca/empresa. **Pré-venda ou piloto:** somente sob condições jurídicas e contratuais apropriadas, sem fingir que pagamentos/atividades reguladas já estejam liberados. **Lançamento:** oferta de Essencial e Intermediário mediante conta, aceite, Pix da plataforma aprovado e suporte funcional; Ampliado desativado até definir teto. **Evolução:** reinvestir receita operacional disponível, avaliar editais e apoios públicos de inovação sem apresentar captação de investimento como oferta pública livre de regras; eventual percentual sobre lucros somente após **nova decisão e validações**.

**CONTROLE MANUAL 15.6:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 15.7 | Fases de verificação: 0/1–7

**15.7. Autonomia de produção de documentos.** O proprietário redigirá os pedidos e utilizará os portais oficiais pelo smartphone com auxílio de ChatGPT/Codex onde admitido. O relatório de auditoria do Codex **não é parecer de advogado, laudo do Banco Central, certificado INPI ou aceite do Mercado Pago**. Manual de usuário, modelo de termos de adesão, documentação de API, plano de negócios e checklist de submissões terão versões sob controle no GitHub **apenas após ordem de criação**.

**CONTROLE MANUAL 15.7:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## SEÇÃO 16 — Matriz de auditoria final: aceites, decisões e bloqueios reais


### Cláusula 16.1 | Fases de verificação: 0/7

**16.1. Itens definidos que NÃO devem voltar como perguntas.** Desenvolvimento individual com Android/Termux/ChatGPT/Codex/**GitHub** e prioridade de custo zero; autonomia de cada administrador e regras configuráveis por tenant; precificação mensal editável somente pelo Master e anual **mensal × 10**; separação de licença e fundos; cronograma financeiro fixo; vedação de ingerência Master; nenhuma taxa da plataforma sobre lucro de terceiros foi aprovada. Além destes:  Natureza SaaS de automação e clientes autônomos; três planos mensais/anuais e desconto equivalente a dois meses; **0 dias de tolerância**; receitas de licença separadas; calendário 01/01–31/12, vencimento mensal dia 10, fechamento 31/12 e pagamento elegível 10/01; políticas financeiras por tenant; remuneração do administrador por tenant e 85/15 **somente** na caixinha do proprietário; papéis simultâneos; autorização coletiva anual por ciclo para crédito próprio; ausência de ingerência Master; Pix integrado; bolões próprios como **módulo futuro condicionado** com preço final maior que custo oficial e margem bruta identificada; no máximo quatro campanhas dessa natureza por ano, sem sorteio privado.

**CONTROLE MANUAL 16.1:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.2 | Fases de verificação: 0/7

**16.2. Quatro convenções financeiras complementares — DEFINIDAS E APROVADAS PELO PROPRIETÁRIO em 16/10/2026.** (1) Pagamento parcial: obrigação vencida mais antiga, depois juros remuneratórios → mora simples → multa única → principal, com apropriação registrada por componente (8.6). (2) Centavos: Carteira Administrativa transitória, seguida de distribuição pelos maiores restos com desempate estável, sem receita extra para o administrador (10.4). (3) Empréstimos: primeiro vencimento dia 10 do mês subsequente ao desembolso confirmado; primeiro intervalo proporcional aos dias corridos/30 e Price ajustado, vencimentos seguintes dia 10, dentro do ciclo (8.4–8.5). (4) Rateio: percentuais por tenant fixos durante o ciclo, alterações válidas apenas no próximo ciclo mediante aceites (4.4, 10.8). **Essas quatro matérias não são mais pendências nem propostas a rediscutir.** Também ficam **expressamente aprovadas como requisitos técnicos documentais** as definições já descritas para dia âncora, renovação/upgrade por segmentos, contagem de capacidades, suporte excepcional de 60/30 minutos, backup diário e metas WAL/RPO/RTO condicionadas à infraestrutura, Price comum de até 12 parcelas (seis na caixinha do proprietário), corte diário Capital-Dias ao fim do dia, reservas atômicas, fechamento auditável, cadastro do contratante 3.1-A e cadastro do membro 6.1-A. A aprovação não inventa capacidade comercial, taxa de terceiro ou parâmetro ausente do tenant. **O teto do plano Ampliado permanece indefinido e checkout desativado.**

**Exemplo de conferência (sem substituir o contrato):** Quatro regras financeiras estão APROVADAS e não podem ser esquecidas.

**CONTROLE MANUAL 16.2:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.2-A | Fases de verificação: 0/7

**16.2-A. Limites externos e recursos não liberados pelo aceite documental.** (i) Teto do Ampliado **PENDENTE**: mantém checkout bloqueado; (ii) eventuais custos/limites da hospedagem, aceitação Mercado Pago e formalização fiscal **DEPENDENTES DE EVIDÊNCIA**; (iii) taxa extra da plataforma como percentual dos lucros **EM ESTUDO**: nenhum backend de cobrança, campo de obrigação financeira ou débito será considerado autorizado por este contrato; (iv) bolões com diferença de preço sobre custo oficial **modelo escolhido para demonstração**, operação comercial condicionada; (v) banco digital e ações digitais de comércio/entretenimento **fora do MVP**, exigem novo escopo.

**CONTROLE MANUAL 16.2-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.3 | Fases de verificação: 0/7

**16.3. Condições de ativação real, não bloqueios de codificação ou demonstração.** O projeto **pode ser desenvolvido e testado com dados fictícios após ordem específica**, mesmo enquanto estão sendo obtidos parecer jurídico/tributário, conformidade das políticas de crédito e autorização/homologação técnica e comercial do provedor para Pix IN/OUT. **NÃO ativar movimentações financeiras reais, capturar valores, publicar serviço transacional nem liberar autoempréstimo com consentimento antecipado** antes das avaliações e aprovações aplicáveis. Ações lotéricas exigem adicionalmente todos os gates da seção 14 e continuam fora da primeira entrega. A aprovação deste contrato **não substitui** autorização para efetuar operação real.

**CONTROLE MANUAL 16.3:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.3-A | Fases de verificação: 0/7

**16.3-A. Limite de decisões não documentadas pelo tenant.** O Codex deve implementar **exatamente** as quatro regras expressas em 16.2, sem voltar a classificá-las como indefinidas. **Ainda depende de aceites específicos de cada caixinha**, quando aplicável, qualquer fórmula numérica de limite individual de empréstimo, multa/encargo particular ou outro parâmetro financeiro cuja regra não tenha sido formalizada. A ausência dessa parametrização em um tenant não autoriza o sistema a inventar limites ou valores: negar operação afetada, informar a regra que falta e preservar as funcionalidades independentes. A parte 12 do relatório de auditoria documental foi posteriormente recebida: confirmou os cálculos **ilustrativos**, sem liberar bolões para operação real.

**CONTROLE MANUAL 16.3-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.4 | Fases de verificação: 0/7

**16.4. Cenários de auditoria documental e posterior teste — AT-01 a AT-23, complementados até AT-50.**

| ID | Cenário de prova | Aceite esperado |
|---|---|---|
| **AT-01** | Admin X seleciona 20 membros/40 cotas e mensal | Essencial R$ 89,90; Pix da plataforma; ativar só confirmado |
| **AT-02** | Admin Y seleciona 45 membros/45 cotas e anual | Intermediário R$ 1.099,00 por 12 meses |
| **AT-03** | Solicitação de 60 cotas antes do teto Ampliado | O plano fica `INATIVO`; não gera Pix, nem promete capacidade ilimitada |
| **AT-04** | Licença vence, sem Pix de renovação | Suspender **imediatamente**, manter quitação de dívidas e fechamento |
| **AT-05** | Dois tenants configuram taxas/percentuais distintos | 20%/85-15 na caixinha própria; outra com taxa e 80-20 definidos, sem contaminação |
| **AT-06** | Admin tenta alterar 31/12 ou 10/01 | Negar; calendário central permanece imutável |
| **AT-07** | Admin é membro, todos os outros assinam para 2027 | Autorizar autoaprovação com controles em 2027; renovar anuência para 2028 |
| **AT-08** | Novo membro entra e não assina autorização anual | Bloquear **novos** empréstimos próprios do administrador até anuência válida |
| **AT-09** | Outro administrador acessa extrato de tenant alheio | Negar pela API, sem revelar dados |
| **AT-10** | Master tenta liberar empréstimo de terceiro | Negar, independentemente de suporte ativo |
| **AT-11** | Pix enviado retorna timeout e webhook duplicado | Uma única transferência; pendente até conciliação |
| **AT-12** | Contribuição parcial vence dia 10 | Status financeiro `PARCIAL` e temporal `VENCIDA` simultaneamente |
| **AT-13** | Rateio em caixinha própria e de cliente | Base só de lucro realizado; percentuais por tenant e pesos válidos |
| **AT-14** | Resultado arredondado deixa resíduo | Método dos maiores restos distribui cada centavo elegível; Carteira Administrativa volta a zero para resíduos atribuídos, sem ganho ao administrador |
| **AT-15** | Bolão com 20 cotas a R$ 25 e aposta oficial R$ 150 | **Somente simulação bloqueada**; margem bruta R$ 350 e prêmios separados |
| **AT-16** | Backup restaurado após Pix já executado | Reconciliar; não repetir Pix nem reabrir obrigação quitada |
| **AT-17** | Revogação de suporte com sessão aberta | Acesso cessado imediatamente; logs preservados |
| **AT-18** | Contrato aprovado, porém proprietário não emitiu ordem separada G2 | Nenhuma criação de diretório/repositório, execução, inspeção de código antigo ou alteração de código |
| **AT-19** | Renovação antecipada em mês curto e assinatura vencida | Preserva dia âncora, não perde dias pagos e não concede período vencido retroativo |
| **AT-20** | Upgrade no meio da vigência e downgrade com excesso de cotas | Diferença proporcional transparente e downgrade recusado até caber na faixa |
| **AT-21** | Suporte consentido expira ou emergência ultrapassa 30 min | Revoga sessões e nega acesso, sem poderes financeiros |
| **AT-22** | Outro tenant escolhe Price 10 parcelas, proprietário máximo seis | Permite somente vencimentos dentro do ciclo e conserva versão da política |
| **AT-23** | Backup criptografado e replay financeiro após falha | Comprova RPO/RTO e reconcilia sem duplicar Pix |

**CONTROLE MANUAL 16.4:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.4-A | Fases de verificação: 0/7

**16.4-A. Testes adicionais da auditoria de evolução e licenciamento (AT-24 a AT-31).**

| ID | Cenário de prova | Aceite esperado |
|---|---|---|
| **AT-24** | Master reajusta Essencial de R$ 89,90 para R$ 99,90 | Anual vira automaticamente R$ 999,00; oferta anterior paga imutável; novo cliente usa versão vigente |
| **AT-25** | Tentativa de alterar anuidade sem alterar mensalidade | Negada: anual é derivado mensal × 10; histórico auditado |
| **AT-26** | Administrador/membro tenta usar capacidade lotérica sem gates | Demonstração fictícia disponível ao auditor autorizado; cobranças e sorteios reais impossíveis |
| **AT-27** | Bolão simulado: 20 cotas × R$ 25; custo oficial fictício R$ 150 | Custo R$ 7,50/cota, margem bruta R$ 350; sem Pix real, sem bilhete falso apresentado como oficial |
| **AT-28** | Envio de webhook simulado ou mudança de conta vinculada | Ledger/auditoria conciliados; nenhuma migração entre titulares/tenants por troca de provedor |
| **AT-29** | Provedor alternativo simulado substitui Mercado Pago | Casos de cobrança, devolução e conciliação continuam funcionando pelas interfaces internas, sem alteração na lógica de rateio |
| **AT-30** | Tentativa de abrir conta de pagamento ou depósito sob marca FRcaixinha no MVP | Sistema não oferece custódia própria, emissão de contas ou promessa de autorização bancária |
| **AT-31** | Auditor pede pacote demonstrável antes da autorização comercial | Documentação, fluxos, logs de teste, provas de segurança e status regulatório exportáveis; operação real continua vedada |

**CONTROLE MANUAL 16.4-A:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.4-C | Fases de verificação: 0/7

**16.4-C. Testes de aceite acrescidos nesta versão (AT-32 a AT-44), após futura programação.**

| ID | Verificação | Resultado esperado |
|---|---|---|
| **AT-32** | Repositório do novo FRcaixinha criado após autorização e verificação CI | Novo GitHub próprio, sem histórico de projetos antigos; segredos ausentes do Git e Actions passam |
| **AT-33** | Fluxo completamente operável apenas com smartphone | Termux/Codex, edição, Git, PR e obtenção de APK por GitHub Actions, sem computador |
| **AT-34** | Master muda R$ 109,90 para outro valor mensal | Anual calculado como ×10, não pode ser editado diretamente; preço pago anterior permanece |
| **AT-35** | Um cliente define 30% administrativo e outro 15%, mesma data global | Complementos 70%/85%, políticas próprias fixas no ciclo e alterações somente no ciclo seguinte |
| **AT-36** | Funções de base e bolões auditadas antes de autorização de operação real | Funciona demonstrador completo com dados fictícios; bloqueio de cobranças reais e artefatos marcados |
| **AT-37** | Lançamento sem parecer de crédito nem aceitação do provedor para finalidade específica | Caminhos financeiros reais não habilitados; demonstração e documentação permanecem possíveis |
| **AT-38** | Tentativa de ativar cobrança da plataforma por 1% dos resultados | Negada: tarifa não aprovada; nenhuma dedução de lucro de membros ou split implícito |
| **AT-39** | Manual de administrador e material comercial antes do piloto | Guias reproduzíveis, campos e telas reais conferidos, preço/vigência/capacidades corretos; sem promessas de rendimento |
| **AT-40** | Preparação de CNPJ, marca, registro de software e requerimentos setoriais | Checklist com órgão, documentos, custo/dispensa, prazo, protocolo e status; nenhuma autorização fictícia |
| **AT-41** | Pagamento parcial cobre juros e parte da mora na parcela vencida mais antiga | Componentes segregados; principal não se reduz até sua apropriação efetiva; mora futura usa somente principal ainda aberto |
| **AT-42** | Rateio gera diferenças de R$ 0,01 e empates de restos | Todos os centavos atribuídos a membros elegíveis pelo maior resto e identificador estável; nenhum Pix isolado de centavos |
| **AT-43** | Pix confirma desembolso em 28/02; primeira parcela vence 10/03 | Primeiro período conforme dias reais/30, simulação Price de prestação constante e última corrigida; nenhum vencimento após 31/12 |
| **AT-44** | Administrador altera 15% para 30% durante o ciclo de 2027 | Rateio de 2027 usa 15%; 30% só poderá valer no ciclo de 2028 após o aceite aplicável |

**CONTROLE MANUAL 16.4-C:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.4-E | Fases de verificação: 0/7

**16.4-E. Testes de cadastro e vínculos incorporados após aprovação dos itens 3.1-A e 6.1-A (AT-45 a AT-50).**

| ID | Cenário | Aceite esperado |
|---|---|---|
| **AT-45** | Pessoa física cadastra nome/CPF/e-mail/telefone e não informa foto nem endereço sem necessidade fiscal | Cadastro válido com e-mail confirmado, foto opcional, endereço condicionado; licença inativa até aceite/Pix confirmado |
| **AT-46** | Contratação PJ com razão social, CNPJ e representante identificado | CPF/CNPJ validados; representante autorizado; identidade e titular contratual separados do tenant e da licença; sem ativação indevida |
| **AT-47** | Identidade com CPF inválido, e-mail não confirmado ou tentativas de recuperação de conta abusivas | Rejeitar cadastro/ação afetada; credenciais protegidas, sem confirmação falsa, auditoria minimizada e recuperação segura |
| **AT-48** | Administrador convida pessoa para a caixinha; convidado não aceita contrato/ciclo | Sem acesso financeiro nem participação ativa antes de autenticação/aceite/ativação; convite não consome capacidade da licença |
| **AT-49** | Pessoa participa legitimamente de dois tenants e é administradora em um deles | Uma identidade, vínculos independentes, papéis explícitos; CPF, extratos, cotas e dívidas isolados; sem privilégios de autoempréstimo |
| **AT-50** | Membro troca/remove foto, atualiza contato e informa chave Pix apenas para operação autorizada | Foto opcional e removível; minimização/LGPD; revalidação de contato quando necessária; chave/destinatário protegidos sem exposição de terceiros |

**CONTROLE MANUAL 16.4-E:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.4-D | Fases de verificação: 0/7

**16.4-D. Auditoria do código efetivamente existente.** Neste marco do FRcaixinha 2.2 **não há aplicativo, diretório novo nem repositório implementado** a auditar. Os testes de arquitetura aqui são **exigências futuras**, não evidência de código existente. Nenhuma análise de projetos antigos substitui a avaliação deste projeto novo. Em futura auditoria de implementação, verificar somente o repositório criado após ordem expressa e registrar versões e artefatos examinados.

**CONTROLE MANUAL 16.4-D:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


### Cláusula 16.5 | Fases de verificação: 0/7

**16.5. Estado deste documento — APROVADO PARA DESENVOLVIMENTO, NÃO PARA EXECUÇÃO AUTOMÁTICA.** O proprietário aprovou expressamente em 16/10/2026 as quatro convenções financeiras, os cadastros 3.1-A e 6.1-A, todas as demais propostas técnicas **já definidas** na especificação e a versão final deste Contrato Técnico Mestre como fonte única de desenvolvimento. A aprovação resolve o **gate G1** e permite que este documento oriente o futuro Codex **somente após ordem G2, separada e expressa**, para criar projeto/repositório e iniciar programação. O relatório documental do Codex foi recebido integralmente, incluindo a parte 12. **Não ficam autorizados** pagamentos reais, empréstimos reais, bolões reais, despesas/infraestrutura paga, novo módulo sem escopo, tarifa da plataforma sobre lucro alheio, ativação comercial do Ampliado sem teto ou qualquer operação condicionada a leis/provedores. Os gates jurídicos, de Mercado Pago, disponibilidade e infraestrutura/backup continuam independentes. A aprovação documental do proprietário não equivale a assinatura eletrônica dos usuários finais nem parecer jurídico.

---

### DECLARAÇÃO DE PARADA E CONTROLE DE VERSÃO

Este documento contém a **especificação técnica mestre final aprovada pelo proprietário na conversa de 16/10/2026**, mas não instrumento assinado por membros, administradores contratantes ou terceiros; não constitui parecer jurídico, homologação financeira, autorização bancária ou aceite formal de um provedor. A redação de contratos de adesão, integração real e os controles operacionais continuam sujeitos aos requisitos legais e aos gates próprios. Nenhum diretório de produção, repositório, banco, hospedagem, integração ativa, cobrança Pix, empréstimo ou bolão foi criado nesta revisão documental. **G1 aprovado; não iniciar programação/infraestrutura até ordem G2 expressa e separada.**

**CONTROLE MANUAL 16.5:** ☐ N/I  ☐ AND  ☐ PASS  ☐ FAIL  ☐ BLOQ  ☐ N/A justificado  |  **Teste/artefato:** ______________________  **Commit/data:** ______________________
**Verificação do responsável:** _____________________________  **Observação/correção:** ___________________________________________________


## Fecho literal do contrato

**Conferência da Parte IV:** 147 cláusulas numeradas transcritas, das seções 1 a 16. Contagem calculada mecanicamente da versão aprovada. Nenhum PASS foi pré-assinalado.

# PARTE V — MATRIZ INDIVIDUAL DE 50 TESTES DE ACEITE

**Fonte:** tabelas AT-01 a AT-50 do §16.4 e subseções. Estes cenários são testes exigidos no contrato, e não evidências de testes já realizados.** Preencher saída real e SHA do commit/artefato. Para cenários condicionados, manter o bloqueio regulatório e validar o demonstrador sem dinheiro real.

### AT-01 — Verificação do contrato

**Cenário aprovado:** Admin X seleciona 20 membros/40 cotas e mensal  
**Resultado esperado contratual:** Essencial R$ 89,90; Pix da plataforma; ativar só confirmado  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-02 — Verificação do contrato

**Cenário aprovado:** Admin Y seleciona 45 membros/45 cotas e anual  
**Resultado esperado contratual:** Intermediário R$ 1.099,00 por 12 meses  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-03 — Verificação do contrato

**Cenário aprovado:** Solicitação de 60 cotas antes do teto Ampliado  
**Resultado esperado contratual:** O plano fica `INATIVO`; não gera Pix, nem promete capacidade ilimitada  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-04 — Verificação do contrato

**Cenário aprovado:** Licença vence, sem Pix de renovação  
**Resultado esperado contratual:** Suspender **imediatamente**, manter quitação de dívidas e fechamento  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-05 — Verificação do contrato

**Cenário aprovado:** Dois tenants configuram taxas/percentuais distintos  
**Resultado esperado contratual:** 20%/85-15 na caixinha própria; outra com taxa e 80-20 definidos, sem contaminação  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-06 — Verificação do contrato

**Cenário aprovado:** Admin tenta alterar 31/12 ou 10/01  
**Resultado esperado contratual:** Negar; calendário central permanece imutável  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-07 — Verificação do contrato

**Cenário aprovado:** Admin é membro, todos os outros assinam para 2027  
**Resultado esperado contratual:** Autorizar autoaprovação com controles em 2027; renovar anuência para 2028  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-08 — Verificação do contrato

**Cenário aprovado:** Novo membro entra e não assina autorização anual  
**Resultado esperado contratual:** Bloquear **novos** empréstimos próprios do administrador até anuência válida  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-09 — Verificação do contrato

**Cenário aprovado:** Outro administrador acessa extrato de tenant alheio  
**Resultado esperado contratual:** Negar pela API, sem revelar dados  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-10 — Verificação do contrato

**Cenário aprovado:** Master tenta liberar empréstimo de terceiro  
**Resultado esperado contratual:** Negar, independentemente de suporte ativo  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-11 — Verificação do contrato

**Cenário aprovado:** Pix enviado retorna timeout e webhook duplicado  
**Resultado esperado contratual:** Uma única transferência; pendente até conciliação  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-12 — Verificação do contrato

**Cenário aprovado:** Contribuição parcial vence dia 10  
**Resultado esperado contratual:** Status financeiro `PARCIAL` e temporal `VENCIDA` simultaneamente  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-13 — Verificação do contrato

**Cenário aprovado:** Rateio em caixinha própria e de cliente  
**Resultado esperado contratual:** Base só de lucro realizado; percentuais por tenant e pesos válidos  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-14 — Verificação do contrato

**Cenário aprovado:** Resultado arredondado deixa resíduo  
**Resultado esperado contratual:** Método dos maiores restos distribui cada centavo elegível; Carteira Administrativa volta a zero para resíduos atribuídos, sem ganho ao administrador  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-15 — Verificação do contrato

**Cenário aprovado:** Bolão com 20 cotas a R$ 25 e aposta oficial R$ 150  
**Resultado esperado contratual:** **Somente simulação bloqueada**; margem bruta R$ 350 e prêmios separados  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-16 — Verificação do contrato

**Cenário aprovado:** Backup restaurado após Pix já executado  
**Resultado esperado contratual:** Reconciliar; não repetir Pix nem reabrir obrigação quitada  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-17 — Verificação do contrato

**Cenário aprovado:** Revogação de suporte com sessão aberta  
**Resultado esperado contratual:** Acesso cessado imediatamente; logs preservados  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-18 — Verificação do contrato

**Cenário aprovado:** Contrato aprovado, porém proprietário não emitiu ordem separada G2  
**Resultado esperado contratual:** Nenhuma criação de diretório/repositório, execução, inspeção de código antigo ou alteração de código  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-19 — Verificação do contrato

**Cenário aprovado:** Renovação antecipada em mês curto e assinatura vencida  
**Resultado esperado contratual:** Preserva dia âncora, não perde dias pagos e não concede período vencido retroativo  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-20 — Verificação do contrato

**Cenário aprovado:** Upgrade no meio da vigência e downgrade com excesso de cotas  
**Resultado esperado contratual:** Diferença proporcional transparente e downgrade recusado até caber na faixa  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-21 — Verificação do contrato

**Cenário aprovado:** Suporte consentido expira ou emergência ultrapassa 30 min  
**Resultado esperado contratual:** Revoga sessões e nega acesso, sem poderes financeiros  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-22 — Verificação do contrato

**Cenário aprovado:** Outro tenant escolhe Price 10 parcelas, proprietário máximo seis  
**Resultado esperado contratual:** Permite somente vencimentos dentro do ciclo e conserva versão da política  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-23 — Verificação do contrato

**Cenário aprovado:** Backup criptografado e replay financeiro após falha  
**Resultado esperado contratual:** Comprova RPO/RTO e reconcilia sem duplicar Pix  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-24 — Verificação do contrato

**Cenário aprovado:** Master reajusta Essencial de R$ 89,90 para R$ 99,90  
**Resultado esperado contratual:** Anual vira automaticamente R$ 999,00; oferta anterior paga imutável; novo cliente usa versão vigente  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-25 — Verificação do contrato

**Cenário aprovado:** Tentativa de alterar anuidade sem alterar mensalidade  
**Resultado esperado contratual:** Negada: anual é derivado mensal × 10; histórico auditado  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-26 — Verificação do contrato

**Cenário aprovado:** Administrador/membro tenta usar capacidade lotérica sem gates  
**Resultado esperado contratual:** Demonstração fictícia disponível ao auditor autorizado; cobranças e sorteios reais impossíveis  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-27 — Verificação do contrato

**Cenário aprovado:** Bolão simulado: 20 cotas × R$ 25; custo oficial fictício R$ 150  
**Resultado esperado contratual:** Custo R$ 7,50/cota, margem bruta R$ 350; sem Pix real, sem bilhete falso apresentado como oficial  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-28 — Verificação do contrato

**Cenário aprovado:** Envio de webhook simulado ou mudança de conta vinculada  
**Resultado esperado contratual:** Ledger/auditoria conciliados; nenhuma migração entre titulares/tenants por troca de provedor  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-29 — Verificação do contrato

**Cenário aprovado:** Provedor alternativo simulado substitui Mercado Pago  
**Resultado esperado contratual:** Casos de cobrança, devolução e conciliação continuam funcionando pelas interfaces internas, sem alteração na lógica de rateio  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-30 — Verificação do contrato

**Cenário aprovado:** Tentativa de abrir conta de pagamento ou depósito sob marca FRcaixinha no MVP  
**Resultado esperado contratual:** Sistema não oferece custódia própria, emissão de contas ou promessa de autorização bancária  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-31 — Verificação do contrato

**Cenário aprovado:** Auditor pede pacote demonstrável antes da autorização comercial  
**Resultado esperado contratual:** Documentação, fluxos, logs de teste, provas de segurança e status regulatório exportáveis; operação real continua vedada  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-32 — Verificação do contrato

**Cenário aprovado:** Repositório do novo FRcaixinha criado após autorização e verificação CI  
**Resultado esperado contratual:** Novo GitHub próprio, sem histórico de projetos antigos; segredos ausentes do Git e Actions passam  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-33 — Verificação do contrato

**Cenário aprovado:** Fluxo completamente operável apenas com smartphone  
**Resultado esperado contratual:** Termux/Codex, edição, Git, PR e obtenção de APK por GitHub Actions, sem computador  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-34 — Verificação do contrato

**Cenário aprovado:** Master muda R$ 109,90 para outro valor mensal  
**Resultado esperado contratual:** Anual calculado como ×10, não pode ser editado diretamente; preço pago anterior permanece  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-35 — Verificação do contrato

**Cenário aprovado:** Um cliente define 30% administrativo e outro 15%, mesma data global  
**Resultado esperado contratual:** Complementos 70%/85%, políticas próprias fixas no ciclo e alterações somente no ciclo seguinte  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-36 — Verificação do contrato

**Cenário aprovado:** Funções de base e bolões auditadas antes de autorização de operação real  
**Resultado esperado contratual:** Funciona demonstrador completo com dados fictícios; bloqueio de cobranças reais e artefatos marcados  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-37 — Verificação do contrato

**Cenário aprovado:** Lançamento sem parecer de crédito nem aceitação do provedor para finalidade específica  
**Resultado esperado contratual:** Caminhos financeiros reais não habilitados; demonstração e documentação permanecem possíveis  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-38 — Verificação do contrato

**Cenário aprovado:** Tentativa de ativar cobrança da plataforma por 1% dos resultados  
**Resultado esperado contratual:** Negada: tarifa não aprovada; nenhuma dedução de lucro de membros ou split implícito  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-39 — Verificação do contrato

**Cenário aprovado:** Manual de administrador e material comercial antes do piloto  
**Resultado esperado contratual:** Guias reproduzíveis, campos e telas reais conferidos, preço/vigência/capacidades corretos; sem promessas de rendimento  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-40 — Verificação do contrato

**Cenário aprovado:** Preparação de CNPJ, marca, registro de software e requerimentos setoriais  
**Resultado esperado contratual:** Checklist com órgão, documentos, custo/dispensa, prazo, protocolo e status; nenhuma autorização fictícia  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-41 — Verificação do contrato

**Cenário aprovado:** Pagamento parcial cobre juros e parte da mora na parcela vencida mais antiga  
**Resultado esperado contratual:** Componentes segregados; principal não se reduz até sua apropriação efetiva; mora futura usa somente principal ainda aberto  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-42 — Verificação do contrato

**Cenário aprovado:** Rateio gera diferenças de R$ 0,01 e empates de restos  
**Resultado esperado contratual:** Todos os centavos atribuídos a membros elegíveis pelo maior resto e identificador estável; nenhum Pix isolado de centavos  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-43 — Verificação do contrato

**Cenário aprovado:** Pix confirma desembolso em 28/02; primeira parcela vence 10/03  
**Resultado esperado contratual:** Primeiro período conforme dias reais/30, simulação Price de prestação constante e última corrigida; nenhum vencimento após 31/12  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-44 — Verificação do contrato

**Cenário aprovado:** Administrador altera 15% para 30% durante o ciclo de 2027  
**Resultado esperado contratual:** Rateio de 2027 usa 15%; 30% só poderá valer no ciclo de 2028 após o aceite aplicável  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-45 — Verificação do contrato

**Cenário aprovado:** Pessoa física cadastra nome/CPF/e-mail/telefone e não informa foto nem endereço sem necessidade fiscal  
**Resultado esperado contratual:** Cadastro válido com e-mail confirmado, foto opcional, endereço condicionado; licença inativa até aceite/Pix confirmado  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-46 — Verificação do contrato

**Cenário aprovado:** Contratação PJ com razão social, CNPJ e representante identificado  
**Resultado esperado contratual:** CPF/CNPJ validados; representante autorizado; identidade e titular contratual separados do tenant e da licença; sem ativação indevida  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-47 — Verificação do contrato

**Cenário aprovado:** Identidade com CPF inválido, e-mail não confirmado ou tentativas de recuperação de conta abusivas  
**Resultado esperado contratual:** Rejeitar cadastro/ação afetada; credenciais protegidas, sem confirmação falsa, auditoria minimizada e recuperação segura  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-48 — Verificação do contrato

**Cenário aprovado:** Administrador convida pessoa para a caixinha; convidado não aceita contrato/ciclo  
**Resultado esperado contratual:** Sem acesso financeiro nem participação ativa antes de autenticação/aceite/ativação; convite não consome capacidade da licença  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-49 — Verificação do contrato

**Cenário aprovado:** Pessoa participa legitimamente de dois tenants e é administradora em um deles  
**Resultado esperado contratual:** Uma identidade, vínculos independentes, papéis explícitos; CPF, extratos, cotas e dívidas isolados; sem privilégios de autoempréstimo  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

### AT-50 — Verificação do contrato

**Cenário aprovado:** Membro troca/remove foto, atualiza contato e informa chave Pix apenas para operação autorizada  
**Resultado esperado contratual:** Foto opcional e removível; minimização/LGPD; revalidação de contato quando necessária; chave/destinatário protegidos sem exposição de terceiros  
☐ PASS ☐ FAIL ☐ BLOQ ☐ NOT_RUN ☐ N/A justificado | **Resultado real:** ______________________ | **Evidência/log:** ______________________ | **SHA:** ______________________ | **Data:** __________
**Ocorrência e decisão do responsável:** ___________________________________________________________________________________________

# PARTE VI — NORMAS INTEGRAIS DE EXECUÇÃO (DOCUMENTO MESTRE DE INSTRUÇÕES)

**Este é o segundo documento normativo, complementar e subordinado ao Contrato Técnico Mestre. A íntegra abaixo evita omitir diretrizes de repositório único, banco único, diagnóstico, backup, orçamento e operação no smartphone.**

---

# FRCAIXINHA 2.2

## DOCUMENTO MESTRE DE INSTRUÇÕES E GOVERNANÇA DO DESENVOLVIMENTO

**Versão:** 1.0 — 16/10/2026  
**Natureza:** instruções operacionais permanentes para ChatGPT, Codex e execução técnica pelo proprietário.  
**Referência normativa principal:** `FRcaixinha_2_2_Contrato_Tecnico_Mestre_FINAL_APROVADO_2026-10-16.md`.  
**Estado do contrato:** G1 — APROVADO em 16/10/2026.  
**Estado da implementação:** G2 — NÃO AUTORIZADO; programação e criação de diretório/repositório ainda não iniciadas.  
**Finalidade:** consolidar o método de trabalho, prevenir erros conhecidos e garantir fidelidade ao Contrato Técnico Mestre. Este documento **não o substitui** nem concede permissões financeiras ou operacionais.

> **MANDAMENTO CENTRAL:** Um diretório raiz; uma base PostgreSQL autoritativa no ambiente de desenvolvimento; nenhuma falha bloqueante ignorada; backups recuperáveis e verificáveis; nenhuma ferramenta duplicada sem necessidade; nenhuma ação fora da autorização expressa.

---

## 1. IDENTIDADE, MISSÃO E PRINCÍPIOS

O FRcaixinha 2.2 é um SaaS de automação de caixinhas privadas, com administradores independentes, membros, cotas, contribuições, empréstimos internos, liquidação, apuração, rateio e prestação de contas, estritamente nos limites aprovados.

ChatGPT e Codex devem atuar como assistência de arquitetura, implementação, testes, diagnóstico, revisão e documentação; o proprietário conserva a decisão final sobre contrato, finanças, despesas, operações reais e prioridades.

A ordem de prioridades é: **integridade financeira e direitos > segurança e conformidade > fidelidade ao contrato > testes e evidências > continuidade > economia de recursos > velocidade**.

Usar português brasileiro claro. Orientar procedimentos executáveis pelo smartphone Android, sem presumir disponibilidade de computador.

## 2. CONTRATO TÉCNICO MESTRE E HIERARQUIA DAS DECISÕES

1. Consultar a versão final aprovada do Contrato Técnico Mestre como **fonte autoritativa dos requisitos**, incluindo suas 16 seções e 50 cenários AT-01 a AT-50.
2. O Markdown aprovado é a fonte textual canônica; DOCX e PDF são exportações. Não tratar outra minuta, conversa parcial ou resumo como substituto do documento final.
3. Em caso de diferença entre instrução operacional e requisito técnico aprovado, prevalece o contrato; comunicar a inconsistência antes de executar a etapa afetada.
4. Não reabrir decisões fechadas sem inconsistência comprovada, alteração legal pertinente ou solicitação expressa do proprietário.
5. Uma mudança de regra exige registro de origem, justificativa, impacto financeiro/técnico, redação proposta, autorização, versão documental, implementação e teste correspondente.
6. Não inventar regras, percentuais, limites, datas, campos, tolerâncias, poderes de usuários ou efeitos financeiros para preencher lacunas. Quando faltar um requisito necessário, registrar bloqueio pontual; outras tarefas independentes podem prosseguir se autorizadas e seguras.
7. Exigir rastreabilidade **cláusula → requisito → tela/API/tabela → teste → evidência**. Não confiar somente em explicações verbais ou em memória da conversa quando for preciso conferir a redação literal.

## 3. GATES, AUTORIZAÇÃO E AÇÕES VEDADAS

**G1 (aprovação documental): concluído. G2 (ordem de criar o projeto e iniciar programação): ainda não autorizado.** A aprovação do contrato não equivale a executar G2.

Até nova ordem expressa: apenas análise, auditoria, planejamento e documentação solicitados. **Não** criar `~/FRcaixinha_2.2`, repositório, serviço, banco, migrations, código, CI ou infraestrutura como consequência automática deste documento.

Após G2, executar somente o escopo aprovado, etapa por etapa. Antes de alterações com risco ou custo, apresentar efeito, alternativas, reversibilidade e autorização necessária. Não abrir conta paga, contratar nuvem, consumir recursos faturáveis, publicar produção nem efetuar transferências de valor por presunção.

Gates independentes após G2: disponibilidade e segurança do ambiente; testes/homologação do código; capacidade efetivamente aceita pelo provedor; validação jurídica/tributária quando aplicável; publicação e dinheiro real; eventuais recursos lotéricos. Uma aprovação não supre outra.

## 4. PROJETO NOVO E SEGREGAÇÃO DO LEGADO

O FRcaixinha 2.2 é desenvolvido **do zero**, sem cópia ou migração implícita de projetos anteriores. É vedado reutilizar sem autorização específica: código, estrutura ativa, migrations, banco, repositório, tokens, chaves, credenciais, artefatos ou identidades financeiras antigas.

Os problemas observados anteriormente são **lições de prevenção**, e não justificativa para herdar sistemas velhos. Não procurar diretórios antigos automaticamente nem criar um segundo ambiente de trabalho para acelerar correções.

## 5. AMBIENTE ANDROID E COMPATIBILIDADE DE FERRAMENTAS

Ambiente previsto: Android + Termux; Debian PRoot **somente quando necessário**; ChatGPT e Codex; Git/GitHub/GitHub Actions; Flutter/Dart (Android); FastAPI/Python; PostgreSQL/SQLAlchemy/Alembic; integração Mercado Pago nas capacidades validadas.

Antes de instalar ou executar, identificar local do comando (Termux, Debian PRoot, GitHub Actions), arquitetura da CPU, shell, versão de Python/Dart/Flutter/Java/Gradle/Kotlin/AGP/SDK e estado real das ferramentas. **Não presumir** que um SDK de desktop funcione nativamente no Android ARM64.

Reutilizar instalações compatíveis; não manter várias versões e ambientes virtuais paralelos sem justificativa. Compilação Android pode ser verificada por CI autorizado em vez de instalar SDKs incompatíveis no celular. Diagnosticar falhas de compatibilidade antes de qualquer reinstalação.

## 6. COMANDOS, EXECUÇÃO GRADUAL E DIAGNÓSTICO

Fornecer comandos completos, no diretório e ambiente corretos, com pré-condições, resultado esperado, risco e forma de validação. Explicar onde copiar e colar e aguardar a saída real quando ela decidir o próximo passo.

Não mascarar erros, supor que um comando foi executado ou declarar êxito apenas porque a instrução foi enviada. Preferir correções pequenas e reversíveis.

**Comandos destrutivos ou de alto risco são proibidos sem justificativa, backup verificável e autorização específica**, incluindo `rm -rf`, `git reset --hard`, `git clean -fd`, `git push --force`, limpeza irrestrita de caches e exclusão de bancos/tabelas.

## 7. GIT, GITHUB, CI E HISTÓRICO REPRODUZÍVEL

Após G2, usar **um repositório novo e próprio**, com branches rastreáveis e commits pequenos. Antes de modificar, verificar raiz, branch, `git status`, commit-base/SHA, arquivos não rastreados e diffs.

Não usar `git add .` indiscriminadamente; adicionar somente arquivos examinados. Não fazer merge, rebase destrutivo, force-push ou publicação sem autorização. Distinguir arquivo gerado, build, cache, artefato de entrega, segredo e fonte versionável.

CI deve conferir sintaxe, lint/análise estática, testes, segurança, integridade de migrations e APK quando aplicável. Verificar versão exata de toolchains e plugins, sem alterar dependências por tentativa e erro. Uma falha no CI deve ser diagnosticada com o log da execução/commit correspondente. Nunca anunciar CI verde sem evidência do job concluído.

Git local e GitHub contribuem para versionamento, **mas não substituem backup recuperável do banco, arquivos não versionados e configurações protegidas**.

## 8. ARQUITETURA MODULAR E DADOS AUTORITATIVOS

Arquitetura modular sem microserviços prematuros. Separar identidade/permissões, contratação/licenças, caixinhas/políticas, membros/cotas/contribuições, empréstimos, ledger/conciliação, Pix/adaptadores, fechamento, evidências e auditoria.

Backend FastAPI é a fonte de decisões de negócio, autorização, cálculos e saldos. Flutter mostra informações e aciona fluxos, mas não se torna autoridade para registrar quitação, aprovar crédito, liberar Pix ou atribuir lucro.

Persistir dados financeiros com aritmética decimal exata; exigir transações, concorrência segura, unicidades, FKs, auditoria e integridade de migrations. Não modificar registros financeiros confirmados silenciosamente: usar estorno/ajuste rastreável e conciliação.

**Uma única base PostgreSQL autoritativa de desenvolvimento** é a regra. O isolamento de cada caixinha é lógico por `tenant_id` e `cycle_id`, não por um banco diferente para cada cliente. Proibir múltiplas bases persistentes de desenvolvimento ou cópias concorrentes dos mesmos lançamentos.

Testes não podem comprometer a base de desenvolvimento: usar transações revertidas ou isolamento tecnicamente seguro; dados sintéticos e ambientes efêmeros devem ser explicitamente delimitados. Separações efetivamente necessárias entre desenvolvimento, homologação e produção requerem justificativa, autorização e isolamento rigoroso, sem partilhar dados reais ou contrariar os gates do contrato.

## 9. REGRAS FINANCEIRAS: IMPLEMENTAÇÃO LITERAL E AUDITÁVEL

Jamais universalizar regras particulares da caixinha do proprietário. Cada administrador configura políticas contratualmente permitidas e aceitas, preservando isolamento, versões e direitos do ciclo.

Parâmetros específicos da caixinha do proprietário: remuneração administrativa **15%** do lucro líquido elegível e membros **85%**; juros remuneratórios contratuais **20% a.m.** com sistema Price e **até seis parcelas**; outras regras conforme contrato. Motor comum Price pode admitir **1 a 12 parcelas** somente dentro do ciclo, quando legal e contratualmente válidas.

Convenções aprovadas, obrigatórias e **não sujeitas a reinvenção**:

1. **Pagamento parcial:** aplicar à parcela vencida mais antiga; dentro dela, juros remuneratórios vencidos → mora simples acumulada → multa única → principal vencido. Segregar componentes e amortizar somente o principal efetivamente recebido.
2. **Centavos:** registrar resíduo em Carteira Administrativa técnica segregada, sem transformá-lo em receita do administrador; distribuir pelo método dos **maiores restos**, com desempate estável e trilha auditável, sem Pix individual desnecessário de centavos.
3. **Primeiro vencimento:** dia **10 do mês seguinte à efetiva liberação confirmada**; primeira incidência proporcional aos dias corridos, com mês financeiro de 30 dias e Price ajustado; demais vencimentos no dia 10, respeitando o ciclo.
4. **Percentuais de rateio:** `admin_pct` e `member_pct` fixos durante o ciclo anual, alteração somente para ciclo futuro com aceites pertinentes.

Na caixinha particular, aplicar multa única de R$ 10 quando incidir nos termos contratados e mora **simples** de `20%/30` ao dia sobre principal vencido efetivamente não pago, sem capitalização. Não cobrar juros remuneratórios futuros na quitação antecipada. Contribuições não recebidas/conciliadas não são capital disponível.

No fechamento, separar capital devolvível, resultado realizado elegível, remuneração administrativa, obrigações pendentes, reservas e resíduos, sem confundir saldo de ledger com dinheiro custodial próprio.

## 10. PIX, CONCILIAÇÃO, IDEMPOTÊNCIA E PROVEDORES

Separar receitas de licenças da plataforma e dinheiro dos tenants; jamais misturar comerciantes ou contas. Dinheiro de caixinha em provedor é dinheiro real e depende de titularidade, autorização e capacidade aprovada.

Não tratar QR gerado, print ou webhook isolado como pagamento confirmado. Conciliar valor, destinatário, origem, obrigação, finalidade, conta, idempotência, provedor e estado autoritativo.

Webhooks duplicados/fora de ordem não podem duplicar efeitos. Um empréstimo não pode ser desembolsado duas vezes. Timeout ou envio ambíguo implica estado pendente e consulta ao provedor **antes** de qualquer repetição. A restauração de backup também exige reconciliação externa antes de retomar Pix.

Validar na documentação oficial vigente do Mercado Pago todos os endpoints, assinatura de webhooks, OAuth/Connect, cobrança e capacidade de saída Pix por finalidade. Não presumir funcionalidades pelo nome de um produto ou por exemplos de API.

Nenhum dinheiro real em DEMO/HOMOLOGAÇÃO; credenciais e dados de teste separados de produção.

## 11. IDENTIDADES, PERFIS, SEGURANÇA E LGPD

Uma identidade pessoal por indivíduo; múltiplos papéis explícitos (`MASTER`, `TENANT_ADMIN`, `TENANT_MEMBER`) e associações independentes por tenant/ciclo. Verificar toda permissão **no backend**, mesmo quando botão ou tela estiver oculto.

Respeitar integralmente **3.1-A (cadastro do Administrador Contratante)** e **6.1-A (cadastro do Membro)**: identificação, nome, CPF, e-mail confirmado, telefone com DDD, endereço quando necessário, foto opcional, validações, aceites e evidências de autenticação; PJ e representante quando aplicável.

O Master não tem acesso arbitrário aos extratos e finanças das caixinhas de terceiros. Acesso excepcional de suporte exige escopo, duração, justificativa, autorização e revogação, sem conferir poderes financeiros indevidos.

Minimizar coleta e exposição de dados. Nunca mostrar segredos, CPFs integrais desnecessariamente, tokens, chaves privadas, senhas, `.env`, credenciais, dados pessoais reais ou chaves de assinatura em código, logs, respostas ou repositórios públicos.

## 12. TESTES OBRIGATÓRIOS, REGRESSÃO E CRITÉRIOS DE ACEITE

Cada requisito implementado deve possuir identificador contratual, critério de aceite, caso de teste e evidência reproduzível. Conferir a matriz **AT-01 a AT-50**; testes adicionais são permitidos quando exigidos por risco real e **não alteram as regras de negócio**.

Cobertura mínima proporcional ao risco: caso normal; inválidos e limites; autorização e isolamento; concorrência; duplicação/idempotência; reversões; truncamento e arredondamento; datas e fuso `America/Belem`; pagamentos parciais e atrasos; simulação/Price; restauração e conciliação; integração Flutter→API.

Classificar execução com `PASS`, `FAIL`, `BLOCKED` ou `NOT_RUN` e explicar evidência. **Não declarar PASS em teste que não rodou**. Não apagar teste falho ou adulterar expectativa financeira para produzir resultado verde.

## 13. INTERFACE, DOCUMENTAÇÃO E EXPERIÊNCIA DO USUÁRIO

Construir telas simples, acessíveis e coerentes com os perfis reais. Para cada tela: entrada, validações, máscara necessária, estados, botões, ações, permissões, erro, carregamento, retry seguro e confirmação legítima. Não mostrar “pago” quando somente solicitado.

Exibir preços, cotas, juros, valores totais, recibos, histórico, período, políticas e versões aceitas na fase correta. Não inventar funcionalidades por ornamentação visual.

Manter documentação de API, modelo de dados, manual do administrador e orientações operacionais sincronizados ao código testado. O manual deve refletir as telas reais, não protótipos ou promessas.

## 14. FRONTEIRA JURÍDICA, PLANOS E RECURSOS FUTUROS

O FRcaixinha 2.2 é inicialmente software, não banco digital, instituição de pagamento nem custodiante por presunção. O uso real de crédito e pagamentos depende dos requisitos específicos e das autorizações aplicáveis.

**Plano Ampliado:** ainda sem teto de membros/cotas; **checkout e ativação bloqueados** até decisão específica. Não atribuir capacidade infinita ou inventar limites.

**Tarifa adicional da plataforma sobre lucros de tenants:** EM ESTUDO, sem implementação ou cobrança aprovada. Não confundir com o percentual administrativo contratado dentro de cada caixinha.

**Bolões oficiais:** escopo demonstrativo/futuro com dados fictícios e gates jurídicos/provedor próprios, fora do núcleo de 60 dias úteis. Nenhuma aposta, prêmio, cobrança real ou divulgação de bilhete fictício como oficial.

**Banco digital, crédito externo, consórcios, sorteios privados, marketplace e custódia própria:** fora do núcleo aprovado; não acrescentar silenciosamente. Os 60 dias úteis são estimativa, não compromisso de prazo.

## 15. CONTINUIDADE DE TRABALHO ENTRE CONVERSAS E ETAPAS

Antes de retomar qualquer etapa, identificar: autorização válida; objetivo; último checkpoint; arquivo/commit/branch; versão do contrato; banco/migration; testes e status; backups; pendências e próxima ação.

Não afirmar execução de algo apenas porque um comando foi recomendado. Não recomeçar o planejamento a cada chat. Não avançar usando resultados presumidos, nem repetir tarefas concluídas sem motivo técnico.

Registros de checkpoint devem distinguir `CONCLUÍDO`, `EM ANDAMENTO`, `BLOCKED`, `NÃO INICIADO` e `NÃO AUTORIZADO`, anexando prova sempre que disponível.

## 16. PADRÃO DAS RESPOSTAS DE CHATGPT E CODEX

Distinguir fato observado, suposição, proposta, risco, decisão do proprietário, comando fornecido e resultado efetivamente validado.

Explicar causa e consequência, priorizar solução mínima, perguntar apenas o indispensável e respeitar a capacidade de trabalho pelo celular.

Nunca afirmar que migração, commit, PR, execução de teste, Pix, backup ou build foi realizado sem a evidência correspondente. Não declarar etapa concluída enquanto houver bloqueio relevante conhecido.

O Codex é executor e auditor técnico, **não** autor comercial, jurídico ou financeiro de novas regras. Uma melhoria técnica não autoriza alterar o contrato.

## 17. ORGANIZAÇÃO ÚNICA, BANCO AUTORITATIVO, CORREÇÃO E BACKUPS

### 17.1. Um único diretório raiz

Após **G2**, todo o projeto deverá existir em **`~/FRcaixinha_2.2`**, com subpastas necessárias como `mobile/`, `backend/`, `docs/`, testes e `.github/`. A organização lógica não justifica duas árvores ativas, forks locais concorrentes ou diretórios de “versão corrigida”.

O repositório deve apontar para o mesmo diretório autorizado. Diretórios efêmeros de build/CI ou backups externos de recuperação **não** constituem novas árvores ativas de desenvolvimento.

### 17.2. Uma única base PostgreSQL autoritativa

Usar **uma base PostgreSQL autoritativa no desenvolvimento**, com segregação multi-tenant por identificadores e vínculos seguros. Não criar bancos persistentes paralelos, bases duplicadas de testes sem justificativa ou fontes de verdade divergentes.

Versionar mudanças com Alembic; examinar `down_revision`, dependências, constraints, histórico e resultado de `upgrade`/verificação. Testar de modo transacional ou isolado, sem poluir a base autoritativa. Ambientes de produção e homologação, quando forem indispensáveis, terão isolamento próprio, justificativa e autorização; **nunca usar dados reais em testes**.

### 17.3. Erro encontrado: parar, corrigir e depois avançar

Procedimento obrigatório na **etapa afetada**:

1. **Reproduzir:** obter comando, contexto, log e comportamento esperado.
2. **Diagnosticar:** identificar causa-raiz, ambiente, versões, dados envolvidos e alcance do impacto.
3. **Preservar:** fazer backup/checkpoint antes da mudança de risco.
4. **Corrigir:** executar a menor alteração tecnicamente segura, sem modificar regra aprovada.
5. **Retestar:** executar o teste que falhou e verificar regressões afetadas.
6. **Registrar:** anotar causa, correção, evidências, SHA, status do banco e backup válido.
7. **Prosseguir:** somente quando a falha bloqueante estiver solucionada. Erros independentes podem ser tratados em etapas diferentes, sem declarar concluída a etapa falha.

Não acumular débitos técnicos bloqueantes, esconder erro, desligar teste ou instalar ferramentas aleatoriamente para tentar resolver.

### 17.4. Backups periódicos, separados e restauráveis

Efetuar backup preventivo **antes** de migrations, alterações estruturais, atualizações críticas, operações destrutivas e ajustes financeiros relevantes; **ao final** de cada etapa estável; e **diariamente** quando houver modificações relevantes.

Git conserva versões do código; backup separado e protegido preserva os dados e configurações não versionados. Guardar recuperação **fora do diretório ativo**, preferencialmente em destino externo protegido e aprovado; backup **não** é projeto paralelo para editar.

Proteger e nunca expor secrets ou dados reais em arquivos desprotegidos. Validar integridade de arquivo, identificação da versão e **testar restauração** periodicamente de forma segura. Registrar data, escopo, destino protegido, checksum quando pertinente, procedimento de recuperação e último teste de restauração. Não declarar backup válido só porque um comando retornou zero.

### 17.5. Consumo controlado de armazenamento e memória

Antes de instalação: inventariar pacotes/SDKs existentes, versão, compatibilidade, localização, tamanho e memória. Preferir uma instalação compatível por função; evitar Flutter, Dart, Java, Python, Android SDK, ambiente virtual, cache e serviço duplicados.

Não reinstalar dependências repetidamente sem hipótese diagnosticada. Não manter serviços residentes desnecessários. Builds intermediários e caches podem ser removidos **seletivamente**, após identificar propriedade, utilidade e possibilidade de reconstrução, sem remover evidências ou backups legítimos.

### 17.6. Monitoramento e checkpoint obrigatório

Durante a execução, acompanhar armazenamento livre, crescimento de caches, RAM disponível, ferramentas críticas e saúde do PostgreSQL, ajustando a frequência ao risco e sem criar monitoramento pesado desnecessário.

Ao concluir cada etapa, registrar: requisitos cumpridos; arquivos modificados; SHA e branch; testes PASS/FAIL/BLOCKED/NOT_RUN; migration e estado do banco; falhas corrigidas; limitações; backup recuperável; próxima etapa e autorização correspondente.

**Invariante operacional:** UM DIRETÓRIO; UMA BASE AUTORITATIVA; NENHUMA FALHA BLOQUEANTE PENDENTE; BACKUPS VERIFICADOS; NENHUMA DUPLICAÇÃO DESNECESSÁRIA.

---

## ANEXO A — PROTOCOLO DE EXECUÇÃO DE CADA ETAPA (APÓS G2)

**Entrada:** autorização explícita → identificar cláusulas e critérios AT → confirmar diretório/branch/estado do banco/backup → listar arquivos permitidos → conferir espaço livre e ferramentas → executar mudanças mínimas → rodar testes e regressões → corrigir falhas → revisar diff/segurança → realizar backup conforme risco → checkpoint → solicitar aceite da etapa.

**Saída permitida:** `PASS` com evidências; `BLOCKED` com causa e plano seguro; `NÃO AUTORIZADO` para ações além do gate. Nenhum teste pode ser anotado como executado quando foi apenas proposto.

## ANEXO B — MODELO MÍNIMO DE CHECKPOINT

```text
FRCAIXINHA 2.2 — CHECKPOINT DE ETAPA
Data/hora e fuso:
Gate/autorização:
Etapa e requisitos contratuais:
Diretório raiz: ~/FRcaixinha_2.2 (após G2)
Branch / commit SHA:
Arquivos alterados:
Banco PostgreSQL autorizado / migration atual:
Testes executados e resultados:
Erros encontrados / causa / correção / regressão:
Backups: data, escopo, destino seguro, verificação e restauração:
Espaço livre / RAM / ferramentas críticas:
Pendências ou bloqueios:
Próxima ação permitida:
Responsável pela aprovação:
```

## ANEXO C — LIÇÕES DO PASSADO CONVERTIDAS EM CONTROLES

| Risco observado em projetos anteriores | Medida preventiva obrigatória |
|---|---|
| Divergências entre Flutter, Gradle, AGP, Kotlin, Java, SDK e plugins | Inventário de versões, compatibilidade verificada e compilação CI rastreável antes de atualizações |
| Divergências Alembic/constraints e tentativas com base SQLite inadequada | PostgreSQL único no desenvolvimento, migrations verificadas e testes que preservam a base |
| Confusão entre Termux, Debian PRoot e CI | Identificar ambiente de cada comando e verificar arquitetura e versões |
| Arquivos não rastreados, artefatos e branches concorrentes | Conferir `git status`, diffs, SHA e arquivos permitidos antes de commit/merge |
| Bugs “corrigidos” mudando regras ou testes | Reproduzir, diagnosticar, corrigir minimamente e retestar com regressão |
| Duplicação de ferramenta e cache consumindo armazenamento do celular | Inventário antes de instalar, reaproveitamento e limpeza seletiva segura |
| Pix duplicado após timeout, webhook ou recuperação | Chave econômica estável, idempotência, reconciliação e testes de restauração |
| Perda de trabalho por falha do aparelho, Git ou banco | Backups separados e restauráveis; checkpoints verificáveis |
| Falta de continuidade entre chats e relatórios de sucesso sem prova | Checkpoint por etapa e classificação honesta de PASS/FAIL/BLOCKED/NOT_RUN |
| Início de operações ou custos sem permissão | Gates separados e autorização escrita antes de programar, contratar ou operar dinheiro real |

## ANEXO D — MATRIZ DE AUTORIDADE E ENTREGA

| Elemento | Situação e fonte |
|---|---|
| Contrato Técnico Mestre FINAL_APROVADO_2026-10-16 | G1 concluído; fonte contratual oficial |
| Documento Mestre de Instruções (este arquivo) | Regras operacionais consolidadas; subordinado ao contrato |
| Diretório `~/FRcaixinha_2.2` e repositório novo | Propostos; criação somente após G2 |
| Banco PostgreSQL de desenvolvimento | Autorização de criação vinculada a G2; uma base autoritativa |
| Plano Ampliado e taxa extra sobre lucros de terceiros | Não habilitados; dependem de decisões específicas |
| Dinheiro real, Pix de produção e recursos regulados | Gates jurídicos, de provedor e publicação independentes |
| Testes contratuais AT-01 a AT-50 | Critérios de aceite futuros; não equivalem a testes executados |

---

**CONTROLE DOCUMENTAL:** Este arquivo consolida instruções permanentes para uso no projeto e no Codex. Não altera as cláusulas, valores ou autorizações do Contrato Técnico Mestre já aprovado. Qualquer incompatibilidade identificada deve ser apontada e resolvida formalmente antes de implementação. **O G2 permanece NÃO AUTORIZADO.**


---


# PARTE VII — FONTES, INTEGRIDADE, PENDÊNCIAS E DOCUMENTOS DE ADESÃO


## 1. Registro de integridade — documentos que devem permanecer arquivados

**Contrato Técnico Mestre APROVADO**  
Arquivo: `FRcaixinha_2_2_Contrato_Tecnico_Mestre_FINAL_APROVADO_2026-10-16.md`  
SHA-256: `300d6fa05f7b924a4bb2119291b54c9e6391ca1310558398a5805ded1fd812be`  
☐ Documento original conferido ☐ Fonte da seção confirmada ☐ Cópia de segurança preservada

**Documento Mestre de Instruções**  
Arquivo: `FRcaixinha_2_2_Documento_Mestre_Instrucoes_Desenvolvimento_2026-10-16.md`  
SHA-256: `33b1ce8c3b13460f3a45367f9e029eb62f64200141ae262021f1e431180f5f8a`  
☐ Documento original conferido ☐ Fonte da seção confirmada ☐ Cópia de segurança preservada

**Minutas dos membros (NÃO aprovadas para uso real)**  
Arquivo: `FRcaixinha_2_2_Minutas_Contratuais_Membros_2026-10-16.md`  
SHA-256: `3f41f594dc4e37234252467dbabcc738d30f799cae8f0a3cc72c9d6e522212b8`  
☐ Documento original conferido ☐ Fonte da seção confirmada ☐ Cópia de segurança preservada


## 2. Contratos destinados aos membros — somente minutas, não operações autorizadas

O caderno de minutas elaborado em 16/10/2026 contém os instrumentos abaixo, que devem ser auditados contra o Contrato Técnico Mestre antes da integração e da assinatura. **A redação de uma minuta não substitui parecer jurídico, aceite do membro, política do tenant nem autoriza execução financeira.**
- ☐ **Instrumento A — Contrato de Adesão e Participação:** Convite, cadastro, cotas, contribuições, transparência, inadimplência, saída, resultados e aceite por tenant/ciclo. **Revisão:** ☐ Texto conferido ☐ Dados preenchidos ☐ Validação jurídica ☐ Aceite individual ☐ Evidências arquivadas.
- ☐ **Instrumento B — Política Financeira do Ciclo:** Quadro específico de valor/cota, juros legalmente aplicáveis, parcela, multa, rateio e política de inadimplência. Não copiar política do proprietário aos terceiros. **Revisão:** ☐ Texto conferido ☐ Dados preenchidos ☐ Validação jurídica ☐ Aceite individual ☐ Evidências arquivadas.
- ☐ **Instrumento C — Contrato Individual de Empréstimo:** Simulação Price vinculada, primeiro período proporcional, cronograma, desembolso, mora, pagamentos parciais e quitação antecipada. **Revisão:** ☐ Texto conferido ☐ Dados preenchidos ☐ Validação jurídica ☐ Aceite individual ☐ Evidências arquivadas.
- ☐ **Instrumento D — Autorização Coletiva Anual:** Consentimento individual, expresso, unânime, específico para o administrador-membro e válido somente naquele ciclo; revogação e bloqueios. **Revisão:** ☐ Texto conferido ☐ Dados preenchidos ☐ Validação jurídica ☐ Aceite individual ☐ Evidências arquivadas.
- ☐ **Instrumento E — Aviso de Privacidade:** Finalidade, base legal adequada, acesso limitado, retenção, direitos dos titulares e opt-ins independentes. **Revisão:** ☐ Texto conferido ☐ Dados preenchidos ☐ Validação jurídica ☐ Aceite individual ☐ Evidências arquivadas.

## 3. Pendências que continuam expressamente delimitadas

- ☐ Definir capacidade máxima de membros e cotas do Plano Ampliado em futura decisão expressa: até lá, indisponível.
- ☐ Eventual taxa comercial adicional da plataforma sobre lucros de terceiros: EM ESTUDO, não aprovada; não há percentual contratual a inventar.
- ☐ Conformidade legal de juros, crédito, distribuição de resultados, sanções de inadimplência e autoempréstimos antes de movimentação real.
- ☐ Contrato, capacidade técnica, finalidade e autorização do Mercado Pago para Pix IN/OUT e contas por tenant antes de operações reais.
- ☐ Infraestrutura de produção, custos, recursos, metas de backup demonstradas e autorização de despesas, conforme gates próprios.
- ☐ Bolões: demonstrador fora dos 60 dias, somente após ordem específica; operação real exige validações e gates do §14.
- ☐ Futura atividade regulada/bancária, custódia própria, crédito externo, comércio adicional e recursos adiados: não incluir no MVP.
- ☐ Parâmetros particulares de cada tenant inexistentes: solicitar decisão e aceite do respectivo administrador, não preencher por analogia.

# PARTE VIII — FORMULÁRIOS IMPRIMÍVEIS DE ACOMPANHAMENTO


## Ficha A — Registro diário de desenvolvimento (copiar esta página conforme necessidade)

**Registro diário 1** — Data ___/___/____  Horário ____  Etapa ____  Cláusulas ____
**Autorização / objetivo:** _____________________________________________________________________________________________________
**Comandos/arquivos alterados:** ______________________________________________________________________________________________
**Commit SHA / branch / Alembic:** ___________________________________________________________________________________________
**Testes executados / resultados:** __________________________________________________________________________________________
**Backup válido (data/local/checksum):** ____________________________________________________________________________________
**Erro encontrado e correção:** ___________________________________________________________________________________________
**Verificação final:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ NÃO EXECUTADO   **Assinatura:** ____________________________

**Registro diário 2** — Data ___/___/____  Horário ____  Etapa ____  Cláusulas ____
**Autorização / objetivo:** _____________________________________________________________________________________________________
**Comandos/arquivos alterados:** ______________________________________________________________________________________________
**Commit SHA / branch / Alembic:** ___________________________________________________________________________________________
**Testes executados / resultados:** __________________________________________________________________________________________
**Backup válido (data/local/checksum):** ____________________________________________________________________________________
**Erro encontrado e correção:** ___________________________________________________________________________________________
**Verificação final:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ NÃO EXECUTADO   **Assinatura:** ____________________________

**Registro diário 3** — Data ___/___/____  Horário ____  Etapa ____  Cláusulas ____
**Autorização / objetivo:** _____________________________________________________________________________________________________
**Comandos/arquivos alterados:** ______________________________________________________________________________________________
**Commit SHA / branch / Alembic:** ___________________________________________________________________________________________
**Testes executados / resultados:** __________________________________________________________________________________________
**Backup válido (data/local/checksum):** ____________________________________________________________________________________
**Erro encontrado e correção:** ___________________________________________________________________________________________
**Verificação final:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ NÃO EXECUTADO   **Assinatura:** ____________________________

**Registro diário 4** — Data ___/___/____  Horário ____  Etapa ____  Cláusulas ____
**Autorização / objetivo:** _____________________________________________________________________________________________________
**Comandos/arquivos alterados:** ______________________________________________________________________________________________
**Commit SHA / branch / Alembic:** ___________________________________________________________________________________________
**Testes executados / resultados:** __________________________________________________________________________________________
**Backup válido (data/local/checksum):** ____________________________________________________________________________________
**Erro encontrado e correção:** ___________________________________________________________________________________________
**Verificação final:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ NÃO EXECUTADO   **Assinatura:** ____________________________

**Registro diário 5** — Data ___/___/____  Horário ____  Etapa ____  Cláusulas ____
**Autorização / objetivo:** _____________________________________________________________________________________________________
**Comandos/arquivos alterados:** ______________________________________________________________________________________________
**Commit SHA / branch / Alembic:** ___________________________________________________________________________________________
**Testes executados / resultados:** __________________________________________________________________________________________
**Backup válido (data/local/checksum):** ____________________________________________________________________________________
**Erro encontrado e correção:** ___________________________________________________________________________________________
**Verificação final:** ☐ PASS ☐ FAIL ☐ BLOQ ☐ NÃO EXECUTADO   **Assinatura:** ____________________________


## Ficha B — Registro de defeito: proibição de avançar com falha bloqueante

**Ocorrência 1:** ID ______  Data ______  Etapa ______  Cláusula ______  Severidade ______
**Como reproduzir / saída real:** _________________________________________________________________________________________
**Causa confirmada:** _____________________________________________________________________________________________________
**Correção mínima / arquivos / SHA:** _______________________________________________________________________________________
**Reteste que falhou anteriormente:** ☐ PASS ☐ FAIL ☐ NÃO EXECUTADO  **Regressão:** ☐ PASS ☐ FAIL
**Autorizado retomar?** ☐ SIM, com evidência  ☐ NÃO, bloqueado  **Assinatura:** ____________________________

**Ocorrência 2:** ID ______  Data ______  Etapa ______  Cláusula ______  Severidade ______
**Como reproduzir / saída real:** _________________________________________________________________________________________
**Causa confirmada:** _____________________________________________________________________________________________________
**Correção mínima / arquivos / SHA:** _______________________________________________________________________________________
**Reteste que falhou anteriormente:** ☐ PASS ☐ FAIL ☐ NÃO EXECUTADO  **Regressão:** ☐ PASS ☐ FAIL
**Autorizado retomar?** ☐ SIM, com evidência  ☐ NÃO, bloqueado  **Assinatura:** ____________________________

**Ocorrência 3:** ID ______  Data ______  Etapa ______  Cláusula ______  Severidade ______
**Como reproduzir / saída real:** _________________________________________________________________________________________
**Causa confirmada:** _____________________________________________________________________________________________________
**Correção mínima / arquivos / SHA:** _______________________________________________________________________________________
**Reteste que falhou anteriormente:** ☐ PASS ☐ FAIL ☐ NÃO EXECUTADO  **Regressão:** ☐ PASS ☐ FAIL
**Autorizado retomar?** ☐ SIM, com evidência  ☐ NÃO, bloqueado  **Assinatura:** ____________________________


## Ficha C — Controle de backup, restauração e espaço de armazenamento

**Backup 1:** Data/hora ______ Tipo (Git/código/config/PostgreSQL/WAL) ______ Local protegido ______
**Hash/verificação:** ________________________  **Arquivo criptografado?** ☐ SIM ☐ N/A justificado
**Restauração testada?** ☐ SIM ☐ NÃO  **Prova/ambiente autorizado:** ___________________________________
**Armazenamento livre antes/depois:** __________ / __________  **RAM disponível:** __________
**Nenhum segredo no backup desprotegido:** ☐ VERIFICADO  **Responsável:** _______________________

**Backup 2:** Data/hora ______ Tipo (Git/código/config/PostgreSQL/WAL) ______ Local protegido ______
**Hash/verificação:** ________________________  **Arquivo criptografado?** ☐ SIM ☐ N/A justificado
**Restauração testada?** ☐ SIM ☐ NÃO  **Prova/ambiente autorizado:** ___________________________________
**Armazenamento livre antes/depois:** __________ / __________  **RAM disponível:** __________
**Nenhum segredo no backup desprotegido:** ☐ VERIFICADO  **Responsável:** _______________________

**Backup 3:** Data/hora ______ Tipo (Git/código/config/PostgreSQL/WAL) ______ Local protegido ______
**Hash/verificação:** ________________________  **Arquivo criptografado?** ☐ SIM ☐ N/A justificado
**Restauração testada?** ☐ SIM ☐ NÃO  **Prova/ambiente autorizado:** ___________________________________
**Armazenamento livre antes/depois:** __________ / __________  **RAM disponível:** __________
**Nenhum segredo no backup desprotegido:** ☐ VERIFICADO  **Responsável:** _______________________

**Backup 4:** Data/hora ______ Tipo (Git/código/config/PostgreSQL/WAL) ______ Local protegido ______
**Hash/verificação:** ________________________  **Arquivo criptografado?** ☐ SIM ☐ N/A justificado
**Restauração testada?** ☐ SIM ☐ NÃO  **Prova/ambiente autorizado:** ___________________________________
**Armazenamento livre antes/depois:** __________ / __________  **RAM disponível:** __________
**Nenhum segredo no backup desprotegido:** ☐ VERIFICADO  **Responsável:** _______________________


## Ficha D — Termo manual de passagem de fase

**Gate de saída da fase 1:** Fase real ______ Data ______ Supervisor ______
Cláusulas verificadas: ____________________  Cenários AT validados: ________________________
☐ Requisitos implementados  ☐ Testes PASS  ☐ Regressão PASS  ☐ Sem FAIL bloqueante
☐ Git/diff/CI conferidos  ☐ Banco/migrations conformes  ☐ Backup comprovado  ☐ Sem despesa indevida
☐ Limites legais/provedor ainda bloqueados corretamente  ☐ Documentação/checkpoint atualizados
**Decisão:** ☐ ACEITO / avançar quando autorizado  ☐ REPROVADO / corrigir  ☐ BLOQUEADO / aguardar
**Ressalvas / evidências:** _____________________________________________________________________________________________________
**Assinatura:** ____________________________

**Gate de saída da fase 2:** Fase real ______ Data ______ Supervisor ______
Cláusulas verificadas: ____________________  Cenários AT validados: ________________________
☐ Requisitos implementados  ☐ Testes PASS  ☐ Regressão PASS  ☐ Sem FAIL bloqueante
☐ Git/diff/CI conferidos  ☐ Banco/migrations conformes  ☐ Backup comprovado  ☐ Sem despesa indevida
☐ Limites legais/provedor ainda bloqueados corretamente  ☐ Documentação/checkpoint atualizados
**Decisão:** ☐ ACEITO / avançar quando autorizado  ☐ REPROVADO / corrigir  ☐ BLOQUEADO / aguardar
**Ressalvas / evidências:** _____________________________________________________________________________________________________
**Assinatura:** ____________________________

**Gate de saída da fase 3:** Fase real ______ Data ______ Supervisor ______
Cláusulas verificadas: ____________________  Cenários AT validados: ________________________
☐ Requisitos implementados  ☐ Testes PASS  ☐ Regressão PASS  ☐ Sem FAIL bloqueante
☐ Git/diff/CI conferidos  ☐ Banco/migrations conformes  ☐ Backup comprovado  ☐ Sem despesa indevida
☐ Limites legais/provedor ainda bloqueados corretamente  ☐ Documentação/checkpoint atualizados
**Decisão:** ☐ ACEITO / avançar quando autorizado  ☐ REPROVADO / corrigir  ☐ BLOQUEADO / aguardar
**Ressalvas / evidências:** _____________________________________________________________________________________________________
**Assinatura:** ____________________________


# DECLARAÇÃO FINAL DE CONTROLE E PARADA

O preenchimento deste caderno serve à verificação MANUAL do desenvolvimento que será autorizado futuramente. **Não é autorização G2, G5, G6, G7, ativação financeira, publicação nem homologação jurídica.** O proprietário somente declara fases tecnicamente concluídas depois de evidências verificáveis, correção de falhas bloqueantes, backups restauráveis e aceite expresso.
**Checklist de encerramento geral:** ☐ 147 cláusulas numeradas conferidas  ☐ AT-01 a AT-50 executados/justificados  ☐ 17 seções de instruções observadas  ☐ 7 fases assinadas  ☐ um diretório  ☐ uma base autoritativa  ☐ backups íntegros  ☐ nenhuma operação proibida
**Proprietário:** ___________________________________  **Data:** ____/____/______  **Versão/commit:** ______________________________

**FIM DO CADERNO MESTRE — TODOS OS CAMPOS DE RESULTADO PERMANECEM EM BRANCO ATÉ EVIDÊNCIA REAL.**
