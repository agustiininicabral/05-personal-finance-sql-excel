# Personal Finance Dashboard — SQL + Excel

Proyecto de portfolio para explorar transacciones sintéticas, calcular balance mensual y gastos por categoría, y presentar un dashboard de Excel.

![Finance data quality CI](https://github.com/agustiininicabral/05-personal-finance-sql-excel/actions/workflows/ci.yml/badge.svg)

**Privacidad:** todos los registros son ficticios. No uses ni subas extractos bancarios reales a este repositorio.

## Dataset

- `data/transactions.csv`: 2.200 transacciones entre enero de 2024 y diciembre de 2025.
- `excel/finance_dashboard.xlsx`: dashboard de demostración.
- `sql/schema.sql`: tabla de hechos `fact_transaction` e índice por fecha.
- `sql/queries.sql`: balance mensual, gastos e ingresos por categoría.

## Validación local

Requiere Python 3.12 o posterior; el validador usa solo la biblioteca estándar:

```powershell
python scripts/validate_transactions.py
python -m unittest discover -s tests -v
```

El validador verifica columnas requeridas, IDs únicos, fechas, importes positivos y métodos de pago admitidos. Genera un JSON con totales, balance neto, resúmenes mensuales y montos por categoría. GitHub Actions ejecuta los tests y publica el reporte como artefacto temporal.

## SQL

1. Crear una base PostgreSQL vacía.
2. Ejecutar `sql/schema.sql`.
3. Importar `data/transactions.csv` a `fact_transaction`.
4. Ejecutar `sql/queries.sql`.

La tabla se llama `fact_transaction` para evitar conflictos con la palabra reservada `TRANSACTION`. Las consultas usan `date_trunc`, por lo que la sintaxis está orientada a PostgreSQL.

## Definiciones

- **Ingresos:** transacciones cuya categoría es `Ingresos`.
- **Gastos:** todas las demás categorías.
- **Balance neto:** ingresos menos gastos.
- Los importes se interpretan como unidades monetarias sintéticas; no se asigna una moneda real.

## Estructura

- `data/transactions.csv`: dataset sintético.
- `scripts/validate_transactions.py`: controles y resúmenes.
- `tests/test_validate_transactions.py`: pruebas del validador.
- `sql/`: esquema y consultas.
- `excel/finance_dashboard.xlsx`: visualización de ejemplo.

## Licencia

MIT.
