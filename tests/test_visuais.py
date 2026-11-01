from decimal import Decimal as D

from app.visuais import brl, brl_compacto, inteiro, plural


def test_moeda_em_portugues():
    assert brl(D("345563.89")) == "R$ 345.563,89"
    assert brl(D("0")) == "R$ 0,00"


def test_valor_compacto_a_partir_de_dez_mil():
    assert brl_compacto(D("345563.89")) == "R$ 345,6 mil"
    assert brl_compacto(D("1135.00")) == "R$ 1.135,00"


def test_plural():
    assert plural(1, "título") == "1 título"
    assert plural(1200, "título") == "1.200 títulos"
    assert inteiro(830) == "830"
