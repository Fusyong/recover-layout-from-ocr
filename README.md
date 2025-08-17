PDF OCR Utils and Examples, especially for workbook text extraction, layout recovery, and conversion to Markdown. 

## scripts

1. pymupdf_example.py 
   - Example of using PyMuPDF for PDF to image conversion 
2. deskew_example.py
    - Example of deskewing images
3. rapidocr_example.py
    - Example of using RapidOCR for OCR
4. ocr_json2text_line.py & filter_example.py
    - Converts OCR JSON output to text lines with filtering capabilities
5. text_line2markdown.py
   - Converts text lines to Markdown format

## TODO


1. [x] OCR pipeline
    1. 使用PyMuPDF进行PDF转换为图片
    1. 使用deskew进行图像去斜处理
    1. 使用RapidOCR进行OCR识别
2. [x] 将OCR结果转换为文本行，过滤不需要的box和row
    * [x] 兼容有道OCR的JSON格式
    * [x] 兼容pymupdf的JSON格式
    * [x] 兼容RapidOCR的JSON格式
3. [x] 给文本行中的标题标出Markdown标记
4. [ ] 分切为独立题目
5. [ ] 转换成数据库，建立专项查询
6. [ ] 使用LLM修复格式错误、分切错误
7. [ ] 使用LLM转换成ConTeXt样式
