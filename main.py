import os
import google.generativeai as genai
from datetime import datetime
import pytz
import time

# 設定 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- 使用 Gemini 3.0 Pro Preview ---
model_name = "gemini-3-pro-preview"
model = genai.GenerativeModel(model_name)

# 取得台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# --- 您的關注清單 ---
prompts = [
    {
        "title": "🚀 LUNR (Intuitive Machines) 動態",
        "query": "請詳細分析美股代碼 LUNR (Intuitive Machines) 的最新股價技術面、近期合約進展、重要新聞以及社群論壇（如 Reddit, X）的討論熱度與情緒。"
    },
    {
        "title": "🌌 FLY (Firefly Aerospace) 追蹤",
        "query": "請深入挖掘 Firefly Aerospace (FLY) 的最新動態，包含上市進度、供應鏈消息、合作夥伴以及任何潛在的政府合約新聞。"
    },
    {
        "title": "💰 黃金與宏觀經濟 (Golden Window)",
        "query": "請分析當前的宏觀經濟數據（通膨、利率），並結合「金穹 (Golden Window)」理論，解讀黃金價格走勢與美國三大戰略計劃（金穹、Janus、Artemis）的關聯性。"
    },
    {
        "title": "⚛️ 核能板塊深度掃描",
        "query": "請針對美股核能板塊重點個股：OKLO, BWXT, SMR, LEU 進行綜合分析。請比較它們近期的消息面利多與利空，並評估短期內的投資風險與機會。"
    },
    {
        "title": "🇹🇼 台積電 (2330/TSM) 戰略分析",
        "query": "請整理台積電 (2330/TSM) 最新的法說會關鍵數據、高層對未來的展望言論，以及華爾街與外資機構對其後市的最新評級與目標價調整。"
    }
]

# --- 生成 HTML 內容 (CSS 優化版) ---
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>個人美股戰情室 (3.0版)</title>
    <style>
        /* 全域設定 */
        body {{ 
            font-family: "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            line-height: 1.8; 
            font-size: 16px; /* 統一內文基準大小 */
            color: #333;
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f4f7f6; 
        }}

        /* 頁面大標題 */
        h1 {{ 
            text-align: center; 
            color: #003366; 
            border-bottom: 3px solid #d32f2f; 
            padding-bottom: 15px; 
            margin-bottom: 10px; 
            font-size: 28px; /* 大標題 */
            font-weight: bold;
        }}

        /* 時間與模型標籤 */
        .timestamp {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; }}
        .model-tag {{ display: inline-block; background: linear-gradient(90deg, #d32f2f, #8e44ad); color: white; padding: 5px 15px; border-radius: 20px; font-size: 13px; margin-bottom: 30px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}

        /* 卡片區塊 */
        .card {{ 
            background: white; 
            padding: 30px; 
            margin-bottom: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        }}

        /* 卡片標題 (股票名稱) */
        h2 {{ 
            color: #d32f2f; 
            margin-top: 0; 
            border-left: 5px solid #003366; 
            padding-left: 15px; 
            font-size: 22px; /* 卡片標題統一大小 */
            font-weight: bold;
        }}

        /* 內文標題 (AI 生成的小標) */
        h3 {{
            color: #2c3e50;
            font-size: 18px; /* 內文小標題 */
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        /* 內文文字 */
        .content-body {{
            font-size: 16px; /* 確保內文一致 */
            text-align: justify; /* 左右對齊 */
        }}
        
        strong {{ color: #000; font-weight: 700; background-color: #fff3cd; padding: 0 4px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <h1>📈 個人美股戰情室 (Gemini 3.0 Pro)</h1>
    <div style="text-align: center;">
        <p class="timestamp">更新時間：{tw_time} (UTC+8)</p>
        <span class="model-tag">🔥 Analysis Engine: {model_name}</span>
    </div>
"""

print(f"🚀 使用次世代模型 {model_name} 開始生成報告...")

for index, item in enumerate(prompts):
    print(f"[{index+1}/{len(prompts)}] 正在深度分析：{item['title']}...")
    try:
        response = model.generate_content(item['query'])
        
        # 格式優化
        text_content = response.text
        # 將 Markdown 語法轉換為 HTML 標籤
        text_content = text_content.replace("### ", "<h3>").replace("###", "</h3>")
        text_content = text_content.replace("**", "<strong>").replace("* ", "<li>").replace("\n", "<br>")
        
        html_content += f"""
        <div class="card">
            <h2>{item['title']}</h2>
            <div class="content-body">{text_content}</div>
        </div>
        """
        print("   ✅ 分析完成")
        
    except Exception as e:
        print(f"   ❌ 發生錯誤：{str(e)}")
        html_content += f"<div class='card'><h2>{item['title']}</h2><p style='color:red; background:#ffe6e6; padding:10px;'>分析失敗：{str(e)}</p></div>"

    if index < len(prompts) - 1:
        print("⏳ 等待 35 秒 (確保 3.0 Pro 連線穩定)...")
        time.sleep(35)

html_content += """
    <footer style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 14px;">
        Generated by Google Gemini 3.0 Pro Preview | Automated via GitHub Actions
    </footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🎉 3.0 Pro 戰情室報告生成完畢！")
