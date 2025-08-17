#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的功能测试
"""

from layout_recovery import LayoutRecovery

def main():
    print("简单功能测试")
    print("=" * 30)

    # 创建版面恢复器
    recovery = LayoutRecovery()
    print("✓ 版面恢复器创建成功")

    # 测试处理实际文件
    try:
        result = recovery.process_file("rapidocr_result.json", "markdown")
        print(f"✓ 文件处理成功，输出长度: {len(result)}")
        print(f"前100字符: {result[:100]}")
    except Exception as e:
        print(f"✗ 文件处理失败: {e}")

    print("\n测试完成！")

if __name__ == "__main__":
    main()
