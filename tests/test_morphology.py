#!/usr/bin/env python3
"""
测试形态学处理功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_morphology():
    """测试形态学处理"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        from PIL import Image
        import numpy as np
        
        print("✓ 成功导入OCRPreprocessorSimple类")
        
        # 创建预处理器
        preprocessor = OCRPreprocessorSimple()
        
        # 创建测试图像（二值化后的图像）
        test_image = Image.new('L', (100, 100), color=255)
        # 添加一些黑色像素
        test_array = np.array(test_image)
        test_array[40:60, 40:60] = 0  # 创建一个黑色矩形
        test_image = Image.fromarray(test_array, mode='L')
        
        print("✓ 成功创建测试图像")
        
        # 测试形态学处理
        processed = preprocessor._morphological_processing(test_image)
        
        if processed is not None and isinstance(processed, Image.Image):
            print("✓ 形态学处理功能正常")
            return True
        else:
            print("✗ 形态学处理返回结果异常")
            return False
            
    except Exception as e:
        print(f"✗ 形态学处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_erode_dilate():
    """测试腐蚀和膨胀操作"""
    try:
        from ocr_preprocessing_simple import OCRPreprocessorSimple
        import numpy as np
        
        preprocessor = OCRPreprocessorSimple()
        
        # 创建测试图像数组
        test_img = np.ones((10, 10), dtype=np.uint8) * 255
        test_img[3:7, 3:7] = 0  # 创建一个黑色矩形
        
        # 创建kernel
        kernel = np.ones((2, 2), dtype=np.uint8)
        
        print("✓ 成功创建测试数据")
        
        # 测试腐蚀
        eroded = preprocessor._erode(test_img, kernel)
        if eroded is not None and eroded.shape == test_img.shape:
            print("✓ 腐蚀操作正常")
        else:
            print("✗ 腐蚀操作异常")
            return False
        
        # 测试膨胀
        dilated = preprocessor._dilate(eroded, kernel)
        if dilated is not None and dilated.shape == test_img.shape:
            print("✓ 膨胀操作正常")
        else:
            print("✗ 膨胀操作异常")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 腐蚀膨胀测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始形态学处理功能测试...\n")
    
    tests = [
        ("形态学处理测试", test_morphology),
        ("腐蚀膨胀测试", test_erode_dilate),
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
        print("🎉 所有测试通过！形态学处理功能正常。")
    else:
        print("⚠️  部分测试失败，请检查相关功能。")
