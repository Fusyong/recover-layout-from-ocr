"""
整理分行纯文本（OCR结果或者PDF转文本）为 Markdown
"""

import os
import re
from typing import List


class TextLineToMarkdown:
    def __init__(self, content_table: str = "", start_level:int=1):
        self.question_line_patterns = [
            r'^[一二三四五六七八九十]+[、]',
        ]
        self.contents_list = self.get_contents_list(content_table, start_level)

    def get_contents_list(self,contents: str, start_level:int=1) -> List:
        """将目录转换为列表，每个元素是一个元组，包含级别、名称、页码
        目录格式（前面的缩进量表示级别，后面的数字和数字前的…没有意义，字符之间的空格没有意义）：
        第一单元 ……………………………………  1
            1 课文名称 ……………………………………  3
            2    课文名称 ……………………………………8
        第二单元 ……………………………………  10
            1* 课文名称 ……………………………………  11
            2  课文名称……………………………………  12
        第三单元 ……………………………………  13
            1*   课文名称 ……………………………………  14
        """
        contents_list = []
        space_num_list = [] # 记录每行前面的空格数
        for line in contents.split('\n'):
            line = line.rstrip()
            if not line:
                continue
            space_num = len(line) - len(line.lstrip(' '))
            space_num_list.append(space_num)
            # 提取最后的数字，即页码
            page = re.search(r'\d+$', line)
            # 删除后面的`…+ *\d*`
            line = re.sub(r'…\s*\d*', '', line)
            # 提取名称
            name = line.strip()
            contents_list.append([space_num, name, page])

        # 整理目录，把空格数量转换成级别，使级别连续
        level_list = list(set(space_num_list))
        level_list.sort()
        for i in contents_list:
            i[0] = level_list.index(i[0]) + start_level

        return contents_list

    def question_line(self, text: str) -> bool:
        """判断是否是问题（大题）行"""
        s = text.strip()
        return any(re.match(p, s) for p in self.question_line_patterns)

    def is_in_contents(self, text: str) -> int|bool:
        text = text.replace(' ', '')
        for i in self.contents_list:
            if i[1].replace(' ', '') == text:
                return i[0]
        return False

    def convert_text_to_markdown(self, lines: List[str]) -> str:
        md_lines: List[str] = []
        for line in lines:
            # 保留空行和整行空格
            if not line:
                md_lines.append('')
                continue
            # 保留行首缩进（不 strip 左侧空格）
            left_spaces = len(line) - len(line.lstrip(' '))
            content = line.lstrip(' ')
            # 如果移除左侧空格后内容为空，说明这行全是空格，应该保留
            if not content:
                md_lines.append(line)
                continue
            if level := self.is_in_contents(content):
                md_lines.append(f"{'#' * level} {line.strip()}")
            elif self.question_line(content):
                md_lines.append(f"{'#' * 4} {content.strip()}")
            else:
                md_lines.append(line)

        # 不做列表合并，保留原始行结构
        return '\n'.join(md_lines)

def markdown_text_with_toc(text_path: str, out_path: str='', toc: str = "", start_level:int=1) -> str:
    """将文本转换为Markdown，根据目录标记标题级别"""
    if not out_path:
        out_path = re.sub(r'\.[^\.]+$', '.md', text_path)   
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
        md_conv = TextLineToMarkdown(toc, start_level)
        md = md_conv.convert_text_to_markdown(text.split('\n'))
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(md)
        return md

def markdown_texts_with_toc(text_dir: str, out_dir: str='', toc: str = "", start_level:int=1) -> str:
    """将文本转换为Markdown，根据目录标记标题级别"""
    if not out_dir:
        out_dir = text_dir
    for text_path in os.listdir(text_dir):
        if text_path.endswith('.txt'):
            markdown_text_with_toc(os.path.join(text_dir, text_path), os.path.join(out_dir, text_path.replace('.txt', '.md')), toc, start_level)

if __name__ == "__main__":
    TOC = """
    语文园地五
        学会运用
    """
    # 转换单个文本
    markdown_text_with_toc('tests/assets/img_1_dsk.txt', 'tests/assets/img_1_dsk.md', TOC, 2)
    # 转换文件夹中的所有文本
    markdown_texts_with_toc('img_dsk', toc=TOC, start_level=2)
