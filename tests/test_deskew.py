#!/usr/bin/env python3
"""
测试deskew库功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_deskew_import():
    """测试deskew库导入"""
    try:
        from deskew import determine_skew
        print("✓ 成功导入deskew库")
        return True
    except ImportError as e:
        print(f"✗ deskew库导入失败: {e}")
        print("请安装deskew库: pip install deskew")
        return False

def test_deskew_functionality():
    """测试deskew库功能"""
    try:
        from deskew import determine_skew
        from PIL import Image
        import numpy as np
        
        # 创建测试图像
        test_image = Image.new('L', (100, 100), color=255)
        # 添加一些黑色像素来模拟文字
        test_array = np.array(test_image)
        test_array[40:60, 20:80] = 0  # 创建黑色矩形
        test_image = Image.fromarray(test_array, mode='L')
        
        print("✓ 成功创建测试图像")
        
        # 测试倾斜检测
        angle = determine_skew(test_image)
        print(f"✓ 倾斜检测成功，角度: {angle:.2f}°")
        
        return True
        
    except Exception as e:
        print(f"✗ deskew功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ocr_preprocessor_deskew():
    """测试OCR预处理器中的deskew功能"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        import numpy as np
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple(deskew_threshold=0.1)
        
        # 创建测试图像
        test_image = Image.new('RGB', (100, 100), color='white')
        test_array = np.array(test_image)
        test_array[40:60, 20:80] = [0, 0, 0]  # 创建黑色矩形
        test_image = Image.fromarray(test_array, mode='RGB')
        
        print("✓ 成功创建OCR预处理器和测试图像")
        
        # 测试倾斜校正
        corrected = preprocessor._deskew_image(test_image)
        
        if corrected is not None and isinstance(corrected, Image.Image):
            print("✓ OCR预处理器倾斜校正功能正常")
            return True
        else:
            print("✗ OCR预处理器倾斜校正返回结果异常")
            return False
            
    except Exception as e:
        print(f"✗ OCR预处理器deskew测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试deskew库功能...\n")
    
    tests = [
        ("deskew库导入测试", test_deskew_import),
        ("deskew库功能测试", test_deskew_functionality),
        ("OCR预处理器deskew测试", test_ocr_preprocessor_deskew),
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
        print("🎉 所有测试通过！deskew库功能正常。")
        print("\n现在可以运行完整的OCR预处理流程：")
        print("python src/ocr_preprocessing_simple.py")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
        
        if passed < 2:  # 如果前两个测试失败
            print("\n建议安装deskew库：")
            print("pip install deskew")
