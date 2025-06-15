from flask import Flask, request, abort, send_from_directory
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

# ---------------- Flask 初始化 ----------------
app = Flask(__name__)

# ---------------- LINE Bot 設定 ----------------
CHANNEL_ACCESS_TOKEN = 'your channel access token'
CHANNEL_SECRET = 'your channel secret'

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ---------------- LINE webhook 路由 ----------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ---------------- LINE 訊息處理 ----------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("有收到 LINE 訊息")

    if event.message.text == "嗨":
        user_id = event.source.user_id
        print("收到用戶 User ID:", user_id)
        reply_text = f"你的 User ID 是：{user_id}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

# ---------------- 影片/圖片 靜態伺服 ----------------
@app.route("/video_static/<path:filename>")
def static_video_file(filename):
    return send_from_directory(
        "video_static",
        filename,
        as_attachment=True,  # 顯示下載按鈕
        mimetype="video/mp4"
    )

@app.route("/preview")
def preview():
    # 搜尋 video_static 資料夾內的 jpg/jpeg/png 檔
    for fname in os.listdir("video_static"):
        if fname.lower().endswith(('.jpg', '.jpeg', '.png')):
            return send_from_directory("video_static", fname)
    
    return "找不到預覽圖", 404


# ---------------- 啟動 Flask ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
