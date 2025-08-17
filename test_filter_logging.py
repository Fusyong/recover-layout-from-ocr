#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试过滤日志功能
"""

import sys
import os
sys.path.append('src')

from src.ocr_json2text_line import OCRJsonToTextLine
from src.ocr_json_filters import filter_small_width, filter_header, filter_page_number
import json

def test_filter_logging():
    """测试过滤日志功能"""
    
    print("开始测试过滤日志功能...")
    
    # 创建转换器实例
    converter = OCRJsonToTextLine()
    
    # 测试1：只使用box级过滤器，查看日志
    print("\n测试1：只使用box级过滤器")
    converter.boxFilter(filter_small_width, filter_header)
    converter.rowBoxFilter()  # 空数组
    
    # 测试文件
    test_file = "img_1_dsk.json"
    
    if not os.path.exists(test_file):
        print(f"测试文件 {test_file} 不存在")
        return
    
    try:
        # 读取JSON文件
        with open(test_file, 'r', encoding='utf-8') as f:
            ocr_json = json.load(f)
        
        print(f"JSON文件加载成功")
        print("开始转换，观察过滤日志...")
        
        # 转换
        text = converter.convert_json_to_text(ocr_json)
        
        # 保存结果
        output_file = "test_filter_logging_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\n转换完成！输出文件：{output_file}")
        print(f"输出文本长度：{len(text)} 字符")
        print(f"输出行数：{len(text.split(chr(10)))}")
        
        # 测试2：只使用行级过滤器，查看日志
        print("\n测试2：只使用行级过滤器")
        converter.boxFilter()  # 空数组
        converter.rowBoxFilter(filter_small_width, filter_header, filter_page_number)
        
        text2 = converter.convert_json_to_text(ocr_json)
        
        output_file2 = "test_row_filter_logging_output.txt"
        with open(output_file2, 'w', encoding='utf-8') as f:
            f.write(text2)
        
        print(f"\n转换完成！输出文件：{output_file2}")
        print(f"输出文本长度：{len(text2)} 字符")
        print(f"输出行数：{len(text2.split(chr(10)))}")
        
        print("\n所有测试完成！请查看上面的过滤日志。")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filter_logging()
