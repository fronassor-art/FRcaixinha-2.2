# FRcaixinha 2.2 — IN06-R2: matriz de evidências, revisor e recuperação

**Data:** 26/10/2026 — America/Belem. **Estado: PROPOSTA / NÃO APROVADA / NÃO OPERACIONAL.**
**Etapa:** Fase 2 — IN06-R2. G2 restrita à elaboração documental; [registro antecipado na Issue #46](https://github.com/fronassor-art/FRcaixinha-2.2/issues/46#issuecomment-6427137819).
**Fonte de verdade de base:** `main@77153a90873b047c05b02850aaf46ee7473612ca`, PRs #61–#63 já merged, backup AGE recuperado e readback Drive privado verificados.
**NÃO constitui** aprovação de suficiência jurídica de provas, designação de revisor, decisão de titularidade, alteração do Contrato Técnico Mestre, parecer jurídico, licença para executar SQL/migration/transferência de dados, nem autorização para integrar esta proposta à main.

## 1. Hierarquia e limites demonstrados

**Norma aprovada:** Contrato Técnico Mestre FINAL_APROVADO de 16/10/2026, especialmente 3.1-A/3.1-A.1/3.1-A.2, 5.4 e 6.1-A/6.1-A.1/6.1-A.2. CPF/CNPJ formalmente válido, e-mail confirmado ou telefone controlado **não comprovam sozinhos identidade civil nem poderes PJ**. Foto de perfil é opcional, endereço somente quando estritamente necessário. Identidade pessoal, contratante, licença, tenant, papel e membership/cotas são distintos. Cadastro, convite, declaração de poderes ou aceite não liberam acesso financeiro, pagamento, papel ou licença por si.
**Normas operacionais:** `AGENTS.md`, Documento Mestre v1.1, Adendo v1.2 P1, matriz histórica `FRcaixinha_2_2_G3C_R12_125_IN05_IN06_Matriz_Integridade_Offline.md` (preservada como registro da época). Não reabrir F2P4 já concluída.
**Código R1 efetivo:** `backend/app/in06_claim_review_offline.py` prepara `ClaimReviewIntent` imutável com `PREPARED_OFFLINE_UNREVIEWED`, identificadores UUID opacos e falha genérica `CLAIM_PREPARATION_DENIED`. Nem requerente, nem autenticidade/suficiência da evidência, nem revisor são verificados. Não decide, persiste ou concede privilégios. `trusted_auth_subject.py` e `resource_authorization.py` são contratos offline; FastAPI publica somente `/health` no snapshot. Unicidade CPF-HMAC, email case-insensitive e CNPJ-HMAC não deve ser relaxada para resolver abuso de reserva.

## 2. IN06-R2-A — matriz de prova da pessoa física (PROPOSTA)

| Situação | Fontes de evidência candidatas — NÃO homologadas | Medida segura hoje | Decisão pendente |
| --- | --- | --- | --- |
| PF1 — cadastro preliminar sem conflito | Campos previstos no contrato, validação formal CPF e confirmação de contato, quando aplicável | Cadastro segue pendente, sem prova civil presumida nem acesso financeiro | Provas mínimas por natureza de ato |
| PF2 — acesso ordinário já autenticado sem disputa | Sujeito/sessão do verificador confiável, contexto de papel já permitido | Somente privilégios previamente aprovados; nunca tomar outra conta | Critério de reautenticação por risco |
| PF3 — CPF/e-mail reservado, alegação de cadastro indevido | Documento oficial conferido por canal legitimamente aprovado, fontes independentes ou meios equivalentes a determinar | Protocolo conceitual em análise; sem remover a reserva ou criar identidade duplicada | Método de autenticidade e suficiência |
| PF4 — invasão, contato perdido ou alterado, disputa de alta criticidade | Evidência independente do canal comprometido; revisor competente e fundamentação | Sem reset, mudança de titularidade ou acesso automático | Revisor, evidência adicional e medidas provisórias |
| PF5 — menor, incapacidade, falecimento ou representante legal | Comprovação de representação e legitimidade conforme o ato, após avaliação jurídica | BLOQUEADO para mudança automática de acesso/direitos | Procedimento legal específico e autoridade |

**Regras invariantes:** CPF válido, selfie, print, OTP, e-mail ou telefone isolados não comprovam disputa de titularidade. Não enumerar contas por mensagens/tempo de resposta; não expor CPF, e-mail ou documento de terceiro. Não presumir integração com gov.br, biometria, SMS ou custo aprovado. Não impor documento forte universalmente sem justificativa jurídica e de necessidade.

## 3. IN06-R2-B — matriz de pessoa jurídica por tipo de ato (PROPOSTA)

| Situação PJ | Verificação candidata | Bloqueio até prova/autorização |
| --- | --- | --- |
| PJ1 — pré-cadastro | CNPJ, representante PF identificado e declaração compatível | PRELIMINAR não equivale a aptidão, mandato nem RoleGrant |
| PJ2 — aceite/gestão contratual | Conferir contrato ou estatuto e alterações pertinentes, situação cadastral e poderes **para aquele ato** | QSA/CNPJ e domínio de e-mail isolados não provam todos os poderes |
| PJ3 — mandatário/procurador | Instrumento aplicável ao ato, autenticidade, cadeia de representação, escopo, validade e revogação, quando exigível | Procuração não é universalmente necessária nem universalmente suficiente |
| PJ4 — mudança de sócio, representante ou poder | Reavaliar fontes societárias e sujeito PF, mudanças, conflitos ou revogação | Nunca transferir papéis, cotas, membership, saldos, extratos ou acesso automaticamente |
| PJ5 — movimentação financeira/conta bancária/terceiros | Gate financeiro, regulatório e jurídico próprio, com tenant/ciclo | Bloqueado neste pacote, ainda que PJ seja APTO em avaliação futura |

**Pendências PJ:** catálogo de natureza societária e atos, fontes de autenticidade, documentação suficiente por ato, poder de assinatura, decisão competente, reavaliação após mudança e periodicidade de rechecagem. Nenhum prazo universal ou obrigação documental nova aprovada aqui.

## 4. IN06-R2-C — contestação e autoridade (PROPOSTA)

**Estados conceituais ilustrativos — NÃO enum de banco:** RECEBIDA → TRIAGEM → (AGUARDANDO_EVIDENCIA | EM_ANALISE) → (DEFERIDA | INDEFERIDA | ESCALADA). Bloqueio por risco é controle excepcional a regulamentar, **não** sentença jurídica, permissão automática de congelamento financeiro, revogação real ou descarte de histórico.
**Princípio de decisão:** a parte interessada não revisa o próprio caso. Administrador diretamente interessado na reserva, conta ou tenant não presume poder de adjudicar titularidade global. O Master não recebe acesso arbitrário a extratos de terceiros nem poder de liberar Pix. **Revisor efetivo, seu substituto, autoridade de recurso, conflito de interesses e esfera de competência ainda NÃO FORAM DESIGNADOS**; não inventar papel `REVIEWER`, grant ou cadastro para preencher o vazio.
**Prova e protocolo conceitual:** case_ref, requerente apenas após autenticação por serviço confiável, classe do pedido, versão de política, referências opacas a evidências, origem/autenticidade de prova, cronologia, atos e impedimentos, decisão motivada, identidade do revisor competente, recurso e histórico imutável. Nenhuma prova de terceiro divulgada ao reclamante. Sem CPF, senha, e-mail integral, documentos ou tokens em logs.
**Preservação:** até decisão validamente autorizada, manter titularidade/vínculos/histórico e contas intactos; não liberar nem tomar identidades reservadas por mera presunção de abandono, não enfraquecer índices UNIQUE e não compartilhar dados de reclamantes.

## 5. IN06-R2-D — limites de recuperação (PROPOSTA)

- **REC1 ordinária:** diferenciar redefinição por canal previamente verificado de acesso excepcional; exigir token de uso único, alta entropia, finalidade específica, expiração e invalidação comprovadas quando houver implementação aprovada. TTL de token NÃO é prazo de retenção de evidência.
- **REC2 canal comprometido/perdido:** canal alterado recentemente não pode ser a única prova; exigir caminho independente e revisor competente definidos pelo gate jurídico.
- **REC3 PF/PJ contestada:** identidade e poderes ficam em disputa; nem a contestação deferida em plano documental gera login, papel, cotas, licença, tenant, saldo, Pix ou conta bancária.
- **REC4 execução futura:** sessões e desafios comprometidos só seriam invalidados em transação real após aprovação do fluxo, proteção concorrente IN-05 e testes PG físicos; não assumir triggers IN-05 instalados por módulos offline.
- **REC5 abuso:** respostas neutras, rate limit, antirreplay, idempotência, falha fechada e notificação pelo canal seguro definido em política; não depender do canal disputado.

## 6. IN06-R2-E — decisão pendente, jurídico e privacidade

| Decisão | Estado atual | Gate indispensável |
| --- | --- | --- |
| PF: prova bastante por risco | PROPOSTA | Aprovação Master, protocolo e revisão jurídica aplicável |
| PJ: prova e poderes por ato | PROPOSTA | Matriz jurídica por natureza/ato e decisão Master |
| Revisor e instância de recurso | SEM TITULAR DESIGNADO | Competência, independência e impedimento formalmente aprovados |
| Reserva global indevida/abandonada | BLOCKED | Política antifraude, preservação e fundamento jurídico antes de exclusão/reuso |
| Recuperação operacional/sessões | NOT_RUN | G2 código, G2 PG físico e IN-05 transacional |
| Coleta, controlador, base legal, guarda e descarte | PENDENTE IN-08 | Parecer datado/competente, LGPD e aprovação específica; sem prazo presumido |
| Gov.br, consulta oficial automatizada, biometria, SMS | NÃO INTEGRADOS | Provedor, segurança, custo e aprovação separados |

Referências externas oficiais para análise, **não parecer jurídico**: [LGPD compilada](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm) (finalidade/minimização/direitos e segurança), [ANPD — direitos dos titulares](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares), [Consulta pública CNPJ](https://www.gov.br/pt-br/servicos/consultar-cadastro-nacional-de-pessoas-juridicas). O controlador, responsabilidade de revisão e enquadramento concreto ainda precisam ser definidos.

## 7. Matriz de testes futuros — TODOS NOT_RUN nesta proposta

| ID | Cenário | Critério mínimo esperado em teste offline futuro |
| --- | --- | --- |
| R2-PF01 | Cadastro formal com contato confirmado | Sem acesso financeiro, titularidade civil não presumida |
| R2-PF02 | Reserva indevida CPF/e-mail, reclamante genuíno | Não duplicar identidade, remover UNIQUE nem enumerar pessoa existente |
| R2-PF03 | Print/selfie/OTP isolado; contato recém-alterado | Negar mudança de titular sem prova extra aprovada |
| R2-PF04 | Menor/representante/falecimento | Escalar; nunca presumir representação legítima |
| R2-PJ01 | QSA confere, mas poder para o ato é insuficiente | Negar privilégio/papel/transferência de tenant |
| R2-PJ02 | Procuração vencida, revogada ou fora de escopo | Negar, preservar histórico |
| R2-PJ03 | Administrador tenta acessar outro tenant | Negar sem dados cruzados |
| R2-C01 | Requerente se indica como próprio revisor | Negar autoaprovação |
| R2-C02 | Dois pedidos de contestação conflitantes | Sem transferência automática nem vazamento de provas |
| R2-C03 | Prova contraditória ou inconclusiva | Manter análise/escalada com trilha mínima |
| R2-REC01 | Token expirado/reutilizado, replay e enumeração | Negar e proteger logs/segredos |
| R2-REC02 | Recuperação por canal comprometido | Sem validação por canal comprometido isolado |
| R2-PG01 | Duas transações, SAVEPOINT, locks, rollback, invalidação | **BLOCKED** até autorização G2 PG/IN-05 real |
| R2-LAW01 | Parecer para PF/PJ, revisor, privacidade e retenção | **PENDENTE**; sem declarar homologação jurídica |

Testes precisam usar dados fictícios e ferramentas já existentes, não relaxar proteção para obter PASS. Nenhum teste novo ou CI foi executado por este documento.

## 8. Próximo portão e proteção do projeto

1. **Nesta PR:** adicionar somente este ADR novo, em DRAFT. Revisão independente do diff e dos checks documentais; não alterar código, contrato, documento mestre ou banco.
2. **Decisão Master/jurídico:** aprovar, ajustar ou recusar a matriz PF/PJ; competência/impedimento de revisor, política de contestação/recuperação; base legal e limites de IN-08. Nada disso se presume autorizado pelo mero merge de documento PROPOSTA.
3. **G2 técnica posterior:** eventualmente desenvolver menor pacote offline/inativo com testes adversariais, sem ligar API/login ou acesso financeiro e sem criar ambientes paralelos.
4. **G2 físico posterior:** se indispensável, verificar IN-05 concorrente no PostgreSQL autoritativo com backup próprio e sem reabrir F2P4; revisão legal/segurança antes de operações reais.
5. **G2 de integração posterior:** CI de HEAD correto, revisão independente, merge por SHA esperado, sync Termux e backup AGE recuperável/offsite do SHA estável quando autorizado.

**STATUS FINAL:** `IN06_R2_DOC_PROPOSAL=PREPARED`; `IN06_R2_POLICY_APPROVED=NO`; `IN06_R2_LEGAL_REVIEW=NOT_RUN`; `IN06_R2_CODE=NOT_RUN`; `IN06_R2_PG=NOT_ACCESSED`; `IN06_R2_OPERATIONAL=BLOCKED`; `IN08=NAO_INICIADA`; `FASE_2=EM_ANDAMENTO`. Documento novo não equivale à conclusão da IN06 integral.
