import os
import google.generativeai as genai
from datetime import datetime
import pytz
import time

# 設定 API Key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 取得台灣時間
tw_time = datetime.now(pytz.timezone('Asia/Taipei')).strftime("%Y-%m-%d %H:%M")

# --- 1. 自動偵測可用模型 ---
print("正在偵測可用模型...")
valid_model = None
model_name_used = "未知"

# 我們想嘗試的優先順序 (從最新的 Pro 開始嘗試)
candidates = [
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "gemini-1.5-pro-latest",
    "gemini-pro",         # 1.0 Pro
    "gemini-1.5-flash"    # 最後保底
]

available_list = []
try:
    # 列出帳號實際可用的所有模型
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_list.append(m.name)
except Exception as e:
    available_list = [f"無法列出模型: {str(e)}"]

# 測試哪個模型能用
for candidate in candidates:
    try:
        print(f"測試模型: {candidate}...")
        test_model = genai.GenerativeModel(candidate)
        # 試發一個極短的請求確認能通
        test_model.generate_content("Hi")
        valid_model = test_model
        model_name_used = candidate
        print(f"✅ 成功鎖定模型: {candidate}")
        break
    except Exception as e:
        print(f"❌ {candidate} 測試失敗: {e}")

# 如果都失敗，強制使用最後一個設定，並在網頁顯示錯誤
if valid_model is None:
    print("⚠️ 所有模型測試失敗，將使用預設設定嘗試...")
    valid_model = genai.GenerativeModel('gemini-1.5-pro')

# --- 2. 您的關注清單 ---
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

# --- 3. 生成 HTML 內容 ---
html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>個人美股戰情室 ({tw_time})</title>
    <style>
        body {{ font-family: "Microsoft JhengHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f0f2f5; color: #1c1e21; }}
        h1 {{ text-align: center; color: #003366; border-bottom: 3px solid #d32f2f; padding-bottom: 15px; margin-bottom: 10px; }}
        .timestamp {{ text-align: center; color: #606770; font-size: 0.9em; margin-bottom: 20px; }}
        .model-info {{ text-align: center; font-size: 0.8em; color: #fff; background-color: #2c3e50; padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 30px; }}
        .card {{ background: white; padding: 30px; margin-bottom: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        h2 {{ color: #d32f2f; margin-top: 0; border-left: 5px solid #003366; padding-left: 10px; }}
        strong {{ color: #000; font-weight: 700; background-color: #fff3cd; padding: 0 4px; }}
        li {{ margin-bottom: 8px; }}
        .debug {{ background: #eee; padding: 10px; margin-top: 50px; font-size: 0.8em; color: #555; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>📈 個人美股戰情室</h1>
    <div style="text-align:center;">
        <p class="timestamp">更新時間：{tw_time} (UTC+8)</p>
        <span class="model-info">使用模型：{model_name_used}</span>
    </div>
"""

print("🚀 開始生成報告...")

for index, item in enumerate(prompts):
    print(f"[{index+1}/{len(prompts)}] 正在分析：{item['title']}...")
    try:
        response = valid_model.generate_content(item['query'])
        
        text_content = response.text
        text_content = text_content.replace("### ", "<h3>").replace("###", "</h3>")
        text_content = text_content.replace("**", "<strong>").replace("* ", "<li>").replace("\n", "<br>")
        
        html_content += f"""
        <div class="card">
            <h2>{item['title']}</h2>
            <div>{text_content}</div>
        </div>
        """
        print("   ✅ 分析完成")
        
    except Exception as e:
        print(f"   ❌ 發生錯誤：{str(e)}")
        html_content += f"<div class='card'><h2>{item['title']}</h2><p style='color:red'>分析失敗：{str(e)}</p></div>"

    # 冷卻時間 (避免 429 錯誤)
    if index < len(prompts) - 1:
        print("⏳ 冷卻 35 秒...")
        time.sleep(35)

# 加入除錯資訊 (列出所有可用模型，方便查修)
html_content += f"""
    <div class="debug">
        <h3>🔍 系統診斷資訊</h3>
        <p><strong>帳號可用模型列表：</strong><br>{'<br>'.join(available_list)}</p>
    </div>
    <footer style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #777; font-size: 0.8em;">
        Generated by Google Gemini | Automated via GitHub Actions
    </footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("🎉 報告生成完畢！")
