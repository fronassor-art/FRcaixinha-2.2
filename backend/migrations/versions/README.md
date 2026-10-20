# Historico de migrations do FRcaixinha 2.2

Este diretorio contem a revisao inicial incremental `c15r2_20261020` para os
15 modelos SQLAlchemy existentes no baseline C14. O DDL PostgreSQL foi
congelado na revisao, incluindo constraints e indices; a ordem de criacao
respeita as FKs e cria `uq_license_plans_id_limits` antes de `license_offers`.

A revisao ainda nao foi aplicada ao banco. A compilacao offline nao substitui
testes de upgrade/downgrade, integridade, dados existentes e restauracao SQL
no PostgreSQL autorizado. `LicenseSubscription` permanece pendente de uma
revisao posterior; nenhum estado financeiro foi ativado nesta revisao.
