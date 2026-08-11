import yfinance as yf
from datetime import datetime, timedelta
import os

print("\nBOJAN FORWARD TEST - AUTOMATED\n")

try:
    START = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    END = datetime.now().strftime('%Y-%m-%d')
    INITIAL = 50000
    CONTRACTS = 5
    POINT_VALUE = 2.0
    
    print(f"Zeitraum: {START} bis {END}")
    print(f"Kapital: ${INITIAL:,.2f}\n")
    
    print("Lade Daten...")
    df = yf.download('QQQ', start=START, end=END, interval='1d', progress=False)
    
    if df.empty:
        print("FEHLER: Keine Daten!")
        exit(1)
    
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    
    print(f"OK - {len(close)} Kerzen\n")
    
    ma20 = [0] * len(close)
    for i in range(20, len(close)):
        ma20[i] = sum(close[i-20:i]) / 20
    
    ma50 = [0] * len(close)
    for i in range(50, len(close)):
        ma50[i] = sum(close[i-50:i]) / 50
    
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
        
        if m20 == 0:
            continue
        
        if in_trade:
            if c >= tp or c <= sl:
                profit = (c - entry) * CONTRACTS * POINT_VALUE
                trades.append(profit)
                in_trade = False
        
        if not in_trade and m20 > m50 and c > m20:
            entry = c
            sl = c - (a * 1.5)
            tp = c + (a * 1.5)
            in_trade = True
    
    print("="*60)
    print("ERGEBNISSE")
    print("="*60 + "\n")
    
    if len(trades) == 0:
        print("Keine Trades")
    else:
        total = sum(trades)
        wins = len([x for x in trades if x > 0])
        final = INITIAL + total
        ret = (total / INITIAL) * 100
        wr = (wins / len(trades) * 100)
        
        print(f"Start:     ${INITIAL:,.2f}")
        print(f"Ende:      ${final:,.2f}")
        print(f"Gewinn:    ${total:,.2f}")
        print(f"Return:    {ret:.2f}%\n")
        print(f"Trades:    {len(trades)}")
        print(f"Wins:      {wins}")
        print(f"Win Rate:  {wr:.2f}%")
    
        csv_file = 'forward_test_results.csv'
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a') as f:
            if not file_exists:
                f.write('Date,Trades,Wins,Win_Rate,Profit,Return_Pct\n')
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M')},{len(trades)},{wins},{wr:.2f},{total:.2f},{ret:.2f}\n")
    
    print("\nOK - Gespeichert")

except Exception as e:
    print(f"FEHLER: {str(e)}")
    exit(1)
