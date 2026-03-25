-- ================================================================
-- UPI Fraud Pattern Analysis — SQL Queries
-- Author: Somya Shrivastava
-- ================================================================

-- ── TABLE CREATION ─────────────────────────────────────────────
CREATE TABLE upi_transactions (
    transaction_id           VARCHAR(12) PRIMARY KEY,
    datetime                 DATETIME,
    hour                     INT,
    day_of_week              VARCHAR(15),
    city                     VARCHAR(20),
    upi_app                  VARCHAR(20),
    category                 VARCHAR(25),
    amount                   INT,
    new_device               TINYINT,
    multiple_failed_attempts TINYINT,
    location_mismatch        TINYINT,
    odd_hour_txn             TINYINT,
    is_fraud                 TINYINT,
    fraud_type               VARCHAR(30),
    risk_score               INT,
    transaction_status       VARCHAR(15)
);

-- ── QUERY 1: Fraud Overview ─────────────────────────────────────
SELECT
    COUNT(*)                                          AS total_transactions,
    SUM(is_fraud)                                     AS fraud_count,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2)            AS fraud_rate_pct,
    SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END)  AS total_fraud_amount,
    ROUND(AVG(CASE WHEN is_fraud=1 THEN amount END),0) AS avg_fraud_amount,
    SUM(CASE WHEN transaction_status='Blocked' THEN 1 ELSE 0 END) AS blocked_count
FROM upi_transactions;

-- ── QUERY 2: Hourly Fraud Pattern ──────────────────────────────
SELECT
    hour,
    COUNT(*)                                 AS total_txns,
    SUM(is_fraud)                            AS fraud_count,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2)  AS fraud_rate_pct,
    CASE
        WHEN hour BETWEEN 0 AND 5   THEN '🌙 Late Night (High Risk)'
        WHEN hour BETWEEN 6 AND 11  THEN '🌅 Morning'
        WHEN hour BETWEEN 12 AND 17 THEN '☀️ Afternoon'
        WHEN hour BETWEEN 18 AND 21 THEN '🌆 Evening'
        ELSE '🌃 Night'
    END AS time_slot
FROM upi_transactions
GROUP BY hour
ORDER BY fraud_rate_pct DESC;

-- ── QUERY 3: Risk Factor Analysis ──────────────────────────────
SELECT
    new_device,
    multiple_failed_attempts,
    location_mismatch,
    odd_hour_txn,
    COUNT(*)                                AS transactions,
    SUM(is_fraud)                           AS fraud_count,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    ROUND(AVG(risk_score), 1)              AS avg_risk_score
FROM upi_transactions
GROUP BY new_device, multiple_failed_attempts, location_mismatch, odd_hour_txn
ORDER BY fraud_rate_pct DESC
LIMIT 10;

-- ── QUERY 4: UPI App Fraud Comparison ──────────────────────────
SELECT
    upi_app,
    COUNT(*)                                AS total_txns,
    SUM(is_fraud)                           AS fraud_txns,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END) AS fraud_amount,
    ROUND(AVG(risk_score), 1)              AS avg_risk_score
FROM upi_transactions
GROUP BY upi_app
ORDER BY fraud_rate_pct DESC;

-- ── QUERY 5: High-Value Fraud Detection ────────────────────────
SELECT
    transaction_id, datetime, city, upi_app, category,
    amount, fraud_type, risk_score, transaction_status
FROM upi_transactions
WHERE is_fraud = 1 AND amount > 50000
ORDER BY amount DESC
LIMIT 20;

-- ── QUERY 6: City-wise Fraud Heatmap ───────────────────────────
SELECT
    city,
    COUNT(*)                                AS total_txns,
    SUM(is_fraud)                           AS fraud_count,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2) AS fraud_rate_pct,
    SUM(CASE WHEN is_fraud=1 THEN amount ELSE 0 END) AS total_fraud_amount,
    ROUND(AVG(CASE WHEN is_fraud=1 THEN amount END)) AS avg_fraud_amount
FROM upi_transactions
GROUP BY city
ORDER BY fraud_count DESC;

-- ── QUERY 7: Fraud Type Breakdown ──────────────────────────────
SELECT
    fraud_type,
    COUNT(*)                                AS cases,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER(), 2) AS pct_of_total_fraud,
    ROUND(AVG(amount), 0)                  AS avg_amount,
    ROUND(AVG(risk_score), 1)              AS avg_risk_score
FROM upi_transactions
WHERE is_fraud = 1
GROUP BY fraud_type
ORDER BY cases DESC;

-- ── QUERY 8: Running Fraud Count (Window Function) ─────────────
SELECT
    DATE(datetime)                          AS txn_date,
    SUM(is_fraud)                           AS daily_fraud,
    SUM(SUM(is_fraud)) OVER (
        ORDER BY DATE(datetime)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )                                       AS rolling_7day_fraud,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 2) AS daily_fraud_rate
FROM upi_transactions
GROUP BY DATE(datetime)
ORDER BY txn_date;
