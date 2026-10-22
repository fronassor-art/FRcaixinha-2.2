# C16-R12.66 — Checkpoint de continuidade: criptografia e backup

Data: 22/10/2026
Baseline integrado: `752d3a34644ca536100930f1ec2006c0b5f9a79a`
PR integrada: #32
Commit da funcionalidade: `3384d111a833bdab4bc028a502cfced68436daae`

## Git e CI

A `main` oficial contém o commit acima. O Backend CI #32 terminou em
SUCCESS com 209/209 testes. O Termux foi sincronizado por fast-forward no
checkpoint C16-R12.61. Não há alteração de código pendente neste checkpoint.

## Proteção documental

O módulo isolado usa AES-256-GCM com envelope versionado, nonce aleatório de
12 bytes e `key_id` autenticado no AAD. A busca exata usa HMAC-SHA256 com
separação de domínio `CPF`/`CNPJ`. HKDF-SHA256 separa finalidades. A
normalização CPF/CNPJ existente inclui CNPJ alfanumérico. O Python oficial é
3.13.5; pins: `cryptography==50.0.2`, `cffi==2.0.0` e `pycparser==2.22`.
Os testes criptográficos foram 13/13 PASS, a regressão 209/209 PASS e `pip
check` PASS.

Não há persistência nova, API de cadastro, operação financeira, migration ou
segredo nos arquivos. A rotação de chaves permanece pendente.

## PostgreSQL

Base autoritativa: `frcaixinha_2_2_dev`, PostgreSQL 18.2. A auditoria READ
ONLY C16-R12.50 registrou 18 tabelas, incluindo `alembic_version`, e 70
índices; revisão `c16r5_20261020`. Nenhuma escrita ou migration foi executada
neste ciclo. A recuperação estrutural anterior foi validada; a recuperação de
dados reais de aplicação não foi comprovada.

## Backup Git

Arquivo: `FRcaixinha_2_2_C16_R12_62_752d3a34644c.bundle.age`
Tamanho: 339124 bytes
SHA-256: `ff08ea2c8351b8a5a0b2770a7af4d72c41133a8be7737876656fbe8e08481094`

O backup AGE foi restaurado independentemente (C16-R12.63), com 524 objetos
e `git fsck --full --strict` PASS. A cópia privada do Google Drive (pasta
`FRcaixinha_2.2_Backups`, arquivo ID `1zgNIbuBeDySFpGqCHcfOdeMK8qz3RKrO`) foi conferida com SHA idêntico (C16-R12.64); a cópia
temporária de Downloads foi removida (C16-R12.65). Senhas AGE e credenciais
não são registradas.

## Limitações e próximo gate

A Fase 2 continua em andamento e a Fase 3 não foi iniciada. Persistência
criptografada, rotação de chaves, integração API, isolamento efetivo,
autorização operacional e fluxos financeiros exigem escopos próprios,
revisão e aprovação. Não declarar cadastro ativo ou pagamentos habilitados.
