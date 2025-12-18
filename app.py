from flask import Flask, request, abort
from QWEN import image_segestion, aigeneration, image_edit
from encode import encode_file

from linebot.v3 import(
    WebhookHandler
)
from linebot.v3.exceptions import(
    InvalidSignatureError
)
from linebot.v3.messaging import(
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
)
from linebot.v3.webhooks import(
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

line_bot_api = Configuration(access_token='b1049Uc4dvnP96EuoKxzsqhK+4M/kq03nhMhiAI26vOAwohRA6ND4rXNCLkWMNq5NYY0sn2CWAxGS1ORkr/MEX+QlXYGANpT/jsngDVSQIEn1B5sWXcma8wmtX5zPJcf9TJOAqlWbz0H9ehNzT4x4QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5c1bbdc4837fad34a73fa623d40a0dd1')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    with ApiClient(line_bot_api) as api_client:
        line_bot_api = MessagingApi(api_client)

        if text == '一鍵修圖':
            path = encode_file(event[0].message.contentProvider.originalContentUrl)
            url = image_edit(path)
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[
                        ImageMessage(originalContentUrl=url, previewImageUrl=url)
                    ]
                )
            )
        elif text == '修圖建議':
            path = encode_file(event[0].message.contentProvider.originalContentUrl)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[
                        TextMessage(text=image_segestion(path))
                    ]
                )
            )
        elif text == 'AI圖片辨識':
            path = encode_file(event[0].message.contentProvider.originalContentUrl)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[
                        TextMessage(text=aigeneration(path))
                    ]
                )
            )
if __name__ == "__main__":
    app.run()