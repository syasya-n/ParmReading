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
from io import BytesIO
import os
from PIL import Image
import traceback
import parmdatabase as pdb
from flask import Flask, render_template, request, redirect, url_for, abort
from pathlib import Path
import merge
import settings

app = Flask(__name__)

line_bot_api = LineBotApi(settings.YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.YOUR_CHANNEL_SECRET)

question_list = ["物事を決断するときは？",
                 "自分のタイプは？",
                 "インドア派？アウトドア派？",
                 "人付き合いは？"]

answer_list = [["自分で決めることが多い", "他人と相談することが多い"],
               ["文系", "理系", "芸術系", "体育系"],
               ["インドア派", "アウトドア派"],
               ["広く浅く", "狭く深く", "他人とは関わらない"]]


def start_question(event, *initial_message):
    question_text = question_list[0]
    actions = [PostbackAction(
        label=f"{ans}", data=f"{ans}")for ans in answer_list[0]]
    buttons_template = ButtonsTemplate(
        title='質問その1', text=question_text, actions=actions
    )
    if len(initial_message) == 0:
        line_bot_api.reply_message(
            event.reply_token, TemplateSendMessage(
                alt_text='Buttons alt text', template=buttons_template))
    else:
        line_bot_api.reply_message(
            event.reply_token, [TextSendMessage(text=initial_message[0]), TemplateSendMessage(
                alt_text='Buttons alt text', template=buttons_template)])


@ app.route("/callback", methods=['POST'])
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


@ app.route('/answer_merge/<int:num>')
def answer(num):
    # 選択肢
    answer_list_show = answer_list[num-1]
    # 選択肢の総数
    option_number = len(answer_list[num-1])
    return render_template('answer_merge.html',
                           option_number=option_number, question_list=question_list, answer_list_show=answer_list_show, num=num, question_total=len(question_list))


@ handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mes = event.message.text
    if mes == "開始":
        messages = TextSendMessage(
            text='まずは手相の画像をお送りください。以下3点ご注意ください。\n\n①右手を撮影ください。\n\n②手のひら全てが画角にギリギリ収まるようにしてください。\n\n③模様のない背景で写真をお撮りください。')

    elif mes == "もう1回アンケートを答え直す":
        start_question(event,)
    else:
        messages = TextSendMessage(text='「開始」と入力をお願いします')

    line_bot_api.reply_message(
        event.reply_token, messages)


@ handler.add(PostbackEvent)
def handle_postback(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    mes = event.postback.data

    for reply_index, answer in enumerate(answer_list, 1):
        if mes in answer:
            # DBの項目をupdateする
            answer_number = answer.index(mes) + 1
            apply_column = f'answer{reply_index}'
            pdb.update_info(profile.user_id,
                            apply_column, answer_number)

            # 最後の問題に回答し、答えがDBに格納済
            if mes in answer_list[-1]:
                messages = TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='質問へのご回答ありがとうございました！',
                        text='次のアクションをお選びください',
                        actions=[
                            MessageAction(
                                label='アンケートをやり直す',
                                text='もう1回アンケートを答え直す'
                            ),
                            URIAction(
                                label='手相サイトへ移動',
                                uri='https://app-parmreading.herokuapp.com/merge/1'
                            )
                        ]
                    )
                )
                merge.merge_parm()
            else:
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

        file_path = f'static/img/original/{file_name}.jpg'
        with open(file_path, 'wb') as fd:
            for chunk in image_bin:
                fd.write(chunk)

        new_dir_name = 'static/img/resized'

        img = Image.open(file_path)
        img_resize = img.resize((400, 500))
        img_resize.save(os.path.join(new_dir_name, f'{file_name}.jpg'))

        initial_message = f'投稿ありがとうございます。\nこれから{len(question_list)}問のアンケートに答えていただきます。'
        start_question(event, initial_message)

    except:
        # エラー時のメッセージ
        text = "エラーです。お手数ですがもう一度画像を送ってください。"
        t = traceback.format_exc()
        print(t)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)
        )


@ handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    pdb.insert_info(profile.user_id)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


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
