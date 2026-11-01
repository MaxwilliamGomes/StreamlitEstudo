# Plano técnico 001: Priorização de orçamentos

**Spec:** [spec.md](spec.md)
**Status:** proposto

## Stack

| Item | Escolha | Motivo |
|---|---|---|
| Linguagem | Python 3.12 | Já instalado |
| Dashboard | Streamlit | Definido na constituição |
| Visuais clicáveis | `st.components.v2` | HTML próprio permite formatação condicional e devolve o clique. Plotly fica só no protótipo da T03 |
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
  componentes.py        visuais clicáveis em HTML, CSS e JavaScript
  visuais.py            tema, formatação e dados de exibição
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

1. O componente envia o item clicado como gatilho (`setTriggerValue`).
2. O callback atualiza a seleção em `st.session_state`, a única fonte de verdade (princípio 7).
3. O Streamlit reexecuta a página.
4. `aplicar_selecao()` filtra os dados já carregados, e todos os visuais são redesenhados.

`aplicar_selecao()` é uma função pura, sem nenhuma dependência do Streamlit. Ela usa `vw_orcamento_item` para ligar cliente, orçamento e produto. A filtragem apenas escolhe linhas, sem recalcular regras (princípio 6).

| Visual | Componente | Gatilho |
|---|---|---|
| Fila | `componentes.fila` | `linha` |
| Vencidos | `componentes.vencidos` | `faixa` e `cliente` |
| Rupturas | `componentes.rupturas` | `produto` |

## Riscos validados na T03

O protótipo com Plotly e `st.dataframe` validou o fluxo de seleção e mostrou seus limites: seleção interna do widget, chave versionada para limpar e posição de linha na tabela. O redesenho trocou esses visuais por componentes próprios. Com gatilhos, cada clique chega uma vez, e o destaque vem sempre do estado, o que elimina esses três problemas.

## Testes por critério de aceite

| Critérios | Como verificar |
|---|---|
| CA1 a CA7, CA10 | `test_regras.py`, contra o banco carregado |
| CA8, CA9 | `test_selecao.py`, com a função pura |
| Clique real e destaque | Roteiro manual no navegador |

## Figma

O [mockup no Figma](https://www.figma.com/design/uYQsNc90YJTsOzRnH2g9Pr) registra a evolução do layout, mas a versão B foi superada na revisão do dashboard, feita a pedido do usuário. **O dashboard é hoje a referência visual**, inspirada nas telas ATM Transaction de `Bi-Referencias`. A T15 decide como alinhar o Figma (princípio 10).

Direção visual atual:

- Fundo escuro com gradientes azul e vinho.
- Painel azul à esquerda, com valor da fila, três anéis por classe e alerta de créditos sem NF.
- Números grandes sem cartão, com cor conforme a situação.
- Fila como protagonista, agrupada por classe, com barra de valor, barra de cobertura e pílula de atraso (RN13).
- Vencidos e rupturas abaixo da fila, com altura fixa para a página não pular ao filtrar.

Alterações em `app/visuais.py` e `app/componentes.py` exigem reiniciar o servidor, porque módulos importados ficam em memória.

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
| 10. Figma como contrato | Seção Figma, com a divergência atual registrada e pendente da T15 |
