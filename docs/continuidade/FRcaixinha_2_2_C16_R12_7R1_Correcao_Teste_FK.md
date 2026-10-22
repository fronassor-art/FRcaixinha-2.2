# C16-R12.7R1 — correção da seleção de FK no teste de catálogo

Base Git: main 0155808916b352cde6f718835df0ab2cdfb10cb5, PR #22 integrada.
Fase 2 EM ANDAMENTO; Fase 3 NÃO INICIADA.
Escopo: correção mínima de teste e continuidade, conforme regra 17.3.
Não autoriza merge desta correção, DDL, ensaio real ou restauração.

## Evidência e reprodução

C16-R12.6: proprietário executou fetch e merge --ff-only no checkout único
~/FRcaixinha_2.2; main 0155808916b352cde6f718835df0ab2cdfb10cb5, árvore limpa, exit 0.
C16-R12.7: Debian PRoot Python 3.13.5, backend/.venv existente:
- python -B -m pip check: No broken requirements found.
- python -B -m unittest discover -s tests -p "test_*.py" -v:
  159 testes executados, 1 falha, exit 1.
- Teste: LicenseCatalogSchemaTests.test_price_foreign_keys_and_version_chain.
- AssertionError: license_price_versions.plan_id != license_plans.id.
Não houve verificação Git final nesse bloco, pois set -e interrompeu na falha.
O CI anterior de 159 testes PASS continua evidência daquela execução, não
invalida a falha local. Nenhum PASS de regressão local deve ser declarado.
Mensagens de ensaio real durante unittest vieram dos mocks, não de DDL real.

## ERR-C16-R12.7 — diagnóstico e menor correção

O modelo LicensePriceVersion declara duas FKs na coluna plan_id:
license_plans.id, direta, e license_price_versions.plan_id, como parte da
FK composta (plan_id, previous_price_version_id) para a versão anterior do mesmo plano.
Ambas são intencionais. O teste usava next(iter(column.foreign_keys)) como se
houvesse somente uma FK e comparava o primeiro elemento com license_plans.id.
A saída local reproduz a escolha da outra FK. A causa demonstrada é a seleção
ambígua no teste, não mudança de modelo, banco, regra financeira ou dependência.
Não atribuir a falha à versão Python ou fixar PYTHONHASHSEED para esconder o erro.

Correção: conferir a coleção completa de dois destinos com assertCountEqual;
selecionar exatamente a FK direta pelo destino; exigir uma única FK de changed_by.
Manter todas as demais asserções de alvos, RESTRICT, composição da cadeia,
unicidades e proibição de autorreferência.
Não há alteração de modelos, migrations C15/C16, executor, acionador, dependências
ou workflows. Não remover teste, relaxar a proteção de planos ou reinstalar pacotes.

## Validação e passagem

A suíte CI executa novamente o teste corrigido e a regressão completa offline.
Resultado PENDENTE na submissão deste checkpoint; consultar job do HEAD da PR
para conclusão. Após revisão/merge autorizados, atualizar o mesmo checkout e
reexecutar o teste local que falhou e a regressão. Somente depois continuar o
backup Git do checkpoint e o planejamento operacional do ensaio.
Backup Git novo do checkpoint 0155808: PENDENTE, não criar como etapa concluída
enquanto a regressão local estiver FAIL. Não remover backups anteriores.

Backups SQL/papéis C16-R12.4.7 a .10 continuam preservados e com cópia privada
Drive comparada byte a byte; referências e hashes no checkpoint C16-R12.5.
Restauração funcional SQL NOT_RUN; ensaio transacional PostgreSQL NOT_RUN;
aplicação permanente de C15/C16 NÃO AUTORIZADA. Nenhuma alteração no PG ocorreu.
