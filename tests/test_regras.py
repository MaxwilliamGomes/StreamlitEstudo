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


# T07: fila e classificação


def test_ca1_fila(banco):
    assert um(banco, "SELECT count(*), sum(valor) FROM vw_orcamento_classificado") == (114, D("345563.89"))


def test_ca2_classificacao(banco):
    linhas = banco.execute(
        "SELECT classe, count(*), sum(valor) FROM vw_orcamento_classificado GROUP BY 1"
    ).fetchall()
    assert {c: (n, v) for c, n, v in linhas} == {
        "Atendível": (13, D("20399.52")),
        "Ruptura": (67, D("199191.07")),
        "Bloqueado": (34, D("125973.30")),
    }


def test_ca3_mensagens_nao_cotaveis(banco):
    linhas = banco.execute("SELECT cod_pedido FROM vw_mensagem_nao_cotavel ORDER BY 1").fetchall()
    assert [l[0] for l in linhas] == ["PED012", "PED016", "PED018", "PED027"]


def test_ca6_produtos_em_ruptura(banco):
    assert um(banco, "SELECT count(*) FROM vw_produto_ruptura") == (21,)


def test_ca7_casos_de_referencia(banco):
    sql = "SELECT classe, valor FROM vw_orcamento_classificado WHERE cod_pedido = '{}'"
    assert um(banco, sql.format("PED003")) == ("Atendível", D("185.00"))
    assert um(banco, sql.format("PED008"))[0] == "Bloqueado"
    assert um(banco, sql.format("PED029")) == ("Ruptura", D("11340.00"))


def test_rn2_preco_por_volume(banco):
    # 200 P001 a 0,85 + 50 P002 a 0,20: só a quantidade acima de 100 usa preço de volume.
    assert um(banco, "SELECT sum(valor) FROM vw_orcamento_item WHERE cod_pedido = 'PED001'") == (D("180.00"),)


def test_rn7_motivo_preenchido(banco):
    assert um(banco, "SELECT count(*) FROM vw_orcamento_classificado WHERE motivo IS NULL") == (0,)


def test_rn8_ordem_da_fila(banco):
    linhas = banco.execute(
        "SELECT classe, valor FROM vw_orcamento_classificado ORDER BY ordem"
    ).fetchall()
    peso = {"Atendível": 0, "Ruptura": 1, "Bloqueado": 2}
    assert linhas == sorted(linhas, key=lambda l: (peso[l[0]], -l[1]))


def test_rn2_meio_centavo_arredonda_para_cima(banco):
    # O valor exato é 4.537,665; com float, o resultado cairia para 4.537,66.
    assert um(banco, "SELECT valor FROM vw_orcamento_classificado WHERE cod_pedido = 'PED2647'") == (D("4537.67"),)


def test_ca11_formatacao_condicional(banco):
    sql = """SELECT cobertura_pct, nivel_cobertura, maior_atraso, nivel_atraso
             FROM vw_orcamento_classificado WHERE cod_pedido = '{}'"""
    assert um(banco, sql.format("PED003")) == (100, "Bom", 0, "Bom")
    assert um(banco, sql.format("PED009"))[:2] == (0, "Crítico")
    assert um(banco, sql.format("PED008")) == (65, "Atenção", 20, "Crítico")
