# C16-R12.29 — Implantacao C15/C16 e auditoria independente

## Autorizacao e baseline
O proprietario respondeu "Prossiga" a proposta especifica C16-R12.28:
aplicar permanentemente C15/C16, incluindo COMMIT, no destino fixo
frcaixinha_2_2_dev, PostgreSQL 18.2, 127.0.0.1:5432, frc22_owner,
codigo 67adc6eda5b93ad0c84d15862b48b8fba4ff53ee.
Nao e autorizacao para novas revisoes, downgrade, stamp, alteracoes de papeis,
dados de negocio ou inicio da Fase 3.

C16-R12.26 atualizacao Termux PASS, exit 0, backend preservado.
C16-R12.27 preflight READ ONLY PASS, exit 0: Git/3 backups/revisoes e hashes
PASS, banco vazio, somente public, quatro bases esperadas, nao replica.
Esse era o estado ANTERIOR a implantacao; nao deve ser usado como estado atual.

## Execucao C16-R12.28
Termux normal -> Debian PRoot independente -> backend/.venv Python 3.13.5.
Gate e URL definidos apenas no processo Python e removidos em finally.
Senha digitada por getpass no celular, sem arquivo de credencial.
Preflight imediato READ ONLY confirmou identidade/banco vazio e ausencia de
outras sessoes cliente na base. Revisoes congeladas e cadeia verificadas.
Alvo fixo c16r5_20261020 pelo Alembic command.upgrade e Config(alembic.ini).
env.py corrigido usa engine.begin() abrangendo identidade e migrations.

Saida fornecida pelo proprietario:
- BASELINE_E_BACKUP=PASS; REVISOES_E_HASHES=PASS.
- PREFLIGHT_IMEDIATO_READ_ONLY=PASS.
- Context impl PostgresqlImpl; Will assume transactional DDL.
- Running upgrade -> c15r2_20261020.
- Running upgrade c15r2_20261020 -> c16r5_20261020.
- ALEMBIC_UPGRADE_RETORNOU=PASS.
- C16_R12_28_EXECUCAO=PASS; MIGRATIONS_EXECUCAO_EXIT_CODE=0.

## Auditoria independente C16-R12.29
Nova conexao psql READ ONLY como frc22_owner em frcaixinha_2_2_dev,
PG 18.2, read_only on, replica f. Comparacao exata dos nomes das tabelas de
aplicacao com os 17 modelos carregados offline, excluindo alembic_version.
Todas as 18 tabelas pertencem a frc22_owner no schema public.

Tabelas de aplicacao:
contracting_parties, cycles, license_entitlement_segments, license_offers,
license_payment_obligations, license_plans, license_price_versions,
license_subscriptions, memberships, payment_attempts, payment_reconciliation_events,
payments, quotas, role_grants, tenants, term_acceptances, user_identities.
Tabela adicional de controle: alembic_version, unica linha c16r5_20261020.

| Tipo de constraint | Quantidade | Nao validadas |
|---|---:|---:|
| CHECK (c) | 95 | 0 |
| Foreign key (f) | 28 | 0 |
| NOT NULL (n) | 176 | 0 |
| Primary key (p), incluindo Alembic | 18 | 0 |
| Unique (u) | 32 | 0 |

70 indices; zero invalidos ou nao prontos.
Gate tambem verificou ausencia de schemas adicionais nao sistemicos e donos
divergentes nas relacoes public.
TABELAS_E_REVISAO_PERSISTIDAS=PASS.
PROPRIETARIOS_E_ESTADO_CATALOGO=PASS.
C16_R12_29_AUDITORIA_POS_MIGRATION=PASS; POS_MIGRATION_EXIT_CODE=0.
Git final main 67adc6e limpo.

## Resultado e limites
C15/C16 agora APLICADAS PERMANENTEMENTE, com persistencia comprovada em nova conexao.
Estado anterior "nao aplicadas/nao autorizadas" foi superado somente para essas
duas revisoes e para a execucao concluida. Nao repetir upgrade por reflexo.
A auditoria de nomes, donos, versao e estado do catalogo nao e comparacao completa
de todas as definicoes de colunas/constraints/indices com as revisoes, nem teste
funcional de dados, isolamento entre tenants, APIs ou fluxos financeiros.
convalidated=true e indisvalid=true nao substituem testes de comportamento.
F2-01/F2-02 continuam PARCIAIS ate avaliacao completa dos seus criterios.
Fase 2 EM ANDAMENTO; Fase 3 nao iniciada.

## Backups e proximo gate
Bundle Git verificado 1386cc3 cobre o backend aplicado, identico ao 67adc6e;
nao cobre registros documentais posteriores. Sem necessidade de novo bundle
somente para documentar o proprio backup.
Dump PostgreSQL anterior de 1281 bytes cobre o estado SEM tabelas de aplicacao;
restauracao limitada ja PASS, sem owner/ACL. NAO e backup do estado implantado.
Backup PostgreSQL POS-MIGRATION: PENDENTE, proxima etapa C16-R12.30,
sem sobrescrever os arquivos anteriores. Depois verificar leitura, indice,
conteudo esperado e copia externa. Restauracao de dados de aplicacao continua
NAO TESTADA; preservam-se limites R12.25.
Papeis nao alterados por esta implantacao; backup separado anterior preservado.
Nenhum erro bloqueante nas execucoes apresentadas. Nenhuma nova operacao SQL foi
executada pelo conector para escrever este registro.
Depois consolidar a evidencia do novo backup nesta PR antes de integra-la.
