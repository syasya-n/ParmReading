from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    QuickReply, QuickReplyButton,
    ImageSendMessage, RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from msrest.authentication import CognitiveServicesCredentials
import Richmenu
from io import BytesIO
import os
import cv2
import traceback
import parmdatabase as pdb
from flask import Flask, render_template, request, redirect, url_for, abort
from pathlib import Path

app = Flask(__name__)

# YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
# YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')

line_bot_api = LineBotApi(
    'ELoyED6pv2ne6UvwBemtYGyQuooplUsTGvJz2sEuHj1heicnKgMueaKI1BHrG1vA0gqDxs1rZIvKw6EpOxyu9T78CkxEX25nl4fuwje07x4Tu1hKWs1FQYTahjp+nfJaNup1o5FVuaBUX6ryv6YeGQdB04t89/1O/w1cDnyilFU')
handler = WebhookHandler('f0dc931487320663e2ae141d53b37213')

answer_list = [["自分で決めることが多い", "他人と相談することが多い"],
               ["文系", "理系", "芸術系", "体育系"],
               ["インドア派", "アウトドア派"],
               ["広く浅く", "狭く深く", "他人とは関わらない"]]

question_list = ["物事を決断するときは？",
                 "自分のタイプは？",
                 "インドア派？アウトドア派？",
                 "人付き合いは？"]


def start_question(event):
    question_text = question_list[0]
    actions = [PostbackAction(
        label=f"{ans}", data=f"{ans}")for ans in answer_list[0]]
    buttons_template = ButtonsTemplate(
        title='質問その1', text=question_text, actions=actions
    )
    messages = TemplateSendMessage(
        alt_text='Buttons alt text', template=buttons_template)

    line_bot_api.reply_message(
        event.reply_token, messages)


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


@app.route('/detail/<int:id>')
def detail(id):
    return render_template('detail.html', id=id)


@app.route('/answer_merge/<int:num>')
def answer(num):
    parms = pdb.ParmInfo.query.all()
    # 選択肢
    answer_list_show = answer_list[num-1]
    # 選択肢の総数
    option_number = len(answer_list[num-1])
    user_answer_list = [
        (i, getattr(parm, f'answer{num}'))for i, parm in enumerate(parms, 1)]
    print(user_answer_list)
    return render_template('answer_merge.html', user_answer_list=user_answer_list,
                           option_number=option_number, question_list=question_list, answer_list_show=answer_list_show, num=num, question_total=len(question_list))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mes = event.message.text
    if mes == "開始":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='ご利用ありがとうございます。まずは手相の画像を送ってください'))

    elif mes == "もう1回アンケートを答え直す":
        start_question()
    else:
        messages = TextSendMessage(text='「開始」と入力をお願いします')

    line_bot_api.reply_message(
        event.reply_token, messages)


@handler.add(PostbackEvent)
def handle_postback(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    mes = event.postback.data

    # 最後の問題に回答し、答えがDBに格納済
    if mes in answer_list[-1] and pdb.is_complete_answer(profile.user_id):
        uri_path = f'https://0d8b336f9d52.ngrok.io/{profile.user_id}'
        answer_number = answer_list[-1].index(mes) + 1
        apply_column = f'answer{answer_list.len - 1}'
        pdb.update_info(profile.user_id,
                        apply_column, answer_number)
        messages = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='質問へのご回答ありがとうございました！',
                text='次のアクションをお選びください',
                actions=[
                    MessageAction(
                        label='アンケートを答え直す',
                        text="もう1回アンケートを答え直す"
                    ),
                    URIAction(
                        label='手相データベースサイトへ移動',
                        uri=uri_path
                    )
                ]
            )
        )
    else:
        for reply_index, answer in enumerate(answer_list, 1):
            if mes in answer:
                # DBの項目をupdateする
                answer_number = answer.index(mes) + 1
                apply_column = f'answer{reply_index}'
                pdb.update_info(profile.user_id,
                                apply_column, answer_number)

                question_text = question_list[reply_index]
                actions = [PostbackAction(
                    label=f"{ans}", data=f"{ans}")for ans in answer_list[reply_index]]
                buttons_template = ButtonsTemplate(
                    title=f'質問その{reply_index + 1}！', text=question_text, actions=actions
                )
                messages = TemplateSendMessage(
                    alt_text='Buttons alt text', template=buttons_template)
    line_bot_api.reply_message(
        event.reply_token, messages)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    file_name = pdb.get_db_id(profile.user_id)
    print(file_name)
    try:
        # メッセージIDを受け取る
        message_id = event.message.id
        # メッセージIDに含まれるmessage_contentを抽出する
        message_content = line_bot_api.get_message_content(message_id)

        # contentの画像データをバイナリデータとして扱えるようにする
        image_bin = BytesIO(message_content.content)

        file_path = f'static/img/{file_name}.jpg'
        with open(file_path, 'wb') as fd:
            for chunk in image_bin:
                fd.write(chunk)

        start_question(event)

        # img.save(f'/static/img/{profile.user_id}.png', "PNG")

        # save_file_path = f'/static/img/{profile.user_id}.png'

        # cv2.imwrite(save_file_path, image)

    #         # Detect from streamで顔検出
    #         detected_faces = face_client.face.detect_with_stream(image)
    #         print(detected_faces)
    #         # 検出結果に応じて処理を分ける
    #         if detected_faces != []:
    #            # 顔検出ができたら顔認証を行う
    #             valified = face_client.face.verify_face_to_person(
    #                 face_id=detected_faces[0].face_id,
    #                 person_group_id=PERSON_GROUP_ID,
    #                 person_id=PERSON_ID_ZAKOSHI
    #             )
    #             # 認証結果に応じて処理を変える
    #             if valified:
    #                 if valified.is_identical:
    #                     # 顔認証が一致した場合（スコアもつけて返す）
    #                     text = 'この写真はザコシショウです(score:{:.3f})'.format(
    #                         valified.confidence)
    #                 else:
    #                     # 顔認証が一致した場合（スコアもつけて返す）
    #                     text = 'この写真はザコシショウではありません(score:{:.3f})'.format(
    #                         valified.confidence)
    #             else:
    #                 text = '識別できませんでした。'
    #         else:
    #             # 検出されない場合のメッセージ
    #             text = "no faces detected"
    except:
        # エラー時のメッセージ
        text = "error"
        t = traceback.format_exc()
        print(t)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text)
    )

# 友達登録された時の挙動(ここで新規テーブル作ると良い)


@ handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    pdb.insert_info(profile.user_id)
    Richmenu.createRichmenu()
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@ handler.add(UnfollowEvent)
def handle_unfollow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    usrname = 'user_' + profile.display_name
    app.logger.info("Got Unfollow event")


@ handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@ handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


if __name__ == "__main__":
    app.run()
