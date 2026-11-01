# Tarefas 001: Priorização de orçamentos

**Spec:** [spec.md](spec.md) | **Plano:** [plan.md](plan.md)

Cada tarefa gera um commit e só é marcada depois de verificada. Se uma tarefa exigir mudança de comportamento, a spec é alterada primeiro.

## Fase 1: Ambiente

- [x] **T01** Criar `docker-compose.yml` e `.env.example` com PostgreSQL 16.
  - Verificação: o container fica saudável e aceita conexão.
- [x] **T02** Criar `requirements.txt` e o ambiente virtual.
  - Verificação: `streamlit`, `plotly`, `psycopg` e `pytest` são importados.

## Fase 2: Protótipo de risco

- [x] **T03** Criar um protótipo de cross filter com dados fictícios, fora de `app/`.
  - Cobre: os três riscos do plano.
  - Verificação: no navegador, selecionar, remover a seleção repetindo o clique e limpar tudo funcionam sem alternância indevida.
  - Se falhar: revisar o plano antes de seguir.

## Fase 3: Dados e regras

- [x] **T04** Criar `db/01_tabelas.sql`, com chaves e a tabela `parametros`.
- [ ] **T05** Criar `scripts/carregar_dados.py`.
  - Verificação: contagem de linhas igual à dos CSVs e nenhuma chave quebrada.
- [ ] **T06** Criar `vw_titulo_saldo`, `vw_cliente_bloqueado` e `vw_credito_sem_nf`, com testes primeiro.
  - Cobre: RN3, RN4, RN5, RN9, RF7, CA4, CA5, CA10 e a parte de clientes do CA6.
- [ ] **T07** Criar `vw_orcamento_item`, `vw_produto_ruptura` e `vw_orcamento_classificado`, com testes primeiro.
  - Cobre: RN1, RN2, RN6, RN7, RN8, CA1, CA2, CA3, CA7 e a parte de produtos do CA6.

## Fase 4: Mockup

- [ ] **T08** Desenhar a página no Figma, com KPIs, alerta, fila, vencidos e rupturas, incluindo o estado com seleção ativa.
  - Verificação: cada requisito RF1 a RF7 aparece no mockup, e você aprova o layout.

## Fase 5: Dashboard

- [ ] **T09** Criar `app/dados.py`, com leitura das views e cache.
- [ ] **T10** Criar `app/selecao.py` e `tests/test_selecao.py`, com testes primeiro.
  - Cobre: RF5, RF6, a matriz de cross filter, CA8 e CA9.
- [ ] **T11** Criar KPIs, alerta e fila em `app/visuais.py`.
  - Cobre: RF1, RF2, RF7.
- [ ] **T12** Criar os gráficos de vencidos e rupturas em `app/visuais.py`.
  - Cobre: RF3, RF4.
- [ ] **T13** Montar `app/main.py` e ligar os visuais à seleção, conforme o Figma.
  - Cobre: RF5, RF6.

## Fase 6: Validação

- [ ] **T14** Rodar todos os testes e o roteiro manual de cada linha da matriz de cross filter no navegador.
  - Verificação: CA1 a CA10 aprovados.
- [ ] **T15** Comparar o dashboard com o Figma e atualizar spec e plano com o que mudou.
- [ ] **T16** Criar o `README.md` com instruções para subir e usar o projeto.

## Dependências

- T01 e T02 podem ser feitas em paralelo.
- T03 depende de T02.
- T04 a T07 dependem de T01, nesta ordem.
- T08 depende de T03.
- T09 depende de T07.
- T10 depende de T03.
- T11 e T12 dependem de T08, T09 e T10.
- T13 depende de T11 e T12.
- T14 a T16 dependem de T13.
