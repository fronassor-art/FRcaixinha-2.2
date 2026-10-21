# C16-R12.5 — autorização temporária do acionador de ensaio

Data: 21/10/2026, America/Belem. Fase 2 EM ANDAMENTO; Fase 3 NÃO INICIADA.
Base de implementação: main `499f9f1bfd891def8bf11596538db367f7a7ee19` (PR #21).
O proprietário autorizou nesta sessão implementar e testar a habilitação controlada.
Não autorizou ensaio real, migrations permanentes, restauração, merge ou dinheiro real.

## Alteração em revisão

O acionador existente mantém o destino e o checkpoint C16-R12.3-SCHEMA-20261021:
127.0.0.1:5432, frcaixinha_2_2_dev, frc22_trial_c16r12,
schema frc22_c16_trial_c16r12.
O novo argumento --authorize-checkpoint só é aceito como habilitação com --execute,
checkpoint exato, confirmação interativa e senha não vazia.
Por padrão as constantes do executor continuam None. A autorização é instalada
apenas durante a chamada, restaurada em finally inclusive após interrupção.
Uma trava local ao acionador rejeita chamadas autorizadas simultâneas nesse processo.
Uso destinado a CLI independente; não representa isolamento entre processos nem
barreira contra código Python arbitrário. Não hospedar em servidor compartilhado.
Não há execução automática, senha em argumentos ou alteração de credenciais.
O caminho anterior com aprovação interna prévia é preservado.

Não foram alterados executor, C15, C16, env.py, dependências ou workflows.
O ensaio chama as funções congeladas das revisões, sem atualizar alembic_version:
não equivale a testar todo o fluxo Alembic nem a aplicar migrations permanentes.

## Evidências anteriores desta sessão

- C16-R12.4.1/.2: consultas psql em READ ONLY, exit 0; PG18.2 original,
  banco pertencente a frc22_owner. Apenas bancos padrão e banco autoritativo.
- Papel restrito: LOGIN, NOINHERIT, sem SUPERUSER/CREATEDB/CREATEROLE/
  REPLICATION/BYPASSRLS, sem associações ou SET ROLE para outros papéis.
  CONNECT e CREATE no banco, TEMP via PUBLIC; USAGE mas não CREATE em public.
  CREATE no banco não restringe criação de schemas a um prefixo.
- Inventário consultado: sem relações de aplicação, public.alembic_version
  ausente e sem schemas de ensaio. Não é auditoria de todos os clusters do celular.
- C16-R12.4.3/.4/.5: backup PostgreSQL de 18/10 conferido por SHA,
  descriptografado e processado sem executar SQL.
- C16-R12.4.6: 52 testes offline PASS em Debian PRoot Python 3.13.5, exit 0,
  main e árvore limpa preservados. Mensagens de ensaio real ocorreram em mocks.
- Regressão de 151 testes e PR #21 são antecedentes informados pelo proprietário;
  não substituem a execução do CI desta alteração.

## Backups atualizados

Diretório original Termux:
~/.local/share/frcaixinha_2_2/backups/C16_R12_4_7_20261021_201558_115mji
Diretório 700; arquivos 600.

| Arquivo original | Bytes | SHA256 |
|---|---:|---|
| frcaixinha_2_2_dev.dump.age | 1281 | 25e333ab7c117c9e4d1b922c853025aeafd6ad8850a5577894e43e0f09c25112 |
| roles_sem_senhas.sql.age | 858 | 89b15b2027433bbbf506423f88161249653e982f8248693ca5282cb4a7f43c72 |

C16-R12.4.8: ambos descriptografados em pipe; dump processado por pg_restore
--create --file=/dev/null, sem conexão ao banco. Exportação de papéis contém
frc22_owner e frc22_trial_c16r12, sem token PASSWORD. Senhas precisarão ser
redefinidas privadamente em recuperação. Não presumir backup de pg_hba.conf,
postgresql.conf, segredos, configurações externas ou recuperação física/WAL.

C16-R12.4.9: cópias criptografadas em Downloads com SHA idêntico.
C16-R12.4.10: cópias externas privadas na pasta oficial do Drive enviadas pela
integração; download independente comparado byte a byte e SHA: PASS, exit 0.
Metadados conferidos: pasta oficial, shared=false e somente proprietário.
- DB: https://drive.google.com/file/d/1E_TyGk6odRCVYka0Hvpu2LtnZIn2h1-n/view
- Papéis: https://drive.google.com/file/d/1GI9cYv9-Ox7n0scv8tzZK_X46e3GrUfz/view

Restauração funcional SQL = NOT_RUN. Cópia externa e leitura não provam restauração.
Não executar automaticamente script de papéis sobre papéis já existentes nem
pg_restore --create sobre a base autoritativa. Preparar reconciliação e recuperação
específicas antes do gate de escrita, sem criar banco concorrente por inferência.

## ADR-C16-R12.5

Decisão: usar o acionador existente, aprovação temporária explícita e dados de
destino já fixados; preservar None em repouso e as travas do executor.
Alternativas rejeitadas: fixar permanentemente constantes; usar mock/patch como
comando operacional; criar novo banco ou clone; editar migrations para facilitar.
A autorização de código não concede autorização operacional para DDL.
Os testes anteriores permanecem, acrescidos de oito cenários offline da habilitação.

## ERR-C16-R12.4.7

Sintoma: age: passphrases didn't match, exit 1, no segundo backup.
Causa: confirmação divergente da senha AGE; não houve falha PostgreSQL demonstrada.
Diagnóstico somente leitura identificou DB completo (1281 bytes), nenhum parcial.
Correção mínima: repetir só exportação dos papéis no mesmo diretório, sem recriar
o dump do banco ou remover arquivos. Reexecução exit 0; checksum do DB preservado.
Validação posterior: descriptografia/leitura de ambos e cópia externa PASS.
Prevenção: prompts separados e confirmação privada no celular; não registrar senhas.

## Validação desta alteração e próxima etapa

O CI da PR deve executar pip check e unittest discover de toda a suíte offline.
Oito testes novos; resultado só pode ser PASS após job concluído no commit da PR.
Esta versão documental registra CI PENDENTE no momento da submissão; consultar
a execução vinculada ao HEAD da PR para seu resultado, sem inferir pelo número.
Ensaio PostgreSQL real = NOT_RUN; migrations permanentes = NÃO AUTORIZADAS;
restauração funcional = NOT_RUN; merge e atualização Termux = PENDENTES.
Após revisão, CI, gate de recuperação e autorização operacional explícita,
preparar um único comando de ensaio no ambiente autorizado. Não executar agora.
