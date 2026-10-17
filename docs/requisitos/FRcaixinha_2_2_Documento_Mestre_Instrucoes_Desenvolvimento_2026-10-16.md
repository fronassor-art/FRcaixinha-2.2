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
