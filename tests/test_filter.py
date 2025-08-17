#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OCR过滤器功能
验证过滤器是否能正确滤除不需要的box
"""

import json
import os
from src.ocr_json2text_line import OCRJsonToTextLine

def test_filter_functionality():
    """测试过滤器功能"""
    
    # 创建转换器实例
    converter = OCRJsonToTextLine()
    
    # 定义测试过滤器
    def filter_small_boxes(box_data, page_info):
        """滤除宽度小于50像素的box"""
        width = box_data['width']
        should_keep = width >= 50
        print(f"过滤检查: 文本='{box_data['text']}', 宽度={width}, 保留={should_keep}")
        return should_keep
    
    def filter_keywords(box_data, page_info):
        """滤除包含特定关键词的box"""
        text = box_data['text'].lower()
        keywords_to_filter = ['page', '第', '页']
        
        for keyword in keywords_to_filter:
            if keyword in text:
                print(f"关键词过滤: 文本='{box_data['text']}', 包含关键词'{keyword}'")
                return False
        return True
    
    # 启动过滤器
    converter.boxFilter(filter_small_boxes, filter_keywords)
    print("已启用过滤器：")
    print("1. 滤除宽度小于50像素的box")
    print("2. 滤除包含'page'、'第'、'页'关键词的box")
    
    # 测试文件
    test_file = "img_dsk/page-1.json"
    
    if not os.path.exists(test_file):
        print(f"测试文件 {test_file} 不存在，跳过测试")
        return
    
    try:
        # 读取JSON文件
        with open(test_file, 'r', encoding='utf-8') as f:
            ocr_json = json.load(f)
        
        print(f"\n正在测试文件: {test_file}")
        
        # 转换前统计
        if isinstance(ocr_json, list):
            print(f"RapidOCR格式，总box数: {len(ocr_json)}")
        elif 'Result' in ocr_json and 'regions' in ocr_json['Result']:
            regions = ocr_json['Result']['regions']
            total_lines = sum(len(region.get('lines', [])) for region in regions)
            print(f"有道智云格式，转换前总行数: {total_lines}")
        
        # 使用过滤器转换
        print("\n开始使用过滤器转换...")
        text_with_filter = converter.convert_json_to_text(ocr_json)
        lines_with_filter = text_with_filter.split('\n')
        lines_with_filter = [line for line in lines_with_filter if line.strip()]
        
        print(f"使用过滤器后行数: {len(lines_with_filter)}")
        
        # 禁用过滤器重新转换
        print("\n开始不使用过滤器转换...")
        converter.boxFilter()
        text_without_filter = converter.convert_json_to_text(ocr_json)
        lines_without_filter = text_without_filter.split('\n')
        lines_without_filter = [line for line in lines_without_filter if line.strip()]
        
        print(f"不使用过滤器行数: {len(lines_without_filter)}")
        
        # 计算过滤效果
        filtered_count = len(lines_without_filter) - len(lines_with_filter)
        print(f"过滤器滤除的行数: {filtered_count}")
        
        # 显示过滤后的前几行
        print(f"\n过滤后的前5行内容:")
        for i, line in enumerate(lines_with_filter[:5]):
            print(f"{i+1}: {line[:100]}...")
        
        print("\n过滤器功能测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filter_functionality()
