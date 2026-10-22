# C16-R12.41 — Validacao cadastral CPF e CNPJ (21/10/2026)

## Autorizacao e base tecnica

O proprietario respondeu "Prossiga" a proposta C16-R12.41 para criar modulo
Python puro de validacao cadastral com testes, PR e CI, sem migration ou escrita
no banco. Baseline main anterior: `37088decbb7e74c2bb43ae50f0f8f099c724bf94`.
Repo unico: `fronassor-art/FRcaixinha-2.2`; raiz Termux:
`~/FRcaixinha_2.2`. Banco autoritativo unico:
`frcaixinha_2_2_dev`, PostgreSQL 18.2, revisao
`c16r5_20261020`, inalterado por esta PR.

Contrato aprovado de 16/10/2026: 3.1-A/3.1-A.1 (CPF/CNPJ e contato),
6.1-A (identidade de membro), 13.1/13.2 (seguranca/LGPD),
AT-45, AT-46 e AT-47. Fonte publica adicional para algoritmo CNPJ:
manual tecnico Serpro/Receita Federal
https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/documentos-tecnicos/cnpj/manual-dv-cnpj.pdf.
Receita Federal confirmou em 31/07/2026 a emissao de CNPJ alfanumerico;
inscricoes numericas anteriores continuam validas.

## Mudancas pequenas e autocontidas

1. `backend/app/document_validation.py`: funcao de normalizacao/validacao
   de CPF, funcao de normalizacao/validacao de CNPJ. Apenas Python stdlib.
2. `backend/tests/test_document_validation.py`: 10 testes novos `unittest`.

Entrada aceita em formato compacto ou com mascara completa convencionada.
CPF: 11 digitos ASCII, dois digitos verificadores e rejeicao de sequencias
uniformes. CNPJ: 12 caracteres ASCII [0-9A-Za-z] e dois DVs numericos.
Modulo 11 com valores ASCII-48 e pesos ciclicos 2..9, incluindo exemplar
oficial ficticio `12.ABC.345/01DE-35`. Maiusculas/minusculas na entrada
alfanumerica resultam em representacao canonica maiuscula. Mascaras parciais,
caracteres Unicode, digitos verificadores errados e entradas nao-string sao
rejeitados. `normalize_*` retorna somente documento validado ou `None`.

Nao ha endpoints novos, persistencia de CPF/CNPJ, criptografia ou HMAC,
autenticacao, registro de usuarios, operacao financeira ou dependencia nova.
O resultado nao prova existencia, situacao cadastral, titularidade ou poderes
de representacao.

## Evidencia de testes

PR: https://github.com/fronassor-art/FRcaixinha-2.2/pull/30
HEAD de codigo testado: `7e8b953fad59f50bb96a923a51d58575d39264ac`.
GitHub Actions, Backend CI, run `39712992632`, job `119608454904`:
- Python 3.13, pinned requirements existentes, instalacao isolada do CI.
- `python -m pip check`: "No broken requirements found."
- `python -B -m unittest discover -s tests -p 'test_*.py' -v`:
  **Ran 176 tests, OK**, zero erros e falhas; 10 casos novos.
- Status do run: `completed/success`.
- Este resultado vale para o HEAD acima; se houver novo HEAD, validar o CI
  correspondente antes da integracao.

## Governanca, limites e proximo passo

O backend nao muda modelos ORM, Alembic, migracoes C15/C16, arquivos de
configuracao, workflow ou dependencias. Nenhum SQL foi executado neste
checkpoint; nenhuma instalacao ou backup feito no Termux. Os backups Git/PG
e a copia privada externa verificados nos checkpoints C16-R12.20 a .37
permanecem preservados. Como e apenas logica Python sem persistencia nem
DDL, nao se repetiu o ensaio de restauracao nem se criou backup PostgreSQL.

F2-05/F2-06/F2-07 seguem parciais ou nao implementados como fluxo completo.
A proxima etapa separada precisara desenhar/criar servicos de identidade
segura, criptografia/HMAC, verificacao de e-mail e operacoes PF/PJ sob
controle de tenant; nenhum cadastro real fica habilitado por esta PR.
Fase 2 EM ANDAMENTO, Fase 3 NAO INICIADA.

Ao receber novo resultado do CI no HEAD final, registrar e aplicar o gate.
Depois integrar PR e atualizar Termux por fast-forward com verificacao de
branch/SHA e arvore limpa. Nenhuma migration por reflexo.
