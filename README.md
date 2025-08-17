PDF OCR Utils and Examples, especially for text extraction, layout recovery, and conversion to Markdown. 

## scripts

1. pymupdf_example.py
2. deskew_example.py
3. rapidocr_example.py
4. ocr_json2text_line.py
5. text_line2markdown.py
6. filter_example.py

## Features

### OCR JSON Filtering System

The `ocr_json2text_line.py` script now includes a powerful filtering system that allows users to:

- **Filter boxes by size**: Remove boxes that are too small or too large
- **Filter by position**: Remove boxes in specific areas (headers, footers, sidebars)
- **Filter by content**: Remove boxes containing specific keywords or patterns
- **Filter by dimensions**: Remove boxes with abnormal height/width ratios
- **Custom filters**: Write your own filtering functions using box data and page information

#### Usage Example

```python
from src.ocr_json2text_line import OCRJsonToTextLine

converter = OCRJsonToTextLine()

# Define custom filter functions
def filter_small_boxes(box_data, page_info):
    return box_data['width'] >= 20

def filter_header_footer(box_data, page_info):
    y = box_data['y']
    page_height = page_info['page_height']
    return 0.1 * page_height <= y <= 0.9 * page_height

# Start the filtering system
converter.boxFilter(filter_small_boxes, filter_header_footer)

# Start the row-level filtering system
converter.rowBoxFilter(filter_short_rows, filter_header_rows)

# Now convert with filters applied
text = converter.convert_json_to_text(ocr_json)
```

#### Filter Function Interface

**Box-level filters:**
Each filter function should:
- Accept parameters: `(box_data, page_info)`
- Return `bool`: `True` to keep the box, `False` to remove it
- `box_data` contains: `text`, `x`, `y`, `width`, `height`, `bbox`, `line`, `region`
- `page_info` contains: `page_width`, `page_height`

**Row-level filters:**
Each filter function should:
- Accept parameters: `(row_data, page_info)`
- Return `bool`: `True` to keep the row, `False` to remove it
- `row_data` contains: `row_fragments`, `row_text`, `row_bounds`, `fragment_count`, `text_length`
- `page_info` contains: `page_width`, `page_height`

## TODO

1. [x] ocr_json过滤，删除不需要的box
2. [ ] text_line过滤，删除不需要的line
3. [ ] 分切为独立题目
4. [ ] 转换成数据库，建立专项查询
5. [ ] 使用LLM修复格式错误、分切错误
6. [ ] 使用LLM转换成ConTeXt样式
