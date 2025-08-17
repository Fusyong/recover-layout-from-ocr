#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试真实OCR数据的行间空行填充
"""

from layout_recovery import LayoutRecovery


def test_real_ocr_line_gaps():
    """测试真实OCR数据的行间空行填充"""
    print("测试真实OCR数据的行间空行填充")
    print("=" * 50)

    recovery = LayoutRecovery()
    boxes = recovery.load_rapidocr_result("rapidocr_result.json")
    result = recovery.recover_layout(boxes)

    print(f"版面恢复参数:")
    print(f"  em单位: {result.em_unit:.2f} 像素")
    print(f"  行高比例: {result.line_height_ratio:.2f}")
    print(f"  期望行高: {result.line_height_ratio * result.em_unit:.2f} 像素")

    # 分析每个block的行间空行
    for block_idx, block in enumerate(result.blocks):
        print(f"\nBlock {block_idx + 1} ({block.block_type}):")
        print("-" * 40)

        # 计算行间距
        sorted_lines = sorted(block.lines, key=lambda l: l.y_position)
        line_gaps = []
        for i in range(1, len(sorted_lines)):
            gap = sorted_lines[i].y_position - (sorted_lines[i-1].y_position + sorted_lines[i-1].line_height)
            if gap > 0:
                line_gaps.append(gap)

        print(f"  行数: {len(sorted_lines)}")
        print(f"  行间距: {[f'{g:.1f}' for g in line_gaps]}")

        # 计算期望的空行数
        expected_line_height = result.line_height_ratio * result.em_unit

        print(f"  空行计算:")
        total_expected_empty = 0
        for i, gap in enumerate(line_gaps):
            empty_lines = round(gap / expected_line_height)
            total_expected_empty += empty_lines
            print(f"    间距{i+1}: {gap:.1f} ÷ {expected_line_height:.1f} = {gap/expected_line_height:.3f} -> {empty_lines} 空行")

        print(f"  总期望空行数: {total_expected_empty}")

        # 生成markdown并分析
        md_output = block.to_markdown(enable_line_gap_fill=True, em_unit=result.em_unit, line_height_ratio=result.line_height_ratio)
        lines = md_output.split('\n')
        empty_lines = [line for line in lines if line.strip() == ""]

        print(f"  实际输出:")
        print(f"    总行数: {len(lines)}")
        print(f"    空行数: {len(empty_lines)}")
        print(f"    空行位置: {[i+1 for i, line in enumerate(lines) if line.strip() == '']}")

        # 验证空行数量
        if len(empty_lines) == total_expected_empty:
            print(f"    ✓ 空行数量正确")
        else:
            print(f"    ✗ 空行数量不匹配: 期望{total_expected_empty}, 实际{len(empty_lines)}")

        # 显示前几行
        print(f"    前8行:")
        for i, line in enumerate(lines[:8]):
            if line.strip() == "":
                print(f"      {i+1}: [空行]")
            else:
                # 显示行首空格数量
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces > 0:
                    print(f"      {i+1}: {' ' * min(leading_spaces, 5)}[{leading_spaces}空格]{line.strip()}")
                else:
                    print(f"      {i+1}: {line}")

    # 整体验证
    print(f"\n整体验证:")
    print("-" * 40)

    # 生成完整markdown
    full_md = result.to_markdown()
    full_lines = full_md.split('\n')
    full_empty_lines = [line for line in full_lines if line.strip() == ""]

    print(f"完整输出:")
    print(f"  总行数: {len(full_lines)}")
    print(f"  空行数: {len(full_empty_lines)}")
    print(f"  空行比例: {len(full_empty_lines)/len(full_lines)*100:.1f}%")

    # 保存输出文件
    print(f"\n保存输出文件:")
    import os
    os.makedirs("output", exist_ok=True)

    with open("output/fixed_line_gaps.md", "w", encoding="utf-8") as f:
        f.write(full_md)
    print(f"  已保存到: output/fixed_line_gaps.md")

    # 显示空行分布
    print(f"\n空行分布分析:")
    empty_positions = [i+1 for i, line in enumerate(full_lines) if line.strip() == ""]
    print(f"  空行位置: {empty_positions[:20]}{'...' if len(empty_positions) > 20 else ''}")

    # 统计连续空行
    consecutive_empty = 0
    max_consecutive = 0
    for line in full_lines:
        if line.strip() == "":
            consecutive_empty += 1
            max_consecutive = max(max_consecutive, consecutive_empty)
        else:
            consecutive_empty = 0

    print(f"  最大连续空行数: {max_consecutive}")


if __name__ == "__main__":
    test_real_ocr_line_gaps()
    print(f"\n测试完成！")
