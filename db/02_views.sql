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
