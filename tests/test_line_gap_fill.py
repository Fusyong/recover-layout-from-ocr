#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试行间空白填充功能
"""

from layout_recovery import LayoutRecovery, OCRBox


def test_line_gap_fill():
    """测试行间空白填充功能"""
    print("测试行间空白填充功能")
    print("=" * 40)

    # 创建测试数据：模拟有行间距的文本框
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一行", 0.9),      # y1=100, height=50
        OCRBox(100, 200, 200, 250, "第二行", 0.9),      # y1=200, height=50 (间距50)
        OCRBox(100, 300, 200, 350, "第三行", 0.9),      # y1=300, height=50 (间距50)
        OCRBox(100, 450, 200, 500, "第四行", 0.9),      # y1=450, height=50 (间距100)
    ]

    # 测试1：启用行间空白填充
    print("1. 启用行间空白填充:")
    config_enabled = {
        'page_left_margin': 50.0,
        'enable_left_margin_fill': True,
        'enable_line_gap_fill': True
    }
    recovery_enabled = LayoutRecovery(config_enabled)
    result_enabled = recovery_enabled.recover_layout(test_boxes)
    md_enabled = result_enabled.to_markdown()
    print(f"输出长度: {len(md_enabled)}")
    print("输出内容:")
    print(md_enabled)
    print("-" * 40)

    # 测试2：禁用行间空白填充
    print("2. 禁用行间空白填充:")
    config_disabled = {
        'page_left_margin': 50.0,
        'enable_left_margin_fill': True,
        'enable_line_gap_fill': False
    }
    recovery_disabled = LayoutRecovery(config_disabled)
    result_disabled = recovery_disabled.recover_layout(test_boxes)
    md_disabled = result_disabled.to_markdown()
    print(f"输出长度: {len(md_disabled)}")
    print("输出内容:")
    print(md_disabled)
    print("-" * 40)

    # 分析结果
    print("结果分析:")
    print(f"启用填充输出长度: {len(md_enabled)}")
    print(f"禁用填充输出长度: {len(md_disabled)}")

    # 验证行间空白填充是否生效
    if len(md_enabled) > len(md_disabled):
        print("✓ 行间空白填充功能正常工作")
    else:
        print("✗ 行间空白填充功能可能有问题")

    print("\n测试完成！")


def explain_line_gap_logic():
    """解释行间空白填充的逻辑"""
    print("\n" + "=" * 40)
    print("行间空白填充逻辑说明")
    print("=" * 40)

    print("""
行间空白填充的工作原理：

1. 行间距计算
   - 计算相邻行之间的实际距离
   - 距离 = 当前行y1 - (上一行y_position + 上一行line_height)

2. 空行数量计算
   - 基于行高比例和em单位计算期望行高
   - 期望行高 = line_height_ratio × em_unit
   - 空行数 = 实际间距 ÷ 期望行高

3. 填充逻辑
   - 如果计算出的空行数 > 0，则插入相应数量的空行
   - 空行用空字符串""表示，在markdown中会显示为换行

4. 配置选项
   - enable_line_gap_fill: 是否启用行间空白填充
   - 默认启用，可以通过配置关闭

5. 应用场景
   - 保持原始版面的行间距
   - 模拟印刷品的排版效果
   - 便于后续编辑和排版
    """)


if __name__ == "__main__":
    test_line_gap_fill()
    explain_line_gap_logic()
