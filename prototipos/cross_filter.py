"""Protótipo da T03: testa o clique entre visuais com dados fictícios.

Rodar: .venv/Scripts/streamlit run prototipos/cross_filter.py
"""
from functools import partial

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DADOS = pd.DataFrame(
    [
        ("O1", "Alfa", "Parafuso", 100),
        ("O2", "Alfa", "Correia", 200),
        ("O3", "Beta", "Correia", 300),
        ("O4", "Beta", "Óleo", 400),
        ("O5", "Gama", "Parafuso", 500),
        ("O6", "Gama", "Luva", 600),
    ],
    columns=["orcamento", "cliente", "produto", "valor"],
)
CAMPOS = ("cliente", "produto", "orcamento")
COR_NORMAL, COR_DESTAQUE, COR_APAGADA = "#2a78b5", "#d9622b", "#c9d3dc"

st.set_page_config(page_title="Protótipo de cross filter", layout="wide")
estado = st.session_state
estado.setdefault("selecao", dict.fromkeys(CAMPOS))
estado.setdefault("versao", 0)
estado.setdefault("eventos", [])


def registrar(texto):
    estado.eventos = ([texto] + estado.eventos)[:8]


def ao_clicar_grafico(campo, key):
    """Alterna a seleção: o redesenho zera o widget, então repetir o clique chega como evento novo."""
    pontos = estado[key].selection.points
    valor = pontos[0]["customdata"] if pontos else None
    if isinstance(valor, list):
        valor = valor[0]
    if valor == estado.selecao[campo]:
        valor = None
    registrar(f"{campo}: {valor}")
    estado.selecao[campo] = valor


def ao_clicar_tabela(codigos, key):
    linhas = estado[key].selection.rows
    valor = codigos[linhas[0]] if linhas else None
    registrar(f"orcamento: {valor}")
    estado.selecao["orcamento"] = valor


def limpar():
    estado.selecao = dict.fromkeys(CAMPOS)
    estado.versao += 1  # chave nova descarta a seleção guardada nos widgets
    registrar("limpar")


def filtrar(df, ignorar=None):
    for campo, valor in estado.selecao.items():
        if valor is not None and campo != ignorar:
            df = df[df[campo] == valor]
    return df


def barras(campo, titulo):
    # A origem ignora o próprio filtro: mantém os itens e só destaca.
    agrupado = filtrar(DADOS, ignorar=campo).groupby(campo, as_index=False).valor.sum()
    atual = estado.selecao[campo]
    cores = [
        COR_NORMAL if atual is None else COR_DESTAQUE if item == atual else COR_APAGADA
        for item in agrupado[campo]
    ]
    fig = go.Figure(go.Bar(x=agrupado[campo], y=agrupado.valor, customdata=agrupado[campo], marker_color=cores))
    fig.update_traces(selected_marker_opacity=1, unselected_marker_opacity=1)
    fig.update_layout(title=titulo, height=320, clickmode="event+select", dragmode=False)
    key = f"grafico_{campo}_{estado.versao}"
    st.plotly_chart(fig, key=key, on_select=partial(ao_clicar_grafico, campo, key), selection_mode="points")


st.title("Protótipo de cross filter")
st.button("Limpar seleções", on_click=limpar)

esquerda, direita = st.columns(2)
with esquerda:
    barras("cliente", "Valor por cliente")
with direita:
    barras("produto", "Valor por produto")

fila = filtrar(DADOS, ignorar="orcamento").reset_index(drop=True)
key_fila = f"fila_{estado.versao}"
st.dataframe(
    fila,
    key=key_fila,
    on_select=partial(ao_clicar_tabela, fila.orcamento.tolist(), key_fila),
    selection_mode="single-row",
    hide_index=True,
)

st.write("Valor filtrado:", int(filtrar(DADOS).valor.sum()))
st.write("Seleção:", estado.selecao)
st.write("Eventos:", estado.eventos)
