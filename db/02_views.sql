-- RN3, RN4, RN9: saldo, atraso e faixa de cada título na data de referência.
CREATE VIEW vw_titulo_saldo AS
WITH pagamentos AS (
    SELECT substring(e.descricao FROM 'NF-[0-9]+') AS nota_fiscal,
           sum(e.valor) AS pago
    FROM extrato e
    CROSS JOIN parametros p
    WHERE e.tipo = 'credito'
      AND e.data <= p.data_referencia
    GROUP BY 1
),
calculo AS (
    SELECT t.cod_titulo,
           t.cod_cliente,
           t.nota_fiscal,
           t.valor,
           t.vencimento,
           coalesce(pg.pago, 0) AS pago,
           greatest(t.valor - coalesce(pg.pago, 0), 0) AS saldo,
           p.data_referencia - t.vencimento AS dias_atraso
    FROM titulos t
    CROSS JOIN parametros p
    LEFT JOIN pagamentos pg USING (nota_fiscal)
    WHERE t.emissao <= p.data_referencia
)
SELECT *,
       saldo > 0 AND dias_atraso > 0 AS vencido,
       CASE
           WHEN saldo = 0 OR dias_atraso <= 0 THEN NULL
           WHEN dias_atraso <= 15 THEN '1–15'
           WHEN dias_atraso <= 30 THEN '16–30'
           WHEN dias_atraso <= 60 THEN '31–60'
           ELSE 'Mais de 60'
       END AS faixa_atraso
FROM calculo;

-- RN5: título vencido há mais de 15 dias bloqueia o cliente.
CREATE VIEW vw_cliente_bloqueado AS
SELECT cod_cliente,
       sum(saldo) AS saldo_vencido,
       count(*) AS titulos,
       max(dias_atraso) AS maior_atraso
FROM vw_titulo_saldo
WHERE vencido
  AND dias_atraso > 15
GROUP BY cod_cliente;

-- RF7: créditos que não abatem títulos por não informarem a NF.
CREATE VIEW vw_credito_sem_nf AS
SELECT e.cod_lancamento, e.data, e.descricao, e.valor
FROM extrato e
CROSS JOIN parametros p
WHERE e.tipo = 'credito'
  AND e.data <= p.data_referencia
  AND e.descricao !~ 'NF-[0-9]+';

-- RN1, RN2: itens dos orçamentos em aberto, com valor calculado.
CREATE VIEW vw_orcamento_item AS
SELECT pe.cod_pedido,
       pe.cod_cliente,
       i.cod_produto,
       pr.descricao,
       pr.categoria,
       i.quantidade,
       i.preco_unitario,
       i.desconto_pct,
       i.quantidade * i.preco_unitario * (1 - i.desconto_pct / 100) AS valor
FROM pedidos pe
JOIN pedido_itens i USING (cod_pedido)
JOIN produtos pr USING (cod_produto)
WHERE pe.status IN ('novo', 'cotado');

-- RN1: mensagens em aberto sem itens ficam fora da fila.
CREATE VIEW vw_mensagem_nao_cotavel AS
SELECT pe.cod_pedido, pe.data, pe.cod_cliente, pe.canal, pe.mensagem
FROM pedidos pe
WHERE pe.status IN ('novo', 'cotado')
  AND NOT EXISTS (SELECT 1 FROM pedido_itens i WHERE i.cod_pedido = pe.cod_pedido);

-- RN6: a demanda somada de toda a fila supera o estoque.
CREATE VIEW vw_produto_ruptura AS
SELECT i.cod_produto,
       i.descricao,
       i.categoria,
       sum(i.quantidade) AS demanda,
       pr.estoque,
       sum(i.quantidade) - pr.estoque AS falta,
       pr.prazo_reposicao_dias
FROM vw_orcamento_item i
JOIN produtos pr USING (cod_produto)
GROUP BY i.cod_produto, i.descricao, i.categoria, pr.estoque, pr.prazo_reposicao_dias
HAVING sum(i.quantidade) > pr.estoque;

-- RN2, RN7, RN8: um orçamento por linha, com classe, motivo e ordem.
CREATE VIEW vw_orcamento_classificado AS
WITH orcamentos AS (
    SELECT cod_pedido, cod_cliente, round(sum(valor), 2) AS valor
    FROM vw_orcamento_item
    GROUP BY cod_pedido, cod_cliente
),
rupturas AS (
    SELECT i.cod_pedido,
           string_agg(r.descricao, ', ' ORDER BY r.descricao) AS produtos
    FROM vw_orcamento_item i
    JOIN vw_produto_ruptura r USING (cod_produto)
    GROUP BY i.cod_pedido
),
demanda AS (
    SELECT cod_produto, sum(quantidade) AS total
    FROM vw_orcamento_item
    GROUP BY cod_produto
),
coberturas AS (
    SELECT i.cod_pedido,
           min(least(100, round(pr.estoque * 100.0 / d.total)))::integer AS cobertura_pct
    FROM vw_orcamento_item i
    JOIN produtos pr USING (cod_produto)
    JOIN demanda d USING (cod_produto)
    GROUP BY i.cod_pedido
),
atrasos AS (
    SELECT cod_cliente, max(dias_atraso) AS maior_atraso
    FROM vw_titulo_saldo
    WHERE vencido
    GROUP BY cod_cliente
),
classificados AS (
    SELECT o.cod_pedido,
           pe.data,
           o.cod_cliente,
           c.nome AS cliente,
           c.segmento,
           pe.canal,
           o.valor,
           co.cobertura_pct,
           coalesce(a.maior_atraso, 0) AS maior_atraso,
           CASE
               WHEN co.cobertura_pct = 100 THEN 'Bom'
               WHEN co.cobertura_pct >= 50 THEN 'Atenção'
               ELSE 'Crítico'
           END AS nivel_cobertura,
           CASE
               WHEN coalesce(a.maior_atraso, 0) = 0 THEN 'Bom'
               WHEN a.maior_atraso <= 15 THEN 'Atenção'
               ELSE 'Crítico'
           END AS nivel_atraso,
           CASE
               WHEN b.cod_cliente IS NOT NULL THEN 'Bloqueado'
               WHEN r.cod_pedido IS NOT NULL THEN 'Ruptura'
               ELSE 'Atendível'
           END AS classe,
           CASE
               WHEN b.cod_cliente IS NOT NULL THEN format('Título vencido há %s dias', b.maior_atraso)
               WHEN r.cod_pedido IS NOT NULL THEN format('Sem estoque: %s', r.produtos)
               ELSE 'Estoque e crédito disponíveis'
           END AS motivo
    FROM orcamentos o
    JOIN pedidos pe USING (cod_pedido)
    JOIN clientes c ON c.cod_cliente = o.cod_cliente
    LEFT JOIN vw_cliente_bloqueado b ON b.cod_cliente = o.cod_cliente
    LEFT JOIN rupturas r USING (cod_pedido)
    LEFT JOIN coberturas co USING (cod_pedido)
    LEFT JOIN atrasos a ON a.cod_cliente = o.cod_cliente
)
SELECT *,
       row_number() OVER (
           ORDER BY CASE classe WHEN 'Atendível' THEN 1 WHEN 'Ruptura' THEN 2 ELSE 3 END,
                    valor DESC,
                    cod_pedido
       ) AS ordem
FROM classificados;
