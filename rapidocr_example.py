"""使用PPOCRV5"""

import json
import os
import re
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR

engine = RapidOCR(
    params={
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Det.lang_type": LangDet.CH,
        "Det.model_type": ModelType.MOBILE,
        "Det.ocr_version": OCRVersion.PPOCRV4,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Rec.lang_type": LangRec.CH,
        "Rec.model_type": ModelType.MOBILE,
        "Rec.ocr_version": OCRVersion.PPOCRV5,
    }
)

def ocr_image(img_url):
    """OCR图片"""
    vis_path = re.sub(r'\.[^\.]+$', '_vis.jpg', img_url)
    json_path = re.sub(r'\.[^\.]+$', '.json', img_url)
    result = engine(img_url)
    result.vis(vis_path)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result.to_json(), f, ensure_ascii=False, indent=2)
    return result

def ocr_images(img_dir):
    """OCR图片目录"""
    if not os.path.exists(img_dir):
        print(f"图片目录不存在: {img_dir}")
        return
    for img_url in os.listdir(img_dir):
        ocr_image(os.path.join(img_dir, img_url))

if __name__ == "__main__":
    # 单张图片ocr
    # IMGURL = "img_1_dsk.jpg"
    # result = ocr_image(IMGURL)
    # print(result)
    # print(result.to_text())
    # print(result.to_markdown())

    # 多张图片ocr
    ocr_images('img_dsk')
    