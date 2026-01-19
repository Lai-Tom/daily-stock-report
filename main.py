import os
import google.generativeai as genai
from datetime import datetime
import pytz
import time
import re
import traceback

# 設定 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 取得台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# --- 您的關注清單 ---
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

# --- V3.4 絕對保底邏輯 ---
def smart_generate(prompt_text):
    # 強制只使用 gemini-1.5-flash
    # 這個模型每天有 1500 次免費額度，幾乎不可能爆
    target_model = "gemini-1.5-flash"
    
    system_instruction = "\n\n(Technical Requirement: Output strictly in HTML format. Use <table> for data tables. Use <b> for headers. Do not use Markdown code blocks.)"
    full_query = prompt_text + system_instruction

    try:
        print(f"   正在使用高額度模型：{target_model}...")
        model = genai.GenerativeModel(target_model)
        response = model.generate_content(full_query)
        
        if not response.parts:
            return "<p>AI 回傳空值</p>", "No Data"
            
        return clean_html(response.text), "Gemini 1.5 Flash (V3.4 Stable)"
    except Exception as e:
        print(f"   ⚠️ 失敗：{e}")
        return f"<p style='color:red; background:#fee; padding:10px;'>分析失敗。<br>錯誤訊息：{e}</p>", "Error"

def clean_html(text):
    text = re.sub(r"^```html", "", text, flags=re.MULTILINE)
    text = re.sub(r"^```", "", text, flags=re.MULTILINE)
    return text.strip()

# --- 主程式 ---
html_content = ""

try:
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>個人美股戰情室 V3.4</title>
        <style>
            body {{ font-family: "Microsoft JhengHei", sans-serif; line-height: 1.6; max-width: 950px; margin: 0 auto; padding: 20px; background-color: #f4f7f6; color: #333; }}
            h1 {{ text-align: center; color: #003366; border-bottom: 3px solid #d32f2f; padding-bottom: 15px; }}
            .timestamp {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 30px; }}
            .card {{ background: white; padding: 30px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            h2 {{ color: #d32f2f; border-left: 5px solid #003366; padding-left: 15px; display: flex; justify-content: space-between; align-items: center; }}
            .model-badge {{ font-size: 12px; background: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 10px; font-weight: normal; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 15px; }}
            th {{ background-color: #003366; color: white; padding: 10px; text-align: left; }}
            td {{ border: 1px solid #ddd; padding: 8px; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            b {{ color: #d32f2f; background-color: #fff3cd; }}
        </style>
    </head>
    <body>
        <h1>📈 個人美股戰情室 (V3.4 穩定版)</h1>
        <p class="timestamp">更新時間：{tw_time} (UTC+8)</p>
        <p style="text-align:center; color:#2e7d32; font-size:12px;">✅ 目前使用高額度穩定模型 (1.5 Flash) 以確保連線</p>
    """

    print("🚀 開始執行 V3.4 分析 (強制使用 1.5 Flash)...")

    for index, item in enumerate(prompts):
        print(f"[{index+1}/{len(prompts)}] 分析項目：{item['title']}...")
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
        
        # 即使是 Flash，我們還是稍微等一下比較保險
        if index < len(prompts) - 1:
            print("⏳ 等待 10 秒...")
            time.sleep(10)

except Exception as e:
    print(f"❌ 嚴重錯誤：{traceback.format_exc()}")
    html_content += f"<div class='card'><h2>系統發生嚴重錯誤</h2><pre>{traceback.format_exc()}</pre></div>"

finally:
    html_content += """
        <footer style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 14px;">
            Automated by GitHub Actions | V3.4 Stable
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("🎉 報告寫入完成 (V3.4)")
