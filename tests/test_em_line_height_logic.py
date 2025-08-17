#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试em单位和行高的计算逻辑

验证：
1. em单位计算（根据页面实际box高度多数情形进行计算）
2. 行高计算（通常是1.2em-2em，根据页面多数情况调整）
3. 行间空行计算（基线距离超过当前行距的倍数，按四舍五入换算成空行）
"""

from layout_recovery import LayoutRecovery, OCRBox
import math


def test_em_and_line_height_calculation():
    """测试em单位和行高的计算逻辑"""
    print("测试em单位和行高计算逻辑")
    print("=" * 50)

    # 创建测试数据：模拟不同高度的文本框
    test_boxes = [
        OCRBox(100, 100, 200, 150, "标题", 0.9),      # height=50
        OCRBox(100, 200, 200, 250, "正文1", 0.9),     # height=50
        OCRBox(100, 300, 200, 350, "正文2", 0.9),     # height=50
        OCRBox(100, 400, 200, 450, "正文3", 0.9),     # height=50
        OCRBox(100, 500, 200, 550, "正文4", 0.9),     # height=50
        OCRBox(100, 600, 200, 650, "正文5", 0.9),     # height=50
        OCRBox(100, 700, 200, 750, "正文6", 0.9),     # height=50
        OCRBox(100, 800, 200, 850, "正文7", 0.9),     # height=50
        OCRBox(100, 900, 200, 950, "正文8", 0.9),     # height=50
        OCRBox(100, 1000, 200, 1050, "正文9", 0.9),  # height=50
    ]

    print("测试数据:")
    for i, box in enumerate(test_boxes):
        print(f"  文本框{i+1}: 高度={box.height}, 位置=({box.x1}, {box.y1})-({box.x2}, {box.y2})")

    # 创建版面恢复器
    recovery = LayoutRecovery()

    # 手动计算em单位
    heights = [box.height for box in test_boxes if box.height > 0]
    import statistics
    median_height = statistics.median(heights)
    print(f"\n手动计算:")
    print(f"  所有高度: {heights}")
    print(f"  中位数高度: {median_height}")

    # 过滤异常值
    filtered_heights = [h for h in heights if median_height * 0.5 <= h <= median_height * 2.0]
    print(f"  过滤后高度: {filtered_heights}")

    # 计算最终em单位
    final_em = statistics.median(filtered_heights) if filtered_heights else median_height
    print(f"  最终em单位: {final_em}")

    # 计算行高比例
    sorted_boxes = sorted(test_boxes, key=lambda b: b.y1)
    line_gaps = []
    for i in range(1, len(sorted_boxes)):
        gap = sorted_boxes[i].y1 - sorted_boxes[i-1].y2
        if gap > 0:
            line_gaps.append(gap)

    print(f"  行间距: {line_gaps}")
    avg_gap = statistics.mean(line_gaps) if line_gaps else 0
    print(f"  平均行间距: {avg_gap}")

    # 计算行高比例
    line_height_ratio = avg_gap / final_em if final_em > 0 else 1.5
    line_height_ratio = max(1.2, min(2.0, line_height_ratio))
    print(f"  行高比例: {line_height_ratio}")

    # 验证版面恢复器的计算
    result = recovery.recover_layout(test_boxes)
    print(f"\n版面恢复器计算结果:")
    print(f"  em单位: {result.em_unit}")
    print(f"  行高比例: {result.line_height_ratio}")

    # 验证行间空行计算
    print(f"\n行间空行计算验证:")
    expected_line_height = result.line_height_ratio * result.em_unit
    print(f"  期望行高: {expected_line_height}")

    for i in range(1, len(line_gaps)):
        gap = line_gaps[i-1]
        empty_lines_needed = round(gap / expected_line_height)  # 四舍五入
        print(f"  间距{i}: {gap} -> 空行数: {empty_lines_needed}")

    print("\n测试完成！")


def test_line_gap_fill_with_rounding():
    """测试行间空行填充的四舍五入逻辑"""
    print("\n" + "=" * 50)
    print("测试行间空行填充的四舍五入逻辑")
    print("=" * 50)

    # 创建测试数据：模拟不同的行间距
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一行", 0.9),      # height=50
        OCRBox(100, 200, 200, 250, "第二行", 0.9),      # height=50, gap=50
        OCRBox(100, 300, 200, 350, "第三行", 0.9),      # height=50, gap=50
        OCRBox(100, 400, 200, 450, "第四行", 0.9),      # height=50, gap=50
        OCRBox(100, 500, 200, 550, "第五行", 0.9),      # height=50, gap=50
        OCRBox(100, 600, 200, 650, "第六行", 0.9),      # height=50, gap=50
        OCRBox(100, 700, 200, 750, "第七行", 0.9),      # height=50, gap=50
        OCRBox(100, 800, 200, 850, "第八行", 0.9),      # height=50, gap=50
        OCRBox(100, 900, 200, 950, "第九行", 0.9),      # height=50, gap=50
        OCRBox(100, 1000, 200, 1050, "第十行", 0.9),    # height=50, gap=50
    ]

    # 创建版面恢复器
    recovery = LayoutRecovery()
    result = recovery.recover_layout(test_boxes)

    print(f"计算结果:")
    print(f"  em单位: {result.em_unit}")
    print(f"  行高比例: {result.line_height_ratio}")
    print(f"  期望行高: {result.line_height_ratio * result.em_unit}")

    # 测试不同配置的输出
    configs = [
        {"name": "默认配置", "config": {}},
        {"name": "禁用行间填充", "config": {"enable_line_gap_fill": False}},
        {"name": "自定义行高", "config": {"line_height_ratio": 1.8}},
    ]

    for config_info in configs:
        print(f"\n{config_info['name']}:")
        recovery_custom = LayoutRecovery(config_info['config'])
        result_custom = recovery_custom.recover_layout(test_boxes)
        md_output = result_custom.to_markdown()

        # 计算空行数量
        lines = md_output.split('\n')
        empty_lines = [line for line in lines if line.strip() == ""]

        print(f"  输出行数: {len(lines)}")
        print(f"  空行数: {len(empty_lines)}")
        print(f"  前100字符: {md_output[:100]}")


if __name__ == "__main__":
    test_em_and_line_height_calculation()
    test_line_gap_fill_with_rounding()
