"""通用OCR JSON过滤器
支持box数据和row数据的自动适配
"""

def _get_data_info(data):
    """自动检测数据类型并返回标准化的数据访问接口
    
    Args:
        data: 可能是box_data或row_data
        
    Returns:
        dict: 包含标准化数据访问方法的字典
    """
    if 'row_bounds' in data:
        # row_data格式
        return {
            'type': 'row',
            'x': data['row_bounds']['x'],
            'y': data['row_bounds']['y'],
            'width': data['row_bounds']['width'],
            'height': data['row_bounds']['height'],
            'text': data['row_text'],
            'text_length': data['text_length'],
            'fragment_count': data['fragment_count']
        }
    else:
        # box_data格式
        return {
            'type': 'box',
            'x': data['x'],
            'y': data['y'],
            'width': data['width'],
            'height': data['height'],
            'text': data['text'],
            'text_length': len(data['text']),
            'fragment_count': 1
        }

def filter_small_width(data, page_info):
    """滤除宽度小于一定像素的内容（box或row）"""
    info = _get_data_info(data)
    return info['width'] >= 15

def filter_abnormal_height(data, page_info):
    """滤除高度异常的内容（可能是噪声）"""
    info = _get_data_info(data)
    height = info['height']
    # 假设正常文本高度在10-100像素之间
    return 10 <= height <= 100

def filter_header(data, page_info):
    """滤除页眉区域的内容"""
    if page_info['page_height'] <= 0:
        return True

    info = _get_data_info(data)
    text = info['text'].lower().replace(' ', '')
    keywords_to_filter = ['语文', '六年级上册']

    if info['y'] <= 0.2 * page_info['page_height'] \
        and all(keyword in text for keyword in keywords_to_filter):
        return False
    return True

def filter_footer(data, page_info):
    """滤除页眉区域的内容"""
    if page_info['page_height'] <= 0:
        return True

    info = _get_data_info(data)
    text = info['text'].lower().replace(' ', '')
    keywords_to_filter = ['时间', '语文·六年级上册']

    if info['y'] >= 0.9 * page_info['page_height'] \
        and all(keyword in text for keyword in keywords_to_filter):
        return False
    return True

def filter_page_number(data, page_info):
    """滤除页码
    条件：
    1. y坐标在页面高度90%之下（左上角为原点）
    2. 文本全部为数字
    """
    info = _get_data_info(data)
    if info['y'] >= 0.9 * page_info['page_height'] \
        and all(char.isdigit() for char in info['text'].replace(' ', '')):
        return False
    return True

def filter_left_sidebar(data, page_info):
    """滤除左侧边栏区域的内容"""
    if page_info['page_width'] <= 0:
        return True
    
    info = _get_data_info(data)
    x = info['x']
    page_width = page_info['page_width']
    
    # 滤除左侧20%的区域（假设是边栏）
    return x >= 0.2 * page_width

def filter_right_sidebar(data, page_info):
    """滤除右侧边栏区域的内容"""
    if page_info['page_width'] <= 0:
        return True
    
    info = _get_data_info(data)
    x = info['x']
    page_width = page_info['page_width']
    
    # 滤除右侧20%的区域（假设是边栏）
    return x <= 0.8 * page_width

def filter_any_keywords(data, page_info):
    """滤除包含特定关键词的内容"""
    info = _get_data_info(data)
    text = info['text'].lower().replace(' ', '')
    keywords_to_filter = ['时间', '语文·六年级上册']
    
    for keyword in keywords_to_filter:
        if keyword in text:
            return False
    return True

def filter_all_keywords(data, page_info):
    """滤除包含所有关键词的内容"""
    info = _get_data_info(data)
    text = info['text'].lower().replace(' ', '')
    keywords_to_filter = ['语文', '六年级上册']
    
    for keyword in keywords_to_filter:
        if keyword not in text:
            return True
    return False



if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.ocr_json2text_line import convert_json_to_text
    
    # 盒级过滤器
    box_filters = [
        # filter_small_width,     # 滤除宽度太小的内容
        # filter_abnormal_height, # 滤除高度异常的内容
        # filter_header,          # 滤除页眉
        # filter_footer,          # 滤除页脚
        # filter_page_number,     # 滤除页码
        # filter_left_sidebar,    # 滤除左侧边栏
        # filter_right_sidebar,   # 滤除右侧边栏
        # filter_any_keywords,    # 滤除包含任意关键词的内容
        # filter_all_keywords,    # 滤除包含所有关键词的内容
    ]
    # 行级过滤器
    row_filters = [
        # filter_small_width,     # 滤除宽度太小的内容
        # filter_abnormal_height, # 滤除高度异常的内容
        filter_header,          # 滤除页眉
        # filter_footer,          # 滤除页脚
        filter_page_number,     # 滤除页码
        # filter_left_sidebar,    # 滤除左侧边栏
        # filter_right_sidebar,   # 滤除右侧边栏
        # filter_any_keywords,    # 滤除包含任意关键词的内容
        # filter_all_keywords,    # 滤除包含所有关键词的内容
    ]
    
    # 可以同时用于box和行级过滤
    convert_json_to_text(
        'img_1_dsk.json', 
        'img_1_dsk.txt',
        box_filters,         # box级过滤
        row_filters          # 行级过滤
    )
