"""
OCR图像预处理示例脚本

从preprocess_configuration_searching.py导入方法，提供单个文件和批量文件处理功能
用户直接通过函数参数传入配置
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import cv2
import numpy as np

# 导入预处理配置搜索模块
from preprocess_configuration_searching import ImageProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('preprocess_example.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def cv_imread(file_path):
    """
    读取图像，解决中文路径问题
    """
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv_img
def cv_imwrite(img, path):
    """
    保存图像，解决中文路径问题
    """
    suffix = Path(path).suffix
    cv2.imencode(suffix, img)[1].tofile(path)

def process_image(input_path: str, output_path: str="", config: Dict[str, Any]={}) -> bool:
    """处理单个图像文件"""
    input_path_obj = Path(input_path)
    if not output_path:
        # 默认输出到输入文件的目录，文件名不变，后缀为.preprocessed.png
        output_path = str(input_path_obj.with_suffix(".preprocessed.jpg"))
    else:
        output_path = str(Path(output_path))
    
    try:
        # 检查输入文件是否存在
        if not input_path_obj.exists():
            logger.error(f"输入文件不存在: {input_path_obj}")
            return False
        
        # 支持的图像格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        if Path(input_path_obj).suffix.lower() not in image_extensions:
            logger.error(f"不支持的图像格式: {Path(input_path_obj).suffix}")
            return False
        
        # 创建输出目录
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建图像处理器
        processor = ImageProcessor()
        
        # 读取原始图像
        print(input_path_obj)
        original_image = cv_imread(str(input_path_obj))
        if original_image is None:
            logger.error(f"无法读取图像: {input_path_obj}")
            return False
        
        logger.info(f"处理图像: {input_path_obj}")
        
        # 处理图像
        processed_image = processor.process_image(original_image, config)
        
        # 保存处理后的图像
        cv_imwrite(processed_image, output_path)
        
        logger.info(f"输出文件: {output_path}")
    
        return True
        
    except Exception as e:
        logger.error(f"处理文件 {input_path} 时出错: {e}")
        return False

def process_images(input_dir: str, output_dir: str="", config: Dict[str, Any]={}) -> None:
    """处理文件夹中的所有图像文件"""

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
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
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
                # 从文件名中截取相对路径和文件名，再增加.preprocessed.jpg后缀
                # 比如
                # input_dir_obj 是 d:/dir
                # output_dir_obj 是 d:/newdir
                # input_path 是 d:/dir/sub/img.png
                # 那么
                # output_path 是 d:/newdir/sub/img.png
                relative_path = input_path.relative_to(input_dir_obj)
                # 保持完整的相对路径结构，只改变扩展名
                output_relative_path = relative_path.with_suffix('.preprocessed.jpg')
                output_path = str(output_dir_obj / output_relative_path)
                
                # 确保输出目录存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                
                # 调用process_image处理单个文件
                process_image(str(input_path), output_path, config)
                
            except Exception as e:
                logger.error(f"处理文件 {input_path} 时出错: {e}")


        logger.info(f"批量处理完成！")
        
    except Exception as e:
        logger.error(f"批量处理时出错: {e}")
    


def get_default_config() -> Dict[str, Any]:
    """获取默认配置
    # 配置参数说明
    # grayscale:
    #   - enabled: 是否启用灰度处理
    #   - method: 灰度处理方法 (cv2/luminance/average)
    # contrast:
    #   - enabled: 是否启用对比度调整
    #   - alpha: 对比度倍数 (0.5-2.0)
    #   - beta: 亮度偏移 (-100到100)
    # threshold:
    #   - enabled: 是否启用二值化处理
    #   - method: 二值化方法 (otsu/binary/adaptive_mean/adaptive_gaussian)
    #   - params: 方法特定参数

    以下配置为效果最好的配置
    （6个配置的结果几乎没有差别,且质量稳定）
    grayscale | contrast | threshold
    --------------------------------
    cv2       |         | otsu
    cv2       | 0.5, b0 | otsu
    cv2       | 1.0, b0 | otsu
    luminance |         | otsu
    luminance | 0.5, b0 | otsu
    luminance | 1.0, b0 | otsu

    以下配置为效果稍差的配置，且质量不稳定
    grayscale | contrast | threshold
    --------------------------------
              | a0.5_b0  |
              | a1.5_b0  |
              | a1.0_b-50|
    cv2       | a0.5_b0  |
    cv2       | a1.0_b50 |
    luminance | a0.5_b0  |
    luminance | a1.0_b50 |
    average   | a0.5_b0  |
    average   | a1.0_b50 |
    """
    return {
        'grayscale': {
            'enabled': True,
            'method': 'cv2'
        },
        'contrast': {
            'enabled': True,
            'alpha': 1.0,
            'beta': 0
        },
        'threshold': {
            'enabled': True,
            'method': 'otsu',
            'params': {}
        }
    }

if __name__ == "__main__":

    
    # 示例配置 - 用户可以根据需要修改
    config = get_default_config()
    
    # process_image(input_path="tests/assets/img_0_dsk.jpg", config=config)

    process_images(input_dir="E:/语文出版社/2025/人教教师教学用书语文一年级上册-集团质检/img_dsk/", config=config)
