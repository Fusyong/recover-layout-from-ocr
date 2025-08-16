"""使用PPOCRV5"""
import json
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

img_url = "img_1_dsk.jpg"
result = engine(img_url)
print(result)

result.vis("vis_result.jpg")
print(result.to_markdown())

with open("rapidocr_result.json", "w", encoding="utf-8") as f:
    json.dump(result.to_json(), f, ensure_ascii=False, indent=2)
