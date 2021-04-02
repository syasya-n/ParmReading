from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face import FaceClient
from io import BytesIO
import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, QuickReplyButton, MessageAction, QuickReply
)

import createRichmenu

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')
YOUR_FACE_API_KEY = os.environ["YOUR_FACE_API_KEY"]
YOUR_FACE_API_ENDPOINT = os.environ["YOUR_FACE_API_ENDPOINT"]
PERSON_GROUP_ID = os.getenv('PERSON_GROUP_ID')
PERSON_ID_ZAKOSHI = os.getenv('PERSON_ID_ZAKOSHI')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

face_client = FaceClient(
    YOUR_FACE_API_ENDPOINT,
    CognitiveServicesCredentials(YOUR_FACE_API_KEY)
)


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
    send_message = event.message.text

    answer_list = [["自分で決めることが多い", "他人と相談することが多い"],
                   ["文系", "理系", "芸術系", "体育系"],
                   ["インドア派", "アウトドア派"],
                   ["広く浅く", "狭く深く", "他人とは関わらない"]]

    question_list = ["物事を決断するときは",
                     "自分のタイプは？",
                     "インドア派？アウトドア派？"
                     "人付き合いは？"]

    for answer, question in zip(answer_list, question_list):

        items = [QuickReplyButton(action=MessageAction(
            label=f"{ans}", text=f"{ans}")) for ans in answer]

        messages = TextSendMessage(text=question,
                                   quick_reply=QuickReply(items=items))

        line_bot_api.reply_message(
            event.reply_token, messages)
    # TextSendMessage(text=event.message.text))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        # メッセージIDを受け取る
        message_id = event.message.id
        # メッセージIDに含まれるmessage_contentを抽出する
        message_content = line_bot_api.get_message_content(message_id)
        # contentの画像データをバイナリデータとして扱えるようにする
        image = BytesIO(message_content.content)

        # Detect from streamで顔検出
        detected_faces = face_client.face.detect_with_stream(image)
        print(detected_faces)
        # 検出結果に応じて処理を分ける
        if detected_faces != []:
           # 顔検出ができたら顔認証を行う
            valified = face_client.face.verify_face_to_person(
                face_id=detected_faces[0].face_id,
                person_group_id=PERSON_GROUP_ID,
                person_id=PERSON_ID_ZAKOSHI
            )
            # 認証結果に応じて処理を変える
            if valified:
                if valified.is_identical:
                    # 顔認証が一致した場合（スコアもつけて返す）
                    text = 'この写真はザコシショウです(score:{:.3f})'.format(
                        valified.confidence)
                else:
                    # 顔認証が一致した場合（スコアもつけて返す）
                    text = 'この写真はザコシショウではありません(score:{:.3f})'.format(
                        valified.confidence)
            else:
                text = '識別できませんでした。'
        else:
            # 検出されない場合のメッセージ
            text = "no faces detected"
    except:
        # エラー時のメッセージ
        text = "error"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )


if __name__ == "__main__":
    app.run()
