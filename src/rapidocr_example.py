"""使用PPOCRV5"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rapidocr_example.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

engine = RapidOCR(
    params={
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Det.lang_type": LangDet.CH,
        "Det.model_type": ModelType.MOBILE,
        "Det.ocr_version": OCRVersion.PPOCRV4,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Rec.lang_type": LangRec.CH,
        "Rec.model_type": ModelType.MOBILE, # MOBILE, SERVER 慢
        "Rec.ocr_version": OCRVersion.PPOCRV5,
    }
)

def ocr_image(input_path: str, output_dir: str="") -> Any:
    """OCR单个图像文件"""
    input_path_obj = Path(input_path)
    
    try:
        # 检查输入文件是否存在
        if not input_path_obj.exists():
            logger.error(f"输入文件不存在: {input_path_obj}")
            return False
        
        # 支持的图像格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        if input_path_obj.suffix.lower() not in image_extensions:
            logger.error(f"不支持的图像格式: {input_path_obj.suffix}")
            return False
        
        # 确定输出目录
        if not output_dir:
            output_dir_obj = input_path_obj.parent
        else:
            output_dir_obj = Path(output_dir)
            output_dir_obj.mkdir(parents=True, exist_ok=True)
        
        # 生成输出文件路径
        base_name = input_path_obj.stem
        vis_path = output_dir_obj / f"{base_name}.vis.jpg"
        json_path = output_dir_obj / f"{base_name}.json"
        
        logger.info(f"处理图像: {input_path_obj}")
        
        # 执行OCR
        result = engine(str(input_path_obj),
        # use_det=True,
        # use_cls=True, # 发生文本行丢失时可关闭
        # use_rec=True,
        # text_score= 0.5,
        # min_height= 20,
        # min_side_len= 30,
        # width_height_ratio= 8,
        # max_side_len= 2000,
        # return_word_box= False,
        # return_single_char_box= False,
        # font_path= None
        )
        
        # 保存可视化结果
        # 无法处理中文路径
        result.vis(str(vis_path))
    
        with open(json_path,
        "w", encoding="utf-8") as f:
            json.dump(result.to_json(), f, ensure_ascii=False, indent=2) # type: ignore
        
        return result
        
    except Exception as e:
        logger.error(f"处理文件 {input_path} 时出错: {e}")
        return False

def ocr_images(input_dir: str, output_dir: str="") -> None:
    """OCR文件夹中的所有图像文件"""
    try:
        # 检查输入文件夹是否存在
        input_dir_obj = Path(input_dir)
        if not input_dir_obj.exists():
            logger.error(f"输入文件夹不存在: {input_dir}")
            return
        
        # 如果输出目录为空，则使用输入目录
        if not output_dir:
            output_dir_obj = input_dir_obj
        else:
            output_dir_obj = Path(output_dir)
            output_dir_obj.mkdir(parents=True, exist_ok=True)
    
        # 处理每个图像文件，支持多种后缀
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_dir_obj.rglob(f"*{ext}"))
        image_files = list(set(image_files))  # 去重

        total_files = len(image_files)
        if total_files == 0:
            logger.info(f"未找到支持的图像文件（{image_extensions}）")
            return

        logger.info(f"共找到 {total_files} 个图像文件，开始处理……")

        for idx, input_path in enumerate(sorted(image_files), 1):
            print(f"[{idx}/{total_files}] processing: {input_path}")
            
            try:
                # 生成输出文件路径：
                # 保持完整的相对路径结构
                relative_path = input_path.relative_to(input_dir_obj)
                output_subdir = output_dir_obj / relative_path.parent
                output_subdir.mkdir(parents=True, exist_ok=True)
                
                # 调用ocr_image处理单个文件
                print(str(input_path))
                ocr_image(str(input_path), str(output_subdir))
                
            except Exception as e:
                logger.error(f"处理文件 {input_path} 时出错: {e}")

        logger.info(f"批量OCR处理完成！")
        
    except Exception as e:
        logger.error(f"批量处理时出错: {e}")

if __name__ == "__main__":
    # 
    # 单张图片ocr
    # 
    # IMGURL = "tests/assets/img_0_dsk.preprocessed.jpg"
    # r= ocr_image(IMGURL)
    # print(r)

    # 
    # 多张图片ocr
    # 
    ocr_images('E:/语文出版社/2025/人教教师教学用书语文一年级上册-集团质检/img_preprocessed/')
    