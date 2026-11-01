"""Tema, formatação e visuais da página. Nenhuma regra de negócio é calculada aqui."""
from base64 import b64encode
from decimal import ROUND_HALF_UP, Decimal
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LARANJA = "#f07a2c"
CINZA = "#8c8c8c"
CLARO = "#c9c9c9"
TEXTO = "#f4f4f4"
TEXTO_2 = "#c9c9c9"
COR_CLASSE = {"Atendível": TEXTO, "Ruptura": LARANJA, "Bloqueado": "#7c7c7c"}
ICONE = {"Atendível": "✓", "Ruptura": "▲", "Bloqueado": "✕"}
FRASE_CLASSE = {
    "Atendível": "do valor pronto para atender",
    "Ruptura": "do valor travado por estoque",
    "Bloqueado": "do valor bloqueado por crédito",
}
COR_FAIXA = {"1–15": CINZA, "16–30": CLARO, "31–60": LARANJA, "Mais de 60": "#d9482b"}

CSS = """
<style>
.stApp { background: linear-gradient(135deg, #111111, #242424); }
header[data-testid="stHeader"] { display: none; }
.block-container { padding: 1rem 1.25rem 1.25rem; max-width: 1440px; }
[class*="st-key-cartao"] {
  background: #2b2b2b; border-radius: 14px; padding: 13px 16px; gap: 6px;
}
.cartao { background: #2b2b2b; border-radius: 14px; padding: 11px 16px; color: #f4f4f4; }
.cartao h1 { font-size: 24px; font-weight: 600; margin: 0; padding: 0; color: #f4f4f4; }
.cartao h1 span { font-weight: 400; color: #c9c9c9; }
.cartao p, .sub { font-size: 13px; color: #a0a0a0; margin: 0; }
.titulo { font-size: 17px; font-weight: 600; color: #f4f4f4; margin: 0; }
.chip {
  background: #f07a2c; color: #111111; border-radius: 14px; padding: 18px 12px;
  font-size: 14px; font-weight: 600; text-align: center;
}
.painel {
  background: linear-gradient(180deg, #3c3c3c, #1b1b1b); border-radius: 14px; color: #f4f4f4;
  padding: 22px 16px 20px; text-align: center; min-height: 978px; display: flex;
  flex-direction: column; align-items: center; gap: 8px; box-sizing: border-box;
}
.painel .rotulo { font-size: 15px; font-weight: 500; color: #c9c9c9; }
.painel .total { font-size: 42px; font-weight: 600; line-height: 1.1; }
.painel .frase { font-size: 14px; color: #c9c9c9; }
.painel .classes { display: flex; width: 100%; margin-top: auto; }
.painel .classe { flex: 1; font-size: 13px; color: #c9c9c9; }
.painel .classe b { display: block; font-size: 30px; font-weight: 600; color: #f07a2c; line-height: 1.25; }
.indicadores { display: grid; grid-template-columns: repeat(3, 1fr) 1.5fr; gap: 10px; }
.indicador b { display: block; font-size: 22px; font-weight: 600; }
.indicador span { display: block; font-size: 13px; font-weight: 500; color: #c9c9c9; }
.alerta { border: 1px solid #f07a2c; }
.alerta b { display: block; font-size: 14px; font-weight: 600; color: #f07a2c; }
.alerta span { font-size: 13px; color: #c9c9c9; }
</style>
"""


def brl(valor):
    valor = Decimal(valor).quantize(Decimal("0.01"), ROUND_HALF_UP)
    texto = f"{valor:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"R$ {texto}"


def brl_compacto(valor):
    valor = Decimal(valor)
    if abs(valor) < 10000:
        return brl(valor)
    mil = (valor / 1000).quantize(Decimal("0.1"), ROUND_HALF_UP)
    return f"R$ {str(mil).replace('.', ',')} mil"


def inteiro(valor):
    return f"{int(valor):,}".replace(",", ".")


def plural(quantidade, singular, varios=None):
    return f"{inteiro(quantidade)} {singular if quantidade == 1 else varios or singular + 's'}"


def tom(cor, ativo=True):
    if ativo:
        return cor
    r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},0.3)"


def aplicar_tema():
    st.html(CSS)


def cabecalho(rotulo_selecao, ao_limpar):
    titulo, data, chip, botao = st.columns([5.6, 2, 2.2, 1.5], vertical_alignment="center")
    titulo.html(
        '<div class="cartao"><h1>Priorização <span>de Orçamentos</span></h1>'
        "<p>O que atender, resolver ou segurar</p></div>"
    )
    data.html('<div class="cartao"><h1>28/08/2026</h1><p>Data de referência</p></div>')
    if rotulo_selecao:
        chip.html(f'<div class="chip">{escape(rotulo_selecao)}</div>')
    botao.button("Limpar seleções", on_click=ao_limpar, width="stretch", disabled=not rotulo_selecao)


def _anel(classes, total):
    tamanho, raio, largura = 230, 90, 30
    circunferencia = 2 * 3.14159265 * raio
    fatia_vazia = (
        f'<circle cx="115" cy="115" r="{raio}" fill="none" stroke="#3a3a3a" stroke-width="{largura}"/>'
    )
    arcos, acumulado = [fatia_vazia], 0.0
    for classe, (_, valor) in classes.items():
        fracao = float(valor / total) if total else 0
        if fracao:
            arcos.append(
                f'<circle cx="115" cy="115" r="{raio}" fill="none" stroke="{COR_CLASSE[classe]}" '
                f'stroke-width="{largura}" stroke-dasharray="{fracao * circunferencia} {circunferencia}" '
                f'stroke-dashoffset="{-acumulado * circunferencia}" transform="rotate(-90 115 115)"/>'
            )
        acumulado += fracao
    if not total:
        destaque, frase = "–", "sem orçamentos nesta seleção"
    else:
        maior = max(classes, key=lambda c: classes[c][1])
        destaque = f"{round(float(classes[maior][1] / total) * 100)}%"
        frase = FRASE_CLASSE[maior]
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 230 230">'
        f'{"".join(arcos)}'
        f'<text x="115" y="130" text-anchor="middle" fill="#f4f4f4" font-size="46" '
        f'font-family="sans-serif" font-weight="500">{destaque}</text></svg>'
    )
    # st.html remove SVG direto, então o anel entra como imagem.
    imagem = b64encode(svg.encode("utf-8")).decode("ascii")
    alt = escape(f"{destaque} {frase}")
    return f'<img src="data:image/svg+xml;base64,{imagem}" width="{tamanho}" alt="{alt}">', frase


def painel(kpis):
    svg, frase = _anel(kpis["classes"], kpis["valor"])
    classes = "".join(
        f'<div class="classe">{ICONE[nome]} {nome}<b>{inteiro(quantidade)}</b>{brl_compacto(valor)}</div>'
        for nome, (quantidade, valor) in kpis["classes"].items()
    )
    st.html(
        f'<div class="painel"><div class="rotulo">Valor na fila</div>'
        f'<div class="total">{brl_compacto(kpis["valor"])}</div>'
        f'<div class="frase">{plural(kpis["orcamentos"], "orçamento")}</div>'
        f'{svg}<div class="frase">{frase}</div><div class="classes">{classes}</div></div>'
    )


def indicadores(kpis, creditos, nao_cotaveis):
    itens = [
        (brl_compacto(kpis["vencido"]), "Vencido", plural(kpis["titulos_vencidos"], "título")),
        (inteiro(kpis["clientes_bloqueados"]), "Clientes bloqueados", "Mais de 15 dias de atraso"),
        (inteiro(kpis["produtos_ruptura"]), "Produtos em ruptura", "Nos orçamentos da fila"),
    ]
    blocos = "".join(
        f'<div class="cartao indicador"><b>{v}</b><span>{r}</span><p>{d}</p></div>' for v, r, d in itens
    )
    valor = sum(creditos.valor, Decimal(0))
    alerta = (
        f'<div class="cartao alerta"><b>⚠ {plural(len(creditos), "crédito")} sem NF: {brl(valor)}</b>'
        f"<span>Não abatem saldos. {plural(len(nao_cotaveis), 'mensagem não cotável', 'mensagens não cotáveis')}.</span></div>"
    )
    st.html(f'<div class="indicadores">{blocos}{alerta}</div>')


def _base(altura, margem=None):
    return dict(
        height=altura,
        margin=margem or dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans, sans-serif", color=TEXTO, size=13),
        showlegend=False,
        clickmode="event+select",
        dragmode=False,
        bargap=0.55,
        barcornerradius=3,
        hoverlabel=dict(bgcolor="#111111", font_color=TEXTO),
    )


def _desenhar(figura, key, ao_selecionar):
    figura.update_traces(selected_marker_opacity=1, unselected_marker_opacity=1)
    st.plotly_chart(
        figura, key=key, on_select=ao_selecionar, selection_mode="points",
        config={"displayModeBar": False}, width="stretch",
    )


def grafico_faixas(vencidos, selecao, key, ao_selecionar):
    totais = vencidos.groupby("faixa_atraso").saldo.sum()
    ativas = set(totais.index)
    if selecao.faixa:
        ativas = {selecao.faixa}
    elif selecao.cliente:
        ativas = set(vencidos.loc[vencidos.cod_cliente == selecao.cliente, "faixa_atraso"])
    figura = go.Figure()
    acumulado = 0.0
    for faixa, cor in COR_FAIXA.items():
        if faixa not in totais.index:
            continue
        valor = float(totais[faixa])
        figura.add_bar(
            x=[valor], y=["Faixas"], orientation="h", customdata=[faixa],
            marker_color=tom(cor, faixa in ativas), marker_line_width=0,
            hovertemplate=f"{faixa} dias<br>{brl(totais[faixa])}<extra></extra>",
        )
        figura.add_annotation(
            x=acumulado, y=0, yref="paper", yshift=-4, xanchor="left", yanchor="top", align="left",
            showarrow=False, text=f"{faixa} dias<br><b>{brl_compacto(totais[faixa])}</b>",
            font=dict(size=12, color=TEXTO if faixa in ativas else "#7c7c7c"),
        )
        acumulado += valor
    figura.update_layout(**_base(66, dict(l=0, r=0, t=0, b=42)), barmode="stack")
    figura.update_layout(bargap=0.2)
    figura.update_xaxes(visible=False, range=[0, acumulado])
    figura.update_yaxes(visible=False)
    _desenhar(figura, key, ao_selecionar)


def grafico_clientes(vencidos, selecao, key, ao_selecionar):
    if vencidos.empty:
        st.caption("Nenhum título vencido nesta seleção.")
        return
    tabela = (
        vencidos.assign(saldo=vencidos.saldo.astype(float))
        .pivot_table(index=["cod_cliente", "cliente"], columns="faixa_atraso", values="saldo", aggfunc="sum")
        .fillna(0)
    )
    tabela["total"] = tabela.sum(axis=1)
    tabela = tabela.sort_values("total", ascending=False).reset_index()
    rotulos = [f"{i + 1}  {nome}" for i, nome in enumerate(tabela.cliente)]
    na_faixa = set(vencidos.loc[vencidos.faixa_atraso == selecao.faixa, "cod_cliente"])
    ativos = [
        (selecao.cliente is None or c == selecao.cliente) and (selecao.faixa is None or c in na_faixa)
        for c in tabela.cod_cliente
    ]
    figura = go.Figure()
    for faixa, cor in COR_FAIXA.items():
        if faixa not in tabela:
            continue
        figura.add_bar(
            x=tabela[faixa], y=rotulos, orientation="h", customdata=tabela.cod_cliente,
            marker_color=[tom(cor, ativo) for ativo in ativos], marker_line_width=0,
            hovertemplate=f"%{{y}}<br>{faixa} dias: R$ %{{x:,.2f}}<extra></extra>",
        )
    for rotulo, total, ativo in zip(rotulos, tabela.total, ativos):
        figura.add_annotation(
            x=total, y=rotulo, xanchor="left", xshift=6, showarrow=False, text=brl(total)[3:],
            font=dict(size=13, color=TEXTO_2 if ativo else "#6a6a6a"),
        )
    figura.update_layout(**_base(25 * len(tabela) + 10), barmode="stack")
    figura.update_xaxes(visible=False, range=[0, float(tabela.total.max()) * 1.32])
    figura.update_yaxes(autorange="reversed", automargin=True, showgrid=False, showline=False, ticks="", title=None)
    _desenhar(figura, key, ao_selecionar)


def grafico_rupturas(rupturas, selecao, key, ao_selecionar):
    if rupturas.empty:
        st.caption("Nenhum produto em ruptura nesta seleção.")
        return
    tabela = rupturas.assign(
        estoque=rupturas.estoque.astype(float),
        demanda=rupturas.demanda.astype(float),
        falta=rupturas.falta.astype(float),
    )
    tabela["coberto"] = tabela.estoque / tabela.demanda * 100
    tabela = tabela.sort_values(["coberto", "falta"], ascending=[True, False])
    ativos = [selecao.produto is None or p == selecao.produto for p in tabela.cod_produto]
    figura = go.Figure()
    for coluna, cor in (("coberto", CINZA), ("restante", LARANJA)):
        valores = tabela.coberto if coluna == "coberto" else 100 - tabela.coberto
        figura.add_bar(
            x=valores, y=tabela.cod_produto, orientation="h", customdata=tabela.cod_produto,
            marker_color=[tom(cor, ativo) for ativo in ativos], marker_line_width=0,
            hovertext=tabela.descricao, hovertemplate="%{hovertext}<extra></extra>",
        )
    for linha, ativo in zip(tabela.itertuples(), ativos):
        cor = TEXTO if ativo else "#6a6a6a"
        comum = dict(y=linha.cod_produto, yshift=16, showarrow=False, font=dict(size=13, color=cor))
        figura.add_annotation(x=0, xanchor="left", text=escape(linha.descricao), **comum)
        figura.add_annotation(
            x=100, xanchor="right",
            text=f"Faltam {inteiro(linha.falta)} · {plural(linha.prazo_reposicao_dias, 'dia')}", **comum,
        )
    figura.update_layout(**_base(46 * len(tabela) + 12, dict(l=0, r=0, t=14, b=0)), barmode="stack")
    figura.update_layout(bargap=0.8)
    figura.update_xaxes(visible=False, range=[0, 100])
    figura.update_yaxes(visible=False, autorange="reversed", type="category")
    _desenhar(figura, key, ao_selecionar)


def tabela_fila(fila, selecao, key, ao_selecionar):
    if fila.empty:
        st.caption("Nenhum orçamento nesta seleção.")
        return []
    exibicao = pd.DataFrame(
        {
            " ": ["●" if c == selecao.orcamento else "" for c in fila.cod_pedido],
            "Orçamento": fila.cod_pedido.values,
            "Cliente": fila.cliente.values,
            "Classe": [f"{ICONE[c]} {c}" for c in fila.classe],
            "Valor": [brl(v) for v in fila.valor],
            "Peso": fila.valor.astype(float).values,
            "Motivo": fila.motivo.values,
        }
    )
    st.dataframe(
        exibicao, key=key, on_select=ao_selecionar, selection_mode="single-row",
        hide_index=True, height=292, width="stretch",
        column_config={
            " ": st.column_config.TextColumn(width=30),
            "Orçamento": st.column_config.TextColumn(width=90),
            "Cliente": st.column_config.TextColumn(width=200),
            "Classe": st.column_config.TextColumn(width=110),
            "Valor": st.column_config.TextColumn(width=110),
            "Peso": st.column_config.ProgressColumn(
                width=90, format=" ", min_value=0, max_value=float(exibicao.Peso.max()),
            ),
        },
    )
    return fila.cod_pedido.tolist()
