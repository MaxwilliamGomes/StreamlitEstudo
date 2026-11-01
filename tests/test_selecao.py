"""Matriz de cross filter da spec, testada sem navegador."""
from decimal import Decimal as D

import pytest

from app.dados import ler_dados
from app.selecao import Selecao, alternar, aplicar_selecao


@pytest.fixture(scope="module")
def dados():
    return ler_dados()


def codigos(recorte):
    return set(recorte.fila.cod_pedido)


def test_sem_selecao_mantem_os_totais(dados):
    k = aplicar_selecao(dados, Selecao()).kpis
    assert (k["orcamentos"], k["valor"]) == (114, D("345563.89"))
    assert k["classes"]["Atendível"] == (13, D("20399.52"))
    assert k["classes"]["Ruptura"] == (67, D("199191.07"))
    assert k["classes"]["Bloqueado"] == (34, D("125973.30"))
    assert (k["titulos_vencidos"], k["vencido"]) == (16, D("27549.39"))
    assert (k["clientes_bloqueados"], k["produtos_ruptura"]) == (8, 21)


def test_ca8_cliente_filtra_fila_e_kpis(dados):
    r = aplicar_selecao(dados, Selecao(cliente="C010"))
    assert codigos(r) == {"PED008", "PED020"}
    assert (r.kpis["orcamentos"], r.kpis["valor"]) == (2, D("1135.00"))
    assert r.kpis["classes"]["Bloqueado"] == (2, D("1135.00"))
    assert r.kpis["classes"]["Atendível"] == (0, D("0"))
    assert (r.kpis["titulos_vencidos"], r.kpis["vencido"]) == (1, D("2100.00"))
    assert (r.kpis["clientes_bloqueados"], r.kpis["produtos_ruptura"]) == (1, 3)


def test_cliente_filtra_rupturas_e_origem_mantem_todos(dados):
    r = aplicar_selecao(dados, Selecao(cliente="C010"))
    assert set(r.rupturas.cod_produto) == {"P001", "P003", "P004"}
    assert len(r.vencidos) == 16


def test_faixa_filtra_clientes_da_faixa(dados):
    r = aplicar_selecao(dados, Selecao(faixa="31–60"))
    clientes = set(dados.vencidos[dados.vencidos.faixa_atraso == "31–60"].cod_cliente)
    assert set(r.fila.cod_cliente) <= clientes
    assert (r.kpis["titulos_vencidos"], r.kpis["vencido"]) == (5, D("6641.25"))
    assert len(r.vencidos) == 16


def test_produto_filtra_fila_e_vencidos(dados):
    r = aplicar_selecao(dados, Selecao(produto="P005"))
    assert codigos(r) == {"PED009"}
    assert len(r.rupturas) == 21
    assert set(r.vencidos.cod_cliente) <= {"C005"}


def test_linha_filtra_cliente_e_produtos_do_orcamento(dados):
    r = aplicar_selecao(dados, Selecao(orcamento="PED008"))
    assert len(r.fila) == 114
    assert set(r.vencidos.cod_cliente) == {"C010"}
    assert set(r.rupturas.cod_produto) == {"P003", "P004"}
    assert (r.kpis["orcamentos"], r.kpis["valor"]) == (1, D("285.00"))


def test_selecoes_se_combinam(dados):
    r = aplicar_selecao(dados, Selecao(cliente="C010", produto="P001"))
    assert codigos(r) == {"PED020"}


def test_combinacao_sem_resultado_fica_vazia(dados):
    r = aplicar_selecao(dados, Selecao(cliente="C010", produto="P005"))
    assert r.fila.empty
    assert r.kpis["orcamentos"] == 0
    assert r.kpis["valor"] == 0


def test_alternar_seleciona_e_remove():
    selecao = alternar(Selecao(), "cliente", "C010")
    assert selecao.cliente == "C010"
    assert alternar(selecao, "cliente", "C010").cliente is None
    assert alternar(selecao, "cliente", "C001").cliente == "C001"


def test_ca9_limpar_devolve_os_totais(dados):
    selecionado = aplicar_selecao(dados, Selecao(cliente="C010", produto="P001"))
    assert selecionado.kpis != aplicar_selecao(dados, Selecao()).kpis
    assert aplicar_selecao(dados, Selecao()).kpis["valor"] == D("345563.89")
