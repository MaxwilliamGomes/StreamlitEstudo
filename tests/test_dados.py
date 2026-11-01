from decimal import Decimal as D

from app.dados import ler_dados


def test_leitura_das_views():
    dados = ler_dados()
    assert len(dados.orcamentos) == 114
    assert dados.orcamentos.valor.sum() == D("345563.89")
    assert dados.orcamentos.ordem.tolist() == list(range(1, 115))
    assert len(dados.vencidos) == 16
    assert len(dados.bloqueados) == 8
    assert len(dados.rupturas) == 21
    assert len(dados.creditos_sem_nf) == 6
    assert len(dados.nao_cotaveis) == 4
    assert set(dados.orcamentos.cod_pedido) == set(dados.itens.cod_pedido)
