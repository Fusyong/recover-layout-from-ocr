#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版心左侧空白填充功能
"""

from layout_recovery import LayoutRecovery, OCRBox


def test_margin_fill():
    """测试版心左侧空白填充功能"""
    print("测试版心左侧空白填充功能")
    print("=" * 40)

    # 创建测试数据：模拟不同位置的文本框
    test_boxes = [
        OCRBox(150, 100, 250, 150, "标题", 0.9),      # 距离版心左侧50像素
        OCRBox(200, 200, 300, 250, "内容", 0.9),      # 距离版心左侧100像素
        OCRBox(120, 300, 220, 350, "列表", 0.9),      # 距离版心左侧20像素
    ]

    # 测试1：默认配置（版心左侧100像素）
    print("1. 默认配置（版心左侧100像素）:")
    recovery_default = LayoutRecovery()
    result_default = recovery_default.recover_layout(test_boxes)
    md_default = result_default.to_markdown()
    print(f"输出长度: {len(md_default)}")
    print("输出内容:")
    print(md_default)
    print("-" * 40)

    # 测试2：自定义版心左侧位置（50像素）
    print("2. 自定义配置（版心左侧50像素）:")
    config_50 = {'page_left_margin': 50.0, 'enable_left_margin_fill': True}
    recovery_50 = LayoutRecovery(config_50)
    result_50 = recovery_50.recover_layout(test_boxes)
    md_50 = result_50.to_markdown()
    print(f"输出长度: {len(md_50)}")
    print("输出内容:")
    print(md_50)
    print("-" * 40)

    # 测试3：禁用空白填充
    print("3. 禁用空白填充:")
    config_disabled = {'page_left_margin': 100.0, 'enable_left_margin_fill': False}
    recovery_disabled = LayoutRecovery(config_disabled)
    result_disabled = recovery_disabled.recover_layout(test_boxes)
    md_disabled = result_disabled.to_markdown()
    print(f"输出长度: {len(md_disabled)}")
    print("输出内容:")
    print(md_disabled)
    print("-" * 40)

    # 分析结果
    print("结果分析:")
    print(f"默认配置输出长度: {len(md_default)}")
    print(f"50像素配置输出长度: {len(md_50)}")
    print(f"禁用填充输出长度: {len(md_disabled)}")

    # 验证空白填充是否生效
    if len(md_default) > len(md_disabled):
        print("✓ 空白填充功能正常工作")
    else:
        print("✗ 空白填充功能可能有问题")

    print("\n测试完成！")


if __name__ == "__main__":
    test_margin_fill()
