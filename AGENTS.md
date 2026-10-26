# AGENTS.md — FRcaixinha 2.2

**Abrangência:** estas instruções se aplicam a toda a árvore do único repositório `fronassor-art/FRcaixinha-2.2`. São uma consolidação operacional das regras aprovadas; **não alteram o Contrato Técnico Mestre e não concedem G2**.

**Carregamento obrigatório:** ao iniciar uma sessão Codex, leia este arquivo, as fontes normativas abaixo e o checkpoint vigente da [Issue #46](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46). O arquivo não contém status permanente de HEAD/migrations: sempre verifique Git/banco/checkpoint no escopo autorizado. **Cada prompt operacional deve reproduzir o cabeçalho obrigatório abaixo com os dados da tarefa, mesmo quando este AGENTS.md já tiver sido lido**.

**Regras prioritárias:** uma única raiz ativa `~/FRcaixinha_2.2`; um único repositório oficial; PostgreSQL 18.2 autoritativo `frcaixinha_2_2_dev` no Termux; ferramentas existentes reutilizadas; sem projetos/clones/bancos/.venv/SDK duplicados; gates G2 granulares; nenhuma falha bloqueante ignorada; backup recuperável e checkpoint registrado no GitHub antes do fechamento.

**Autoridade operacional:** Codex é executor principal de código/Git quando possui ambiente/G2; o Master executa ações interativas com segredos no Termux normal ou Debian PRoot independente. ChatGPT orienta e verifica; não simular execução. A atualização GitHub pós-backup ocorre **na mesma interação ativa** com conector autorizado, nunca como promessa de trabalho em segundo plano.

## A. Cabeçalho obrigatório em TODOS os prompts operacionais para Codex

```text
FRCAIXINHA 2.2 — [ID E OBJETIVO DA TAREFA]

INSTRUÇÕES PERMANENTES — NÃO OMITIR

1. IDENTIDADE E RAIZ ÚNICA
   Projeto: FRcaixinha 2.2, sem reutilização implícita do legado.
   Raiz ativa autorizada: ~/FRcaixinha_2.2.
   PROIBIDO criar segundo clone, segunda raiz ativa, nova versão concorrente
   ou estrutura duplicada. Artefatos temporários isolados e backups externos
   protegidos não constituem outro projeto ativo.

2. REPOSITÓRIO OFICIAL E GIT
   Repositório: fronassor-art/FRcaixinha-2.2.
   Antes de agir conferir pwd, remote, branch, HEAD, refs de main/origin/main,
   git status, diff e arquivos não rastreados. Preservar alterações legítimas.
   NÃO utilizar reset --hard, clean -fd, force-push, merge/rebase destrutivo,
   push ou PR sem G2 específica correspondente.

3. BANCO ÚNICO E ISOLAMENTO
   Banco autoritativo: PostgreSQL 18.2 no Termux, frcaixinha_2_2_dev.
   Isolamento multi-tenant e por ciclo conforme contrato e migrations Alembic.
   PROIBIDO banco persistente paralelo, uma base por administrador, bases
   financeiras divergentes, DDL/DML, migration, downgrade ou stamp sem G2.
   Não abrir PG em tarefa documental ou de Git que não precise dele.

4. FERRAMENTAS E NÃO DUPLICAÇÃO
   Android/Termux, Codex CLI, Git/GitHub/Actions, Debian PRoot somente quando
   necessário, Python oficial 3.13.5 em .venv existente para testes backend,
   FastAPI/SQLAlchemy/Alembic, Flutter/Dart, Java e Android CI.
   Verificar versões reais e compatibilidade; valores dos checkpoints são
   históricos. Reusar instalações e backend/requirements.txt existentes.
   PROIBIDO reinstalar/atualizar por tentativa, criar .venv/SDK/toolchain
   duplicados ou manter serviços permanentes sem necessidade autorizada.

5. GATES E DADOS FINANCEIROS
   Executar APENAS o escopo da G2 atual. Nenhuma G2 geral autoriza custos,
   regras financeiras, migração, login/cadastro/e-mail/Pix reais, Mercado Pago,
   implantação ou acesso a dados reais; cada operação precisa de gate próprio.
   Os ensaios físicos PostgreSQL, triggers IN-05, decisões IN-06/IN-08 e
   restauração funcional específica de C205 permanecem pendentes até prova.

6. ERROS: PARAR → REPRODUZIR → CAUSA → MENOR CORREÇÃO → RETESTAR →
   REGRESSÃO → REGISTRAR. Não esconder falhas ou retirar testes para passar.

7. BACKUP E ESPAÇO
   Verificar RAM, espaço livre e necessidade antes de ações de risco.
   Backup preventivo antes de ações estruturais e backup final recuperável
   de tarefa estável; Git/código e PostgreSQL/dados com backups distintos.
   Criptografar AGE onde exigido, manter segredos fora do chat, validar
   restauração, SHA256 e cópia externa privada por download e comparação.
   Não apagar backups válidos nem criar projeto paralelo para recuperá-los.

8. INTERFACE CORRETA
   Este texto é PROMPT para o Codex CLI, NÃO comando Bash do Termux.
   O Codex é executor preferencial de código/Git dentro de G2; quando não
   possuir acesso/senha, PARAR e reportar EXECUTOR, O_QUE_TENTOU, BLOQUEIO,
   CAUSA, EVIDÊNCIA, O_QUE_NÃO_FEZ e ALTERNATIVA SEGURA.
   ChatGPT prepara o menor comando necessário para Termux normal ou Debian
   PRoot separado; o proprietário executa e devolve saída real.

9. ATUALIZAÇÃO OBRIGATÓRIA NO GITHUB / NÃO DEIXAR TAREFAS ABERTAS
   Antes do backup final, reconciliar a documentação versionável autorizada,
   testes, PR e checklist, de modo que o backup cubra o SHA estável.
   Quando o backup final, sua recuperação e cópia externa forem validados,
   ChatGPT, NO MESMO ATENDIMENTO e sem precisar de segundo pedido do Master,
   deverá atualizar: (a) comentário de encerramento da PR/issue aplicável;
   (b) topo da Issue #46 com status, SHA, banco, testes, erro, hash, Drive,
   restrições e próxima G2; (c) conferir por leitura que o GitHub recebeu.
   Nunca declarar ENCERRAMENTO_INTEGRAL=PASS antes de confirmar essas escritas.
   Atualizações versionadas faltantes do Documento Mestre/ADR/ERR/cartão exigem
   edição e Git/PR autorizados pelo gate; não presumir que atualizar a Issue
   equivale a alterar arquivos do repositório. Registrar pendência se faltar.
   Se GitHub estiver inacessível, sinalizar CHECKPOINT_GITHUB=BLOCKED, manter
   evidências e NÃO avançar para tarefa dependente. Sem execução autônoma
   em background e sem prometer atualização futura fora de sessão ativa.

10. RETORNO FINAL E PROVA
    Informar EXECUTOR, AUTORIZACAO_G2, diretório, remote, branch, SHA anterior
    e novo, arquivos, testes PASS/FAIL/BLOCKED/NOT_RUN, migração/banco,
    correções/regressões, backup recuperado, SHA256, Drive privado,
    URLs do checkpoint GitHub e próxima G2. PASS apenas com prova real.

DADOS DA TAREFA:
- ID: [ID]
- OBJETIVO: [objetivo exato]
- G2: [autorização explícita]
- BASELINE: [SHA e branch verificados]
- ARQUIVOS PERMITIDOS: [escopo]
- OPERAÇÕES VEDADAS: [limites adicionais]
- TESTES E EVIDÊNCIAS: [critérios]
- CONDIÇÃO DE PARADA: [fail/bloqueio]
- RESULTADO ESPERADO: [provas e link do checkpoint]
```

## B. Modelo de entrega para Termux (NÃO executar texto de Codex no shell)

Toda instrução Bash entregue ao proprietário deve indicar claramente **Termux normal** ou **Debian PRoot independente**, o diretório, a finalidade, as pré-condições e o que será modificado. Oferecer um bloco completo, específico à etapa, sem incluir credenciais ou comandos de instalação/destruição não autorizados. Usar `set -euo pipefail` quando aplicável, conferir o SHA e a branch antes de tocar refs e parar no primeiro erro. Pedir a saída real, evitando simular PASS.

Exemplo puramente READ ONLY de validação do contexto (não serve como autorização para executar outras operações):

```bash
(
  set -euo pipefail
  cd "$HOME/FRcaixinha_2.2"
  echo '===== TERMUX — PREFLIGHT READ ONLY ====='
  pwd
  git remote get-url origin
  git branch --show-current
  git rev-parse HEAD
  git rev-parse refs/heads/main
  git status --short
  echo 'PREFLIGHT_READ_ONLY=PASS'
)
```

## C. Ritual de encerramento obrigatório, sem tarefas órfãs

1. **Preflight da etapa:** ler contrato, instruções, checkpoint mais recente da Issue #46 e ADR/ERR relevante; confirmar G2, SHA, branch, banco/backup e ambiente.
2. **Execução permitida:** implementar ou inspecionar apenas o escopo autorizado; caso surja FAIL/BLOCKED, interromper, investigar, corrigir e retestar antes de avançar.
3. **Conferência:** testar no executor correto, confirmar regressões e revisão independente quando exigida. Registrar o que NÃO foi testado.
4. **Git/documentação versionável:** no gate autorizado, registrar alterações canônicas em commits/PR e conferir os SHAs antes do backup final para evitar que uma edição posterior invalide a fotografia recuperável.
5. **Backup final e externo:** somente após estabilidade; criptografia, recuperação independente, hash e cópia externa privada confirmados.
6. **Ação imediata de ChatGPT na mesma conversa:** ao receber o PASS do backup/cópia, publicar registro final na PR e atualizar o topo da Issue #46, sem aguardar outra solicitação. Ler de volta ambas as atualizações e confirmar sua gravação. Não atribuir PASS a testes não realizados.
7. **Gate de saída:** somente com todas as evidências e confirmações de GitHub, declarar `ENCERRAMENTO_INTEGRAL=PASS` para o escopo exato. Se o conector GitHub ou aprovação de mudança canônica faltar, registrar a limitação e manter `BLOCKED/PENDENTE` no aspecto afetado; não abrir a etapa dependente.
8. **Protocolo novo chat:** reler este padrão e Issue #46 ANTES de qualquer prompt, validar `main`/branch e conferir adendos históricos. Não confiar exclusivamente na memória do modelo; a fonte versionada e a Issue são as referências.

## E. Fontes normativas

- Contrato Técnico Mestre FINAL_APROVADO (16/10/2026), cláusulas 1.8, 15 e 16.
- Documento Mestre v1.1 (20/10/2026), seções 5–7, 15–17, Anexo I, ADR/ERR.
- Instruções Permanentes (20/10/2026), linha 12: após correção/checkpoint/merge/backup, atualizar as fontes canônicas.
- Documento Mestre Adendo v1.2 (25/10/2026), seção 2 e ADR-020 (raiz, banco, ferramentas, G2 e metodologia).
- GitHub Issue #46: histórico e checkpoint vigente, verificado a cada tarefa.

**Importante:** esta edição documenta o pedido de governança do Administrador Master de 26/10/2026. Não é licença automática para editar contratos, abrir PR, executar migration ou publicar código. Qualquer versão que for integrada no Git será sujeita à G2/PR e aos testes de escopo próprios.

## F. Verificação antes de considerar esta política efetivamente instalada

Após PR documental, revisão independente e merge autorizados, conferir o SHA da `main`, sincronizar o único checkout local preservando alterações existentes e confirmar em **nova sessão do Codex** que `AGENTS.md` foi localizado/lido. A mera presença em uma branch de PR **não prova** instalação nem carregamento pelo executor local. O fechamento requer checkpoint GitHub e backup verificável quando a etapa estável exigir.

**Não** criar o segundo projeto para validar; nenhuma migration, nova base, instalação ou execução financeira decorre deste arquivo.
