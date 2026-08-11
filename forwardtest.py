import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
import os

print("\n" + "="*60)
print("🤖 BOJAN FORWARD TEST - AUTOMATED")
print("="*60 + "\n")

# Konfiguration
START = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')  # Letzte 60 Tage
END = datetime.now().strftime('%Y-%m-%d')
INITIAL_CAPITAL = 50000
CONTRACTS = 5
POINT_VALUE = 2.0

print(f"Zeitraum: {START} bis {END}")
print(f"Kapital: ${INITIAL_CAPITAL:,.2f}")
print(f"Contracts: {CONTRACTS} MNQ\n")

# Daten laden
print("📥 Lade NQ Futures Daten...")
try:
    df = yf.download('NQ=F', start=START, end=END, interval='1d', progress=False)
except Exception as e:
    print(f"❌ Fehler beim Download: {e}")
    exit()

if df.empty:
    print("❌ Keine Daten!")
    exit()

close = df['Close'].values
high = df['High'].values
low = df['Low'].values

print(f"✅ {len(close)} Kerzen geladen\n")
print("📊 Berechne Indikatoren...\n")

# MA20
ma20 = [0] * len(close)
for i in range(20, len(close)):
    ma20[i] = sum(close[i-20:i]) / 20

# MA50
ma50 = [0] * len(close)
for i in range(50, len(close)):
    ma50[i] = sum(close[i-50:i]) / 50

# ATR
atr = [0] * len(close)
for i in range(1, len(close)):
    if i >= 14:
        tr_list = []
        for j in range(i-13, i+1):
            tr = max(high[j] - low[j], abs(high[j] - close[j-1]), abs(low[j] - close[j-1]))
            tr_list.append(tr)
        atr[i] = sum(tr_list) / 14
    else:
        atr[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))

# STRATEGY - BOJAN LOGIC
trades = []
in_trade = False
entry = 0
sl = 0
tp = 0

for i in range(60, len(close)):
    c = close[i]
    m20 = ma20[i]
    m50 = ma50[i]
    a = atr[i]
    
    if m20 == 0 or m50 == 0:
        continue
    
    # EXIT
    if in_trade:
        if c >= tp or c <= sl:
            profit = (c - entry) * CONTRACTS * POINT_VALUE
            trades.append({
                'profit': profit,
                'type': 'LONG',
                'pct': ((c - entry) / entry) * 100
            })
            in_trade = False
    
    # ENTRY - MA Crossover (einfache Version)
    if not in_trade:
        if m20 > m50 and c > m20:  # LONG Signal
            entry = c
            sl = c - (a * 1.5)
            tp = c + (a * 1.5)
            in_trade = True

# RESULTS
print("="*60)
print("📊 FORWARD-TEST ERGEBNISSE")
print("="*60 + "\n")

if len(trades) == 0:
    print("❌ Keine Trades gefunden")
else:
    total_profit = sum([t['profit'] for t in trades])
    wins = len([t for t in trades if t['profit'] > 0])
    losses = len([t for t in trades if t['profit'] < 0])
    total = len(trades)
    
    final_capital = INITIAL_CAPITAL + total_profit
    ret_pct = (total_profit / INITIAL_CAPITAL) * 100
    win_rate = (wins / total * 100) if total > 0 else 0
    
    print(f"Start Kapital:     ${INITIAL_CAPITAL:,.2f}")
    print(f"End Kapital:       ${final_capital:,.2f}")
    print(f"Gewinn/Verlust:    ${total_profit:,.2f}")
    print(f"Return %:          {ret_pct:.2f}%\n")
    
    print(f"Trades Gesamt:     {total}")
    print(f"✅ Wins:            {wins}")
    print(f"❌ Losses:          {losses}")
    print(f"Win Rate:          {win_rate:.2f}%\n")
    
    if wins > 0:
        print(f"Best Trade:        ${max([t['profit'] for t in trades]):,.2f}")
    if losses > 0:
        print(f"Worst Trade:       ${min([t['profit'] for t in trades]):,.2f}")

print("\n" + "="*60)

# Speichere Ergebnisse in CSV
csv_file = 'forward_test_results.csv'
file_exists = os.path.isfile(csv_file)

with open(csv_file, 'a', newline='') as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(['Date', 'Trades', 'Wins', 'Win_Rate', 'Profit', 'Return_Pct'])
    
    if len(trades) > 0:
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M'),
            total,
            wins,
            f"{win_rate:.2f}",
            f"{total_profit:.2f}",
            f"{ret_pct:.2f}"
        ])

print("✅ Ergebnisse gespeichert in 'forward_test_results.csv'")
