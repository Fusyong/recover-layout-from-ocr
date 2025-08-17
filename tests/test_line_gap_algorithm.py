#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的行间空行填充算法
验证空行是否被正确插入到相邻行之间
"""

from layout_recovery import LayoutRecovery, OCRBox


def test_line_gap_algorithm():
    """测试行间空行填充算法"""
    print("测试修复后的行间空行填充算法")
    print("=" * 50)

    # 创建测试数据：模拟不同的行间距
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一行", 0.9),      # height=50
        OCRBox(100, 200, 200, 250, "第二行", 0.9),      # height=50, gap=50
        OCRBox(100, 300, 200, 350, "第三行", 0.9),      # height=50, gap=50
        OCRBox(100, 400, 200, 450, "第四行", 0.9),      # height=50, gap=50
        OCRBox(100, 500, 200, 550, "第五行", 0.9),      # height=50, gap=50
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

    # 测试不同配置
    configs = [
        {"name": "启用行间填充", "config": {"enable_line_gap_fill": True}},
        {"name": "禁用行间填充", "config": {"enable_line_gap_fill": False}},
    ]

    for config_info in configs:
        print(f"\n{config_info['name']}:")
        print("-" * 30)

        recovery = LayoutRecovery(config_info['config'])
        result = recovery.recover_layout(test_boxes)

        print(f"  em单位: {result.em_unit}")
        print(f"  行高比例: {result.line_height_ratio}")
        print(f"  期望行高: {result.line_height_ratio * result.em_unit}")

        # 生成markdown
        md_output = result.to_markdown()
        lines = md_output.split('\n')
        empty_lines = [line for line in lines if line.strip() == ""]

        print(f"  输出行数: {len(lines)}")
        print(f"  空行数: {len(empty_lines)}")
        print(f"  输出内容:")
        for i, line in enumerate(lines):
            if line.strip() == "":
                print(f"    {i+1}: [空行]")
            else:
                print(f"    {i+1}: {line}")

        # 分析空行位置
        empty_positions = [i+1 for i, line in enumerate(lines) if line.strip() == ""]
        print(f"  空行位置: {empty_positions}")

        # 验证空行是否在正确位置
        if config_info['config'].get('enable_line_gap_fill', False):
            print(f"  验证空行位置:")
            for i, gap in enumerate(line_gaps):
                expected_empty_lines = round(gap / (result.line_height_ratio * result.em_unit))
                if expected_empty_lines > 0:
                    print(f"    间距{i+1}: {gap}像素 -> 期望{expected_empty_lines}空行")
                    # 检查是否有对应数量的空行


def test_real_ocr_data():
    """测试真实OCR数据的行间空行填充"""
    print(f"\n" + "=" * 50)
    print("测试真实OCR数据的行间空行填充")
    print("=" * 50)

    recovery = LayoutRecovery()
    boxes = recovery.load_rapidocr_result("rapidocr_result.json")
    result = recovery.recover_layout(boxes)

    print(f"版面恢复参数:")
    print(f"  em单位: {result.em_unit:.2f} 像素")
    print(f"  行高比例: {result.line_height_ratio:.2f}")
    print(f"  期望行高: {result.line_height_ratio * result.em_unit:.2f} 像素")

    # 分析第一个block的行间空行
    if result.blocks:
        first_block = result.blocks[0]
        print(f"\n第一个block ({first_block.block_type}):")
        print(f"  行数: {len(first_block.lines)}")

        # 计算行间距
        sorted_lines = sorted(first_block.lines, key=lambda l: l.y_position)
        line_gaps = []
        for i in range(1, len(sorted_lines)):
            gap = sorted_lines[i].y_position - (sorted_lines[i-1].y_position + sorted_lines[i-1].line_height)
            if gap > 0:
                line_gaps.append(gap)

        print(f"  行间距: {[f'{g:.1f}' for g in line_gaps]}")

        # 计算期望的空行数
        expected_line_height = result.line_height_ratio * result.em_unit
        print(f"  期望行高: {expected_line_height:.1f} 像素")

        print(f"  空行计算:")
        for i, gap in enumerate(line_gaps):
            empty_lines = round(gap / expected_line_height)
            print(f"    间距{i+1}: {gap:.1f} ÷ {expected_line_height:.1f} = {gap/expected_line_height:.3f} -> {empty_lines} 空行")

        # 生成markdown并分析
        md_output = first_block.to_markdown(enable_line_gap_fill=True, em_unit=result.em_unit, line_height_ratio=result.line_height_ratio)
        lines = md_output.split('\n')
        empty_lines = [line for line in lines if line.strip() == ""]

        print(f"\n实际输出:")
        print(f"  总行数: {len(lines)}")
        print(f"  空行数: {len(empty_lines)}")
        print(f"  空行位置: {[i+1 for i, line in enumerate(lines) if line.strip() == '']}")

        # 显示前几行
        print(f"  前10行:")
        for i, line in enumerate(lines[:10]):
            if line.strip() == "":
                print(f"    {i+1}: [空行]")
            else:
                print(f"    {i+1}: {line}")


if __name__ == "__main__":
    # 测试简单数据
    test_line_gap_algorithm()

    # 测试真实OCR数据
    test_real_ocr_data()

    print(f"\n测试完成！")
