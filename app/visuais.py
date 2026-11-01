"""Tema, formatação e dados de exibição. Nenhuma regra de negócio é calculada aqui."""
from base64 import b64encode
from decimal import ROUND_HALF_UP, Decimal
from html import escape

import streamlit as st

from app import componentes

COR_CLASSE = {"Atendível": "#34d399", "Ruptura": "#fbbf24", "Bloqueado": "#fb7185"}
ICONE = {"Atendível": "✓", "Ruptura": "▲", "Bloqueado": "✕"}
COR_FAIXA = {"1–15": "#60a5fa", "16–30": "#fbbf24", "31–60": "#fb7185", "Mais de 60": "#e11d48"}
COR_NIVEL = {"Bom": "#3b9dff", "Atenção": "#fbbf24", "Crítico": "#fb7185"}

CSS = """
<style>
.stApp {
  background:
    radial-gradient(900px 500px at 0% 0%, #0d4a70 0, transparent 70%),
    radial-gradient(900px 600px at 100% 100%, #2c1430 0, transparent 70%),
    #02040c;
}
header[data-testid="stHeader"] { display: none; }
.block-container { padding: 1.2rem 1.6rem 1.4rem; max-width: 1480px; }
[class*="st-key-cartao"] {
  background: rgba(12, 22, 48, .86); border: 1px solid rgba(255,255,255,.07);
  border-radius: 22px; padding: 15px 18px; gap: 8px; backdrop-filter: blur(8px);
}
.st-key-limpar button {
  border-radius: 999px; border: 2px solid #dfe8f5; background: rgba(8,20,45,.7); color: #fff; min-height: 44px;
}
.st-key-limpar button:disabled { border-color: rgba(223,232,245,.28); color: rgba(223,232,245,.45); background: transparent; }
.marca-titulo { color: #fff; font-size: 30px; font-weight: 400; line-height: 1.1; }
.marca-titulo small { display: block; color: #9fb3d1; font-size: 14px; margin-top: 3px; }
.chip {
  border-radius: 999px; background: rgba(37,99,235,.35); border: 2px solid #60a5fa; color: #fff;
  padding: 9px 14px; font-size: 14px; font-weight: 600; text-align: center;
}
.painel {
  background: linear-gradient(165deg, #2f6cab 0%, #24437c 50%, #5a2b3d 100%);
  border-radius: 26px; color: #fff; padding: 24px 22px; min-height: 1012px; display: flex;
  flex-direction: column; gap: 10px; box-sizing: border-box; box-shadow: 0 18px 50px rgba(0,0,0,.45);
}
.painel h2 { font-size: 24px; font-weight: 400; margin: 0; padding: 0; color: #fff; }
.painel .sub { color: #c4d4ea; font-size: 14px; margin: 0; }
.painel .caixa {
  border: 2px solid rgba(255,255,255,.5); border-radius: 26px; padding: 12px 18px; margin: 10px 0 8px; text-align: center;
}
.painel .caixa b { display: block; font-size: 36px; font-weight: 600; line-height: 1.15; }
.painel .caixa span { color: #d7e3f4; font-size: 14px; }
.painel .classe { display: flex; align-items: center; gap: 16px; padding: 10px 2px; }
.painel .classe strong { display: block; font-size: 17px; font-weight: 600; }
.painel .classe span { display: block; color: #d7e3f4; font-size: 14px; }
.painel .aviso {
  margin-top: auto; background: rgba(0,0,0,.32); border-radius: 16px; padding: 12px 14px; font-size: 13px; color: #d7e3f4;
}
.painel .aviso b { display: block; color: #fcd34d; font-size: 14px; font-weight: 600; }
.numeros { display: grid; grid-template-columns: repeat(3, 1fr); text-align: center; padding: 10px 0 6px; }
.numeros b { display: block; font-size: 31px; font-weight: 600; color: #fff; line-height: 1.15; }
.numeros b.critico { color: #fda4af; }
.numeros b.atencao { color: #fcd34d; }
.numeros span { color: #a9bbd4; font-size: 14px; }
.titulo { font-size: 20px; font-weight: 400; color: #fff; margin: 0; }
.sub { font-size: 13px; color: #9fb3d1; margin: 0; }
.cabeca { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
.resumo { display: flex; gap: 26px; text-align: center; }
.resumo small { display: block; color: #b9c7dc; font-size: 12px; }
.resumo b { font-size: 19px; font-weight: 600; }
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


def aplicar_tema():
    st.html(CSS)


def cabecalho(rotulo_selecao, ao_limpar):
    titulo, chip, botao = st.columns([6.6, 3.6, 1.7], vertical_alignment="center")
    titulo.html(
        '<div class="marca-titulo">Priorização de Orçamentos'
        "<small>O que atender, resolver ou segurar · Referência: 28/08/2026</small></div>"
    )
    if rotulo_selecao:
        chip.html(f'<div class="chip">{escape(rotulo_selecao)}</div>')
    botao.button("Limpar seleções", on_click=ao_limpar, width="stretch", disabled=not rotulo_selecao, key="limpar")


def _anel(fracao, cor):
    raio, largura = 40, 13
    circunferencia = 2 * 3.14159265 * raio
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="104" height="104" viewBox="0 0 104 104">'
        f'<circle cx="52" cy="52" r="{raio}" fill="none" stroke="#3f5f99" stroke-width="{largura}"/>'
        f'<circle cx="52" cy="52" r="{raio}" fill="none" stroke="{cor}" stroke-width="{largura}" stroke-linecap="round" '
        f'stroke-dasharray="{fracao * circunferencia} {circunferencia}" transform="rotate(-90 52 52)"/>'
        f'<text x="52" y="58" text-anchor="middle" fill="#ffffff" font-size="17" font-family="sans-serif" '
        f'font-weight="600">{round(fracao * 100)}%</text></svg>'
    )
    # st.html remove SVG direto, então o anel entra como imagem.
    imagem = b64encode(svg.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{imagem}" width="104" alt="{round(fracao * 100)}%">'


def painel(kpis, creditos, nao_cotaveis):
    total = kpis["valor"]
    classes = ""
    for nome, (quantidade, valor) in kpis["classes"].items():
        fracao = float(valor / total) if total else 0
        classes += (
            f'<div class="classe">{_anel(fracao, COR_CLASSE[nome])}<div><strong>{ICONE[nome]} {nome}</strong>'
            f"<span>{plural(quantidade, 'orçamento')}</span><span>{brl_compacto(valor)}</span></div></div>"
        )
    soma = sum(creditos.valor, Decimal(0))
    mensagens = plural(len(nao_cotaveis), "mensagem não cotável", "mensagens não cotáveis")
    st.html(
        '<div class="painel"><h2>Fila de decisão</h2><p class="sub">Valor em orçamentos abertos</p>'
        f'<div class="caixa"><b>{brl_compacto(total)}</b><span>{plural(kpis["orcamentos"], "orçamento")}</span></div>'
        f'{classes}<div class="aviso"><b>⚠ {plural(len(creditos), "crédito")} sem NF: {brl(soma)}</b>'
        f"Não abatem saldos. {mensagens}.</div></div>"
    )


def indicadores(kpis):
    vencido = "critico" if kpis["vencido"] else ""
    bloqueados = "critico" if kpis["clientes_bloqueados"] else ""
    em_ruptura = "atencao" if kpis["produtos_ruptura"] else ""
    st.html(
        '<div class="numeros">'
        f'<div><b class="{vencido}">{brl_compacto(kpis["vencido"])}</b>'
        f'<span>Vencido, {plural(kpis["titulos_vencidos"], "título")}</span></div>'
        f'<div><b class="{bloqueados}">{inteiro(kpis["clientes_bloqueados"])}</b><span>Clientes bloqueados</span></div>'
        f'<div><b class="{em_ruptura}">{inteiro(kpis["produtos_ruptura"])}</b><span>Produtos em ruptura</span></div>'
        "</div>"
    )


def cabeca_fila(kpis):
    resumo = "".join(
        f'<div><small>{nome}</small><b style="color:{COR_CLASSE[nome]}">{inteiro(quantidade)}</b></div>'
        for nome, (quantidade, _) in kpis["classes"].items()
    )
    st.html(
        '<div class="cabeca"><div><p class="titulo">Fila de orçamentos</p>'
        '<p class="sub">Clique em uma linha para filtrar o restante</p></div>'
        f'<div class="resumo">{resumo}</div></div>'
    )


def dados_fila(tabela, selecao):
    maior = max((float(v) for v in tabela.valor), default=1) or 1
    grupos = []
    for classe in COR_CLASSE:
        parte = tabela[tabela.classe == classe]
        if parte.empty:
            continue
        linhas = [
            {
                "cod": linha.cod_pedido,
                "cliente": linha.cliente,
                "valor": brl(linha.valor),
                "peso": round(float(linha.valor) / maior * 100, 1),
                "topo": float(linha.valor) == maior,
                "cobertura": int(linha.cobertura_pct),
                "nivel_cobertura": linha.nivel_cobertura,
                "atraso": int(linha.maior_atraso),
                "nivel_atraso": linha.nivel_atraso,
                "motivo": linha.motivo,
            }
            for linha in parte.itertuples()
        ]
        grupos.append(
            {
                "nome": f"{ICONE[classe]} {classe}",
                "valor": brl(sum(parte.valor, Decimal(0))),
                "quantidade": plural(len(parte), "orçamento"),
                "linhas": linhas,
            }
        )
    return {"grupos": grupos, "selecionado": selecao.orcamento}


def dados_vencidos(tabela, selecao):
    totais = tabela.groupby("faixa_atraso").saldo.sum()
    ativas = set(totais.index)
    if selecao.faixa:
        ativas = {selecao.faixa}
    elif selecao.cliente:
        ativas = set(tabela.loc[tabela.cod_cliente == selecao.cliente, "faixa_atraso"])
    faixas = [
        {"nome": f, "valor": brl_compacto(totais[f]), "peso": float(totais[f]), "cor": cor, "ativa": f in ativas}
        for f, cor in COR_FAIXA.items()
        if f in totais.index
    ]
    na_faixa = set(tabela.loc[tabela.faixa_atraso == selecao.faixa, "cod_cliente"])
    somas = tabela.groupby(["cod_cliente", "cliente"]).saldo.sum().sort_values(ascending=False)
    maior = float(somas.max()) if len(somas) else 1
    clientes = []
    for posicao, ((cod, nome), soma) in enumerate(somas.items(), start=1):
        titulos = tabela[tabela.cod_cliente == cod]
        partes = [
            {"peso": round(float(titulos.loc[titulos.faixa_atraso == f, "saldo"].sum()) / maior * 100, 1), "cor": cor}
            for f, cor in COR_FAIXA.items()
            if f in set(titulos.faixa_atraso)
        ]
        clientes.append(
            {
                "cod": cod, "nome": nome, "posicao": posicao, "total": brl(soma)[3:], "partes": partes,
                "selecionado": cod == selecao.cliente,
                "ativo": (selecao.cliente is None or cod == selecao.cliente)
                and (selecao.faixa is None or cod in na_faixa),
            }
        )
    return {"faixas": faixas, "clientes": clientes}


def dados_rupturas(tabela, selecao):
    tabela = tabela.assign(coberto=[float(e) / float(d) * 100 for e, d in zip(tabela.estoque, tabela.demanda)])
    tabela = tabela.sort_values(["coberto", "falta"], ascending=[True, False])
    produtos = []
    for linha in tabela.itertuples():
        nivel = "Atenção" if linha.coberto >= 50 else "Crítico"
        produtos.append(
            {
                "cod": linha.cod_produto, "nome": linha.descricao, "coberto": round(linha.coberto, 1),
                "cor": COR_NIVEL[nivel],
                "detalhe": f"Faltam {inteiro(linha.falta)} · {plural(linha.prazo_reposicao_dias, 'dia')}",
                "selecionado": linha.cod_produto == selecao.produto,
                "ativo": selecao.produto is None or linha.cod_produto == selecao.produto,
            }
        )
    return {"produtos": produtos}


def fila(dados, key, ao_clicar):
    componentes.fila(data=dados, key=key, on_linha_change=ao_clicar)


def vencidos(dados, key, ao_faixa, ao_cliente):
    componentes.vencidos(data=dados, key=key, on_faixa_change=ao_faixa, on_cliente_change=ao_cliente)


def rupturas(dados, key, ao_clicar):
    componentes.rupturas(data=dados, key=key, on_produto_change=ao_clicar)
