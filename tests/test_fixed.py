#!/usr/bin/env python3
"""
测试修复后的OCR预处理功能
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
        import traceback
        traceback.print_exc()
        return False

def test_simple_image():
    """简单图像处理测试"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple()
        
        # 创建简单的测试图像
        test_image = Image.new('RGB', (50, 50), color='white')
        
        print("✓ 成功创建测试图像")
        
        # 测试图像处理（不保存中间结果）
        processed = preprocessor.preprocess_image(
            test_image, 
            save_intermediate=False
        )
        
        if processed is not None and isinstance(processed, Image.Image):
            print("✓ 图像处理功能正常")
            return True
        else:
            print("✗ 图像处理返回结果异常")
            return False
            
    except Exception as e:
        print(f"✗ 图像处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试修复后的OCR预处理功能...\n")
    
    tests = [
        ("基本功能测试", test_basic),
        ("简单图像处理测试", test_simple_image),
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
