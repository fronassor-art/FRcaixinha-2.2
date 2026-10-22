# FRCAIXINHA 2.2

## DOCUMENTO MESTRE DE INSTRUÇÕES E GOVERNANÇA DO DESENVOLVIMENTO

**Versão:** 1.1 — 20/10/2026 (atualização operacional auditada; contrato de 16/10 preservado)  
**Natureza:** instruções operacionais permanentes para ChatGPT, Codex e execução técnica pelo proprietário.  
**Referência normativa principal:** `FRcaixinha_2_2_Contrato_Tecnico_Mestre_FINAL_APROVADO_2026-10-16.md`.  
**Estado do contrato:** G1 — APROVADO em 16/10/2026.  
**Estado da implementação em 20/10/2026:** G2 já exercido na prática, com repositório oficial criado e Fase 1 implementada; Fase 2 EM ANDAMENTO no checkpoint C15-R7. O histórico documental do G2 exige referência à autorização original na trilha da fase; a evidência da execução é GitHub PRs #1–#17. Nenhuma nova operação é autorizada por esta atualização.  
**Finalidade:** consolidar o método de trabalho, prevenir erros conhecidos e garantir fidelidade ao Contrato Técnico Mestre. Este documento **não o substitui** nem concede permissões financeiras ou operacionais.

> **MANDAMENTO CENTRAL:** Um diretório raiz; uma base PostgreSQL autoritativa no ambiente de desenvolvimento; nenhuma falha bloqueante ignorada; backups recuperáveis e verificáveis; nenhuma ferramenta duplicada sem necessidade; nenhuma ação fora da autorização expressa.

---

## LEITURA OBRIGATÓRIA — ESTADO ATUAL E FONTES (20/10/2026)

> **Este documento v1.1 substitui as instruções operacionais desatualizadas da edição 1.0 de 16/10/2026, preservando as cláusulas permanentes e sem alterar o Contrato Técnico Mestre.** O Caderno Mestre de 17/10/2026 é um registro histórico/prospectivo; seus itens ainda não marcados não comprovam não execução. O estado atual deve ser obtido dos checkpoints e das provas GitHub/Termux/backup.

- **Projeto único:** `~/FRcaixinha_2.2`, repositório GitHub `fronassor-art/FRcaixinha-2.2`.
- **Último checkpoint concluído:** C15-R7, `main` `0316c3cc29aa6966033e52d5d21d5f378683ba97`; PR #17 integrada; CI backend **89/89 PASS**.
- **Banco único:** PostgreSQL Termux **18.2**, `frcaixinha_2_2_dev`, usuário `frc22_owner`, `127.0.0.1:5432`. Autenticação e consultas somente leitura validadas; a migration C15 **NÃO foi aplicada**; `public.alembic_version` ausente na última leitura.
- **Backup do código C15:** AGE/scrypt local e no Google Drive privado; restauração independente Git testada; SHA-256 `d77fc40bbedd54c98e04e5d92d87cc493c514dcfffe01340be3af6732a274919`. Backup do PostgreSQL é separado e a **restauração SQL ainda não foi testada**.
- **Próximo passo técnico proposto, não autorizado automaticamente:** análise de pré-migration C16, incluindo identificação/segurança de objetos, planejamento de upgrade/downgrade e verificação do backup PostgreSQL, sem alterar o banco antes de gate explícito.
- **Documentos de continuidade:** Anexos E–M deste documento; auditoria/checklist independente e cartão de retomada da mesma data. **Não reabrir problema já resolvido antes de consultar o Registro de Decisões e Erros (anexos G/H).**

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

**G1:** contrato documental aprovado em 16/10/2026. **G2:** início do projeto já realizado e evidenciado pelo histórico GitHub; o registro original de 16/10/2026 era prospectivo, não representa o estado atual. **A autorização de G2 NÃO autoriza automaticamente migrations, custos, dinheiro real, publicação operacional nem etapas futuras.**

No estado atual, o projeto, o repositório, a estrutura Flutter/FastAPI, o banco autoritativo PostgreSQL 18.2 e o código Alembic já existem. **Proibido recriá-los ou duplicá-los.** Qualquer desenvolvimento adicional, migration real, escrita em banco, publicação operacional ou custo depende de autorização própria e de preflight contextualizado.

Em cada checkpoint após G2, executar somente o escopo aprovado, etapa por etapa. Antes de alterações com risco ou custo, apresentar efeito, alternativas, reversibilidade e autorização necessária. Não abrir conta paga, contratar nuvem, consumir recursos faturáveis, publicar produção nem efetuar transferências de valor por presunção.

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
| Diretório `~/FRcaixinha_2.2` e repositório oficial | Existentes, com `main` em `0316c3cc29aa6966033e52d5d21d5f378683ba97` (C15) |
| Banco PostgreSQL de desenvolvimento | Instalação PostgreSQL 18.2 existente e acesso validado: `frcaixinha_2_2_dev`, `frc22_owner`, `127.0.0.1:5432`; ainda sem aplicação da migration C15 |
| Plano Ampliado e taxa extra sobre lucros de terceiros | Não habilitados; dependem de decisões específicas |
| Dinheiro real, Pix de produção e recursos regulados | Gates jurídicos, de provedor e publicação independentes |
| Testes contratuais AT-01 a AT-50 | Critérios de aceite futuros; não equivalem a testes executados |

---

**CONTROLE DOCUMENTAL:** Este arquivo consolida instruções permanentes para uso no projeto e no Codex. Não altera as cláusulas, valores ou autorizações do Contrato Técnico Mestre já aprovado. Qualquer incompatibilidade identificada deve ser apontada e resolvida formalmente antes de implementação. **O G2 já foi exercido; novas etapas continuam sujeitas a autorizações específicas.**


---

## ANEXO E — INVENTÁRIO DE EVIDÊNCIAS E HIERARQUIA DE CONFIANÇA

**Congelamento desta auditoria:** 20/10/2026, após C15-R7. Não presume fatos posteriores. Nunca preencher lacunas com hipóteses.

| Código | Fonte | O que comprova | Limitação |
|---|---|---|---|
| F-CTM | Contrato Técnico Mestre `FINAL_APROVADO_2026-10-16.md` no repositório `main` | Requisitos financeiros, comerciais, de dados, segurança, gates e AT-01–AT-50 | Não prova implementação/execução |
| F-DM | Documento Mestre de 16/10, blob Git `0ba235d4cc6230bea6b0d3ff35c88b6e694d1b2f` | Regras operacionais originalmente aprovadas | Trazia G2 prospectivo; desatualizado |
| F-CAD | Caderno Mestre de 17/10, blob Git `509861ed90eed68b30eafe836646c85f0714e772` | Planejamento em fases, treze controles da Fase 2 e checklist | Caixas não preenchidas não são medição de hoje |
| F-GIT | Repositório `fronassor-art/FRcaixinha-2.2`, PRs #1–#17 e seus commits de merge | Integração do código e linhagem verificáveis | PR verde não prova efeito no banco real |
| F-CI | GitHub Actions: `backend-ci.yml`, `flutter-ci.yml`, `android-apk-ci.yml` | Jobs executados e respectivos estados | Confirma apenas testes efetivamente configurados |
| F-TERM | Saídas do responsável em Termux/Debian PRoot nesta e em conversas anteriores | Estado local e comandos executados, quando completos | Não é acesso remoto contínuo à máquina |
| F-BKP | AGE local, teste de recuperação Git independente e download de verificação do Drive | Integridade do backup de código C15, SHA idêntico | Não é backup do banco nem teste de restauração SQL |
| F-CLOUD | Histórico da investigação do Codex Cloud, em conversas anteriores | Proxies, identidade do ambiente, falha de conectividade observada | Conectividade atual exige novo teste; não presumir que persistiu |

**Regra:** evidência oficial efetiva > relatório reproduzível > relato histórico > inferência. Documentos operacionais nunca prevalecem sobre o contrato aprovado. Resultados não medidos são `NOT_RUN` ou `BLOCKED`, não `PASS`.

## ANEXO F — LINHA DO TEMPO AUDITADA E CHECKPOINTS

A relação abaixo é uma trilha do código versionado, não uma declaração de que todas as funcionalidades finais estão operantes.

| Etapa | PR | Commit merge na main (prefixo) | Entrega comprovável pelo título, diff e histórico Git | Situação |
|---|---:|---|---|---|
| Fase 1 — API FastAPI mínima | #1 | `17216413c80c` | Endpoint de saúde e testes | Integrada |
| Fase 1 — CI backend | #2 | `2de50c26f7cc` | Backend CI em PR; job `unittest` bem-sucedido | Integrada |
| Fase 1 — Flutter inicial | #3 | `ad6c5498ba0c` | Bootstrap Flutter; CI `flutter` bem-sucedido | Integrada |
| Fase 1 — APK debug CI | #4 | `e9d8b86dfcb2` | Compilação debug em GitHub Actions; job `debug-apk` bem-sucedido | Integrada |
| Fase 2 — dependências PostgreSQL | #5 | `6b2c795cf4bd` | Dependências fixadas | Integrada |
| Fase 2 — scaffold Alembic | #6 | `45b693cb00f0` | Configuração Alembic com bloqueios de escrita | Integrada |
| Fase 2 — identidade/contratante | #7 | `7240acdb476f` | Modelos UserIdentity e ContractingParty | Integrada |
| C06 — Tenant, papéis e correção do guard | #8 | `68edccaca3bd` | Modelos tenant/RoleGrant e proteção Alembic | Integrada |
| C07 — ciclo/calendário | #9 | `8627d61fe2f8` | Modelo Cycle inativo | Integrada |
| C08 — adesão | #10 | `0fd63ac12323` | Membership inativo | Integrada |
| C09 — cotas | #11 | `fc83ddb87812` | Quota e índice de Membership | Integrada |
| C10 — catálogo de licença | #12 | `c1ebf9abaceb` | LicensePlan e LicensePriceVersion | Integrada |
| C11 — oferta e aceite | #13 | `b3e443cd9c40` | LicenseOffer e TermAcceptance | Integrada |
| C12 — obrigação de licença | #14 | `8733317a8bc7` | LicensePaymentObligation e Payment lógico inativo | Integrada |
| C13 — tentativa e conciliação | #15 | `034c51ee712c` | PaymentAttempt e PaymentReconciliationEvent inativos | Integrada |
| C14 — isolamento de ambiente | #16 | `95fddcb82432` | Correção da vinculação do ambiente de pagamentos | Integrada; CI PASS |
| C15 — migration Alembic inicial | #17 | `0316c3cc29aa` | 15 tabelas e 18 índices declarados, 9 testes offline novos, `target_metadata = Base.metadata` | Integrada; CI 89/89 PASS; **não aplicada** |

**Fase 1:** base de código e CI integrada; os jobs correspondentes tiveram sucesso, conforme GitHub. **Fase 2:** em andamento; não confundir modelagem SQLAlchemy e migration versionada com tabelas criadas ou recursos acessíveis ao usuário. **Fases 3–7:** não declaradas concluídas; o plano inicial continua referencial, sujeito a checkpoints e autorizações. A passagem de dias do cronograma é estimativa e não substitui gates.

**SHA autoritativo atual:** `0316c3cc29aa6966033e52d5d21d5f378683ba97`, merge da PR #17, pais `95fddcb824328da3b75dee23be0a5a156174fb3f` e `fe67747ac87d6f53fd2b3897b682001552116ffc`.

## ANEXO G — REGISTRO DE DECISÕES TÉCNICAS DURÁVEIS (ADR)

O número ADR identifica a decisão para referência obrigatória em cada novo chat e relatório. `APROVADO` significa regra confirmada pelo proprietário/contrato ou executada em checkpoint; `CONTROLADO` exige autorização por etapa; `EM ESTUDO` não pode ser implementado.

| ADR | Decisão e aplicação obrigatória | Fonte/estado |
|---|---|---|
| ADR-001 | **Um diretório ativo:** `~/FRcaixinha_2.2`; frontend/backend/docs/testes/CI em subpastas. Não abrir outro clone como ambiente de desenvolvimento. | Contrato/Instruções 17; APROVADO |
| ADR-002 | **Uma base autoritativa:** PostgreSQL Termux 18.2, base `frcaixinha_2_2_dev`, usuário `frc22_owner`, loopback `127.0.0.1:5432`. Sem SQLite substituto, PostgreSQL 17 do Debian ou um banco por tenant. | C15 verificação local; APROVADO |
| ADR-003 | Identificar o executor por comando. **Codex planeja, inspeciona, implementa e testa só o permitido; quando sua sessão ou sandbox não acessa ferramentas/permissões já existentes, PARA e entrega relatório; ChatGPT fornece procedimento no Termux; o proprietário executa atos interativos e retorna a saída; Codex retoma depois da evidência.** Não deixar a limitação local reabrir arquitetura aprovada. | Determinação do proprietário 20/10; APROVADO |
| ADR-004 | Termux normal é executor de PostgreSQL 18, `git` e AGE; Debian PRoot independente hospeda `.venv` Python **3.13.5**. É proibido tratar Python Termux 3.14 auxiliar como teste oficial; não aninhar `proot-distro login` dentro do PRoot. | C15-R2/R2V; APROVADO |
| ADR-005 | Dependências fixas no `backend/requirements.txt`: FastAPI 0.141.1, Uvicorn 0.52.1, HTTPX 0.28.1, SQLAlchemy 2.0.55, Alembic 1.20.0, psycopg 3.3.6; transitivas também fixadas. `pip check` antes dos testes; sem instalações repetidas. | `main` C15; APROVADO |
| ADR-006 | Alembic mantém `FRCAIXINHA_DATABASE_URL`, gate exato `FRCAIXINHA_ALEMBIC_WRITE_GATE`, driver `postgresql+psycopg`, identidade de banco/usuário/host/porta e PG 18.x; execução offline vedada. `target_metadata = Base.metadata` desde C15. Autorização de execução é SEPARADA da autorização de escrever migration. | PR #6/#8/#17; APROVADO/CONTROLADO |
| ADR-007 | Etapa Git: confirmar origem, SHA, branch, `git status` e diff; lista exata de arquivos; mudanças mínimas; commit local → push → PR → CI → merge → sincronização → backup, **com autorização distinta** para cada mudança de risco. Sem `git add .`, force/reset/clean por reflexo. | PRs #1–#17; APROVADO |
| ADR-008 | CI no GitHub é o teste de referência quando o celular tem restrição de toolchain; status PASS só com job terminado e log, sem confundir teste offline com DDL real. Fase 1 Flutter/Android usa GH Actions; backend CI Python 3.13. | PRs #2–#4/#17; APROVADO |
| ADR-009 | Erro bloqueante: reproduzir → encontrar causa → corrigir minimamente → repetir teste → regressão → checkpoint → só então avançar. Não remover testes nem alterar contrato para ficar verde. | Instruções 17.3; APROVADO |
| ADR-010 | **Regra antirrepetição:** antes de investigar problema similar, consultar ADR e Registro de Erros. Verificar condições/versões; reaplicar solução comprovada se a causa for a mesma. Abrir nova investigação apenas se houver evidência de cenário diferente; documentar sua diferença. | Determinação do proprietário 20/10; APROVADO |
| ADR-011 | Backups Git são bundles completos, AGE protegido com **scrypt/senha interativa apenas no Termux**, sem enviar senha ao ChatGPT/Codex e sem gravar bundle não criptografado permanente. `git bundle verify`, recuperação Git independente, SHA256 local e download SHA256 idêntico no Drive privado. | C15-R7; APROVADO |
| ADR-012 | Backup PostgreSQL é independente de Git. Dump AGE existe e checksum local/remoto já foi conferido; **restauração SQL ainda NÃO foi testada**. Antes de migrations, verificar salvaguarda SQL atual, identidade e objetos; nenhuma criação de banco concorrente para contornar problema. | Auditorias C15; CONTROLADO |
| ADR-013 | Alterações na semântica financeira exigem nova decisão; preservar convenções aprovadas sobre pagamento parcial, Price/dia 10, resíduos/maiores restos, percentuais fixos por ciclo. | Contrato aprovado 16/10; APROVADO |
| ADR-014 | Licenças e pagamentos ficam **inativos** até validações; receita de plataforma segregada da caixinha; nenhum Pix, checkout ou ativação real por ter modelo SQL. Plano Ampliado sem teto e taxa adicional sobre lucro de terceiros ainda bloqueados. | Contrato + C10–C14; APROVADO |
| ADR-015 | UserIdentity é única por pessoa; papel Master/admin/membro é explícito e segregado por tenant/ciclo; Master não vê dados financeiros de outros tenants por padrão. Os modelos são apenas fase inicial, não prova de autorização real no backend. | Contrato 3.1-A, 6.1-A e 12; APROVADO |
| ADR-016 | O **Contrato Técnico Mestre FINAL_APROVADO 16/10** é autoridade normativa. Documento Mestre operacional, Caderno e chats são subsidiários; nunca deduzir autorização de simples sugestão ou arquivo. | Contrato + Instruções 2; APROVADO |
| ADR-017 | Codex Cloud/ponte Termux→Cloud: incidente de rede `proxy:8080` com `PermissionError` foi observado, mas a integração não foi comprovada. Não tentar contornar proxy ou reinstalar; utilizar executor Termux comprovado até nova auditoria da ponte. | Histórico 18/10; **BLOCKED/PENDENTE** |
| ADR-018 | Ao terminar um checkpoint relevante, atualizar **o registro canônico de continuidade no repositório** além da conversa, com SHA, PR, estado do banco, testes, erro/causa/solução, backup, próximo gate; gerar cartão curto para novo chat. | Determinação do proprietário 20/10; APROVADO COMO PROCESSO; implantação documental pendente de sincronização Git |

**Nota:** escolhas contratuais aprovadas não precisam ser revalidadas em cada conversa. Se surgir conflito, anexar trecho exato do contrato e abrir mudança controlada; não “solucionar” divergência alterando a regra silenciosamente.

## ANEXO H — HISTÓRICO DE ERROS, CAUSAS, CORREÇÕES E NÃO REPETIÇÃO

| ID | Sintoma observado | Causa/diagnóstico comprovado ou limite da evidência | Solução/conduta já adotada | Teste/estado |
|---|---|---|---|---|
| ERR-001 | Codex não consegue `proot-distro login` dentro do executor atual | Sessão já dentro de Debian PRoot; aninhamento recusado | Parar no Codex, executar via **nova sessão Termux fora do PRoot**: `proot-distro login debian -- bash -lc '... backend/.venv/bin/python ...'`. Não reinstalar Python | C15-R2V: Python 3.13.5, `pip check` PASS, 89/89 PASS |
| ERR-002 | Suíte auxiliar deu 84 PASS, 1 FAIL, 1 ERROR de 86 | Python Termux 3.14.6, SQLAlchemy 2.0.43 (vs pin 2.0.55); `httpx` ausente no auxiliar; ordem de enumeração FKs mudou | Não modificar teste antigo nem instalar por tentativa; rodar suíte oficial na `.venv` Debian | Oficial 89/89 PASS; GH Actions 89/89 PASS |
| ERR-003 | `pg_ctl status` sem processo, `pg_controldata` mostra `in production`; `postmaster.pid` antigo; porta inicialmente recusada | Indício de interrupção não limpa; não é prova de perda/corrupção nem autoriza recriação do cluster | Confirmar data dir, PG_VERSION, backups, integridade e único servidor; inicialização controlada do cluster existente, depois `pg_isready` | PostgreSQL 18.2 iniciou; conexão `frc22_owner` READ ONLY PASS, `pg_is_in_recovery()=false` |
| ERR-004 | Guard Alembic falhou/representação de IP divergente em C06 | Forma SQL de obter endereço não correspondia ao esperado | Empregar `host(inet_server_addr())` com verificação estrita de identidade do servidor, preservando bloqueio de escrita | PR #8 integrada; guard vigente em `env.py` |
| ERR-005 | AGE pede senha misturada com progresso de `git bundle`; aparente parada em 32% | `git bundle` imprime progresso ao stderr enquanto AGE usa tty para senha, sem evidência de demora por tamanho | `git -c pack.threads=2 bundle create --quiet - --all \| age -p -o ...`; senha só no Termux | C15-R7: `ENCRYPTION=PASS` |
| ERR-006 | `git bundle verify -` imprime `<stdin> is okay`, mas script termina sem `BUNDLE_VERIFY=PASS` | Pipeline com `set -o pipefail`; Git fecha o pipe depois de verificar e AGE recebe `SIGPIPE` (código 141, reproduzido na auditoria operacional) | `age -d "$PART" \| { git bundle verify -; cat >/dev/null; }`, garantindo consumo completo do fluxo | C15-R7: `BUNDLE_VERIFY=PASS`; histórico completo, 33 refs |
| ERR-007 | Execução interrompida deixa `*.partial` | Criptografia/verificação abortada antes da promoção atômica | Nunca sobrescrever backup final; conferir caminho, symlink e tamanho; solicitar `SIM` ao usuário para excluir **somente** parcial; `trap` seletivo | C15-R7: arquivo final AGE criado; não declarar parcial como backup |
| ERR-008 | Recuperação Git não está comprovada só por `git bundle verify` | Verificação do bundle não equivale a reconstrução do checkout; backup Git não inclui PostgreSQL | Descriptografar em repositório **bare temporário e descartável**, `git bundle unbundle`, `cat-file` do SHA, `git fsck` e `update-ref`; apagar área temporária segura ao final | C15-R7: `INDEPENDENT_RECOVERY=PASS`, commit exato C15 |
| ERR-009 | Backup externo pode estar com mesmo nome/tamanho mas bytes distintos | Metadata, existência e tamanho não provam SHA | Upload somente `.bundle.age` para pasta privada oficial; download e SHA256 ou `cmp` contra original; sem uso de senha na nuvem | C15: remoto 166431 bytes, SHA `d77fc40b...274919`, comparação byte a byte PASS |
| ERR-010 | Codex Cloud não consegue GitHub/PyPI por `proxy:8080` | Em verificação anterior, proxy resolvia, mas TCP falhou com `PermissionError` mesmo com configuração aparente correta; problema **não provou** incompatibilidade de plataforma | Manter identificação do executor Cloud afetado, reportar logs sem secretos; não alterar proxy ou reinstalar; usar Termux/PRot e GitHub connector autorizados | PONTE CLOUD pendente; reavaliar apenas em etapa específica |
| ERR-011 | Novos chats repetem G2 não autorizado, reabrem decisões e sugerem banco/instalações novos | Documento Mestre e Caderno eram snapshots de 16–17/10 e nunca tiveram seu status atualizado após PRs #1–#17 | Manter Documento Mestre operacional v1.1, checklist por checkpoint, registro ADR/ERR e **cartão de retomada**; na abertura do chat ler a fonte canônica e validar SHA atual | Documentação preparada em 20/10; publicação no repositório precisa checkpoint específico |
| ERR-012 | Suíte “PASS” no Python auxiliar ou relatório Codex sem execução real | Ferramentas, versões, executor e CI diferentes; uma conclusão transmitida não substitui logs | Evidência deve citar executor, comando, versão, SHA, quantidade e estado; separar `PASS`, `BLOCKED`, `NOT_RUN` e `NÃO AUTORIZADO` | C15-R2: 9 testes novos auxiliar PASS; R2V: 89/89 oficial; R5: 89/89 CI |

**Procedimento diante de incidente repetido:** 1) procurar ID ERR; 2) confirmar versão, ambiente, logs e SHA; 3) se coincidirem, executar correção documentada (somente no escopo autorizado); 4) retestar; 5) registrar recorrência e resultado; 6) se divergirem, abrir ERR novo com causa, solução e teste. **Não repetir toda a pesquisa nem mover o banco para contornar falha de ferramenta.**

## ANEXO I — MATRIZ EXECUTOR / PERMISSÃO / RETORNO OBRIGATÓRIO

| Operação | Executor principal | Fronteira / quando parar | Evidência de retorno |
|---|---|---|---|
| Arquitetura, contrato, escolha de etapa | ChatGPT com aprovação do proprietário | Não editar regras comerciais aprovadas sem decisão | Escopo, ADR, gate, texto aprovado |
| Edição de código, testes sem DB, Git local autorizado | Codex no Termux ou executor validado | Parar se permissão/ambiente não permite ou escopo muda | Diff, SHA, comandos, testes, `PASS/FAIL/BLOCKED` |
| PostgreSQL 18 Termux, `psql -W`, operações com senha | Proprietário no Termux normal | Nunca fornecer senha a agente; sem migração sem autorização separada | Saída sem segredos; versão, DB, host, resultado |
| `.venv` Python 3.13.5 e suíte oficial | Proprietário em Termux → Debian PRoot **novo, não aninhado** | Não trocar por Python Termux 3.14 | Python, `pip check`, contagem unittest |
| Branch, PR, revisão e CI GitHub | Codex/ChatGPT via conexão GitHub aprovada | Push, PR e merge por gates distintos; PR verde não executa DDL | URLs, SHA, job ID/logs |
| AGE criptografado/scrypt | Proprietário no Termux normal | Interativo; não registrar senha nem gerar texto claro persistente | SHA256, verificações, recuperação bare |
| Upload backup Git Drive privado | ChatGPT com arquivo AGE anexado e autorização do proprietário | Sem upload de `.env`, `.dump` desprotegido ou bundle aberto | Drive file ID, pasta, SHA256 download, permissões |
| Codex Cloud | Somente se conectividade efetiva demonstrada | Se rede/privilegios bloqueados, fallback Termux | Relatório de limitação, **não** tentativa de contornar proxy |

**Handoff obrigatório:** executor limitado informa `EXECUTOR`, `O_QUE_TENTOU`, `BLOQUEIO`, `EVIDÊNCIA`, `ALTERNATIVA_PROPOSTA`, `O_QUE_NÃO_FEZ`. ChatGPT devolve **um procedimento Termux mínimo**, orienta ambiente e aguarda saída; proprietário executa; ChatGPT valida resultado; Codex prossegue somente se a etapa continuar autorizada. **Não tratar a palavra “BLOCKED” como ordem para reinstalar, duplicar ou reabrir decisão.**

## ANEXO J — ESTADO ATUAL, BACKUPS E BLOQUEIOS

### J.1. Código

- **Origem:** `fronassor-art/FRcaixinha-2.2`; raiz Termux `~/FRcaixinha_2.2`; checkout `main` atualizado por fast-forward à PR #17.
- **`main` oficial:** `0316c3cc29aa6966033e52d5d21d5f378683ba97`.
- **PR #17:** `https://github.com/fronassor-art/FRcaixinha-2.2/pull/17`, MERGED, 4 arquivos, 1 commit de funcionalidade + merge.
- **Migração:** `backend/migrations/versions/c15r2_20261020_initial_schema.py`, `revision=c15r2_20261020`, `down_revision=None`, esquema de 15 modelos / 18 índices, verificações estáticas PASS, testes CI 89/89 PASS.
- **As 15 entidades:** `license_plans`, `user_identities`, `contracting_parties`, `license_price_versions`, `tenants`, `cycles`, `license_offers`, `role_grants`, `memberships`, `term_acceptances`, `license_payment_obligations`, `quotas`, `payments`, `payment_attempts`, `payment_reconciliation_events`.
- **Fase 2 não concluída:** `LicenseSubscription` ainda ausente; APIs operacionais PF/PJ, autenticação, convites, isolamento real e termos efetivos não se declaram prontos por terem modelos; os 50 testes AT do contrato não estão automaticamente validados.

### J.2. Banco

- Único PostgreSQL Termux 18.2: data dir `$PREFIX/var/lib/frcaixinha_2_2_pg18`, DB `frcaixinha_2_2_dev`, user `frc22_owner`, `127.0.0.1:5432`.
- Teste somente leitura: `pg_is_in_recovery()=false`. Query em `pg_catalog.pg_class` para tabelas `relkind IN ('r','p')` fora de schemas sistêmicos retornou **0 linhas**; `to_regclass('public.alembic_version')` retornou `NULL` em 20/10. Não extrapolar para todos os tipos de objeto; fazer inventário complementar antes da migração real.
- **`alembic upgrade`, downgrade e stamp nunca executados nesta fase**; C15 schema não está materializado no banco.

### J.3. Backups separados e provas

| Artefato | Escopo, verificação e situação |
|---|---|
| `FRcaixinha_2_2_C15_FINAL_0316c3cc29aa.bundle.age` | Bundle Git completo (33 refs), AGE/scrypt, 166431 bytes, 241 objetos, `git bundle verify` PASS, restauração bare e `git fsck` PASS, SHA256 `d77fc40bbedd54c98e04e5d92d87cc493c514dcfffe01340be3af6732a274919`. Local protegido e cópia Drive id `1KiryYKBrG4muW6VYE9f3wQEAS72obMeI`; download remoto comparado byte a byte, PASS; privado/proprietário. |
| `frcaixinha_2_2_dev_20261018_173109_8123.dump.age` | Backup lógico PostgreSQL AGE **separado**; SHA256 `95991140611c029d923e62baa05bcae3a4c0e8341fa5b1ac6ab11f5e7503b027`, Drive id `1mIDfpAjbDnDFxELgQIrgwwd5_owNLH82`; integridade AGE/local/remoto previamente informada como PASS; **restauração SQL não testada**. |
| C14 e checkpoints anteriores | Backups AGE anteriores preservados, não substituir por C15 nem deletar indiscriminadamente. |

**Pasta privada oficial do Drive:** `https://drive.google.com/drive/folders/1SPEujdnAjbU2IG6YdI1S0Bjb5PgJSNGf`. Somente arquivos criptografados dos backups protegidos. Cópia Git não inclui dados PostgreSQL, `.env`, arquivos soltos, credenciais ou configuração local não versionada.

### J.4. Próxima ação permitida, somente após autorização

**C16 — auditoria pré-aplicação no PostgreSQL 18 original:** validar objetos não sistêmicos, constraints/dDL, identidades, dependências e guard; confrontar decisões de modelo pendentes (sobretudo `LicenseSubscription`); revisar cobertura e plano de rollback; verificar backup físico/lógico atual e plano de teste de restauração SQL; propor execução supervisionada. **NÃO rodar upgrade/downgrade/stamp sem gate de escrita específico, backup válido e plano aprovado.**

## ANEXO K — PROTOCOLO DE NOVO CHAT: SEM REINVENTAR OU REPETIR

1. **Fonte canônica:** solicitar o Documento Mestre v1.1 da biblioteca/projeto e a versão aprovada do Contrato Técnico Mestre no GitHub. Confirmar que este documento está acessível; se não, o responsável deve anexá-lo. Memória de chat é auxiliar e pode estar incompleta.
2. **Cartão de retomada:** ler cartão de 20/10 ou checkpoint posterior e o registro ADR/ERR; identificar situação do projeto, data e SHA. Nunca tomar o snapshot G2 não autorizado de 16/10 como o estado atual.
3. **Verificação sem repetição:** `git rev-parse HEAD`, branch, status, `origin/main` e PR/CI. Consultar saúde do PG apenas se a etapa depende dele; nenhuma ação de servidor reflexa.
4. **Contratos:** preservar porcentagens, calendário, convenções, gates financeiros, escopo de C15. Não reabrir pesquisa ou alterar projeto para contornar limitação de um executor.
5. **Execução escalonada:** ChatGPT define menor próxima tarefa e quais passos Codex consegue; Codex para quando faltar acesso; proprietário executa via Termux e fornece prova; ChatGPT valida; prosseguir só dentro da autorização.
6. **Registro novo:** ao fechar qualquer etapa, acrescentar nova linha à matriz de checkpoints e, se houve correção/decisão, atualizar ADR/ERR na mesma PR/documentação aprovada. Reexportar cartão atualizado.
7. **Transição documental:** publicar via revisão e commit controlado o Documento Mestre atualizado dentro de `docs/requisitos/` sem reescrever o Contrato. Esta versão disponibilizada em ChatGPT/Library **não altera por si só o arquivo atual do GitHub**; exige etapa Git específica.

**Mensagem curta para abrir novo chat:**

> Continuar exclusivamente o FRcaixinha 2.2. Ler o Documento Mestre de Instruções v1.1 de 20/10/2026, o Contrato Técnico Mestre FINAL APROVADO de 16/10/2026, a auditoria Fase 1–C15 e o Cartão de Retomada. Última `main`: `0316c3cc29aa6966033e52d5d21d5f378683ba97`; CI 89/89 PASS; backup C15 Git/AGE local e Drive PASS; banco PostgreSQL Termux 18.2 `frcaixinha_2_2_dev` único e ainda sem migration aplicada. Antes de propor instalação, nova base ou investigação, consultar ADR/ERR. Codex limitado entrega relatório; execução privada e PRoot independente via Termux; retornar saída ao ChatGPT. Próximo gate é análise pré-migration C16, NÃO AUTORIZADO a aplicar SQL. Confirmar estado real antes de agir.

## ANEXO L — POLÍTICA DE PERSISTÊNCIA E ANTIRREGRESSÃO

**Documento mestre não é memória automática:** o agente pode não ler anexos de outros chats espontaneamente. Deve-se manter arquivo versionado no repositório e/ou disponível como arquivo permanente do Projeto/Library e referenciá-lo explicitamente no início da nova conversa. Resumo de memória do ChatGPT não equivale ao contrato ou ao checklist.

**Ao concluir cada checkpoint, manter quatro registros acoplados:**

- **Checkpoint factual:** ID, data/fuso, autorizações, SHA local e remoto, PR, arquivos, testes reais/CI, estado DB/migration, backups e próximo bloqueio.
- **ADR:** decisão nova ou alteração da anterior; alternativa descartada, aprovação, cláusula, alcance, custos e condição de reabertura.
- **ERR:** sintoma exato, reprodução, diagnóstico, correção mínima, comando seguro, testes/regressão, ambiente e prevenção; marcar quando a hipótese não foi provada.
- **Passagem de chat:** uma página com situação atual, o que NÃO repetir, o que NÃO está autorizado e próximo procedimento mínimo.

**Disparadores obrigatórios de atualização:** erro resolvido; mudança de ambiente/versão; checkpoint Git integrado; migration aplicada; backup restaurado; requisito aprovado/revogado; nova limitação de executor. Modificação pendente de versionamento documental deve ser identificada como `PENDENTE DE SINCRONIZAÇÃO`.

**Checagens automáticas futuras a propor, não existentes por presunção:** validação CI de links de checkpoint, IDs ADR/ERR, alinhamento SHA documentado com `main`, presença de `LicenseSubscription` contratual nas matrizes e detecção de status G2 obsoleto. Introduzir somente mediante nova autorização; não quebrar o CI vigente por criar verificação sem teste.

## ANEXO M — REGISTRO DE REVISÕES DO DOCUMENTO

| Versão | Data | Alteração | Evidência | Estado |
|---|---|---|---|---|
| 1.0 | 16/10/2026 | Edição original, G1 aprovado e G2 ainda prospectivo | Blob Git `0ba235d4...` | Histórico preservado em Git |
| 1.1 | 20/10/2026 | Atualiza G2 e estado até C15; acrescenta inventário, PRs, ADRs, ERRs, fluxo Codex→Termux, backups, gates e protocolo novo chat | PRs #1–#17, CI 89/89, Termux e backup Drive C15 | **Documento preparado; publicação no repositório oficial ainda requer checkpoint de documentação** |

**CONTROLE FINAL V1.1:** este documento é instrução operacional, não altera o Contrato Técnico Mestre de 16/10. Não autoriza novas migrations, Pix, dinheiro real, políticas ou custos. **Nenhum erro conhecido deve ser rediagnosticado sem consulta ao histórico e evidência de alteração de causa.**


## Atualização de continuidade — C16-R12.5 (21/10/2026)

Este adendo prevalece sobre a fotografia de status de 20/10 acima, preservada
como histórico. A base main desta revisão é 499f9f1bfd891def8bf11596538db367f7a7ee19
(PR #21); Fase 2 em andamento, Fase 3 não iniciada. Auditorias READ ONLY
C16-R12.4.1/.2 PASS; 52 testes offline C16-R12.4.6 PASS. Backups PostgreSQL e papéis
atualizados, criptografados, lidos e copiados ao Drive privado com comparação de
bytes/SHA PASS. Restauração funcional e ensaio real PostgreSQL continuam NOT_RUN.
C16-R12.5 implementa apenas habilitação temporária e testes, em revisão/CI;
não autoriza DDL, merge ou aplicação permanente das migrations.
ADR, ERR corrigido, hashes, evidências, limites e próximo gate estão em
[checkpoint C16-R12.5](FRcaixinha_2_2_C16_R12_5_Habilitacao_Controlada_2026-10-21.md).
Resultado do CI desta alteração deve ser lido no job do HEAD da PR, não presumido.


## Bloqueio posterior — C16-R12.7 e correção C16-R12.7R1

PR #22 integrada; main 0155808916b352cde6f718835df0ab2cdfb10cb5 e atualização
Termux C16-R12.6 PASS. Regressão local C16-R12.7 FAIL (1/159), exit 1,
Python 3.13.5 e pip check PASS: seleção ambígua da FK de plan_id no teste de
catálogo. A causa foi identificada no teste; modelo e migrations preservados.
Correção em revisão no checkpoint [C16-R12.7R1](FRcaixinha_2_2_C16_R12_7R1_Correcao_Teste_FK.md).
CI anterior verde não substitui correção e revalidação local. Interromper avanço
para backup Git/ensaio até corrigir e verificar regressão. Fase 2 em andamento.
SQL/papéis protegidos preservados; restauração e ensaio real NOT_RUN.


## Estado posterior — C16-R12.14, ensaio real concluído

Base main/Termux 13a87726491f55fe20dfa04a6d5b754979fc6355, PR #23.
Correção FK validada: teste original e regressão local/CI 159/159 PASS.
Backup Git recuperado independentemente e cópia privada Drive com bytes iguais:
fffe247fedb91871d4e3222f3d5cccfcfe30c4409a8219d22e70dac758755f7f.
Ensaio transacional REAL C15/C16 C16-R12.13R1 PASS, exit 0. Chamada direta exige
PYTHONPATH apontando a backend; falha inicial de importação corrigida sem editar fontes.
Auditoria independente pós-ensaio C16-R12.14 READ ONLY PASS, exit 0: zero schemas
de ensaio, relações e constraints de aplicação nos inventários consultados;
public.alembic_version ausente. DDL revertido, sem migrations permanentes.
Restauração funcional SQL NOT_RUN; F2-01/F2-02 continuam PARCIAIS; Fase 2 EM ANDAMENTO.
Fonte atual de evidências, ADR/ERR, backups e próximo gate:
[checkpoint C16-R12.14](FRcaixinha_2_2_C16_R12_14_Ensaio_Real_e_PosAuditoria.md).
Esta atualização documental não autoriza novo ensaio, implantação ou Fase 3.


## C16-R12.16R1 — Correcao da transacao Alembic em revisao

Main/Termux 14ae65f9524e2e38bd8cf48585c7e80f8b7b314c, PR #24, atualizacao
C16-R12.15 PASS. Inspecao offline C16-R12.16 PASS identificou autobegin da
consulta de identidade sem commit externo no env.py. Correcao proposta:
engine.begin() envolvendo identidade e migrations; nenhuma revisao alterada.
Novo teste usa SQLAlchemy/Alembic reais com DBAPI gravador, sem banco ou sockets.
CI e validacao Debian pendentes; nao presumir PASS. Fonte ADR/ERR e gates:
FRcaixinha_2_2_C16_R12_16R1_Transacao_Alembic.md.
Ensaio real anterior e pos-auditoria seguem PASS. Aplicacao permanente e
restauracao funcional NOT_RUN. Fase 2 em andamento; Fase 3 nao iniciada.
