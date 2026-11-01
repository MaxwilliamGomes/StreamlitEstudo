# Plano técnico 001: Priorização de orçamentos

**Spec:** [spec.md](spec.md)
**Status:** proposto

## Stack

| Item | Escolha | Motivo |
|---|---|---|
| Linguagem | Python 3.12 | Já instalado |
| Dashboard | Streamlit | Definido na constituição |
| Gráficos | Plotly | Devolve os pontos clicados ao Streamlit |
| Banco | PostgreSQL 16 em Docker Compose | Definido na constituição |
| Acesso ao banco | psycopg 3 | Cliente direto, com SQL explícito para estudo |
| Testes | pytest | Já instalado |

Dependências ficam em um ambiente virtual, com versões fixadas em `requirements.txt`. pandas 2.2.3 e NumPy 2.2.2 são obrigatórios, porque `gerar_dados.py` falha ou muda de resultado em versões mais novas. Credenciais ficam em um `.env`, fora do versionamento.

## Estrutura

```text
docker-compose.yml
.env.example
requirements.txt
db/
  01_tabelas.sql
  02_views.sql
scripts/
  gerar_dados.py        (já existe)
  carregar_dados.py     recria as tabelas a partir dos CSVs
app/
  conexao.py            conexão com o banco, usada por app, scripts e testes
  main.py               monta a página
  dados.py              lê as views
  selecao.py            estado e aplicação do cross filter
  visuais.py            KPIs, tabela e gráficos
tests/
  test_regras.py        CA1 a CA7 e CA10, nas views
  test_selecao.py       CA8, CA9 e matriz de cross filter
```

## Modelo de dados

**Tabelas:** `clientes`, `produtos`, `pedidos`, `pedido_itens`, `titulos`, `extrato`, com chaves primárias e estrangeiras.

**Parâmetros:** a tabela `parametros` tem uma linha com a `data_referencia`, 28/08/2026 por padrão, e as views a consultam (princípio 9).

**Views:** concentram todas as regras (princípio 6).

| View | Regra | Conteúdo |
|---|---|---|
| `vw_titulo_saldo` | RN3, RN4, RN9 | Saldo, dias de atraso e faixa por título |
| `vw_cliente_bloqueado` | RN5 | Clientes bloqueados |
| `vw_orcamento_item` | RN1, RN2 | Itens da fila com valor |
| `vw_produto_ruptura` | RN6 | Demanda, estoque e prazo dos produtos em ruptura |
| `vw_orcamento_classificado` | RN2, RN7, RN8 | Um orçamento por linha, com classe, motivo e ordem |
| `vw_credito_sem_nf` | RF7 | Créditos sem NF até a data de referência |
| `vw_mensagem_nao_cotavel` | RN1 | Pedidos em aberto sem itens |

A NF do extrato é extraída da descrição com a expressão `NF-[0-9]+`.

## Cross filter

Fluxo a cada clique:

1. O visual devolve o item clicado.
2. `selecao.py` atualiza o estado em `st.session_state`, a única fonte de verdade (princípio 7).
3. O Streamlit reexecuta a página.
4. `aplicar_selecao()` filtra os dados já carregados, e todos os visuais são redesenhados.

`aplicar_selecao()` é uma função pura, sem nenhuma dependência do Streamlit. Isso permite testar a matriz de cross filter com pytest. Ela usa `vw_orcamento_item` para ligar cliente, orçamento e produto.

Os dados das views são carregados uma vez, em cache, e filtrados em memória. Isso mantém a interação rápida, e o volume é pequeno. A filtragem da seleção não recalcula regras: ela apenas escolhe linhas, respeitando o princípio 6.

| Visual | Componente | Como informa a seleção |
|---|---|---|
| Vencidos | Plotly barras empilhadas | `on_select="rerun"`, com cliente e faixa em `customdata` |
| Rupturas | Plotly barras | `on_select="rerun"`, com o produto em `customdata` |
| Fila | `st.dataframe` | `on_select="rerun"`, com `selection_mode="single-row"` |

## Riscos validados na T03

Testados no navegador com Streamlit 1.66.1 e `prototipos/cross_filter.py`.

| Risco | Resultado | Decisão |
|---|---|---|
| Repetir o clique não remove a seleção | Confirmado: o redesenho zera o widget, e o clique chega como evento novo | Tratar a seleção em callback de `on_select` e alternar quando o valor já estiver selecionado |
| Seleção do widget não limpa por código | Confirmado e resolvido | Incrementar uma versão usada na `key` dos widgets a cada limpeza |
| Redesenho apaga o destaque no gráfico de origem | Resolvido | Calcular a cor de cada barra a partir do estado, sem depender da seleção do Plotly |
| Tabela guarda a posição da linha, não o orçamento | Confirmado: o estado segue correto, mas a marcação some quando a fila muda | Guardar o código do orçamento no estado, alternar a seleção como nos gráficos e mostrar o destaque em uma coluna da fila |

O callback substitui a comparação com o último evento, prevista na versão inicial do plano, e evita que um gráfico desenhado antes fique desatualizado na mesma execução.

Também passaram: combinação de seleções entre visuais, nova seleção depois de remover ou limpar e clique na tabela.

Não foi testado: desmarcar uma linha pela própria tabela. O caso entra no roteiro manual da T14.

## Testes por critério de aceite

| Critérios | Como verificar |
|---|---|
| CA1 a CA7, CA10 | `test_regras.py`, contra o banco carregado |
| CA8, CA9 | `test_selecao.py`, com a função pura |
| Clique real e destaque | Roteiro manual no navegador |

## Figma

O mockup vem depois deste plano e antes da construção dos visuais. Ele define layout, hierarquia e cores de uma página única, com os componentes acima. Toda divergência será registrada aqui (princípio 10).

## Verificação da constituição

| Princípio | Atendido por |
|---|---|
| 2. Separação entre o quê e o como | Tecnologia aparece só neste plano |
| 4. Rastreabilidade | Visuais ligados aos requisitos RF1 a RF4 e RF7 |
| 5. Critério verificável | Tabela de testes |
| 6. Regra em um só lugar | Views; Python apenas filtra e exibe |
| 7. Cross filter explícito | `selecao.py` e `st.session_state` |
| 8. Dados reproduzíveis | `carregar_dados.py` recria o banco a partir dos CSVs |
| 9. Data de referência explícita | Tabela `parametros` |
| 10. Figma como contrato | Seção Figma e registro de divergências |
