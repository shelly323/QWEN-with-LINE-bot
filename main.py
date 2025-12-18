from flask import Flask, request, abort
from QWEN import image_segestion, aigeneration, image_edit
from encode import encode_file
import json
import os

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    MessagingApiBlob,
    ShowLoadingAnimationRequest,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
)

app = Flask(__name__)

# 全域設定檔
secret = os.getenv('ChannelSecret', None)
token = os.getenv('ChannelAccessToken', None)

configuration = Configuration(access_token=token)
handler = WebhookHandler(secret)
user_status = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text
    if text in ['一鍵修圖', '修圖建議', 'AI圖片辨識']:
        user_status[user_id] = text
        
        # 修正：這裡傳入 configuration
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"請上傳圖片")]
                )
            )

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_message(event):
    user_id = event.source.user_id

    if user_id in user_status:
        current = user_status[user_id]
        message_id = event.message.id  

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.show_loading_animation(ShowLoadingAnimationRequest(
                    chatId=user_id, loadingSeconds=20))
            line_bot_blob_api = MessagingApiBlob(api_client)

            # 下載圖片
            message_content = line_bot_blob_api.get_message_content(message_id)
            file_path = f"{message_id}.jpg"
            
            with open(file_path, 'wb') as f:
                f.write(message_content)
            
            # 轉碼一次就好
            base64_img = encode_file(file_path)
            
            reply_messages = []
                
            if current == '一鍵修圖':
                result_url = image_edit(base64_img)
                if result_url:
                    reply_messages = [ImageMessage(originalContentUrl=result_url, previewImageUrl=result_url)]
                else:
                    reply_messages = [TextMessage(text="修圖失敗，請稍後再試。")]
                        
            elif current == '修圖建議':
                suggestion = image_segestion(base64_img)
                reply_messages = [TextMessage(text=suggestion)]
                    
            elif current == 'AI圖片辨識':
                result = aigeneration(base64_img)
                reply_messages = [TextMessage(text=result)]
                
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=reply_messages
                )                
            )
                
            del user_status[user_id]

            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    app.run(port=5000)