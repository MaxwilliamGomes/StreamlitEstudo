# Validação 001: Priorização de orçamentos

**Data:** 01/11/2026 | **Ambiente:** Chrome em 1500 × 1040, Streamlit 1.66.1

## Critérios de aceite

| Critério | Teste automático | Navegador | Resultado |
|---|---|---|---|
| CA1 Fila | `test_ca1_fila` | 114 orçamentos, R$ 345,6 mil | Aprovado |
| CA2 Classes | `test_ca2_classificacao` | 13, 67 e 34 | Aprovado |
| CA3 Não cotáveis | `test_ca3_mensagens_nao_cotaveis` | 4 mensagens | Aprovado |
| CA4 Títulos | `test_ca4_titulos_com_saldo` | 16 títulos, R$ 27,5 mil | Aprovado |
| CA5 Faixas | `test_ca5_vencido_por_faixa` | R$ 12,1 mil, R$ 8.823,90 e R$ 6.641,25 | Aprovado |
| CA6 Bloqueios e rupturas | `test_ca6_*` | 8 clientes e 21 produtos | Aprovado |
| CA7 Casos de referência | `test_ca7_*` | Não conferido caso a caso | Aprovado por teste automático |
| CA8 Cliente | `test_ca8_*` | Móveis Lima: 2 orçamentos, R$ 1.135,00 | Aprovado |
| CA9 Limpar | `test_ca9_*` | Voltou a todos os totais | Aprovado |
| CA10 Créditos sem NF | `test_ca10_*` | 6 créditos, R$ 12.978,95 | Aprovado |
| CA11 Formatação | `test_ca11_*` | PED008 e PED009 não conferidos na tela | Aprovado por teste automático |

## Matriz de cross filter

| Ação | Resultado na tela | Situação |
|---|---|---|
| Clicar em cliente | Filtra fila, KPIs e rupturas. Origem mantém os itens e destaca | Aprovado |
| Repetir o clique no cliente | Remove a seleção | Aprovado |
| Clicar em faixa | 14 orçamentos, 5 títulos, R$ 8.823,90, clientes fora da faixa apagados | Aprovado |
| Repetir o clique na faixa | Remove a seleção | Aprovado |
| Clicar em produto | Arruela lisa 3/8: 3 orçamentos, R$ 425,00 | Aprovado |
| Repetir o clique no produto | Não testado no navegador; coberto por `test_alternar_seleciona_e_remove` | Parcial |
| Clicar em linha da fila | Filtra KPIs e demais visuais, linha destacada | Aprovado |
| Repetir o clique na linha | Remove a seleção | Aprovado |
| Combinar produto e cliente | PED001, R$ 180,00 | Aprovado |
| Seleção sem dados | PED2636 mostra mensagens de vazio em vencidos e rupturas | Aprovado |
| Limpar seleções | Restaura todos os valores | Aprovado |

## Ocorrências

| Ocorrência | Tratamento |
|---|---|
| Na combinação, o KPI mostrava 2 produtos e o cartão dizia "3 produtos" | Comportamento correto, pois o cartão é a origem. Texto trocado para "3 na lista" |
| Servidor escutava em todas as interfaces de rede | Restrito a `127.0.0.1` em `.streamlit/config.toml` |
| Capturas reduzidas deslocaram os cliques do teste automatizado | Erro do roteiro de teste, não do dashboard. Testes refeitos em tamanho real |

## Não coberto

- Larguras de tela diferentes de 1500 px.
- Outros navegadores.
- Leitores de tela e navegação por teclado.
- Comportamento com a base recarregada enquanto a página está aberta, pois os dados ficam em cache.
