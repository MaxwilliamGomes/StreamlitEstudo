"""Dashboard de priorização de orçamentos.

Rodar: .venv/Scripts/streamlit run app/main.py
"""
import sys
from functools import partial
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import visuais  # noqa: E402
from app.dados import carregar  # noqa: E402
from app.selecao import Selecao, alternar, aplicar_selecao  # noqa: E402

st.set_page_config(page_title="Priorização de orçamentos", layout="wide")
estado = st.session_state
estado.setdefault("selecao", Selecao())


def ao_clicar(campo, key, gatilho):
    """Cada clique chega como gatilho; repetir o mesmo item remove a seleção."""
    valor = getattr(estado[key], gatilho)
    if valor:
        estado.selecao = alternar(estado.selecao, campo, valor)


def limpar():
    estado.selecao = Selecao()


def rotulo(selecao, dados):
    partes = []
    if selecao.cliente:
        nomes = dados.vencidos.loc[dados.vencidos.cod_cliente == selecao.cliente, "cliente"]
        partes.append(f"Cliente: {nomes.iloc[0]}")
    if selecao.faixa:
        partes.append(f"Faixa: {selecao.faixa} dias")
    if selecao.produto:
        nomes = dados.rupturas.loc[dados.rupturas.cod_produto == selecao.produto, "descricao"]
        partes.append(f"Produto: {nomes.iloc[0]}")
    if selecao.orcamento:
        partes.append(f"Orçamento: {selecao.orcamento}")
    return " · ".join(partes)


visuais.aplicar_tema()
dados = carregar()
selecao = estado.selecao
recorte = aplicar_selecao(dados, selecao)

visuais.cabecalho(rotulo(selecao, dados), limpar)
esquerda, direita = st.columns([1, 3.05], gap="medium")
with esquerda:
    visuais.painel(recorte.kpis, dados.creditos_sem_nf, dados.nao_cotaveis)
with direita:
    visuais.indicadores(recorte.kpis)
    with st.container(key="cartao_fila"):
        visuais.cabeca_fila(recorte.kpis)
        visuais.fila(
            visuais.dados_fila(recorte.fila, selecao), "fila",
            partial(ao_clicar, "orcamento", "fila", "linha"),
        )
    coluna_vencidos, coluna_rupturas = st.columns(2)
    with coluna_vencidos, st.container(key="cartao_vencidos"):
        st.html('<p class="titulo">Vencido por cliente</p><p class="sub">Clique em uma faixa ou cliente</p>')
        visuais.vencidos(
            visuais.dados_vencidos(recorte.vencidos, selecao), "vencidos",
            partial(ao_clicar, "faixa", "vencidos", "faixa"),
            partial(ao_clicar, "cliente", "vencidos", "cliente"),
        )
    with coluna_rupturas, st.container(key="cartao_rupturas"):
        st.html(
            f'<p class="titulo">Produtos em ruptura</p><p class="sub">{len(recorte.rupturas)} produtos. '
            "Barra: estoque coberto.</p>"
        )
        visuais.rupturas(
            visuais.dados_rupturas(recorte.rupturas, selecao), "rupturas",
            partial(ao_clicar, "produto", "rupturas", "produto"),
        )
