"""Estado e aplicação do cross filter. Sem Streamlit, para poder ser testado."""
from dataclasses import dataclass, replace
from decimal import Decimal

import pandas as pd

from app.dados import Dados

CLASSES = ("Atendível", "Ruptura", "Bloqueado")


@dataclass(frozen=True)
class Selecao:
    cliente: str | None = None
    faixa: str | None = None
    produto: str | None = None
    orcamento: str | None = None


@dataclass(frozen=True)
class Recorte:
    fila: pd.DataFrame
    vencidos: pd.DataFrame
    rupturas: pd.DataFrame
    kpis: dict


def alternar(selecao, campo, valor):
    """Selecionar de novo o mesmo item remove a seleção."""
    atual = getattr(selecao, campo)
    return replace(selecao, **{campo: None if valor == atual else valor})


def _soma(serie):
    return sum(serie, Decimal(0))


def _clientes_da_faixa(dados, faixa):
    return set(dados.vencidos.loc[dados.vencidos.faixa_atraso == faixa, "cod_cliente"])


def _orcamentos(dados, selecao, ignorar=()):
    """Orçamentos que atendem à seleção. Cada visual ignora o próprio filtro."""
    fila = dados.orcamentos
    if selecao.cliente and "cliente" not in ignorar:
        fila = fila[fila.cod_cliente == selecao.cliente]
    if selecao.faixa and "faixa" not in ignorar:
        fila = fila[fila.cod_cliente.isin(_clientes_da_faixa(dados, selecao.faixa))]
    if selecao.produto and "produto" not in ignorar:
        com_produto = dados.itens.loc[dados.itens.cod_produto == selecao.produto, "cod_pedido"]
        fila = fila[fila.cod_pedido.isin(com_produto)]
    if selecao.orcamento and "orcamento" not in ignorar:
        fila = fila[fila.cod_pedido == selecao.orcamento]
    return fila


def _vencidos(dados, selecao, ignorar=()):
    """Produto e orçamento chegam aos títulos pelo cliente, conforme a spec."""
    vencidos = dados.vencidos
    if selecao.cliente and "cliente" not in ignorar:
        vencidos = vencidos[vencidos.cod_cliente == selecao.cliente]
    if selecao.faixa and "faixa" not in ignorar:
        vencidos = vencidos[vencidos.faixa_atraso == selecao.faixa]
    if selecao.produto or selecao.orcamento:
        clientes = _orcamentos(dados, selecao, ignorar=("cliente", "faixa")).cod_cliente
        vencidos = vencidos[vencidos.cod_cliente.isin(clientes)]
    return vencidos


def _rupturas(dados, orcamentos):
    produtos = dados.itens.loc[dados.itens.cod_pedido.isin(orcamentos.cod_pedido), "cod_produto"]
    return dados.rupturas[dados.rupturas.cod_produto.isin(produtos)]


def _kpis(dados, selecao):
    fila = _orcamentos(dados, selecao)
    vencidos = _vencidos(dados, selecao)
    bloqueados = set(dados.bloqueados.cod_cliente) & set(vencidos.cod_cliente)
    classes = {}
    for classe in CLASSES:
        grupo = fila[fila.classe == classe]
        classes[classe] = (len(grupo), _soma(grupo.valor))
    return {
        "orcamentos": len(fila),
        "valor": _soma(fila.valor),
        "classes": classes,
        "titulos_vencidos": len(vencidos),
        "vencido": _soma(vencidos.saldo),
        "clientes_bloqueados": len(bloqueados),
        "produtos_ruptura": len(_rupturas(dados, fila)),
    }


def aplicar_selecao(dados: Dados, selecao: Selecao) -> Recorte:
    """O visual de origem mantém os itens; os demais são filtrados pela seleção."""
    return Recorte(
        fila=_orcamentos(dados, selecao, ignorar=("orcamento",)),
        vencidos=_vencidos(dados, selecao, ignorar=("cliente", "faixa")),
        rupturas=_rupturas(dados, _orcamentos(dados, selecao, ignorar=("produto",))),
        kpis=_kpis(dados, selecao),
    )
