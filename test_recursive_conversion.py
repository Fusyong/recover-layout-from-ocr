#!/usr/bin/env python3
"""
测试递归JSON转换功能
"""

import os
import tempfile
import shutil
from pathlib import Path
import json

# 导入要测试的模块
import sys
sys.path.append('src')
from ocr_json2text_line import convert_jsons_to_text

def create_test_structure():
    """创建测试目录结构"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"创建测试目录: {temp_dir}")
    
    # 创建子目录结构
    subdirs = [
        "level1",
        "level1/level2",
        "level1/level2/level3",
        "another_branch"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(temp_dir, subdir), exist_ok=True)
    
    # 创建测试JSON文件
    test_jsons = [
        "root.json",
        "level1/sub1.json", 
        "level1/level2/sub2.json",
        "level1/level2/level3/sub3.json",
        "another_branch/branch.json"
    ]
    
    # 创建简单的测试JSON内容（RapidOCR格式）
    test_data = [
        {
            "txt": "测试文本",
            "box": [[10, 10], [100, 10], [100, 30], [10, 30]],
            "score": 0.95
        }
    ]
    
    for json_file in test_jsons:
        json_path = os.path.join(temp_dir, json_file)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print(f"创建测试文件: {json_path}")
    
    return temp_dir

def test_recursive_conversion():
    """测试递归转换功能"""
    print("开始测试递归JSON转换功能...")
    
    # 创建测试结构
    test_dir = create_test_structure()
    
    try:
        # 测试转换
        print("\n执行递归转换...")
        convert_jsons_to_text(test_dir)
        
        # 检查结果
        print("\n检查转换结果...")
        test_dir_path = Path(test_dir)
        
        # 查找所有生成的.txt文件
        txt_files = list(test_dir_path.rglob("*.txt"))
        print(f"找到 {len(txt_files)} 个生成的txt文件:")
        
        for txt_file in sorted(txt_files):
            print(f"  {txt_file.relative_to(test_dir_path)}")
            
            # 检查文件内容
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"    内容: {repr(content)}")
        
        # 验证目录结构是否保持
        print("\n验证目录结构:")
        for root, dirs, files in os.walk(test_dir):
            level = root.replace(test_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        print("\n测试完成！")
        
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir)
        print(f"清理测试目录: {test_dir}")

if __name__ == "__main__":
    test_recursive_conversion()
