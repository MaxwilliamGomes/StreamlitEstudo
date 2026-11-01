"""Dashboard de priorização de orçamentos.

Rodar: .venv/Scripts/streamlit run app/main.py
"""
import sys
from dataclasses import replace
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
estado.setdefault("versao", 0)  # chave nova descarta a seleção guardada nos widgets


def ao_clicar_grafico(campo, key):
    """O redesenho zera o widget, então repetir o clique chega como evento novo."""
    pontos = estado[key].selection.points
    if pontos:
        valor = pontos[0]["customdata"]
        valor = valor[0] if isinstance(valor, list) else valor
        estado.selecao = alternar(estado.selecao, campo, valor)
    else:
        estado.selecao = replace(estado.selecao, **{campo: None})


def ao_clicar_fila(codigos, key):
    """A tabela guarda a posição da linha; o estado guarda o código do orçamento."""
    linhas = estado[key].selection.rows
    if linhas:
        estado.selecao = alternar(estado.selecao, "orcamento", codigos[linhas[0]])
    estado.versao += 1


def limpar():
    estado.selecao = Selecao()
    estado.versao += 1


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
versao = estado.versao

visuais.cabecalho(rotulo(selecao, dados), limpar)
esquerda, direita = st.columns([1, 3.1])
with esquerda:
    visuais.painel(recorte.kpis)
with direita:
    visuais.indicadores(recorte.kpis, dados.creditos_sem_nf, dados.nao_cotaveis)
    vencidos, rupturas = st.columns(2)
    with vencidos, st.container(key="cartao_vencidos"):
        st.html(
            '<p class="titulo">Vencido por cliente</p>'
            '<p class="sub">Clique em uma faixa ou cliente para filtrar</p>'
        )
        key = f"faixas_{versao}"
        visuais.grafico_faixas(recorte.vencidos, selecao, key, partial(ao_clicar_grafico, "faixa", key))
        key = f"clientes_{versao}"
        visuais.grafico_clientes(recorte.vencidos, selecao, key, partial(ao_clicar_grafico, "cliente", key))
    with rupturas, st.container(key="cartao_rupturas"):
        st.html(
            '<p class="titulo">Produtos em ruptura</p>'
            f'<p class="sub">{len(recorte.rupturas)} produtos, do menor para o maior estoque coberto. '
            "Cinza: estoque. Laranja: falta.</p>"
        )
        with st.container(height=392, border=False):
            key = f"rupturas_{versao}"
            visuais.grafico_rupturas(recorte.rupturas, selecao, key, partial(ao_clicar_grafico, "produto", key))
    with st.container(key="cartao_fila"):
        st.html(
            '<p class="titulo">Fila de orçamentos</p>'
            '<p class="sub">Atendível, depois Ruptura, depois Bloqueado, do maior para o menor valor</p>'
        )
        key = f"fila_{versao}"
        codigos = recorte.fila.cod_pedido.tolist()
        visuais.tabela_fila(recorte.fila, selecao, key, partial(ao_clicar_fila, codigos, key))
