#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试text和markdown输出的差异
验证行间空行填充是否在两种输出中都生效
"""

from layout_recovery import LayoutRecovery


def test_text_vs_markdown():
    """测试text和markdown输出的差异"""
    print("测试text和markdown输出的差异")
    print("=" * 50)

    # 创建版面恢复器
    recovery = LayoutRecovery()

    # 加载OCR结果
    boxes = recovery.load_rapidocr_result("rapidocr_result.json")
    result = recovery.recover_layout(boxes)

    print(f"版面恢复结果:")
    print(f"  em单位: {result.em_unit:.2f}")
    print(f"  行高比例: {result.line_height_ratio:.2f}")
    print(f"  期望行高: {result.line_height_ratio * result.em_unit:.2f}")

    # 生成markdown输出
    print(f"\n1. Markdown输出:")
    print("-" * 30)
    md_output = result.to_markdown()
    md_lines = md_output.split('\n')
    md_empty_lines = [line for line in md_lines if line.strip() == ""]

    print(f"  总行数: {len(md_lines)}")
    print(f"  空行数: {len(md_empty_lines)}")
    print(f"  空行比例: {len(md_empty_lines)/len(md_lines)*100:.1f}%")

    # 显示前几行
    print(f"  前10行:")
    for i, line in enumerate(md_lines[:10]):
        if line.strip() == "":
            print(f"    {i+1:2d}: [空行]")
        else:
            print(f"    {i+1:2d}: {line}")

    # 生成text输出
    print(f"\n2. Text输出:")
    print("-" * 30)
    text_output = result.text
    text_lines = text_output.split('\n')
    text_empty_lines = [line for line in text_lines if line.strip() == ""]

    print(f"  总行数: {len(text_lines)}")
    print(f"  空行数: {len(text_empty_lines)}")
    print(f"  空行比例: {len(text_empty_lines)/len(text_lines)*100:.1f}%")

    # 显示前几行
    print(f"  前10行:")
    for i, line in enumerate(text_lines[:10]):
        if line.strip() == "":
            print(f"    {i+1:2d}: [空行]")
        else:
            print(f"    {i+1:2d}: {line}")

    # 对比分析
    print(f"\n3. 对比分析:")
    print("-" * 30)
    print(f"  Markdown vs Text:")
    print(f"    总行数差异: {len(md_lines) - len(text_lines)}")
    print(f"    空行数差异: {len(md_empty_lines) - len(text_empty_lines)}")

    if len(md_empty_lines) == len(text_empty_lines):
        print(f"    ✓ 空行数量一致，行间填充在两种输出中都生效")
    else:
        print(f"    ✗ 空行数量不一致，行间填充可能有问题")

    # 保存输出文件进行对比
    print(f"\n4. 保存输出文件:")
    import os
    os.makedirs("output", exist_ok=True)

    with open("output/test_markdown.md", "w", encoding="utf-8") as f:
        f.write(md_output)
    print(f"  Markdown已保存到: output/test_markdown.md")

    with open("output/test_text.txt", "w", encoding="utf-8") as f:
        f.write(text_output)
    print(f"  Text已保存到: output/test_text.txt")

    print(f"\n测试完成！请查看输出文件进行详细对比")


if __name__ == "__main__":
    test_text_vs_markdown()
