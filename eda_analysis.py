"""
UPI Transaction Fraud Pattern Analysis
Author: Somya Shrivastava
Tools: Python (Pandas, Matplotlib, Seaborn), SQL
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style="darkgrid")
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.titlesize': 13,
                     'axes.titleweight': 'bold', 'figure.facecolor': '#0A0E1A'})

DARK_BG = '#0A0E1A'; CARD_BG = '#12192B'
RED     = '#FF4B4B'; GREEN   = '#00D68F'
BLUE    = '#4D9FFF'; GOLD    = '#FFD166'
PURPLE  = '#C77DFF'; ORANGE  = '#FF9A3C'
WHITE   = '#E8EDF5'; GRAY    = '#3A4460'

df = pd.read_csv('upi_transactions.csv')
df['datetime'] = pd.to_datetime(df['datetime'])
df['month'] = df['datetime'].dt.month_name()

print("="*60)
print("UPI FRAUD PATTERN ANALYSIS REPORT")
print("="*60)
print(f"Total Transactions : {len(df):,}")
print(f"Total Amount       : ₹{df['amount'].sum():,.0f}")
print(f"Fraud Transactions : {df['is_fraud'].sum():,} ({df['is_fraud'].mean()*100:.1f}%)")
print(f"Fraud Amount       : ₹{df[df['is_fraud']==1]['amount'].sum():,.0f}")
print(f"Blocked Txns       : {(df['transaction_status']=='Blocked').sum()}")
print(f"Avg Risk Score     : {df['risk_score'].mean():.1f}/99")

# ── Fig 1: Main Dashboard ─────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle('🔐 UPI Transaction Fraud Pattern Analysis Dashboard',
             fontsize=17, fontweight='bold', color=RED, y=1.01)
for ax in axes.flat:
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=WHITE)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.title.set_color(GOLD)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRAY)

# 1. Hourly fraud rate
hourly = df.groupby('hour').agg(
    total=('is_fraud','count'), fraud=('is_fraud','sum')).reset_index()
hourly['fraud_rate'] = hourly['fraud'] / hourly['total'] * 100
hour_colors = [RED if r > 15 else ORANGE if r > 10 else GREEN for r in hourly['fraud_rate']]
axes[0,0].bar(hourly['hour'], hourly['fraud_rate'], color=hour_colors, edgecolor=DARK_BG)
axes[0,0].set_title('🕐 Fraud Rate by Hour of Day')
axes[0,0].set_xlabel('Hour'); axes[0,0].set_ylabel('Fraud Rate (%)')
axes[0,0].axhline(hourly['fraud_rate'].mean(), color=GOLD, linestyle='--',
                   label=f"Avg: {hourly['fraud_rate'].mean():.1f}%")
axes[0,0].legend(facecolor=CARD_BG, labelcolor=WHITE, fontsize=8)

# 2. Fraud by UPI App
app_fraud = df.groupby('upi_app')['is_fraud'].agg(['sum','count']).reset_index()
app_fraud['rate'] = app_fraud['sum']/app_fraud['count']*100
app_fraud = app_fraud.sort_values('rate', ascending=False)
bar_colors = [RED if r > 12 else ORANGE if r > 10 else GREEN for r in app_fraud['rate']]
axes[0,1].bar(app_fraud['upi_app'], app_fraud['rate'], color=bar_colors, edgecolor=DARK_BG)
axes[0,1].set_title('📱 Fraud Rate by UPI App')
axes[0,1].set_ylabel('Fraud Rate (%)')
for i, v in enumerate(app_fraud['rate']):
    axes[0,1].text(i, v+0.2, f'{v:.1f}%', ha='center', color=WHITE, fontsize=9)

# 3. Fraud type breakdown (pie)
fraud_only = df[df['is_fraud']==1]
ft = fraud_only['fraud_type'].value_counts()
pie_colors = [RED, ORANGE, PURPLE, BLUE, GREEN]
wedges, texts, autos = axes[0,2].pie(ft.values, labels=ft.index,
    autopct='%1.1f%%', colors=pie_colors, startangle=90,
    textprops={'color': WHITE, 'fontsize': 8})
axes[0,2].set_title('🎭 Fraud Type Breakdown')

# 4. Risk factors heatmap
risk_factors = df.groupby(['new_device', 'odd_hour_txn'])['is_fraud'].mean().reset_index()
pivot = risk_factors.pivot(index='new_device', columns='odd_hour_txn', values='is_fraud') * 100
sns.heatmap(pivot, ax=axes[1,0], annot=True, fmt='.1f', cmap='Reds',
            linewidths=0.5, linecolor=DARK_BG,
            xticklabels=['Normal Hour', 'Odd Hour'],
            yticklabels=['Known Device', 'New Device'])
axes[1,0].set_title('🔥 Fraud Rate Heatmap\n(Device × Time)')
axes[1,0].set_xlabel(''); axes[1,0].set_ylabel('')
axes[1,0].tick_params(colors=WHITE)

# 5. Amount distribution — fraud vs normal
normal_amt = df[df['is_fraud']==0]['amount'].clip(0, 20000)
fraud_amt  = df[df['is_fraud']==1]['amount'].clip(0, 20000)
axes[1,1].hist(normal_amt, bins=40, color=GREEN, alpha=0.6, label='Legitimate', density=True)
axes[1,1].hist(fraud_amt,  bins=40, color=RED,   alpha=0.6, label='Fraudulent', density=True)
axes[1,1].set_title('💰 Transaction Amount Distribution')
axes[1,1].set_xlabel('Amount (₹)')
axes[1,1].set_ylabel('Density')
axes[1,1].legend(facecolor=CARD_BG, labelcolor=WHITE)

# 6. City-wise fraud volume
city_fraud = df.groupby('city').agg(fraud=('is_fraud','sum'), total=('is_fraud','count')).reset_index()
city_fraud['rate'] = city_fraud['fraud']/city_fraud['total']*100
city_fraud = city_fraud.sort_values('fraud', ascending=True)
city_colors = [RED if r > 12 else ORANGE if r > 10 else BLUE for r in city_fraud['rate']]
axes[1,2].barh(city_fraud['city'], city_fraud['fraud'], color=city_colors, edgecolor=DARK_BG)
axes[1,2].set_title('🏙️ Fraud Volume by City')
axes[1,2].set_xlabel('Fraud Transactions')
for i, (_, row) in enumerate(city_fraud.iterrows()):
    axes[1,2].text(row['fraud']+0.5, i, f"{row['rate']:.1f}%", va='center', color=WHITE, fontsize=9)

plt.tight_layout()
plt.savefig('upi_fraud_dashboard.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("\n✅ Dashboard saved: upi_fraud_dashboard.png")

# ── Fig 2: Deep Dive ──────────────────────────────────────────────
fig2, axes2 = plt.subplots(1, 3, figsize=(20, 6))
fig2.patch.set_facecolor(DARK_BG)
fig2.suptitle('🔍 Fraud Deep Dive — Risk Factor Analysis', fontsize=15, fontweight='bold', color=RED)
for ax in axes2:
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=WHITE)
    ax.xaxis.label.set_color(WHITE)
    ax.yaxis.label.set_color(WHITE)
    ax.title.set_color(GOLD)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRAY)

# Risk score distribution
axes2[0].hist(df[df['is_fraud']==0]['risk_score'], bins=30, color=GREEN, alpha=0.7,
              label='Legitimate', density=True)
axes2[0].hist(df[df['is_fraud']==1]['risk_score'], bins=30, color=RED, alpha=0.7,
              label='Fraudulent', density=True)
axes2[0].set_title('Risk Score Distribution')
axes2[0].set_xlabel('Risk Score'); axes2[0].set_ylabel('Density')
axes2[0].legend(facecolor=CARD_BG, labelcolor=WHITE)

# Category fraud rate
cat_fraud = df.groupby('category')['is_fraud'].mean().sort_values(ascending=False) * 100
cat_colors = [RED if v > 12 else ORANGE if v > 10 else GREEN for v in cat_fraud.values]
axes2[1].barh(cat_fraud.index, cat_fraud.values, color=cat_colors, edgecolor=DARK_BG)
axes2[1].set_title('Fraud Rate by Transaction Category')
axes2[1].set_xlabel('Fraud Rate (%)')
for i, v in enumerate(cat_fraud.values):
    axes2[1].text(v+0.1, i, f'{v:.1f}%', va='center', color=WHITE, fontsize=9)

# Transaction status breakdown
status_counts = df['transaction_status'].value_counts()
status_colors = [GREEN, RED, ORANGE]
axes2[2].pie(status_counts.values, labels=status_counts.index,
             autopct='%1.1f%%', colors=status_colors, startangle=90,
             textprops={'color': WHITE})
axes2[2].set_title('Transaction Status Breakdown')

plt.tight_layout()
plt.savefig('upi_deep_dive.png', dpi=150, bbox_inches='tight', facecolor=DARK_BG)
plt.close()
print("✅ Deep Dive saved: upi_deep_dive.png")

print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)
peak_fraud_hour = hourly.loc[hourly['fraud_rate'].idxmax(), 'hour']
top_fraud_city = city_fraud.sort_values('fraud', ascending=False).iloc[0]
riskiest_app = app_fraud.iloc[0]
print(f"1. Peak Fraud Hour   : {peak_fraud_hour}:00 hrs")
print(f"2. Highest Fraud City: {top_fraud_city['city']} ({top_fraud_city['fraud']} cases)")
print(f"3. Riskiest App      : {riskiest_app['upi_app']} ({riskiest_app['rate']:.1f}% fraud rate)")
print(f"4. New Device Risk   : {df[df['new_device']==1]['is_fraud'].mean()*100:.1f}% fraud vs {df[df['new_device']==0]['is_fraud'].mean()*100:.1f}% on known devices")
print(f"5. Top Fraud Type    : {fraud_only['fraud_type'].value_counts().index[0]}")
print(f"6. High-Value Fraud  : ₹{df[df['is_fraud']==1]['amount'].mean():,.0f} avg fraud amount vs ₹{df[df['is_fraud']==0]['amount'].mean():,.0f} normal")
print("\n✅ UPI Fraud Analysis Complete!")
