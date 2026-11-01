# Priorização de orçamentos

Dashboard de estudo em Streamlit e PostgreSQL, construído com Spec Driven Development.

Uma distribuidora fictícia recebe orçamentos sem saber quais pode atender. O dashboard cruza fila, estoque e financeiro para responder: **o que atender, resolver ou segurar hoje?** Clicar em um cliente, faixa de atraso, produto ou orçamento filtra os demais visuais, como no cross filter do Power BI.

## Como rodar

Requisitos: Python 3.12 e Docker. Os comandos são para PowerShell no Windows.

```powershell
Copy-Item .env.example .env        # troque a senha no arquivo .env
docker compose up -d
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python scripts/carregar_dados.py
.venv/Scripts/streamlit run app/main.py
```

O dashboard abre em http://localhost:8501. Depois de alterar arquivos em `app/`, reinicie o servidor.

## Testes

Com o banco carregado:

```powershell
.venv/Scripts/python -m pytest tests
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `specs/` | Constituição, spec, plano, tarefas e validação |
| `db/` | Tabelas e views com as regras de negócio |
| `app/` | Dashboard e cross filter |
| `dados/` | CSVs da base; `dados/originais/` guarda os arquivos de partida |
| `scripts/` | Geração da base sintética e carga no banco |
| `tests/` | Testes das regras, do cross filter e da formatação |
| `prototipos/` | Protótipo usado para validar o clique entre visuais |

## Spec Driven Development

Para acompanhar o método, leia nesta ordem:

1. [Constituição](specs/constituicao.md): regras permanentes.
2. [Spec](specs/001-priorizacao-orcamentos/spec.md): o que construir e por quê.
3. [Plano](specs/001-priorizacao-orcamentos/plan.md): como construir.
4. [Tarefas](specs/001-priorizacao-orcamentos/tasks.md): ordem de execução.
5. [Validação](specs/001-priorizacao-orcamentos/validacao.md): resultado dos critérios de aceite.

## Dados

Os dados são fictícios. A base foi ampliada por `scripts/gerar_dados.py`, com seed fixa. Para reproduzir os mesmos arquivos, use as versões de pandas e NumPy de `requirements.txt`.

A data de referência é 28/08/2026 e fica na tabela `parametros`.
