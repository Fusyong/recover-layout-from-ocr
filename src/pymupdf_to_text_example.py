"""
使用pymupdf抽取pdf中的活文本和文本块信息
"""

import os
import json
import pymupdf


def pdf_to_json(pdf_path: str, output_path: str=""):
    if not output_path:
        output_path = pdf_path.replace(".pdf", ".json")

    doc = pymupdf.open(pdf_path) # Replace with your PDF file

    for page_num in range(doc.page_count):
        json_output = []
        page = doc.load_page(page_num)
        # https://pymupdf.readthedocs.io/en/latest/app1.html
        # "text", sort=True 按原始顺序提取文本
        # “xhtml” 包含文本和图像
        # "blocks", sort=True 按原始顺序提取块（文本和图像）为列表：
        # (x0, y0, x1, y1, "lines in block", block_no, block_type)
        # “words”, sort=True 按原始顺序提取单词为列表：
        # (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        # “html”
        # “xml”
        # “dict”/"json", sort=False 输出全备的页面信息包括base64图像
        # “rawdict”, sort=False 同上，文本细化为字符级别
        page_json_str = page.get_text("json", sort=False) 
        json_output.append(json.loads(page_json_str))
        
        # 逐页保存为json
        page_json_path = output_path.replace(".json", f"_{page_num + 1}.json")
        with open(page_json_path, "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=4, ensure_ascii=False)

    doc.close()

def pdfs_to_json(pdf_dir: str, output_dir: str=""):
    if not output_dir:
        output_dir = pdf_dir
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith(".pdf"):
            pdf_to_json(os.path.join(pdf_dir, pdf_file), os.path.join(output_dir, pdf_file.replace(".pdf", ".json")))

if __name__ == "__main__":
    # 转换单个pdf
    pdf_path = "C:/Users/DELL/Desktop/南宋经学史/南宋经学史.pdf"
    pdf_to_json(pdf_path)

    # # 转换多个pdf
    # pdf_dir = "pdf"
    # pdfs_to_json(pdf_dir)