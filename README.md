# Parmreading

## アプリケーション概要

---

手相占いは本当に信頼性があるのか検証目的でユーザに Line から手相投稿とアンケートへの回答をしてもらう。  
プログラム内部で回答別に手相を合成し、Web 上に表示する。

## 利用方法

---

下記 QR コードを読み取って、Line アプリの友達になる。  
![QRコード](https://qr-official.line.me/sid/L/685nmdcj.png)

## Web サイト URL

---

デプロイしだい記入。

## 実装機能の説明

---

1. Line アプリ機能

   - 手相の画像を投稿する
   - 性格や日々の行動パターンを問う簡単なアンケートが通知される
   - 表示された選択肢のボタンをタップして回答
   - 全てのアンケートに回答すると、最後に以下選択肢が表示
   - [実際のアプリ画面](https://drive.google.com/file/d/17z3FXQMsyGAbXqGl2uSdRALQW5ES782f/view?usp=sharing)

2. 投稿手相の合成

   - 1.Line アプリでユーザがアンケート全問に回答後に、バックサイドで処理が行われる。
   - アンケートで同じ選択肢を選んだ人同士の手相画像を合成。画像をサーバに保存する。

3. 画像の合成結果を Web 上に表示

   - プルダウンから結果を確認したいアンケートの質問を選択。左部にアンケートの選択肢がタブで表示。
     [![Image from Gyazo](https://i.gyazo.com/ec0cdef83bd8c3abc334781a9700ca2c.gif)](https://gyazo.com/ec0cdef83bd8c3abc334781a9700ca2c)

   - アンケート回答毎の手相の合成結果が表示。「全回答」タブを選ぶと各回答の合成画像が横並びに表示され、比較ができる
     [![Image from Gyazo](https://i.gyazo.com/a4a3e97595cf8b7e02b75d0eac117816.gif)](https://gyazo.com/a4a3e97595cf8b7e02b75d0eac117816)
