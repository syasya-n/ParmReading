import app
from pathlib import Path
import cv2
import parmdatabase as pdb
import numpy as np

def get_img_paths(img_dir):
    """画像のパスを取得する。
    """
    IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")
    img_paths = [p for p in img_dir.iterdir() if p.suffix in IMG_EXTENSIONS]

    return img_paths

def merge_parm():
    input_dir = Path("static/img/resized")  # 画像があるディレクトリ

    # 質問総数
    question_num = len(app.question_list)
    for question_index in range(question_num):
        for answer_index in range(len(app.answer_list[question_index])):
            imgs = []
            for path in get_img_paths(input_dir):
                img = cv2.imread(str(path))
                parms = pdb.ParmInfo.query.all()

                answer = [getattr(parm, f'answer{question_index + 1}')
                          for parm in parms if parm.id == int(Path(path).stem)]
                if answer[0] == answer_index + 1:
                    # 画像を読み込む。
                    imgs.append(img)

            imgs_np = np.array(imgs)
            if imgs_np.ndim == 4:
                mean_img = imgs_np.mean(axis=0)
                cv2.imwrite(
                    f'static/img/merge/{question_index + 1}-{answer_index + 1}.jpg', mean_img)
