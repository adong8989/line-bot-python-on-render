import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage
from member_db import init_db, is_member, apply_member
from analyze_image import ocr_analyze
from analyze_text import text_analyze

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
init_db()

common_quick = [
    {"type":"action","action":{"type":"message","label":"📷 給圖分析","text":"我要圖片分析"}},
    {"type":"action","action":{"type":"message","label":"🔤 文字分析","text":"我要文字分析"}},
    {"type":"action","action":{"type":"message","label":"🔓 開通按我","text":"我要開通"}}
]

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get("X-Line-Signature", "")
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    uid, msg = event.source.user_id, event.message.text.strip()
    if msg == "我要開通":
        apply_member(uid)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="✅ 已收到申請，請等待審核！"))
        return

    if msg in ("我要圖片分析", "我要文字分析") and not is_member(uid):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="❌ 尚未開通會員權限，請點「開通按我」申請。",
                              quick_reply={"items": common_quick}))
        return

    if msg == "我要圖片分析":
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="📷 請上傳圖片，我會為你分析。", quick_reply={"items": common_quick}))
        return

    if msg == "我要文字分析":
        guide = ("🔤 請依格式輸入：
"
                 "今日RTP：XX%
今日下注：NNNN
"
                 "30日RTP：XX%
30日下注：NNNN
"
                 "未開轉數：N
前一轉轉數：N")
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=guide, quick_reply={"items": common_quick}))
        return

    if is_member(uid) and msg.startswith("今日RTP"):
        result = text_analyze(msg)
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text=result, quick_reply={"items": common_quick}))
        return

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    uid = event.source.user_id
    if not is_member(uid):
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="❌ 尚未開通會員，無法使用圖片分析。"))
        return

    msg_id = event.message.id
    content = line_bot_api.get_message_content(msg_id)
    with open("tmp.jpg", "wb") as f:
        for chunk in content.iter_content():
            f.write(chunk)
    result = ocr_analyze("tmp.jpg")
    line_bot_api.reply_message(event.reply_token,
        TextSendMessage(text=result, quick_reply={"items": common_quick}))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))