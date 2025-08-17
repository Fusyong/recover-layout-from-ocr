#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试行间空行计算逻辑
"""

from layout_recovery import LayoutRecovery, OCRBox


def test_detailed_line_gap():
    """详细测试行间空行计算"""
    print("详细测试行间空行计算")
    print("=" * 40)

    # 创建测试数据：模拟不同的行间距
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一行", 0.9),      # height=50
        OCRBox(100, 200, 200, 250, "第二行", 0.9),      # height=50, gap=50
        OCRBox(100, 300, 200, 350, "第三行", 0.9),      # height=50, gap=50
        OCRBox(100, 400, 200, 450, "第四行", 0.9),      # height=50, gap=50
    ]

    print("测试数据:")
    for i, box in enumerate(test_boxes):
        print(f"  文本框{i+1}: 高度={box.height}, 位置=({box.x1}, {box.y1})-({box.x2}, {box.y2})")

    # 计算行间距
    sorted_boxes = sorted(test_boxes, key=lambda b: b.y1)
    line_gaps = []
    for i in range(1, len(sorted_boxes)):
        gap = sorted_boxes[i].y1 - sorted_boxes[i-1].y2
        line_gaps.append(gap)

    print(f"\n行间距: {line_gaps}")

    # 创建版面恢复器
    recovery = LayoutRecovery()
    result = recovery.recover_layout(test_boxes)

    print(f"\n计算结果:")
    print(f"  em单位: {result.em_unit}")
    print(f"  行高比例: {result.line_height_ratio}")
    print(f"  期望行高: {result.line_height_ratio * result.em_unit}")

    # 手动计算空行数
    expected_line_height = result.line_height_ratio * result.em_unit
    print(f"\n手动计算空行数:")
    for i, gap in enumerate(line_gaps):
        empty_lines = round(gap / expected_line_height)
        print(f"  间距{i+1}: {gap} ÷ {expected_line_height} = {gap/expected_line_height:.3f} -> 空行数: {empty_lines}")

    # 测试不同配置
    configs = [
        {"name": "启用行间填充", "config": {"enable_line_gap_fill": True}},
        {"name": "禁用行间填充", "config": {"enable_line_gap_fill": False}},
    ]

    for config_info in configs:
        print(f"\n{config_info['name']}:")
        recovery_custom = LayoutRecovery(config_info['config'])
        result_custom = recovery_custom.recover_layout(test_boxes)
        md_output = result_custom.to_markdown()

        # 分析输出
        lines = md_output.split('\n')
        empty_lines = [line for line in lines if line.strip() == ""]

        print(f"  总行数: {len(lines)}")
        print(f"  空行数: {len(empty_lines)}")
        print(f"  内容行数: {len(lines) - len(empty_lines)}")

        # 显示前几行
        print(f"  前10行:")
        for i, line in enumerate(lines[:10]):
            if line.strip() == "":
                print(f"    {i+1}: [空行]")
            else:
                print(f"    {i+1}: {line}")


if __name__ == "__main__":
    test_detailed_line_gap()
