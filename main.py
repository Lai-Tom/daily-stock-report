import os
import google.generativeai as genai
from datetime import datetime
import pytz
import time

# 設定 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 取得台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# --- 您的關注清單 (已同步 Google App 排程：移除台積電) ---
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
    }
]

# --- 智慧生成函數 (含自動救援機制) ---
def smart_generate(prompt_text):
    # 第一優先：嘗試使用最強的 Gemini 3.0 Pro Preview
    try:
        model_3 = genai.GenerativeModel("gemini-3-pro-preview")
        response = model_3.generate_content(prompt_text)
        return response.text, "Gemini 3.0 Pro Preview"
    except Exception as e:
        print(f"⚠️ 3.0 Preview 暫時不穩 ({e})，正在切換至 2.5 Pro 救援...")
        # 救援方案：切換至穩定的 Gemini 2.5 Pro
        try:
            model_25 = genai.GenerativeModel("gemini-2.5-pro")
            response = model_25.generate_content(prompt_text)
            return response.text, "Gemini 2.5 Pro (救援模式)"
        except Exception as e2:
            return f"分析失敗，系統暫時無法回應。錯誤訊息：{e2}", "Error"

# --- 生成 HTML 內容 ---
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>個人美股戰情室</title>
    <style>
        /* 全域設定 */
        body {{ 
            font-family: "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            line-height: 1.8; 
            font-size: 16px; 
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
            font-size: 28px; 
            font-weight: bold;
        }}

        /* 時間 */
        .timestamp {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 30px; }}

        /* 卡片區塊 */
        .card {{ 
            background: white; 
            padding: 30px; 
            margin-bottom: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        }}

        /* 卡片標題 */
        h2 {{ 
            color: #d32f2f; 
            margin-top: 0; 
            border-left: 5px solid #003366; 
            padding-left: 15px; 
            font-size: 22px; 
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        /* 模型標籤 (顯示在每個卡片右上角) */
        .model-badge {{
            font-size: 12px;
            background: #eee;
            color: #666;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: normal;
        }}

        /* 內文標題 */
        h3 {{
            color: #2c3e50;
            font-size: 18px; 
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        /* 內文 */
        .content-body {{
            font-size: 16px; 
            text-align: justify; 
        }}
        
        strong {{ color: #000; font-weight: 700; background-color: #fff3cd; padding: 0 4px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
    <h1>📈 個人美股戰情室</h1>
    <p class="timestamp">更新時間：{tw_time} (UTC+8)</p>
"""

print("🚀 開始執行排程分析...")

for index, item in enumerate(prompts):
    print(f"[{index+1}/{len(prompts)}] 分析項目：{item['title']}...")
    
    # 呼叫智慧生成函數
    result_text, used_model = smart_generate(item['query'])
    
    # 格式優化
    result_text = result_text.replace("### ", "<h3>").replace("###", "</h3>")
    result_text = result_text.replace("**", "<strong>").replace("* ", "<li>").replace("\n", "<br>")
    
    html_content += f"""
    <div class="card">
        <h2>
            {item['title']}
            <span class="model-badge">{used_model}</span>
        </h2>
        <div class="content-body">{result_text}</div>
    </div>
    """
    
    # 冷卻時間
    if index < len(prompts) - 1:
        print("⏳ 等待 35 秒...")
        time.sleep(35)

html_content += """
    <footer style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 14px;">
        Automated by GitHub Actions | Powered by Google Gemini
    </footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🎉 報告生成完畢！")
