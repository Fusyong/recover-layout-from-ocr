"""
将文件夹下的所有markdown文件合并为一个markdown文件
支持可选的分页标记和文件排序功能
"""

import os
import re
from typing import List, Optional, Callable
from pathlib import Path


class MarkdownMerger:
    def __init__(self, 
                 input_dir: str,
                 output_file: str = "",
                 add_page_breaks: bool = True,
                 page_break_marker: str = "---",
                 sort_by: str = "name",  # "name", "mtime", "ctime"
                 encoding: str = "utf-8"):
        """
        初始化Markdown合并器
        
        Args:
            input_dir: 输入文件夹路径
            output_file: 输出文件路径，默认为输入文件夹名.md
            add_page_breaks: 是否添加分页标记
            page_break_marker: 分页标记内容
            sort_by: 排序方式 ("name", "mtime", "ctime")
            encoding: 文件编码
        """
        self.input_dir = Path(input_dir)
        self.output_file = output_file or f"{self.input_dir.name}.md"
        self.add_page_breaks = add_page_breaks
        self.page_break_marker = page_break_marker
        self.sort_by = sort_by
        self.encoding = encoding
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"输入文件夹不存在: {input_dir}")
        if not self.input_dir.is_dir():
            raise NotADirectoryError(f"输入路径不是文件夹: {input_dir}")

    def natural_sort_key(self, filename: str) -> List:
        """
        生成自然排序的键值，将字符串中的数字按数值大小排序
        例如: "file9.md" < "file10.md" < "file20.md"
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', filename)]

    def get_markdown_files(self) -> List[Path]:
        """获取文件夹中的所有markdown文件并排序"""
        md_files = []
        for file_path in self.input_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.md', '.markdown']:
                md_files.append(file_path)
        
        # 根据指定方式排序
        if self.sort_by == "name":
            # 使用自然排序，数字按数值大小排序
            md_files.sort(key=lambda x: self.natural_sort_key(x.name))
        elif self.sort_by == "mtime":
            md_files.sort(key=lambda x: x.stat().st_mtime)
        elif self.sort_by == "ctime":
            md_files.sort(key=lambda x: x.stat().st_ctime)
        else:
            raise ValueError(f"不支持的排序方式: {self.sort_by}")
        
        return md_files

    def read_file_content(self, file_path: Path) -> str:
        """读取文件内容，处理编码问题"""
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            for encoding in ['gbk', 'gb2312', 'latin1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        print(f"警告: 文件 {file_path.name} 使用 {encoding} 编码读取")
                        return content
                except UnicodeDecodeError:
                    continue
            raise UnicodeDecodeError(f"无法读取文件 {file_path.name}，尝试了多种编码")

    def add_file_header(self, file_path: Path, content: str) -> str:
        """为文件内容添加文件头信息"""
        header = f"<!-- 文件: {file_path.name} -->\n"
        return header + content

    def merge_files(self) -> str:
        """合并所有markdown文件"""
        md_files = self.get_markdown_files()
        
        if not md_files:
            print(f"警告: 在文件夹 {self.input_dir} 中未找到markdown文件")
            return ""
        
        merged_content = []
        
        for i, file_path in enumerate(md_files):
            try:
                print(f"正在处理: {file_path.name}")
                content = self.read_file_content(file_path)
                
                # 添加文件头
                content = self.add_file_header(file_path, content)
                
                # 添加内容
                merged_content.append(content)
                
                # 添加分页标记（除了最后一个文件）
                if self.add_page_breaks and i < len(md_files) - 1:
                    merged_content.append(f"\n{self.page_break_marker}\n")
                    
            except Exception as e:
                print(f"错误: 处理文件 {file_path.name} 时出错: {e}")
                continue
        
        return "\n".join(merged_content)

    def save_merged_file(self, content: str) -> None:
        """保存合并后的文件"""
        output_path = Path(self.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding=self.encoding) as f:
            f.write(content)
        
        print(f"合并完成，输出文件: {output_path.absolute()}")

    def merge(self) -> str:
        """执行合并操作"""
        print(f"开始合并文件夹: {self.input_dir}")
        print(f"排序方式: {self.sort_by}")
        print(f"添加分页标记: {self.add_page_breaks}")
        
        content = self.merge_files()
        
        if content:
            self.save_merged_file(content)
            print(f"成功合并 {len(self.get_markdown_files())} 个文件")
        else:
            print("没有内容可合并")
        
        return content


def merge_markdown_files(input_dir: str, 
                        output_file: str = "",
                        add_page_breaks: bool = True,
                        page_break_marker: str = "---",
                        sort_by: str = "name",
                        encoding: str = "utf-8") -> str:
    """
    合并文件夹中的所有markdown文件
    
    Args:
        input_dir: 输入文件夹路径
        output_file: 输出文件路径，默认为输入文件夹名.md
        add_page_breaks: 是否添加分页标记
        page_break_marker: 分页标记内容
        sort_by: 排序方式 ("name", "mtime", "ctime")
        encoding: 文件编码
    
    Returns:
        合并后的内容字符串
    """
    merger = MarkdownMerger(
        input_dir=input_dir,
        output_file=output_file,
        add_page_breaks=add_page_breaks,
        page_break_marker=page_break_marker,
        sort_by=sort_by,
        encoding=encoding
    )
    return merger.merge()


if __name__ == "__main__":
    # 示例用法
    merge_markdown_files("E:/语文出版社/2025/人教教师教学用书语文一年级上册-集团质检/img_preprocessed/", "E:/语文出版社/2025/人教教师教学用书语文一年级上册-集团质检/合并.md", add_page_breaks=True, page_break_marker="---page---", sort_by="name", encoding="utf-8")   