CREATE TABLE clientes (
    cod_cliente          text PRIMARY KEY,
    nome                 text NOT NULL,
    cidade               text NOT NULL,
    segmento             text NOT NULL,
    prazo_pagamento_dias integer NOT NULL,
    desconto_maximo_pct  numeric(5, 2) NOT NULL,
    cliente_desde        date NOT NULL
);

CREATE TABLE produtos (
    cod_produto          text PRIMARY KEY,
    descricao            text NOT NULL UNIQUE,
    categoria            text NOT NULL,
    unidade              text NOT NULL,
    preco_unitario       numeric(12, 2) NOT NULL,
    preco_acima_100_un   numeric(12, 2) NOT NULL,
    estoque              integer NOT NULL,
    prazo_reposicao_dias integer NOT NULL
);

CREATE TABLE pedidos (
    cod_pedido  text PRIMARY KEY,
    data        date NOT NULL,
    cod_cliente text REFERENCES clientes,  -- spam não tem cliente
    canal       text NOT NULL,
    mensagem    text NOT NULL,
    status      text NOT NULL
);

CREATE TABLE pedido_itens (
    cod_pedido     text NOT NULL REFERENCES pedidos,
    cod_produto    text NOT NULL REFERENCES produtos,
    quantidade     integer NOT NULL CHECK (quantidade > 0),
    preco_unitario numeric(12, 2) NOT NULL,
    desconto_pct   numeric(5, 2) NOT NULL,
    PRIMARY KEY (cod_pedido, cod_produto)
);

CREATE TABLE titulos (
    cod_titulo  text PRIMARY KEY,
    cod_cliente text NOT NULL REFERENCES clientes,
    nota_fiscal text NOT NULL UNIQUE,
    valor       numeric(12, 2) NOT NULL,
    emissao     date NOT NULL,
    vencimento  date NOT NULL,
    status      text NOT NULL,
    cod_pedido  text REFERENCES pedidos  -- vazio nos títulos originais
);

CREATE TABLE extrato (
    cod_lancamento text PRIMARY KEY,
    data           date NOT NULL,
    descricao      text NOT NULL,
    valor          numeric(12, 2) NOT NULL,
    tipo           text NOT NULL CHECK (tipo IN ('credito', 'debito'))
);

CREATE TABLE parametros (
    id              boolean PRIMARY KEY DEFAULT true CHECK (id),  -- garante uma única linha
    data_referencia date NOT NULL
);

INSERT INTO parametros (data_referencia) VALUES ('2026-08-28');
