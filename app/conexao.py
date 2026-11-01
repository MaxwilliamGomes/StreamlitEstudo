"""Conexão com o Postgres a partir do arquivo .env."""
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parents[1]


def conectar():
    texto = (RAIZ / ".env").read_text(encoding="utf-8")
    env = dict(linha.split("=", 1) for linha in texto.splitlines() if "=" in linha)
    return psycopg.connect(
        host=env["POSTGRES_HOST"],
        port=env["POSTGRES_PORT"],
        dbname=env["POSTGRES_DB"],
        user=env["POSTGRES_USER"],
        password=env["POSTGRES_PASSWORD"],
    )
