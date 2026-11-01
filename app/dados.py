"""Leitura das views. As regras de negócio ficam no banco (princípio 6)."""
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from app.conexao import conectar

CONSULTAS = {
    "orcamentos": "SELECT * FROM vw_orcamento_classificado ORDER BY ordem",
    "itens": "SELECT cod_pedido, cod_cliente, cod_produto FROM vw_orcamento_item",
    "vencidos": """
        SELECT t.cod_titulo, t.cod_cliente, c.nome AS cliente, t.saldo, t.dias_atraso, t.faixa_atraso
        FROM vw_titulo_saldo t
        JOIN clientes c USING (cod_cliente)
        WHERE t.vencido
        ORDER BY t.cod_cliente, t.cod_titulo
    """,
    "bloqueados": "SELECT cod_cliente, maior_atraso FROM vw_cliente_bloqueado",
    "rupturas": "SELECT * FROM vw_produto_ruptura ORDER BY cod_produto",
    "creditos_sem_nf": "SELECT * FROM vw_credito_sem_nf ORDER BY data",
    "nao_cotaveis": "SELECT * FROM vw_mensagem_nao_cotavel ORDER BY cod_pedido",
}


@dataclass(frozen=True)
class Dados:
    orcamentos: pd.DataFrame
    itens: pd.DataFrame
    vencidos: pd.DataFrame
    bloqueados: pd.DataFrame
    rupturas: pd.DataFrame
    creditos_sem_nf: pd.DataFrame
    nao_cotaveis: pd.DataFrame


def ler_dados():
    with conectar() as conexao, conexao.cursor() as cursor:
        tabelas = {}
        for nome, sql in CONSULTAS.items():
            cursor.execute(sql)
            colunas = [coluna.name for coluna in cursor.description]
            tabelas[nome] = pd.DataFrame(cursor.fetchall(), columns=colunas)
    return Dados(**tabelas)


@st.cache_data(show_spinner=False)
def carregar():
    return ler_dados()
