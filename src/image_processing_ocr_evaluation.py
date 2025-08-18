"""
图像处理与OCR效果评估脚本

对图像进行灰度、对比度、二值化处理，循环组合不同参数，
调用RapidOCR进行识别，输出结果用于评估效果。
"""

import os
import cv2
import numpy as np
import json
from pathlib import Path
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR
from typing import List, Tuple, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('image_processing_evaluation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ImageProcessor:
    """图像处理类"""
    
    def __init__(self):
        self.rapidocr_engine = RapidOCR(
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
    
    def apply_grayscale(self, image: np.ndarray, method: str = 'cv2') -> np.ndarray:
        """应用灰度处理"""
        if method == 'cv2':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif method == 'luminance':
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif method == 'average':
            return np.mean(image, axis=2).astype(np.uint8)
        else:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def apply_contrast(self, image: np.ndarray, alpha: float, beta: int) -> np.ndarray:
        """应用对比度调整"""
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    def apply_threshold(self, image: np.ndarray, method: str, **kwargs) -> np.ndarray:
        """应用二值化处理"""
        if method == 'binary':
            thresh = kwargs.get('thresh', 127)
            maxval = kwargs.get('maxval', 255)
            _, binary = cv2.threshold(image, thresh, maxval, cv2.THRESH_BINARY)
            return binary
        elif method == 'adaptive_mean':
            block_size = kwargs.get('block_size', 11)
            c = kwargs.get('c', 2)
            return cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, c
            )
        elif method == 'adaptive_gaussian':
            block_size = kwargs.get('block_size', 11)
            c = kwargs.get('c', 2)
            return cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
            )
        elif method == 'otsu':
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return binary
        else:
            return image
    
    def process_image(self, image: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
        """根据配置处理图像"""
        processed = image.copy()
        
        # 应用灰度处理
        if config.get('grayscale', {}).get('enabled', False):
            method = config['grayscale'].get('method', 'cv2')
            processed = self.apply_grayscale(processed, method)
        
        # 应用对比度调整
        if config.get('contrast', {}).get('enabled', False):
            alpha = config['contrast'].get('alpha', 1.0)
            beta = config['contrast'].get('beta', 0)
            processed = self.apply_contrast(processed, alpha, beta)
        
        # 应用二值化处理
        if config.get('threshold', {}).get('enabled', False):
            method = config['threshold'].get('method', 'binary')
            thresh_params = config['threshold'].get('params', {})
            processed = self.apply_threshold(processed, method, **thresh_params)
        
        return processed
    
    def generate_filename(self, config: Dict[str, Any], index: int) -> str:
        """生成处理后的文件名"""
        parts = [f"processed_{index:03d}"]
        
        if config.get('grayscale', {}).get('enabled', False):
            method = config['grayscale'].get('method', 'cv2')
            parts.append(f"gray_{method}")
        
        if config.get('contrast', {}).get('enabled', False):
            alpha = config['contrast'].get('alpha', 1.0)
            beta = config['contrast'].get('beta', 0)
            parts.append(f"contrast_a{alpha}_b{beta}")
        
        if config.get('threshold', {}).get('enabled', False):
            method = config['threshold'].get('method', 'binary')
            thresh_params = config['threshold'].get('params', {})
            if method == 'binary':
                parts.append(f"thresh_{method}_{thresh_params.get('thresh', 127)}")
            elif method in ['adaptive_mean', 'adaptive_gaussian']:
                parts.append(f"thresh_{method}_b{thresh_params.get('block_size', 11)}_c{thresh_params.get('c', 2)}")
            else:
                parts.append(f"thresh_{method}")
        
        return "_".join(parts) + ".jpg"
    
    def ocr_image(self, image: np.ndarray, image_path: str) -> Dict[str, Any]:
        """对图像进行OCR识别"""
        try:
            # 保存图像
            cv2.imwrite(image_path, image)
            
            # 进行OCR识别
            result = self.rapidocr_engine(image_path)
            
            # 提取文本
            text_result = result.to_text() if hasattr(result, 'to_text') else str(result)
            
            return {
                'success': True,
                'text': text_result,
                'raw_result': str(result),
                'image_path': image_path
            }
        except Exception as e:
            logger.error(f"OCR处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'image_path': image_path
            }

def generate_processing_configs() -> List[Dict[str, Any]]:
    """生成所有可能的处理配置组合"""
    configs = []
    
    # 灰度处理配置
    grayscale_configs = [
        {'enabled': False, 'method': 'cv2'},
        {'enabled': True, 'method': 'cv2'},
        {'enabled': True, 'method': 'luminance'},
        {'enabled': True, 'method': 'average'}
    ]
    
    # 对比度配置
    contrast_configs = [
        {'enabled': False, 'alpha': 1.0, 'beta': 0},
        {'enabled': True, 'alpha': 0.5, 'beta': 0},
        {'enabled': True, 'alpha': 1.0, 'beta': 0},
        {'enabled': True, 'alpha': 1.5, 'beta': 0},
        {'enabled': True, 'alpha': 2.0, 'beta': 0},
        {'enabled': True, 'alpha': 1.0, 'beta': -50},
        {'enabled': True, 'alpha': 1.0, 'beta': 50},
    ]
    
    # 二值化配置
    threshold_configs = [
        {'enabled': False, 'method': 'binary', 'params': {}},
        {'enabled': True, 'method': 'binary', 'params': {'thresh': 127, 'maxval': 255}},
        {'enabled': True, 'method': 'binary', 'params': {'thresh': 100, 'maxval': 255}},
        {'enabled': True, 'method': 'binary', 'params': {'thresh': 150, 'maxval': 255}},
        {'enabled': True, 'method': 'otsu', 'params': {}},
        {'enabled': True, 'method': 'adaptive_mean', 'params': {'block_size': 11, 'c': 2}},
        {'enabled': True, 'method': 'adaptive_mean', 'params': {'block_size': 15, 'c': 3}},
        {'enabled': True, 'method': 'adaptive_gaussian', 'params': {'block_size': 11, 'c': 2}},
        {'enabled': True, 'method': 'adaptive_gaussian', 'params': {'block_size': 15, 'c': 3}},
    ]
    
    # 生成所有组合
    for gs in grayscale_configs:
        for ct in contrast_configs:
            for th in threshold_configs:
                config = {
                    'grayscale': gs,
                    'contrast': ct,
                    'threshold': th
                }
                configs.append(config)
    
    return configs

def main():
    """主函数"""
    # 输入图像路径
    input_image_path = "tests/assets/img_0_dsk.jpg"
    
    # 检查输入图像是否存在
    if not os.path.exists(input_image_path):
        logger.error(f"输入图像不存在: {input_image_path}")
        return
    
    # 创建输出目录
    output_dir = "processed_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建图像处理器
    processor = ImageProcessor()
    
    # 生成所有处理配置
    configs = generate_processing_configs()
    logger.info(f"生成了 {len(configs)} 种处理配置组合")
    
    # 读取原始图像
    original_image = cv2.imread(input_image_path)
    if original_image is None:
        logger.error(f"无法读取图像: {input_image_path}")
        return
    
    logger.info(f"原始图像尺寸: {original_image.shape}")
    
    # 存储所有结果
    results = []
    
    # 处理每种配置
    for i, config in enumerate(configs):
        logger.info(f"处理配置 {i+1}/{len(configs)}: {config}")
        
        try:
            # 处理图像
            processed_image = processor.process_image(original_image, config)
            
            # 生成输出文件名
            filename = processor.generate_filename(config, i)
            output_path = os.path.join(output_dir, filename)
            
            # 进行OCR识别
            ocr_result = processor.ocr_image(processed_image, output_path)
            
            # 记录结果
            result = {
                'config_index': i,
                'config': config,
                'filename': filename,
                'output_path': output_path,
                'ocr_result': ocr_result
            }
            results.append(result)
            
            logger.info(f"配置 {i+1} 完成: {filename}")
            if ocr_result['success']:
                logger.info(f"OCR文本: {ocr_result['text'][:100]}...")
            else:
                logger.warning(f"OCR失败: {ocr_result['error']}")
                
        except Exception as e:
            logger.error(f"处理配置 {i+1} 时出错: {e}")
            continue
    
    # 保存结果到JSON文件
    results_file = os.path.join(output_dir, "processing_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    # 生成汇总报告
    report_file = os.path.join(output_dir, "evaluation_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("图像处理与OCR效果评估报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"总配置数: {len(configs)}\n")
        f.write(f"成功处理: {len([r for r in results if r['ocr_result']['success']])}\n")
        f.write(f"处理失败: {len([r for r in results if not r['ocr_result']['success']])}\n\n")
        
        f.write("详细结果:\n")
        f.write("-" * 30 + "\n")
        
        for result in results:
            f.write(f"\n配置 {result['config_index']}: {result['filename']}\n")
            f.write(f"处理配置: {result['config']}\n")
            
            if result['ocr_result']['success']:
                f.write(f"OCR文本: {result['ocr_result']['text']}\n")
            else:
                f.write(f"OCR失败: {result['ocr_result']['error']}\n")
            f.write("-" * 30 + "\n")
    
    logger.info(f"处理完成！结果保存在: {output_dir}")
    logger.info(f"详细结果: {results_file}")
    logger.info(f"评估报告: {report_file}")

if __name__ == "__main__":
    main()
