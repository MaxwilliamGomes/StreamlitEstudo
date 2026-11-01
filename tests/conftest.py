import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.conexao import conectar  # noqa: E402


@pytest.fixture(scope="session")
def banco():
    with conectar() as conexao:
        conexao.autocommit = True  # um erro não contamina os testes seguintes
        yield conexao
