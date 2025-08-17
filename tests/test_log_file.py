#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志文件功能
"""

import sys
import os
sys.path.append('src')

from src.ocr_json2text_line import OCRJsonToTextLine
from src.ocr_json_filters import filter_small_width, filter_header, filter_page_number
import json

def test_log_file():
    """测试日志文件功能"""
    
    print("开始测试日志文件功能...")
    
    # 创建转换器实例
    converter = OCRJsonToTextLine()
    
    # 设置自定义日志文件名
    log_file = "test_filter_log.txt"
    converter.set_log_file(log_file)
    print(f"设置日志文件: {log_file}")
    
    # 启用过滤器
    converter.boxFilter(filter_small_width, filter_header)
    converter.rowBoxFilter(filter_header, filter_page_number)
    
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
        output_file = "test_log_file_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\n转换完成！输出文件：{output_file}")
        print(f"输出文本长度：{len(text)} 字符")
        print(f"输出行数：{len(text.split(chr(10)))}")
        
        # 检查日志文件
        if os.path.exists(log_file):
            print(f"\n日志文件已生成: {log_file}")
            print("日志文件内容:")
            
            # 用Python读取日志文件内容
            with open(log_file, 'r', encoding='utf-8-sig') as f:
                log_content = f.read()
                print(log_content)
            
            # 统计过滤记录
            filter_count = log_content.count('[FILTER_LOG]')
            print(f"\n总共记录了 {filter_count} 条过滤信息")
            
        else:
            print(f"\n错误：日志文件 {log_file} 未生成")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_log_file()
