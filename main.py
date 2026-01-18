import os
import google.generativeai as genai
from datetime import datetime
import pytz
import time
import re

# 設定 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 取得台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# --- 您的關注清單 (已更新為最新詳細版) ---
# 為了讓表格正常顯示，我們稍後會自動在每個指令後加入「請用 HTML 輸出」的系統提示
prompts = [
    {
        "title": "🚀 LUNR (Intuitive Machines) 每日追蹤",
        "query": "請提供美股代碼 LUNR (Intuitive Machines) 的完整每日快訊，需以台灣時間最新的資訊為主（含盤後數據）。內容需包含：1. 股價動態（收盤與盤後）與 KD/MACD 技術指標分析；2. 業務項目進度（特別關注 IM-2 發射時程、NSNS 合約執行、與 X-energy 的核能合作）；3. 指數影響分析與分析師評級/預估；4. 相關太空產業重大消息，並附上「阿提密斯計劃 (Artemis Program)」的每日進度表與未來規劃時間軸。"
    },
    {
        "title": "🚀 FLY (Firefly Aerospace) 每日追蹤",
        "query": "請提供美股 FLY (Firefly Aerospace) 的完整每日快訊，需以台灣時間最新的資訊為主。內容需包含：1. 股價動態與 KD/MACD 技術指標分析；2. 按業務項目（Alpha 火箭「包含 Flight 7 具體進度」、Blue Ghost、與 NOC 合作的 Eclipse、Elytra 等）分類說明的最新消息與里程碑，並追蹤法律訴訟進度；3. 指數影響分析與分析師評級/預估；4. 美國航天產業重大消息（如 SpaceX IPO、Rocket Lab 等同業動態）。"
    },
    {
        "title": "🌕 美國三大戰略計劃整合快訊",
        "query": "請提供【美國三大戰略計劃：金穹 (Golden Dome)、雅努斯 (Janus)、阿提密斯 (Artemis)】的每日進度整合快訊。內容需以**表格方式**呈現，**表格結構請務必採『先分類業務項目/任務代號，再列出供應商』的格式**。關鍵要求：阿提密斯計劃 (Artemis) 必須包含 Artemis II, III, CLPS (IM-2), LTV, Gateway, FSP, DRACO 等項目，並在供應商欄位**明確標註美股代碼** (如 $LUNR, $LMT, $NOC, $BWXT)。"
    },
    {
        "title": "⚛️ 核能產業 (OKLO, BWXT, SMR, LEU, NNE) 每日快訊",
        "query": "請提供美股代碼 OKLO, BWXT, SMR, LEU, NNE 的完整每日快訊，需以台灣時間最新的資訊為主（含盤後數據）。內容需包含：1. 股價動態（收盤與盤後）與 KD/MACD 技術指標分析。2. **分析師評級與目標價分析**（需詳列最新機構目標價、評級變動，並**特別針對 LEU 進行估值分析**）。3. 按業務項目分別介紹各進度及消息。4. 美國核能產業重大消息（涵蓋其他相關核能供應鏈與同業）。"
    }
]

# --- 智慧生成函數 (含 HTML 格式優化) ---
def smart_generate(prompt_text):
    # 強制要求 AI 使用 HTML 格式輸出，這樣表格才會漂亮
    system_instruction = "\n\n(重要技術要求：請直接以 HTML 程式碼格式輸出回答。不要使用 Markdown。請使用 <table> 製作表格，使用 <b> 標示重點，使用 <ul><li> 製作清單。請確保 HTML 語法正確，不需要 <html> 或 <body> 標籤，只要內容即可。)"
    full_query = prompt_text + system_instruction

    # 優先嘗試 Gemini 3.0 Pro Preview
    try:
        model_3 = genai.GenerativeModel("gemini-3-pro-preview")
        response = model_3.generate_content(full_query)
        return clean_html(response.text), "Gemini 3.0 Pro Preview"
    except Exception as e:
        print(f"⚠️ 3.0 Preview 暫時不穩 ({e})，切換至 2.5 Pro 救援...")
        # 救援：切換至 Gemini 2.5 Pro
        try:
            model_25 = genai.GenerativeModel("gemini-2.5-pro")
            response = model_25.generate_content(full_query)
            return clean_html(response.text), "Gemini 2.5 Pro (救援模式)"
        except Exception as e2:
            return f"<p style='color:red'>分析失敗：{e2}</p>", "Error"

def clean_html(text):
    # 清除 AI 可能會多加的 ```html 標籤
    text = re.sub(r"^```html", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```", "", text, flags=re.MULTILINE)
    return text.strip()

# --- 生成 HTML 網頁結構 ---
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
            line-height: 1.6; 
            font-size: 16px; 
            color: #333;
            max-width: 950px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f4f7f6; 
        }}
        h1 {{ text-align: center; color: #003366; border-bottom: 3px solid #d32f2f; padding-bottom: 15px; margin-bottom: 10px; }}
        .timestamp {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 30px; }}
        
        /* 卡片設計 */
        .card {{ 
            background: white; 
            padding: 30px; 
            margin-bottom: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        }}
        
        /* 標題設計 */
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
        .model-badge {{ font-size: 12px; background: #eee; color: #666; padding: 2px 8px; border-radius: 10px; font-weight: normal; }}

        /* --- 針對您要求的表格與排版優化 --- */
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 15px; }}
        th {{ background-color: #003366; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
        
        b, strong {{ color: #d32f2f; background-color: #fff3cd; padding: 0 2px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 6px; }}
    </style>
</head>
<body>
    <h1>📈 個人美股戰情室</h1>
    <p class="timestamp">更新時間：{tw_time} (UTC+8)</p>
"""

print("🚀 開始執行高階分析 (HTML 模式)...")

for index, item in enumerate(prompts):
    print(f"[{index+1}/{len(prompts)}] 分析項目：{item['title']}...")
    
    # 呼叫智慧生成
    result_text, used_model = smart_generate(item['query'])
    
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
