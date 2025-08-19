#!/usr/bin/env python3
"""
OCR预处理功能测试脚本
用于验证预处理脚本的基本功能
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_functionality():
    """测试基本功能"""
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
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 创建预处理器失败: {e}")
        return False

def test_image_processing():
    """测试图像处理功能"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        import numpy as np
        
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

def test_file_operations():
    """测试文件操作功能"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple()
        
        # 测试输出路径生成
        test_path = "test_image.jpg"
        output_path = preprocessor._generate_output_path(test_path)
        
        expected_path = "test_image_preprocessed.jpg"
        if output_path == expected_path:
            print("✓ 输出路径生成功能正常")
            return True
        else:
            print(f"✗ 输出路径生成异常: 期望 {expected_path}, 实际 {output_path}")
            return False
            
    except Exception as e:
        print(f"✗ 文件操作测试失败: {e}")
        return False

def test_parameters_validation():
    """测试参数验证功能"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        
        # 测试有效参数
        try:
            preprocessor = OCRPreprocessorSimple(
                deskew_threshold=0.5,
                denoise_strength=3,
                binarization_method='otsu',
                contrast_enhancement=True
            )
            print("✓ 有效参数验证通过")
        except Exception as e:
            print(f"✗ 有效参数验证失败: {e}")
            return False
        
        # 测试无效参数
        try:
            preprocessor = OCRPreprocessorSimple(denoise_strength=10)  # 超出范围
            print("✗ 无效参数验证失败：应该抛出异常")
            return False
        except ValueError:
            print("✓ 无效参数验证通过：正确抛出异常")
        
        return True
        
    except Exception as e:
        print(f"✗ 参数验证测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始OCR预处理功能测试...\n")
    
    tests = [
        ("基本功能测试", test_basic_functionality),
        ("图像处理测试", test_image_processing),
        ("文件操作测试", test_file_operations),
        ("参数验证测试", test_parameters_validation),
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
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
