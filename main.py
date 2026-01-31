import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

# 設定台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# 1. 定義產業分類
industry_map = {
    "🚀 太空火箭": ['FLY', 'LUNR', 'RKLB'],
    "⚛️ 核能能源": ['UUUU', 'LEU', 'OKLO', 'SMR', 'USAR', 'NNE'],
    "🪨 稀土戰略": ['CRML', 'AREC', 'NB', 'LAC'],
    "🛡️ 軍工產業": ['LMT', 'NOC'],
    "🤖 AI 與晶片": ['TSLA', 'TSM', 'NVDA', 'AMD']
}

# 攤平清單
all_tickers = [ticker for sublist in industry_map.values() for ticker in sublist]

print(f"正在抓取 {len(all_tickers)} 檔標的資料...")

# 下載資料 (6個月以確保 SMA60 計算無誤)
df = yf.download(all_tickers, period="6mo", group_by='ticker', auto_adjust=True, threads=True)

# --- HTML 樣式 (CSS) ---
# 採用台灣股市習慣：紅漲 (Up) / 綠跌 (Down)
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>美股每日追蹤儀表板</title>
    <style>
        body {{ font-family: "Microsoft JhengHei", -apple-system, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        
        /* 標題區 */
        header {{ text-align: center; margin-bottom: 30px; }}
        h1 {{ color: #003366; margin-bottom: 5px; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        
        /* 卡片設計 */
        .category-card {{ background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 25px; overflow: hidden; }}
        .card-header {{ background-color: #003366; color: white; padding: 12px 20px; font-weight: bold; font-size: 1.1em; }}
        
        /* 表格設計 */
        table {{ width: 100%; border-collapse: collapse; font-size: 0.95em; }}
        th {{ background-color: #f8f9fa; color: #666; font-weight: 600; padding: 12px 8px; text-align: right; border-bottom: 2px solid #eee; }}
        th:first-child {{ text-align: left; padding-left: 20px; }}
        td {{ padding: 12px 8px; text-align: right; border-bottom: 1px solid #eee; }}
        td:first-child {{ text-align: left; padding-left: 20px; font-weight: bold; color: #2c3e50; }}
        
        /* 漲跌顏色 (台灣習慣：紅漲綠跌) */
        .up {{ color: #e74c3c; font-weight: bold; }}
        .down {{ color: #27ae60; font-weight: bold; }}
        .neutral {{ color: #7f8c8d; }}
        
        /* 訊號徽章 */
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; color: white; font-weight: normal; }}
        .badge-bull {{ background-color: #e74c3c; }} /* 多頭 */
        .badge-bear {{ background-color: #27ae60; }} /* 空頭 */
        .badge-neutral {{ background-color: #95a5a6; }}
        
        /* 手機響應式調整 */
        @media (max-width: 600px) {{
            table, thead, tbody, th, td, tr {{ display: block; }}
            thead tr {{ position: absolute; top: -9999px; left: -9999px; }}
            tr {{ border: 1px solid #ccc; margin-bottom: 10px; border-radius: 8px; padding: 10px; }}
            td {{ border: none; position: relative; padding-left: 50%; text-align: right; margin-bottom: 5px; }}
            td:before {{ position: absolute; top: 12px; left: 10px; width: 45%; padding-right: 10px; white-space: nowrap; text-align: left; font-weight: bold; color: #999; }}
            
            /* 手機版欄位標籤 */
            td:nth-of-type(1):before {{ content: "代碼"; }}
            td:nth-of-type(2):before {{ content: "收盤價"; }}
            td:nth-of-type(3):before {{ content: "漲跌幅"; }}
            td:nth-of-type(4):before {{ content: "月線(20MA)"; }}
            td:nth-of-type(5):before {{ content: "季線(60MA)"; }}
            td:nth-of-type(6):before {{ content: "RSI"; }}
            td:nth-of-type(7):before {{ content: "訊號"; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 美股每日追蹤儀表板</h1>
            <div class="timestamp">更新時間：{tw_time} (UTC+8)</div>
        </header>
"""

# --- 資料處理與表格生成 ---
for category, tickers in industry_map.items():
    html_content += f"""
        <div class="category-card">
            <div class="card-header">{category}</div>
            <table>
                <thead>
                    <tr>
                        <th>代碼</th>
                        <th>收盤價</th>
                        <th>漲跌幅</th>
                        <th>月線 (20MA)</th>
                        <th>季線 (60MA)</th>
                        <th>RSI</th>
                        <th>訊號</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for ticker in tickers:
        try:
            # 處理單一 ticker 或多 ticker 的 dataframe 結構差異
            if len(all_tickers) == 1:
                stock_data = df.copy()
            else:
                if ticker not in df.columns.levels[0]:
                    continue
                stock_data = df[ticker].copy()
            
            stock_data.dropna(subset=['Close'], inplace=True)
            if len(stock_data) < 60:
                continue

            # 計算指標
            stock_data['SMA_20'] = ta.sma(stock_data['Close'], length=20)
            stock_data['SMA_60'] = ta.sma(stock_data['Close'], length=60)
            stock_data['RSI_14'] = ta.rsi(stock_data['Close'], length=14)

            # 取得最新數據
            latest = stock_data.iloc[-1]
            prev = stock_data.iloc[-2]
            
            # 數值計算
            price = latest['Close']
            change = price - prev['Close']
            pct_change = (change / prev['Close']) * 100
            sma20 = latest['SMA_20']
            sma60 = latest['SMA_60']
            rsi = latest['RSI_14']

            # 樣式邏輯 (台灣紅漲綠跌)
            if change > 0:
                trend_class = "up"
                sign_arrow = "▲"
            elif change < 0:
                trend_class = "down"
                sign_arrow = "▼"
            else:
                trend_class = "neutral"
                sign_arrow = "-"

            # 多空訊號判斷
            if price > sma20:
                signal_html = '<span class="badge badge-bull">多頭</span>'
            else:
                signal_html = '<span class="badge badge-bear">空頭</span>'
            
            # 處理 NaN 顯示
            sma20_str = f"{sma20:.2f}" if pd.notna(sma20) else "-"
            sma60_str = f"{sma60:.2f}" if pd.notna(sma60) else "-"
            rsi_str = f"{rsi:.1f}" if pd.notna(rsi) else "-"

            # 生成 HTML 行
            html_content += f"""
                    <tr>
                        <td>{ticker}</td>
                        <td>${price:.2f}</td>
                        <td class="{trend_class}">{sign_arrow} {abs(change):.2f} ({pct_change:.2f}%)</td>
                        <td>{sma20_str}</td>
                        <td>{sma60_str}</td>
                        <td>{rsi_str}</td>
                        <td>{signal_html}</td>
                    </tr>
            """
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    html_content += """
                </tbody>
            </table>
        </div>
    """

# --- 結尾 ---
html_content += """
        <footer style="text-align: center; margin-top: 30px; color: #999; font-size: 0.8em;">
            Automated by GitHub Actions | Data via yfinance
        </footer>
    </div>
</body>
</html>
"""

# 寫入檔案
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🎉 網頁生成完畢！")
