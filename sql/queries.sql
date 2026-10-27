-- Balance mensual (ingresos - egresos)
WITH monthly AS (
  SELECT date_trunc('month', tx_date)::date AS month,
         SUM(CASE WHEN category='Ingresos' THEN amount ELSE 0 END) AS income,
         SUM(CASE WHEN category<>'Ingresos' THEN amount ELSE 0 END) AS expense
  FROM fact_transaction
  GROUP BY 1
)
SELECT month, income, expense, (income - expense) AS net
FROM monthly
ORDER BY month;

-- Top categorías de gasto (últimos 90 días)
SELECT category, SUM(amount) AS spent
FROM fact_transaction
WHERE category <> 'Ingresos'
  AND tx_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY 1
ORDER BY spent DESC;

-- Distribución por método de pago (gastos)
SELECT method, SUM(amount) AS spent
FROM fact_transaction
WHERE category <> 'Ingresos'
GROUP BY 1
ORDER BY spent DESC;