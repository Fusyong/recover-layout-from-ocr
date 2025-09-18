#!/usr/bin/env python3
"""
测试自然排序功能
"""

from src.cat_page_markdown_to_book import MarkdownMerger
import tempfile
import os

def test_natural_sorting():
    """测试自然排序功能"""
    # 创建测试文件
    test_files = ['file1.md', 'file2.md', 'file9.md', 'file10.md', 'file20.md', 'file100.md']
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        for filename in test_files:
            with open(os.path.join(temp_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f'# {filename}')
        
        # 测试自然排序
        merger = MarkdownMerger(temp_dir)
        files = merger.get_markdown_files()
        
        print('自然排序结果:')
        for f in files:
            print(f'  {f.name}')
        
        # 验证排序是否正确
        expected_order = ['file1.md', 'file2.md', 'file9.md', 'file10.md', 'file20.md', 'file100.md']
        actual_order = [f.name for f in files]
        
        print(f'\n期望顺序: {expected_order}')
        print(f'实际顺序: {actual_order}')
        print(f'排序正确: {actual_order == expected_order}')

if __name__ == "__main__":
    test_natural_sorting()
