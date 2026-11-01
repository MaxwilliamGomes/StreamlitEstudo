"""Critérios de aceite das regras, verificados nas views do banco."""
from decimal import Decimal as D


def um(banco, sql):
    return banco.execute(sql).fetchone()


# T06: financeiro


def test_ca4_titulos_com_saldo(banco):
    assert um(banco, "SELECT count(*), sum(saldo) FROM vw_titulo_saldo WHERE saldo > 0") == (67, D("178288.54"))
    assert um(banco, "SELECT count(*), sum(saldo) FROM vw_titulo_saldo WHERE vencido") == (16, D("27549.39"))


def test_ca5_vencido_por_faixa(banco):
    linhas = banco.execute(
        "SELECT faixa_atraso, count(*), sum(saldo) FROM vw_titulo_saldo WHERE vencido GROUP BY 1"
    ).fetchall()
    assert {f: (n, v) for f, n, v in linhas} == {
        "1–15": (6, D("12084.24")),
        "16–30": (5, D("8823.90")),
        "31–60": (5, D("6641.25")),
    }


def test_ca6_clientes_bloqueados(banco):
    assert um(banco, "SELECT count(*) FROM vw_cliente_bloqueado") == (8,)


def test_ca7_quinze_dias_exatos_nao_bloqueia(banco):
    assert um(banco, "SELECT dias_atraso FROM vw_titulo_saldo WHERE cod_titulo = 'T0012'") == (15,)
    assert um(banco, "SELECT count(*) FROM vw_cliente_bloqueado WHERE cod_cliente = 'C003'") == (0,)


def test_rn3_saldo_nao_fica_negativo(banco):
    # T0009 foi pago em dobro e não pode gerar saldo negativo.
    assert um(banco, "SELECT saldo FROM vw_titulo_saldo WHERE cod_titulo = 'T0009'") == (D("0.00"),)


def test_rn3_credito_sem_nf_nao_abate(banco):
    # L013 (R$ 3.050) não informa NF, então T0011 segue integralmente em aberto.
    assert um(banco, "SELECT saldo FROM vw_titulo_saldo WHERE cod_titulo = 'T0011'") == (D("1200.00"),)


def test_ca10_creditos_sem_nf(banco):
    assert um(banco, "SELECT count(*), sum(valor) FROM vw_credito_sem_nf") == (6, D("12978.95"))
