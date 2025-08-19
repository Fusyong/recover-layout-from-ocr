#!/usr/bin/env python3
"""
测试OCR预处理脚本功能
"""

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
            denoise_strength=2,
            binarization_method='adaptive',
            contrast_enhancement=True
        )
        print("✓ 成功创建预处理器实例")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_processing():
    """测试图像处理功能"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        import numpy as np
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple()
        
        # 创建简单的测试图像
        test_image = Image.new('RGB', (100, 100), color='white')
        test_array = np.array(test_image)
        test_array[40:60, 20:80] = [0, 0, 0]  # 创建黑色矩形
        test_image = Image.fromarray(test_array, mode='RGB')
        
        print("✓ 成功创建测试图像")
        
        # 测试图像处理（不保存中间结果）
        processed = preprocessor.preprocess_image(
            test_image, 
            save_intermediate=False
        )
        
        if processed is not None and isinstance(processed, Image.Image):
            print("✓ 图像处理功能正常")
            print(f"  输出图像尺寸: {processed.size}")
            print(f"  输出图像模式: {processed.mode}")
            return True
        else:
            print("✗ 图像处理返回结果异常")
            return False
            
    except Exception as e:
        print(f"✗ 图像处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_validation():
    """测试参数验证"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        
        # 测试无效的去噪强度
        try:
            preprocessor = OCRPreprocessorSimple(denoise_strength=6)
            print("✗ 应该抛出异常：去噪强度超出范围")
            return False
        except ValueError as e:
            if "去噪强度应在1-5之间" in str(e):
                print("✓ 去噪强度验证正常")
            else:
                print(f"✗ 去噪强度验证异常: {e}")
                return False
        
        # 测试无效的二值化方法
        try:
            preprocessor = OCRPreprocessorSimple(binarization_method='invalid')
            print("✗ 应该抛出异常：无效的二值化方法")
            return False
        except ValueError as e:
            if "二值化方法应为" in str(e):
                print("✓ 二值化方法验证正常")
            else:
                print(f"✗ 二值化方法验证异常: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ 参数验证测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试OCR预处理脚本功能...\n")
    
    tests = [
        ("基本功能测试", test_basic_functionality),
        ("图像处理测试", test_image_processing),
        ("参数验证测试", test_parameter_validation),
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
        print("\n现在可以尝试运行完整的预处理流程：")
        print("python src/ocr_preprocessing_simple.py")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
