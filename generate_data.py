import pandas as pd
import numpy as np

np.random.seed(77)
n = 3000

cities = ['Mumbai', 'Pune', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Ahmedabad']
city_w  = [0.20, 0.15, 0.18, 0.15, 0.10, 0.08, 0.07, 0.07]
apps    = ['GPay', 'PhonePe', 'Paytm', 'BHIM', 'Amazon Pay']
app_w   = [0.35, 0.30, 0.20, 0.08, 0.07]
categories = ['Food & Dining', 'Shopping', 'Recharge', 'Bill Payment',
              'Money Transfer', 'Entertainment', 'Travel', 'Investment']
cat_w   = [0.18, 0.22, 0.12, 0.15, 0.14, 0.07, 0.08, 0.04]

dates = pd.date_range('2024-01-01', '2024-12-31', freq='h')
sample_dates = np.random.choice(dates, n, replace=True)
hours = pd.DatetimeIndex(sample_dates).hour

# Fraud more likely at odd hours, high amounts, new devices
is_odd_hour = np.isin(hours, list(range(0, 6)) + list(range(22, 24))).astype(int)
amount = np.where(
    np.random.random(n) < 0.1,
    np.random.randint(50000, 200000, n),   # high value — suspicious
    np.random.randint(10, 15000, n)         # normal
)

new_device     = np.random.choice([0, 1], n, p=[0.80, 0.20])
multiple_fails = np.random.choice([0, 1], n, p=[0.85, 0.15])
location_mismatch = np.random.choice([0, 1], n, p=[0.88, 0.12])

# Fraud probability based on risk factors
fraud_prob = (
    0.02
    + is_odd_hour         * 0.08
    + new_device          * 0.10
    + multiple_fails      * 0.15
    + location_mismatch   * 0.12
    + (amount > 50000).astype(int) * 0.10
)
fraud_prob = np.clip(fraud_prob, 0, 0.95)
is_fraud = (np.random.random(n) < fraud_prob).astype(int)

fraud_types = ['Account Takeover', 'Phishing', 'SIM Swap',
               'Fake UPI ID', 'Unauthorized Transfer', 'None']
fraud_type_assigned = np.where(
    is_fraud == 1,
    np.random.choice(fraud_types[:-1], n),
    'None'
)

df = pd.DataFrame({
    'transaction_id':    [f'TXN{str(i).zfill(6)}' for i in range(1, n+1)],
    'datetime':          sample_dates,
    'hour':              hours,
    'day_of_week':       pd.DatetimeIndex(sample_dates).day_name(),
    'city':              np.random.choice(cities, n, p=city_w),
    'upi_app':           np.random.choice(apps, n, p=app_w),
    'category':          np.random.choice(categories, n, p=cat_w),
    'amount':            amount,
    'new_device':        new_device,
    'multiple_failed_attempts': multiple_fails,
    'location_mismatch': location_mismatch,
    'odd_hour_txn':      is_odd_hour,
    'is_fraud':          is_fraud,
    'fraud_type':        fraud_type_assigned,
    'risk_score':        np.clip((fraud_prob * 100).astype(int), 1, 99),
    'transaction_status': np.where(is_fraud & (np.random.random(n) < 0.3), 'Blocked', 
                          np.where(is_fraud, 'Fraudulent', 'Successful'))
})

df.to_csv('upi_transactions.csv', index=False)
print(f"Dataset: {len(df)} transactions")
print(f"Fraud Rate: {df['is_fraud'].mean()*100:.1f}%")
print(df.head())
