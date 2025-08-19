#!/usr/bin/env python3
"""
简单的OCR预处理测试脚本
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic():
    """基本功能测试"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        print("✓ 成功导入OCRPreprocessorSimple类")
        
        # 创建预处理器实例
        preprocessor = OCRPreprocessorSimple(
            deskew_threshold=0.5,
            denoise_strength=2,
            binarization_method='adaptive',
            contrast_enhancement=True
        )
        print("✓ 成功创建预处理器实例")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_image_processing():
    """图像处理测试"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        
        # 创建测试图像
        test_image = Image.new('RGB', (100, 100), color='white')
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple()
        
        # 测试图像处理
        processed = preprocessor.preprocess_image(test_image)
        
        if processed is not None and isinstance(processed, Image.Image):
            print("✓ 图像处理功能正常")
            return True
        else:
            print("✗ 图像处理返回结果异常")
            return False
            
    except Exception as e:
        print(f"✗ 图像处理测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始OCR预处理功能测试...\n")
    
    tests = [
        ("基本功能测试", test_basic),
        ("图像处理测试", test_image_processing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} 通过\n")
        else:
            print(f"✗ {test_name} 失败\n")
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！OCR预处理脚本功能正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
