"""
整理分行纯文本（OCR结果或者PDF转文本）为 Markdown
"""

import os
import re
from typing import List


class TextLineToMarkdown:
    def __init__(self, content_table: str = "", toc_start_level:int=1, centered_level:int=4, chinese_list_level:int=5):
        self.question_line_patterns = [
            r'^[一二三四五六七八九十]+[、]',
        ]
        self.contents_list = self.get_contents_list(content_table, toc_start_level)
        self.centered_level = centered_level
        self.chinese_list_level = chinese_list_level

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
            line = re.sub(r'…*\s*\d*$', '', line)
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
        """判断是否是汉字序号列表行"""
        s = text.strip()
        return any(re.match(p, s) for p in self.question_line_patterns)

    def is_in_contents(self, text: str) -> int|bool:
        text = text.replace(' ', '')
        for i in self.contents_list:
            if i[1].replace(' ', '') == text:
                return i[0]
        return False

    def is_centered(self, text:str) -> bool:
        """判断是否是居中行
        左右填充有个数大致相同的空格"""
        threshold = 4
        left_spaces = len(text) - len(text.lstrip(' '))
        right_spaces = len(text) - len(text.rstrip(' '))
        if (left_spaces + right_spaces) > 40 and abs(left_spaces - right_spaces) < threshold:
            return True
        return False

    def convert_text_to_markdown(self, lines: List[str], centered_level: int | None = None, chinese_list_level: int | None = None) -> str:
        # 未显式传入时，使用实例初始化时的配置
        effective_centered_level = centered_level if centered_level is not None else self.centered_level
        effective_chinese_list_level = chinese_list_level if chinese_list_level is not None else self.chinese_list_level
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
            # 标记目录
            if level := self.is_in_contents(content):
                md_lines.append(f"{'#' * level} {line.strip()}")
            # 标记居中行（基于原始行的左右空格判断）
            elif self.is_centered(line):
                md_lines.append(f"{'#' * effective_centered_level} {content.strip()}")
            # 标记习题大题行
            elif self.question_line(content):
                md_lines.append(f"{'#' * effective_chinese_list_level} {content.strip()}")
            else:
                md_lines.append(line)

        # 不做列表合并，保留原始行结构
        return '\n'.join(md_lines)

def markdown_text_with_toc(text_path: str, out_path: str='', toc: str = "", toc_start_level:int=1, centered_level:int=4, chinese_list_level:int=5) -> str:
    """将文本转换为Markdown，根据目录标记标题级别"""
    if not out_path:
        out_path = re.sub(r'\.[^\.]+$', '.md', text_path)   
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
        md_conv = TextLineToMarkdown(toc, toc_start_level, centered_level, chinese_list_level)
        md = md_conv.convert_text_to_markdown(text.split('\n'))
        if out_path:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(md)
        return md

def markdown_texts_with_toc(text_dir: str, out_dir: str='', toc: str = "", toc_start_level:int=1, centered_level:int=4, chinese_list_level:int=5) -> str:
    """将文本转换为Markdown，根据目录标记标题级别"""
    if not out_dir:
        out_dir = text_dir
    for text_path in os.listdir(text_dir):
        if text_path.endswith('.txt'):
            markdown_text_with_toc(os.path.join(text_dir, text_path), os.path.join(out_dir, text_path.replace('.txt', '.md')), toc, toc_start_level, centered_level, chinese_list_level)

if __name__ == "__main__":
    TOC = """
目录

第一单元
    1    古诗三首                    1
    2    燕子                      4
    3    荷花                      7
    4* 昆虫备忘录                  10
    单元巩固练习                  12

第二单元
    5    守株待兔                   15
    6    陶罐和铁罐                  18
    7    鹿角和鹿腿                  21
    8* 池子与河流                  24
    快乐读书吧                   26
    单元巩固练习                  28

第三单元
    9    古诗三首                   30
    10 纸的发明                   33
    11 赵州桥                    36
    12* 一幅名扬中外的画               39
    单元巩固练习                  41

第四单元
    13 花钟                     44
    14 蜜蜂                     47
    15* 小虾                     50
    单元巩固练习                  52

第五单元
    16 宇宙的另一边                 54
    17 我变成了一棵树                57
    单元巩固练习                 60

第六单元
    18 童年的水墨画                 62
    19 剃头大师                   65
    20 肥皂泡                    68
    21* 我不能失信                  71
    单元巩固练习                  73

第七单元
    22 我们奇妙的世界                76
    23 海底世界                   79
    24 火烧云                    82
    单元巩固练习                  85

第八单元
    25 慢性子裁缝和急性子顾客            88
    26* 方帽子店                   91
    27 漏                      93
    28* 枣核                     96
    单元巩固练习                  98

部分参考答案                 101
    栏目设置
        基础练习
        阅读拓展
        实践运用
    """
    # 转换单个文本
    # markdown_text_with_toc('tests/assets/img_1_dsk.txt', 'tests/assets/img_1_dsk.md', TOC, 2)
    # 转换文件夹中的所有文本
    markdown_texts_with_toc('E:\\语文出版社\\2025\\四川同步学与练修订项目下册\\校对\\', toc=TOC, toc_start_level=1, centered_level=5, chinese_list_level=5)
