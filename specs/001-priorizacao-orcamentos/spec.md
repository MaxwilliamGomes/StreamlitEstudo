# Spec 001: Priorização de orçamentos

**Status:** esclarecida, pronta para o plano
**Data de referência:** 28/08/2026

## Problema

A distribuidora recebe orçamentos por e-mail, WhatsApp e telefone sem saber quais pode atender com o estoque atual e para quais clientes é seguro vender a prazo. A decisão depende de informações comerciais, de estoque e financeiras que hoje estão separadas.

## Usuário

Uma única pessoa: o dono ou gestor da distribuidora, que decide o que liberar, priorizar ou segurar.

## Perguntas de negócio

- **PN1:** Quais orçamentos posso atender agora?
- **PN2:** Quais orçamentos devo segurar por risco de crédito?
- **PN3:** Quais produtos estão travando orçamentos, e quem é afetado?
- **PN4:** Quanto tenho vencido, com quem e há quanto tempo?

## Histórias de usuário

- **H1:** Como gestor, quero ver a fila de orçamentos classificada para decidir por onde começar.
- **H2:** Como gestor, quero clicar em um cliente para ver seus orçamentos, títulos e produtos pedidos.
- **H3:** Como gestor, quero clicar em um produto em ruptura para ver os orçamentos e clientes afetados.

## Regras de negócio

- **RN1 – Fila:** contém pedidos com status `novo` ou `cotado` que têm itens. Mensagens sem itens ficam fora e são apenas contadas como "não cotáveis".
- **RN2 – Valor do orçamento:** soma de quantidade × preço × (1 − desconto). O preço por volume vale apenas para quantidade acima de 100. O total de cada orçamento é arredondado para 2 casas, com meio centavo para cima.
- **RN3 – Saldo do título:** valor do título menos os créditos do extrato com a mesma NF até a data de referência, nunca negativo. Crédito sem NF não abate.
- **RN4 – Vencido:** título com saldo maior que zero e vencimento anterior à data de referência.
- **RN5 – Cliente bloqueado:** tem título vencido há mais de 15 dias. Exatamente 15 dias não bloqueia.
- **RN6 – Ruptura:** a soma das quantidades do produto em toda a fila supera o estoque. Mensagens de reforço ou acréscimo, como PED025 e PED013, contam como pedidos separados.
- **RN7 – Classificação:** cada orçamento recebe uma única classe, nesta ordem de precedência:
  1. **Bloqueado:** o cliente está bloqueado.
  2. **Ruptura:** tem ao menos um produto em ruptura.
  3. **Atendível:** nos demais casos.
- **RN8 – Ordem da fila:** Atendível, depois Ruptura, depois Bloqueado. Dentro de cada classe, do maior para o menor valor.
- **RN9 – Faixas de atraso:** 1–15, 16–30, 31–60 e mais de 60 dias.

- **RN10 – KPIs com seleção ativa:** "Vencido" soma apenas os títulos que atendem à seleção. "Clientes bloqueados" conta os clientes bloqueados que têm algum desses títulos, mesmo que o bloqueio venha de outro título do cliente.

## Requisitos funcionais

- **RF1:** Exibir KPIs de valor na fila, quantidade por classe, valor vencido, clientes bloqueados e produtos em ruptura. (PN1, PN2, PN4)
- **RF2:** Exibir a fila com orçamento, cliente, valor, classe e motivo da classe. (PN1, PN2)
- **RF3:** Exibir o valor vencido por cliente e faixa de atraso. (PN4)
- **RF4:** Exibir os produtos em ruptura com demanda, estoque e prazo de reposição. (PN3)
- **RF5:** Permitir cross filter entre os visuais conforme a matriz abaixo. (H2, H3)
- **RF6:** Permitir limpar todas as seleções com uma única ação.
- **RF7:** Exibir alerta com a quantidade e o valor dos créditos sem NF até a data de referência. (PN2)

## Cross filter

| Ao selecionar | KPIs | Fila | Vencidos | Rupturas |
|---|---|---|---|---|
| Cliente em Vencidos | Filtra | Orçamentos do cliente | Destaca o cliente | Produtos em ruptura pedidos pelo cliente |
| Faixa em Vencidos | Filtra | Orçamentos de clientes com títulos na faixa | Destaca a faixa | Produtos em ruptura pedidos por esses clientes |
| Produto em Rupturas | Filtra | Orçamentos com o produto | Clientes com orçamento desse produto | Destaca o produto |
| Linha da Fila | Filtra | Destaca o orçamento | Cliente do orçamento | Produtos em ruptura do orçamento |

Comportamento:

- Selecionar de novo o mesmo item remove a seleção.
- Seleções em visuais diferentes se combinam, e o resultado precisa atender a todas.
- O visual de origem mantém todos os itens e destaca o selecionado.
- Os visuais afetados informam quando o filtro não retornar dados.

Limite conhecido: títulos não têm itens de produto com ligação direta nos dados originais. Por isso, a seleção de produto chega aos vencidos pelo cliente, não pelo título.

## Critérios de aceite

Sem seleção ativa, com data de referência 28/08/2026:

- **CA1:** A fila tem 114 orçamentos, somando R$ 345.563,89.
- **CA2:** A classificação retorna:

| Classe | Orçamentos | Valor |
|---|---|---:|
| Atendível | 13 | R$ 20.399,52 |
| Ruptura | 67 | R$ 199.191,07 |
| Bloqueado | 34 | R$ 125.973,30 |

- **CA3:** São 4 mensagens não cotáveis: PED012, PED016, PED018 e PED027.
- **CA4:** Há 67 títulos com saldo, somando R$ 178.288,54, dos quais 16 vencidos somam R$ 27.549,39.
- **CA5:** Vencido por faixa:

| Faixa | Títulos | Valor |
|---|---|---:|
| 1–15 dias | 6 | R$ 12.084,24 |
| 16–30 dias | 5 | R$ 8.823,90 |
| 31–60 dias | 5 | R$ 6.641,25 |
| Mais de 60 dias | 0 | R$ 0,00 |

- **CA6:** Há 8 clientes bloqueados e 21 produtos em ruptura.
- **CA7:** Casos de referência:
  - PED003 é Atendível, com R$ 185,00.
  - PED008 é Bloqueado, mesmo tendo produto em ruptura.
  - PED029 é Ruptura, com R$ 11.340,00.
  - Ferragens Central (C003) não fica bloqueada, porque T0012 está vencido há exatamente 15 dias.
- **CA8:** Ao selecionar Móveis Lima (C010), a fila mostra apenas orçamentos desse cliente e os KPIs acompanham.
- **CA9:** Limpar as seleções devolve exatamente os valores de CA1 a CA6.
- **CA10:** O alerta mostra 6 créditos sem NF, somando R$ 12.978,95.

## Fora de escopo

- Conciliação detalhada de títulos e extrato (feature 002).
- Interpretação automática das mensagens.
- Alteração de status ou aprovação de orçamento pelo dashboard.
- Reserva de estoque entre orçamentos.
- Tendências históricas e análise de margem.
- Sinalização de desconto acima da política, como na PED011.

## Esclarecimentos

Decididos em 01/11/2026:

- **E1 – Crédito sem NF:** não abate o saldo e aparece como alerta (RF7), pois não se sabe a quais títulos se refere.
- **E2 – Pedidos possivelmente repetidos:** PED025 e PED013 contam como pedidos separados, para não subestimar a ruptura.
- **E3 – Desconto acima da política:** fica fora desta feature, pois só existe no texto da mensagem.
