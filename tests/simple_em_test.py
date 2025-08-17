#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的em单位和行高测试
"""

from layout_recovery import LayoutRecovery, OCRBox


def test_simple():
    """简单测试"""
    print("简单em单位和行高测试")
    print("=" * 30)

    # 创建测试数据
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一行", 0.9),      # height=50
        OCRBox(100, 200, 200, 250, "第二行", 0.9),      # height=50, gap=50
        OCRBox(100, 300, 200, 350, "第三行", 0.9),      # height=50, gap=50
    ]

    # 创建版面恢复器
    recovery = LayoutRecovery()
    result = recovery.recover_layout(test_boxes)

    print(f"em单位: {result.em_unit}")
    print(f"行高比例: {result.line_height_ratio}")
    print(f"期望行高: {result.line_height_ratio * result.em_unit}")

    # 测试行间空行填充
    md_output = result.to_markdown()
    lines = md_output.split('\n')
    empty_lines = [line for line in lines if line.strip() == ""]

    print(f"\n输出行数: {len(lines)}")
    print(f"空行数: {len(empty_lines)}")
    print(f"输出内容:")
    print(md_output)


if __name__ == "__main__":
    test_simple()
