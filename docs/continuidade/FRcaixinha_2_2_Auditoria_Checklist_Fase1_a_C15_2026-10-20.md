# FRCAIXINHA 2.2 — AUDITORIA E CHECKLIST DE CONTINUIDADE

**Versão:** 1.0 — 20/10/2026. **Corte:** após C15-R7 e backup externo C15. **Repositório:** `fronassor-art/FRcaixinha-2.2`; **`main`:** `0316c3cc29aa6966033e52d5d21d5f378683ba97`.

> **Não confundir:** `INTEGRADO` = código mergeado; `CI PASS` = job configurado executado; `DB PASS` = efeito comprovado no PostgreSQL; `BLOQ` = sem autorização ou dependência bloqueante; `PARCIAL` = só parte do requisito atendido; `NOT_RUN` = não testado. Fases e itens do Caderno de 17/10 permanecem referências; esta auditoria é a fotografia factual posterior.

## 1. Fontes auditadas

1. Contrato Técnico Mestre FINAL_APROVADO 16/10 (normativo; sem alterações).
2. Documento Mestre v1.0 16/10 (historicamente G2 não autorizado, desatualizado).
3. Caderno Mestre de 17/10 (cronograma prospectivo e checklist em 7 fases, 60 dias úteis estimados).
4. GitHub PRs #1–#17, todas integradas; `main` C15, diffs, workflows e checks.
5. Relatórios Termux/Codex C15: PG18, Python 3.13.5, SQLA2.0.55, 89 testes, AGE, recuperação e Drive.
6. Histórico anterior do Codex Cloud/PRoot: observação operacional; não pressupor que limitações atuais permaneçam idênticas.

## 2. Auditoria da Fase 0/Gates

| Controle | Estado e comprovação | Pendência |
|---|---|---|
| Contrato G1 | **PASS documental**, aprovado em 16/10 | Preservar canônico sem revisões tácitas |
| G2 | **EXECUTADO**, projeto Git criado e PRs #1–#17; a documentação de 16/10 era anterior | Localizar autorização textual original se necessária para auditoria de governança |
| Nenhum custo/serviço financeiro presumido | **Regra vigente**, nenhuma ativação real evidenciada | Verificar gates antes de produção |
| Ferramentas | Termux, Debian PRoot, GitHub Actions, Git, AGE e PG18 utilizados; versões conhecidas | Inventário Android completo e atualização Codex Cloud/ponte ainda pendentes |

## 3. Fase 1 — base do projeto (10 itens do Caderno)

| Item | Estado | Evidência e limite |
|---|---|---|
| F1-01 raiz única | PASS conforme checkpoints | `~/FRcaixinha_2.2` |
| F1-02 estrutura Flutter/backend/docs/CI | PASS Git | PRs #1–#4 |
| F1-03 repositório novo | PASS GitHub | `fronassor-art/FRcaixinha-2.2` |
| F1-04 inventário toolchains | PARCIAL | Python 3.13.5, CI, PG18; não presumir SDK local completo |
| F1-05 reúso de ferramentas | PASS nas etapas auditadas | Nada foi instalado no C15-R2–R7 por reação automática |
| F1-06 Git, .gitignore, CI e segurança | PASS código inicial; verificação de segredos por checkpoint | Auditoria de segurança integral futura |
| F1-07 API/Flutter mínimos | PASS código inicial | PRs #1 e #3; teste operacional end-to-end ainda não demonstrado |
| F1-08 APK debug CI | PASS GitHub job | PR #4 `debug-apk` success; não prova instalação em aparelho |
| F1-09 SHA, CI, backup | PASS no checkpoint C15 | Backup anterior preservado; novo C15 verificável |
| F1-10 encerramento | **Concluída no escopo de bootstrap** | Não equivale a MVP entregue |

## 4. Fase 2 — PostgreSQL, identidade e segurança (13 itens do Caderno)

| Item | Estado em 20/10 | Evidência / falta |
|---|---|---|
| F2-01 Banco único PG | **PARCIAL/operacional PASS** | PG18.2 original acessível; isolamento transacional de todos os testes de dados reais ainda não provado |
| F2-02 Alembic reversible | **PARCIAL** | Migration C15 gerada e compilada offline; `upgrade/downgrade` na base autorizada **NOT_RUN** |
| F2-03 entidades identidades/licenças | **PARCIAL** | 15 modelos ORM em `models.py`; `LicenseSubscription` ausente; entidades financeiras futuras incompletas |
| F2-04 isolamento FKs/índices | **PARCIAL** | Constraints/indexes declarados e comparados à migration, não implantados/testados no PG real |
| F2-05 cadastro PF real | **NOT_RUN/não implementado como fluxo completo** | Estrutura `UserIdentity` não demonstra API de cadastro/confirmacão |
| F2-06 PJ/representação | **NOT_RUN** | `ContractingParty` estrutural; verificação de representação pendente |
| F2-07 CPF/CNPJ, senha, email, sessão | **NOT_RUN** | Não atribuir autenticacão funcional aos modelos ORM |
| F2-08 convites/admissão | **NOT_RUN** | Membership inicial, sem fluxo de convite aprovado em execução |
| F2-09 convite sem acesso/tenant | **NOT_RUN** | Casos de autorização futura pendentes |
| F2-10 isolamento cruzado e Master | **NOT_RUN** | Constraints de DDL não substituem autorização por API |
| F2-11 aceite, políticas, consentimento versionado | **PARCIAL** | TermAcceptance e ofertas estruturais; fluxo/tamper protection e aceite efetivo pendentes |
| F2-12 calendário global | **PARCIAL** | Cycle declarado; regras de bloqueio no backend ainda não demonstradas |
| F2-13 LGPD/logs/segredos | **PARCIAL** | práticas de segurança de código e revisão de segredos; implementação integral pendente |

**Portão Fase 2:** **NÃO CONCLUÍDA**. A migration não foi aplicada; funcionalidades PF/PJ, autenticação, tenant cross-access, consentimento e LicenseSubscription ainda dependem de implementação/testes.

## 5. Fases posteriores

| Fase | Escopo | Veredito |
|---|---|---|
| Fase 3 | automação central, preço/licença, cotas, empréstimo, rateio | **NÃO CONCLUÍDA**; só modelos preparatórios |
| Fase 4 | pagamentos, Pix, idempotência, ledger e conciliação real | **NÃO CONCLUÍDA**; modelos de pagamento são inativos |
| Fase 5 | integração Flutter/API, experiência e telas reais | **NÃO CONCLUÍDA** |
| Fase 6 | testes integrais, segurança, relatórios | **NÃO CONCLUÍDA** |
| Fase 7 | validação/entrega e gates de publicação | **NÃO CONCLUÍDA** |

Não iniciar recursos financeiros reais nem considerar o plano de 60 dias transcorrido como prova de implementação.

## 6. Checkpoints técnicos e GitHub

| Checkpoint | PR | Entrega | CI/estado |
|---|---:|---|---|
| F1 FastAPI | #1 | API mínima | INTEGRADO |
| F1 CI | #2 | backend CI | sucesso GH Actions |
| F1 Flutter | #3 | Bootstrap Flutter | sucesso GH Actions |
| F1 APK | #4 | APK debug CI | sucesso GH Actions |
| F2 dependências | #5 | PostgreSQL pins | INTEGRADO |
| F2 scaffold | #6 | Alembic guard | INTEGRADO |
| F2 identidade | #7 | UserIdentity + ContractingParty | INTEGRADO |
| C06 | #8 | Tenant/RoleGrant, correção guard | GH backend PASS |
| C07 | #9 | Cycle | INTEGRADO |
| C08 | #10 | Membership | INTEGRADO |
| C09 | #11 | Quota + índice | INTEGRADO |
| C10 | #12 | Plans/pricing | INTEGRADO |
| C11 | #13 | Offer/Acceptance | INTEGRADO |
| C12 | #14 | Obligation/Payment inativo | INTEGRADO |
| C13 | #15 | Attempts/Reconciliation events inativos | INTEGRADO |
| C14 | #16 | Isolamento environment Payment | GH backend PASS |
| C15 | #17 | Primeira migration para 15 modelos | GH backend 89/89 PASS; **DB não migrado** |

**C15-R2:** revisão offline (9 testes novos); `unittest` auxiliar Python3.14: **não oficial**, apresentou falhas por dependências divergentes e ausência de httpx. **C15-R2V:** Debian PRoot `.venv` 3.13.5, pins corretos, `pip check` PASS e **89/89**. **C15-R2F:** revisão estática PASS. **C15-R3:** commit local `fe67747...`, quatro arquivos. **C15-R4:** branch publicada. **C15-R5:** PR #17 + CI oficial 89/89 PASS. **C15-R6:** merge `0316c3...`, PR concluída. **C15-R7:** main local fast-forward + AGE Git restaurado e Drive comparado: PASS.

## 7. Defeitos corrigidos e procedimento de não recorrência

| Erro | Correção registrada | Veredito |
|---|---|---|
| Alembic endereço host mismatch | `host(inet_server_addr())`, mantendo hard gate | PR #8, CI PASS |
| PRoot aninhado | nova sessão Termux independente para Debian `.venv` | C15 89/89 PASS |
| Python auxiliar incompatível | usar 3.13.5 e pins no Debian, sem tocar testes | CI 89/89 PASS |
| PG parado e PID antigo | startup controlado da instância existente, nunca novo initdb | Conexão read-only PASS |
| AGE pede senha por cima do progresso | `git bundle create --quiet`; senha direta no Termux | ENCRYPTION PASS |
| `git bundle verify -` SIGPIPE/141 | `age -d "$PART" \| { git bundle verify -; cat >/dev/null; }` | BUNDLE_VERIFY PASS |
| AGE interrompido `.partial` | confirmação manual antes da limpeza seletiva | Backup C15 PASS |
| Sem teste de recuperação real | bare temporário + unbundle/fsck/SHA, descarte final | RESTORE GIT PASS |
| Drive apenas metadados | baixar e comparar SHA-256/bytes, pasta privada | C15 BACKUP CLOUD PASS |
| Codex Cloud proxy TCP bloqueado | registrar executor e erro; não contornar nem reinstalar; fallback Termux | **PENDENTE CLOUD** |
| Documento G2 antigo causa reinício | v1.1, ADR/ERR e cartão de retomada | Documento preparado; publicação canônica pendente |

**Detalhamento completo e invariantes:** Documento Mestre v1.1, anexos G e H. Nunca repetir investigação resolvida sem evidência de mudança de causa.

## 8. Backups, artefatos e armazenamento

- Git C15: `FRcaixinha_2_2_C15_FINAL_0316c3cc29aa.bundle.age`, 166431 bytes, SHA-256 `d77fc40bbedd54c98e04e5d92d87cc493c514dcfffe01340be3af6732a274919`, local protegido e Drive id `1KiryYKBrG4muW6VYE9f3wQEAS72obMeI`, privado; descarga remota byte igual, restauração Git bare PASS.
- Dump PostgreSQL: `frcaixinha_2_2_dev_20261018_173109_8123.dump.age`, SHA-256 `95991140611c029d923e62baa05bcae3a4c0e8341fa5b1ac6ab11f5e7503b027`, remoto Drive id `1mIDfpAjbDnDFxELgQIrgwwd5_owNLH82`; **restauração SQL ainda não demonstrada**.
- Git e PostgreSQL não se substituem; sem deletar backups anteriores e sem credenciais em arquivo acessível.

## 9. Lista obrigatória ao retomar em novo chat

- [ ] Consultar contrato canônico e Documento Mestre v1.1, anexos E–M.
- [ ] Ler registro ADR/ERR antes de revisar problema já conhecido.
- [ ] Confirmar SHA da `main`, branch, status e último checkpoint; não repetir operações já PASS.
- [ ] Identificar executor: ChatGPT, Codex, Termux normal, Debian PRoot, Cloud ou CI.
- [ ] Conferir versão Python oficial e PostgreSQL 18 antes de diagnosticar falha de ambiente.
- [ ] Confirmar que `LicenseSubscription` ainda está pendente e a migration C15 **não está aplicada**.
- [ ] Conferir último backup Git/PG e suas limitações, sem restaurar automaticamente.
- [ ] Selecionar uma única ação mínima com autorização expressa.
- [ ] Ao fechar nova etapa, registrar SHA, PR, testes, estado do banco, ADR/ERR, backup e próximo gate no repositório.

## 10. Pendências e próximo gate

- [ ] **Publicar por processo documental controlado** o Documento Mestre v1.1, checklist e cartão no repositório original, sem modificar contrato e sem operações no banco.
- [ ] Corrigir a versão operacional referenciada pelo Caderno (ou publicar errata claramente vinculada), preservando original histórico.
- [ ] C16 inspeção de objetos PostgreSQL (somente leitura) e pré-migration: **autorização separada**.
- [ ] Resolver modelagem `LicenseSubscription` e eventual estratégia de revisão antes/depois da primeira aplicação, mediante contrato; não improvisar.
- [ ] Plano seguro de teste de restauração do dump PostgreSQL, sem banco persistente concorrente; autorização separada.
- [ ] Implantar `upgrade/downgrade` controlados e testar enforcement/isolamento (não realizado).
- [ ] Implementar fluxos de PF/PJ, CPF/CNPJ, autenticação, convites, aceites e autorização tenant.
- [ ] Checar integração Codex Cloud/Termux apenas em checkpoint próprio; estado Cloud ainda PENDENTE.

**STATUS GERAL:** Fase 1 BASE INTEGRADA; Fase 2 EM ANDAMENTO; código até C15 integrado e validado offline/CI; Git backup local/remoto verificado; banco PG18 existente sem migration; futura aplicação SQL NÃO AUTORIZADA.


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
