# C16-R12.143 — Gate independente: novo caso adversarial IN-02 e evidências de PR #55

**Data:** 23/10/2026. **Base autoritativa:** `main@751da8f8f380fc45d58de68cf707a3c2f9149777`. PR #55 em DRAFT, sem merge, sem Termux sync, sem escrita no PostgreSQL.<br>
**Commit do código offline submetido a CI:** `faafe6defd7c2034e0e993a1712b52869cf8ce1a`.<br>
**Código sujeito a revisão externa:** `backend/app/g3c_initial_registration_pg.py` e novos testes `backend/tests/test_g3c_initial_registration_pg_offline.py`.

## 1. Reprovação adversarial seguida de correção

**Achados:** `_valid_intent` não checava `attempt_expires_at` nem `challenge.revoked_at`. Isso deixava passar preparações com datas inválidas/revogadas. A condição `complete_attempt_statement` verificava só o novo TTL PostgreSQL de 15 minutos, medido a partir da RESERVA, permitindo renovar na prática uma preparação antiga antes do commit.

**RED:** novo conjunto de **2 testes/unittest methods**, com subcasos de expiração original não verificada, campos ausentes, datetime ingênuo, prazo 16min, janela menor que desafio, `revoked_at` presente, início do desafio inconsistente. [CI 39965694536](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/39965694536) sobre `8704c6d8e01a2902cc0d7306739df17e1ab67eaa`: `Ran 425 tests`, `FAILED (failures=7)` (um teste de SQL + seis subcasos), `pip check` PASS. Nenhum teste foi removido.

**FIX:** o writer valida janela preparada com `challenge.expires_at - issued_at == 10 min` e `attempt_expires_at - challenge.issued_at == 15 min`, recusa challenge revogado e timestamps sem timezone. O UPDATE final `RESERVED→COMPLETED` exige, além do `registration_idempotency.expires_at > clock_timestamp()`, `clock_timestamp() < intent.attempt_expires_at` vinculado como parâmetro SQLAlchemy. Uma conclusão inválida causa exceção e rollback do savepoint, sem COMMIT externo.

**GREEN:** [CI 39965872317](https://github.com/fronassor-art/FRcaixinha-2.2/actions/runs/39965872317) no SHA **`faafe6defd7c2034e0e993a1712b52869cf8ce1a`**: `No broken requirements found`, `Ran 425 tests in 3.615s`, `OK`, workflow success. Total=**339 históricos + 86 testes novos**. Testes somente offline/SQL compilado e mock, sem concorrência PostgreSQL efetiva.

## 2. Revisor independente deve conferir

1. A igualdade estrita das duas janelas coincide com `prepare_initial_registration` e `prepare_email_challenge` (ambos derivados da mesma hora confiável). Falhas de clocks/truncamento e timestamp SQL devem ser verificadas sob ensaio PG isolado autorizado.
2. O bound `clock_timestamp() < intent.attempt_expires_at` é avaliado **no final da escrita**, já em transação externa, e rollback real do savepoint precisa de teste físico. Ainda não existe verificação da proveniência do `InitialRegistrationIntent` no próprio adaptador: este deve ser criado exclusivamente por serviço server-side auditado.
3. `ON CONFLICT DO NOTHING` do escritor e `FOR UPDATE` de replay: assegurar que RESERVED concorrente e expirada não seja indevidamente reutilizada; antecipar deadlocks entre writer, confirmação, sessão e triggers de revogação.
4. `g3c_f2p4_rollback_audit_offline.py` **somente DETECTA** o downgrade destrutivo; o `downgrade()` real ainda contém quatro `DROP TABLE` e três `DROP INDEX`. Exigir nova estratégia real de rollback antes de autorização de F2P4, sem apagar dados.
5. Política de recuperação/contestação CPF/CNPJ/e-mail e retenção física IN-06/08 ainda exige decisão jurídica e do proprietário. Não presumir expurgo por TTL.
6. Executar no Codex/ambiente INDEPENDENTE **sem modificar main/banco**, revisar diff completo da PR #55, executar CI/testes em SHA exato, entregar PASS/FAIL/BLOCKED por IN01–IN08 com logs de falha e reteste. Somente após todas as correções cabe propor merge/Termux.
7. Não tratar PR #54 (plano documental), PR #55 ou este checkpoint como autorização para migration, deploy, login, Pix, e-mail real ou alteração no PostgreSQL autoritativo.

## 3. Status final deste checkpoint

**IN-02 nova correção offline:** PASS; **regressão histórica:** PASS; **auditoria independente Codex:** NOT_RUN; **IN-05 triggers real:** BLOCKED; **IN-07 downgrade seguro:** BLOCKED; **IN-06/08 política:** BLOCKED; **F2P4 aplicável:** NOT_AUTHORIZED. Não houve backup consolidado porque ainda não houve integração aprovada. Backups anteriores AGE Git/PG e recuperação C16-R12.131–136 permanecem válidos.

## Adendo posterior — C16-R12.161 (23/10/2026)

A descrição acima de `DROP TABLE` e `DROP INDEX` no downgrade real corresponde ao estado deste checkpoint histórico. A proteção posterior C16-R12.147 e suas limitações estão detalhadas na nota C16-R12.161 do checkpoint C16-R12.142; as evidências IN-02 deste documento permanecem inalteradas.
