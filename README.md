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

## Usage

### Layout Parameters

The `OCRJsonToTextLine` class now allows users to set layout parameters during initialization or optionally override them later:

```python
from src.ocr_json2text_line import OCRJsonToTextLine

# Method 1: Set parameters during initialization (recommended)
converter = OCRJsonToTextLine(
    dpi=300,                    # DPI resolution (default: 300)
    char_height=28.0,           # Character height in pixels (default: 50.0)
    line_height_multiplier=1.6  # Line height multiplier (default: 1.5)
)

# Method 2: Override parameters after initialization (optional)
converter.set_layout_params(
    char_height=32.0,           # Override character height
    line_height_multiplier=1.8  # Override line height multiplier
)

# Convert OCR JSON to text
text = converter.convert_json_to_text(ocr_json)
```

**Parameters:**
- `dpi`: DPI resolution for coordinate conversion, especially important for pymupdf format (default: 300)
- `char_height`: Character height in pixels, used for calculating spaces and indentation (default: 50.0)
- `line_height_multiplier`: Line height multiplier, used for calculating line spacing (default: 1.5)

**Default values:**
- `dpi`: 300
- `char_height`: 50.0 pixels
- `line_height_multiplier`: 1.5

**Note:** Parameters are now set during initialization, making the converter ready to use immediately. The `set_layout_params()` method is optional and only needed if you want to override the initial values.

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
