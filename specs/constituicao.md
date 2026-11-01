# Constituição do projeto

Regras permanentes, válidas para todas as features. Specs, planos e tarefas não podem contrariá-las.
Para mudar uma regra, altere este arquivo primeiro e registre o motivo no histórico.

## Stack

- Python, Streamlit e PostgreSQL em Docker.
- Figma para o mockup.

## Princípios

1. **Spec antes do código.** Nada é implementado sem requisito na spec. Se a necessidade mudar, a spec muda primeiro e o código depois.
2. **Separação entre o quê e o como.** A spec descreve comportamento e valor de negócio, sem citar tecnologia. Decisões técnicas ficam no plano.
3. **Sem suposição silenciosa.** Toda dúvida fica marcada como `[A ESCLARECER]` e precisa ser resolvida antes do plano.
4. **Rastreabilidade.** Todo visual responde a uma pergunta de negócio, ligada a um requisito e a um critério de aceite. Visual sem pergunta não entra.
5. **Critério de aceite verificável.** Cada critério descreve um resultado que pode ser conferido, com valores esperados quando existirem.
6. **Regra de negócio em um só lugar.** Status, KPIs e conciliação são calculados no banco. O Streamlit apenas filtra e exibe.
7. **Cross filter explícito.** O estado da seleção tem uma única fonte de verdade, e a spec declara o que cada visual filtra e não filtra.
8. **Dados reproduzíveis.** `dados/originais/` é imutável, e a base é sempre recriada por `scripts/gerar_dados.py`.
9. **Data de referência explícita.** Nenhum cálculo depende da data do sistema. O padrão é 28/08/2026.
10. **Figma como ponto de partida.** O mockup orienta o início do visual, e o dashboard validado é a referência final. Mudanças relevantes em relação ao mockup são registradas no plano com o motivo.

## Definição de pronto

Uma tarefa só termina quando seus critérios de aceite foram verificados e spec, plano e código continuam coerentes.

## Histórico

- 2026-11-01: versão inicial.
- 2026-11-01: princípio 10 alterado. O visual evoluiu no dashboard depois do mockup, e manter o Figma como contrato exigiria retrabalho sem ganho para o estudo.
