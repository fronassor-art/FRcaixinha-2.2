# C16-R12.141 — IN-02 e IN-05: escritor futuro e invalidação de artefatos (OFFLINE)

**Data:** 23/10/2026 (America/Belem). **Referência:** Issue #46, PR #55 DRAFT.
**Base autoritativa preservada:** `main@751da8f8f380fc45d58de68cf707a3c2f9149777`. Banco PostgreSQL 18.2 `frcaixinha_2_2_dev`, Alembic `c16r5_20261020`; F2P4 **NÃO APLICADA**.

## Estado das provas acumuladas

O ciclo histórico G3-C.4 **IN-01 a IN-08 OFFLINE** permanece concluído com **339/339 PASS**. Estes testes não foram reabertos.

O novo pacote PR #55 contém componentes **inativos**, nunca chamados por endpoints, que pressupõem a minuta F2P4 e um contrato transacional ainda não aprovado.

1. `g3c_completed_replay_pg.py`: JOIN `registration_idempotency` + `contracting_parties`, `FOR UPDATE`, `clock_timestamp()` após lock, vinculação PF/PJ e comparação de HMACs do pedido.
2. `g3c_session_pg.py`: JOIN sessão, identidade e credencial atuais sob `FOR SHARE`, sem RoleGrant implícito, sem login.
3. `g3c_email_confirmation_pg.py`: `FOR UPDATE`, SAVEPOINT, verificador ligado ao contato corrente, UPDATE condicional único para marcar consumo e contato. Não promove identidade `ATIVA` nem PJ `APTO`.
4. **Novo IN-02:** `g3c_initial_registration_pg.py` propõe `INSERT ... ON CONFLICT ON CONSTRAINT uq_registration_idempotency_origin_attempt DO NOTHING RETURNING`, inserções de identidade/parte/credencial/desafio e `RESERVED → COMPLETED` em um SAVEPOINT do chamador. Conflito só produz replay a partir de `COMPLETED` legitimamente vinculado; RESERVED prévio ou conflito de fingerprint falham fechados. **Não reusa/libera reserva expirada**, não comita transação externa e não devolve segredo. A emissão física do desafio usa `statement_timestamp()` do banco para não confiar no relógio da preparação.
5. **Novo IN-05:** `g3c_updated_at_trigger_plan_offline.py` propõe uma função PostgreSQL `BEFORE UPDATE` em identidade/parte/credencial para sobrepor `updated_at` em escritas ORM **e** SQL diretas, usando `GREATEST(clock_timestamp(), OLD.updated_at + INTERVAL '1 microsecond')`. **Somente texto de DDL**, não aplicado.
6. **Revogação material independente do relógio:** `g3c_artifact_invalidation_plan_offline.py` propõe triggers `AFTER UPDATE OF email, status` na identidade e `AFTER UPDATE OF password_digest, status` na credencial, invalidando desafios não consumidos e sessões não revogadas. Não apaga dados, não cria políticas de expurgo nem habilita operação.

## Prova adversarial — clock retroativo

Um timestamp atualizado por `GREATEST(clock_timestamp(), OLD.updated_at+1us)` é monotônico **por registro**, mas pode continuar **anterior** a um desafio `issued_at` se o relógio de parede retroceder: por exemplo, desafio emitido às 13:00, `OLD.updated_at=12:58`, clock corrigido para 12:55; um UPDATE pode produzir 12:58:00.000001, e `updated_at <= issued_at` continuaria verdadeiro. Portanto o gatilho IN-05 de timestamp **não basta** para impedir token A→B→A ou sessão revalidada depois de alteração de credencial. Teste offline positivo deste contraexemplo comprova **a lacuna**; proposta de revogação explícita visa impedir a reativação retroativa. Ainda faltam provas reais PostgreSQL sob concorrência e lock ordering.

## Gates NÃO cumpridos

- **Riscos de segurança/consistência:** lock-order entre sessão, identidade, credencial e desafio; deadlocks nas triggers AFTER UPDATE; colisões UNIQUE, retry/rollback, concorrência de dois escritores sob diferentes isolamentos, sessão após suspensão/reativação, restauração com dados populados. Nenhuma prova real autorizada nesta PR.
- **Autorização estrutural:** as quatro tabelas F2P4 não existem no banco corrente. A minuta inclui downgrade destrutivo `DROP TABLE` e **não foi aprovada para aplicação**. Estes triggers requerem migration nova proposta separadamente e auditoria de cadeia de dependências.
- **Política jurídica/antifraude:** recuperação/contestação PF/PJ de CPF/e-mail/CNPJ e retenção física/expurgo IN-06/IN-08 ainda não aprovados. Não presumir autorização, prazo ou apropriação de identidade.
- **Dependência de confiança:** o escritor recebe `InitialRegistrationIntent` preparado no servidor. A guarda estrutural não comprova proveniência de `origin_scope`, HMAC e IDs sem serviço confiável; nunca passar objetos arbitrários do Flutter.
- **Auditoria externa:** GitHub CI e inspeção do autor **não são parecer independente de Codex**. Solicitar auditoria independente, revisar o diff e reexecutar suite/CI em HEAD exato antes de merge.

## Ordem de conclusão determinada pelo proprietário

1. Terminar **todos** os pacotes de código e testes OFFLINE na branch/PR, corrigir falhas antes de avançar.
2. Executar testes completos, parecer independente, CI e obtenção de **aprovação expressa** sobre o pacote e políticas pendentes.
3. Só depois integrar GitHub/Termux com checkup e provas PostgreSQL isoladas **especificamente autorizadas**.
4. Somente após estado estável gerar **backup consolidado final Git/PG AGE**, recuperar, enviar ao Google Drive privado e verificar SHA/bytes. Exceção obrigatória: **backup preventivo válido antes de migrations/operações estruturais de risco** autorizadas.

**Até este checkpoint: GitHub CI do último código/ensaios offline 415/415 PASS, mas G3-C transacional real continua BLOCKED.** Nenhuma alteração foi feita no banco principal, nas migrations, no Termux ou nos backups históricos.

## Adendo posterior — C16-R12.161 (23/10/2026)

A referência acima ao downgrade destrutivo descreve corretamente o estado deste checkpoint histórico. A proteção efetiva introduzida depois e seus limites estão registrados na nota C16-R12.161 do checkpoint C16-R12.142. Este adendo não altera as evidências nem os portões pendentes documentados acima.
