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

Dependências ficam em um ambiente virtual, com versões fixadas em `requirements.txt`. Credenciais ficam em um `.env`, fora do versionamento.

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

## Riscos

| Risco | Efeito | Resposta |
|---|---|---|
| Streamlit guarda o último clique no widget | O mesmo evento alternaria a seleção a cada reexecução | Comparar com o último evento processado |
| Seleção do widget não limpa por código | "Limpar seleções" manteria o destaque | Trocar a `key` do widget a cada limpeza |
| Redesenhar um gráfico muda seus dados | O visual de origem perderia o destaque | Manter todos os itens no visual de origem e destacar por cor |

Esses riscos são a parte menos certa do plano. Por isso, a primeira tarefa de código será um protótipo mínimo do clique, com dados fictícios, antes de construir o restante.

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
