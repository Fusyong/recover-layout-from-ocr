#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR版面恢复模块测试文件

测试各个功能模块是否正常工作
"""

import json
import tempfile
import os
from layout_recovery import LayoutRecovery, OCRBox, TextLine, TextBlock


def test_ocrbox_creation():
    """测试OCRBox创建和属性"""
    print("测试OCRBox创建...")

    # 创建OCRBox
    box = OCRBox(
        x1=100, y1=200, x2=300, y2=250,
        text="测试文本", score=0.95
    )

    # 测试属性
    assert box.center_x == 200
    assert box.center_y == 225
    assert box.width == 200
    assert box.height == 50
    assert box.text == "测试文本"
    assert box.score == 0.95

    print("✓ OCRBox测试通过")


def test_ocrbox_from_rapidocr():
    """测试从RapidOCR数据创建OCRBox"""
    print("测试从RapidOCR数据创建OCRBox...")

    rapidocr_data = {
        "box": [[100, 200], [300, 200], [300, 250], [100, 250]],
        "txt": "测试文本",
        "score": 0.95
    }

    box = OCRBox.from_rapidocr(rapidocr_data)

    assert box.x1 == 100
    assert box.y1 == 200
    assert box.x2 == 300
    assert box.y2 == 250
    assert box.text == "测试文本"
    assert box.score == 0.95

    print("✓ RapidOCR数据转换测试通过")


def test_textline_creation():
    """测试TextLine创建和功能"""
    print("测试TextLine创建...")

    # 创建文本框
    box1 = OCRBox(100, 200, 200, 250, "第一", 0.9)
    box2 = OCRBox(250, 200, 350, 250, "第二", 0.9)

    # 创建文本行
    line = TextLine(boxes=[box1], y_position=225, line_height=50)
    line.add_box(box2)

    # 测试属性
    assert len(line.boxes) == 2
    assert line.text == "第一第二"
    assert line.x_range == (100, 350)

    # 测试Markdown转换
    md = line.to_markdown()
    assert "第一" in md
    assert "第二" in md

    print("✓ TextLine测试通过")


def test_textblock_creation():
    """测试TextBlock创建和功能"""
    print("测试TextBlock创建...")

    # 创建文本行
    line1 = TextLine(boxes=[OCRBox(100, 200, 200, 250, "标题", 0.9)],
                     y_position=225, line_height=50)
    line2 = TextLine(boxes=[OCRBox(100, 300, 400, 350, "内容文本", 0.9)],
                     y_position=325, line_height=50)

    # 创建文本块
    block = TextBlock(lines=[line1], block_type="title")
    block.add_line(line2)

    # 测试属性
    assert len(block.lines) == 2
    assert "标题" in block.text
    assert "内容文本" in block.text

    # 测试Markdown转换
    md = block.to_markdown()
    assert md.startswith("#")

    print("✓ TextBlock测试通过")


def test_layout_recovery():
    """测试版面恢复功能"""
    print("测试版面恢复功能...")

    # 创建测试数据
    test_boxes = [
        OCRBox(100, 100, 200, 150, "第一单元", 0.9),
        OCRBox(100, 200, 300, 250, "1观潮", 0.9),
        OCRBox(100, 300, 400, 350, "导学", 0.9),
        OCRBox(100, 400, 500, 450, "课前准备", 0.9),
    ]

    # 创建版面恢复器
    recovery = LayoutRecovery()

    # 执行版面恢复
    result = recovery.recover_layout(test_boxes)

    # 测试结果
    assert result.em_unit > 0
    assert result.line_height_ratio > 0
    assert len(result.blocks) > 0

    print("✓ 版面恢复测试通过")


def test_file_processing():
    """测试文件处理功能"""
    print("测试文件处理功能...")

    # 创建临时测试文件
    test_data = [
        {
            "box": [[100, 100], [200, 100], [200, 150], [100, 150]],
            "txt": "测试标题",
            "score": 0.9
        },
        {
            "box": [[100, 200], [300, 200], [300, 250], [100, 250]],
            "txt": "测试内容",
            "score": 0.9
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_file = f.name

    try:
        # 测试文件处理
        recovery = LayoutRecovery()
        result = recovery.process_file(temp_file, "markdown")

        assert "测试标题" in result
        assert "测试内容" in result

        print("✓ 文件处理测试通过")

    finally:
        # 清理临时文件
        os.unlink(temp_file)


def test_output_formats():
    """测试输出格式"""
    print("测试输出格式...")

    # 创建测试数据
    test_boxes = [
        OCRBox(100, 100, 200, 150, "测试", 0.9),
    ]

    recovery = LayoutRecovery()
    result = recovery.recover_layout(test_boxes)

    # 测试Markdown输出
    md = result.to_markdown()
    assert isinstance(md, str)
    assert len(md) > 0

    # 测试JSON输出
    json_str = result.to_json()
    assert isinstance(json_str, str)
    json_data = json.loads(json_str)
    assert 'blocks' in json_data
    assert 'em_unit' in json_data

    # 测试纯文本输出
    text = result.text
    assert isinstance(text, str)
    assert "测试" in text

    print("✓ 输出格式测试通过")


def run_all_tests():
    """运行所有测试"""
    print("开始运行OCR版面恢复模块测试...")
    print("=" * 50)

    try:
        test_ocrbox_creation()
        test_ocrbox_from_rapidocr()
        test_textline_creation()
        test_textblock_creation()
        test_layout_recovery()
        test_file_processing()
        test_output_formats()

        print("=" * 50)
        print("🎉 所有测试通过！OCR版面恢复模块工作正常。")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
