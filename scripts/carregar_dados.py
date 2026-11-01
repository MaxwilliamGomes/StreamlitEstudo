"""Recria o banco a partir de db/*.sql e dos CSVs de dados/."""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from app.conexao import conectar  # noqa: E402

# Em ordem de dependência das chaves estrangeiras.
CARGAS = {
    "clientes": "clientes.csv",
    "produtos": "produtos.csv",
    "pedidos": "pedidos_orcamento.csv",
    "pedido_itens": "pedido_itens.csv",
    "titulos": "titulos_receber.csv",
    "extrato": "extrato_bancario.csv",
}


def carregar():
    with conectar() as conexao, conexao.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE")
        cursor.execute("CREATE SCHEMA public")
        for arquivo in sorted((RAIZ / "db").glob("*.sql")):
            cursor.execute(arquivo.read_text(encoding="utf-8"))

        for tabela, nome in CARGAS.items():
            caminho = RAIZ / "dados" / nome
            with caminho.open(encoding="utf-8", newline="") as csv_arquivo:
                colunas = ", ".join(next(csv.reader(csv_arquivo)))
                csv_arquivo.seek(0)
                comando = f"COPY {tabela} ({colunas}) FROM STDIN WITH (FORMAT csv, HEADER true)"
                with cursor.copy(comando) as copia:
                    copia.write(csv_arquivo.read())
            linhas = cursor.execute(f"SELECT count(*) FROM {tabela}").fetchone()[0]
            with caminho.open(encoding="utf-8", newline="") as csv_arquivo:
                esperado = sum(1 for _ in csv.reader(csv_arquivo)) - 1
            if linhas != esperado:
                raise RuntimeError(f"{tabela}: {linhas} linhas no banco, {esperado} no CSV")
            print(f"{tabela}: {linhas} linhas")


if __name__ == "__main__":
    carregar()
