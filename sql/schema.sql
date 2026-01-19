CREATE TABLE IF NOT EXISTS transaction (
  tx_id       INT PRIMARY KEY,
  tx_date     DATE NOT NULL,
  category    TEXT NOT NULL,
  method      TEXT NOT NULL,
  amount      NUMERIC(12,2) NOT NULL,
  description TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tx_date ON transaction(tx_date);
CREATE INDEX IF NOT EXISTS idx_tx_category ON transaction(category);