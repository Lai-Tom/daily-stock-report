import yfinance as yf
import pandas as pd
import pandas_ta as ta

# 1. 定義產業分類
industry_map = {
    "太空火箭": ['FLY', 'LUNR', 'RKLB'],
    "核能能源": ['UUUU', 'LEU', 'OKLO', 'SMR', 'USAR'],
    "稀土戰略": ['CRML', 'AREC', 'NB', 'LAC'],
    "軍工產業": ['LMT', 'NOC'],
    "AI產業": ['TSLA', 'TSM', 'NVDA', 'AMD']
}

# 攤平清單以利 yfinance 下載
all_tickers = [ticker for sublist in industry_map.values() for ticker in sublist]

print(f"正在抓取 {len(all_tickers)} 檔標的的最新股價資料...")

# 抓取最近 3 個月的數據
df = yf.download(all_tickers, period="3mo", group_by='ticker', auto_adjust=True)

# 用來存放計算結果
results = {}

for ticker in all_tickers:
    try:
        # 取得該檔股票的 DataFrame
        stock_data = df[ticker].copy()
        stock_data.dropna(subset=['Close'], inplace=True)
        
        if len(stock_data) < 2:
            continue

        # 2. 計算技術指標
        stock_data['SMA_20'] = ta.sma(stock_data['Close'], length=20)
        stock_data['SMA_60'] = ta.sma(stock_data['Close'], length=60)
        stock_data['RSI_14'] = ta.rsi(stock_data['Close'], length=14)
        
        # 取得最新一筆與前一筆資料
        latest = stock_data.iloc[-1]
        prev = stock_data.iloc[-2]
        
        change = latest['Close'] - prev['Close']
        pct_change = (change / prev['Close']) * 100
        
        results[ticker] = {
            "Date": latest.name.strftime('%Y-%m-%d'),
            "Close": round(latest['Close'], 2),
            "Change": round(change, 2),
            "Pct_Change": round(pct_change, 2),
            "SMA_20": round(latest['SMA_20'], 2) if pd.notna(latest['SMA_20']) else "N/A",
            "RSI": round(latest['RSI_14'], 2) if pd.notna(latest['RSI_14']) else "N/A"
        }
    except Exception as e:
        print(f"處理 {ticker} 時發生錯誤: {e}")

# 3. 依照產業分類顯示結果
print("\n" + "★"*30)
print("  美股產業分類監控報表")
print("★"*30)

for category, tickers in industry_map.items():
    print(f"\n【{category}】")
    print("-" * 65)
    print(f"{'代碼':<8} {'日期':<12} {'現價':<10} {'漲跌(%)':<15} {'月線(SMA20)':<12} {'RSI':<6}")
    
    for ticker in tickers:
        if ticker in results:
            d = results[ticker]
            change_str = f"{d['Change']} ({d['Pct_Change']}%)"
            print(f"{ticker:<8} {d['Date']:<12} {d['Close']:<10} {change_str:<15} {d['SMA_20']:<12} {d['RSI']:<6}")
        else:
            print(f"{ticker:<8} 無法取得資料")
    print("-" * 65)

請協助幫我執行上述程式看看
