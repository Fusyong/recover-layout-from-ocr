"""
OCR JSON结果转文本行（含版面空格/空行）转换器
支持有道智云OCR API和pymupdf返回的JSON格式
"""

import json
import os
import pathlib
import statistics
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class TextDirection(Enum):
    """文本方向枚举"""
    HORIZONTAL = 'h'  # 水平
    VERTICAL = 'v'    # 垂直


@dataclass
class BoundingBox:
    """边界框信息"""
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_string(cls, bbox_str: str) -> 'BoundingBox':
        """从字符串解析边界框信息

        兼容两类格式：
        - "x,y,width,height"
        - "x1,y1,x2,y2,x3,y3,x4,y4"（四角点坐标，多边形）
        """
        try:
            parts = [p.strip() for p in bbox_str.split(',') if p.strip()]
            # 宽高格式
            if len(parts) == 4:
                x, y, w, h = map(int, parts)
                return cls(x=x, y=y, width=w, height=h)

            # 四点格式（取外接矩形）
            if len(parts) == 8:
                xs = list(map(int, [parts[0], parts[2], parts[4], parts[6]]))
                ys = list(map(int, [parts[1], parts[3], parts[5], parts[7]]))
                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)
                return cls(x=min_x, y=min_y, width=max_x - min_x, height=max_y - min_y)
        except (ValueError, IndexError):
            pass
        return cls(0, 0, 0, 0)


@dataclass
class Word:
    """单词信息"""
    word: str
    boundingBox: BoundingBox

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Word':
        return cls(
            word=data.get('word', ''),
            boundingBox=BoundingBox.from_string(data.get('boundingBox', '0,0,0,0'))
        )


@dataclass
class Line:
    """行信息"""
    text: str
    words: List[Word]
    boundingBox: BoundingBox
    text_height: int = 0
    style: str = ''

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Line':
        words = [Word.from_dict(word_data) for word_data in data.get('words', [])]
        return cls(
            text=data.get('text', ''),
            words=words,
            boundingBox=BoundingBox.from_string(data.get('boundingBox', '0,0,0,0')),
            text_height=int(data.get('text_height', 0) or 0),
            style=str(data.get('style', '') or '')
        )


@dataclass
class Region:
    """区域信息"""
    lang: str
    dir: str
    lines: List[Line]
    boundingBox: BoundingBox

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Region':
        lines = [Line.from_dict(line_data) for line_data in data.get('lines', [])]
        return cls(
            lang=data.get('lang', ''),
            dir=data.get('dir', 'h'),
            lines=lines,
            boundingBox=BoundingBox.from_string(data.get('boundingBox', '0,0,0,0'))
        )


class OCRJsonToTextLine:
    """OCR JSON → 纯文本行（含版面空格/空行）转换器"""

    def __init__(self, dpi: int = 300, char_height: float = 50.0, line_height_multiplier: float = 1.5):
        # 同行判定阈值（占行距比例）
        self.same_line_threshold_ratio = 0.8
        # 盒级过滤器列表
        self.box_filters: List[callable] = []
        # 行级过滤器列表
        self.row_filters: List[callable] = []
        # 页面尺寸信息（用于过滤器）
        self.page_width: int = 0
        self.page_height: int = 0
        # 过滤日志文件
        self.log_file: str = "ocr_json2text_line_filter.log"
        # 用户设置的布局参数
        self.char_height: float = char_height  # 汉字字符高度（像素），必须通过set_layout_params设置
        self.line_height_multiplier: float = line_height_multiplier  # 行高是汉字字符高度的倍数
        self.dpi: int = dpi  # 分辨率

    def set_log_file(self, log_file: str) -> None:
        """设置过滤日志文件名

        Args:
            log_file: 日志文件名
        """
        self.log_file = log_file

    def set_layout_params(self, dpi: int = None, char_height: float = None, line_height_multiplier: float = None) -> None:
        """设置布局参数（可选，用于覆盖初始化时的设置）

        Args:
            char_height: 字符高度（像素），用于计算空格和缩进，如果提供则必须大于0
            line_height_multiplier: 行高倍数，用于计算行间距
        """
        if dpi is not None:
            self.dpi = int(dpi)

        if char_height is not None:
            if char_height <= 0:
                raise ValueError("char_height必须大于0，不能小于等于0")
            self.char_height = float(char_height)

        if line_height_multiplier is not None:
            self.line_height_multiplier = float(line_height_multiplier)

        # print(f"[DEBUG] 布局参数: 字符高度={self.char_height:.2f}, 行高倍数={self.line_height_multiplier:.3f}, DPI={self.dpi}")

    def boxFilter(self, *filter_functions: callable) -> None:
        """启动用户自定义过滤器系统

        允许用户使用box的数据（如BoundingBox，text）和页面长宽数据，
        编写自己的一个或多个过滤函数，滤除不需要的box。

        Args:
            *filter_functions: 一个或多个过滤函数，每个函数应该：
                - 接受参数：(box_data, page_info)
                - 返回 bool: True表示保留该box，False表示滤除
                - box_data包含: text, x, y, width, height, bbox等
                - page_info包含: page_width, page_height等

        Example:
            # 滤除宽度小于10像素的box
            def filter_small_boxes(box_data, page_info):
                return box_data['width'] >= 10

            # 滤除特定区域的box
            def filter_header_footer(box_data, page_info):
                y = box_data['y']
                page_height = page_info['page_height']
                # 滤除页面顶部和底部20%的区域
                return 0.2 * page_height <= y <= 0.8 * page_height

            # 启动过滤器
            converter.boxFilter(filter_small_boxes, filter_header_footer)
        """
        self.box_filters = list(filter_functions)

    def rowBoxFilter(self, *filter_functions: callable) -> None:
        """启动行级box过滤器系统

        允许用户对聚类后的每一行（row）进行过滤，
        每行包含该行中所有文本片段的box信息。

        Args:
            *filter_functions: 一个或多个过滤函数，每个函数应该：
                - 接受参数：(row_data, page_info)
                - 返回 bool: True表示保留该行，False表示滤除
                - row_data包含: row_fragments, row_text, row_bounds等
                - page_info包含: page_width, page_height等

        Example:
            # 滤除文本内容少于5个字符的行
            def filter_short_rows(row_data, page_info):
                return len(row_data['row_text']) >= 5

            # 滤除特定位置的行
            def filter_header_rows(row_data, page_info):
                y = row_data['row_bounds']['y']
                page_height = page_info['page_height']
                # 滤除页面顶部10%的区域
                return y >= 0.1 * page_height

            # 启动行级过滤器
            converter.rowBoxFilter(filter_short_rows, filter_header_rows)
        """
        self.row_filters = list(filter_functions)

    def _log_filtered_item(self, item_type: str, filter_name: str, item_data: Dict[str, Any]) -> None:
        """记录被过滤掉的项目信息

        Args:
            item_type: 项目类型 ('box' 或 'row')
            filter_name: 过滤器函数名称
            item_data: 项目数据
        """
        try:
            # 提取基本信息
            if item_type == 'box':
                text = item_data.get('text', '')
                x = item_data.get('x', 0)
                y = item_data.get('y', 0)
                width = item_data.get('width', 0)
                height = item_data.get('height', 0)
            else:  # row
                text = item_data.get('row_text', '')
                bounds = item_data.get('row_bounds', {})
                x = bounds.get('x', 0)
                y = bounds.get('y', 0)
                width = bounds.get('width', 0)
                height = bounds.get('height', 0)

            # 记录过滤信息
            log_msg = f"[FILTER_LOG] {item_type.upper()}被过滤 - 过滤器: {filter_name}, 文本: {repr(text[:50])}, 坐标: ({x}, {y}), 尺寸: {width}x{height}"

            # 输出到控制台
            # print(log_msg)

            # 输出到日志文件
            try:
                # 在Windows上使用utf-8-sig编码，避免BOM问题
                with open(self.log_file, 'a', encoding='utf-8-sig') as f:
                    f.write(log_msg + '\n')
            except Exception as log_e:
                print(f"[FILTER_LOG] 写入日志文件时出错: {log_e}")

        except Exception as e:
            error_msg = f"[FILTER_LOG] 记录过滤信息时出错: {e}"
            print(error_msg)
            # 尝试记录错误到日志文件
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(error_msg + '\n')
            except:
                pass

    def _apply_box_filters(self, box_data: Dict[str, Any], page_info: Dict[str, Any]) -> bool:
        """应用用户自定义过滤器

        Args:
            box_data: 包含box信息的字典
            page_info: 包含页面信息的字典

        Returns:
            bool: True表示保留，False表示滤除
        """
        if not self.box_filters:
            return True  # 没有过滤器时保留所有box

        # 所有过滤器都必须返回True才保留该box
        for filter_func in self.box_filters:
            try:
                filter_name = filter_func.__name__
                if not filter_func(box_data, page_info):
                    # 记录被过滤掉的box信息
                    self._log_filtered_item('box', filter_name, box_data)
                    return False
            except Exception as e:
                # 过滤器出错时记录错误但继续处理，默认保留
                print(f"过滤器执行出错: {e}, 默认保留box: {box_data}")
                continue

        return True

    def _apply_row_box_filters(self, row: List[Dict[str, Any]], page_info: Dict[str, Any]) -> bool:
        """应用行级过滤器

        Args:
            row: 包含该行所有文本片段信息的列表
            page_info: 包含页面信息的字典

        Returns:
            bool: True表示保留该行，False表示滤除
        """
        if not self.row_filters:
            return True  # 没有过滤器时保留所有行

        # 准备行数据用于过滤
        if not row:
            return False  # 空行直接滤除

        # 计算行的边界信息
        row_xs = [frag['x'] for frag in row]
        row_ys = [frag['y'] for frag in row]
        row_rights = [frag['x'] + frag['width'] for frag in row]
        row_bottoms = [frag['y'] + frag['height'] for frag in row]

        # 合并该行所有文本
        row_text = ''.join(frag['text'] for frag in row)

        # 构建行数据字典
        row_data = {
            'row_fragments': row,  # 原始片段列表
            'row_text': row_text,  # 合并后的文本
            'row_bounds': {
                'x': min(row_xs),
                'y': min(row_ys),
                'width': max(row_rights) - min(row_xs),
                'height': max(row_bottoms) - min(row_ys),
                'right': max(row_rights),
                'bottom': max(row_bottoms)
            },
            'fragment_count': len(row),  # 片段数量
            'text_length': len(row_text)  # 文本长度
        }

        # 所有过滤器都必须返回True才保留该行
        for filter_func in self.row_filters:
            try:
                filter_name = filter_func.__name__
                if not filter_func(row_data, page_info):
                    # 记录被过滤掉的行信息
                    self._log_filtered_item('row', filter_name, row_data)
                    return False
            except Exception as e:
                # 过滤器出错时记录错误但继续处理，默认保留
                print(f"行级过滤器执行出错: {e}, 默认保留行: {row_data}")
                continue

        return True

    def _update_page_dimensions(self, regions: List[Region]) -> None:
        """更新页面尺寸信息，用于过滤器"""
        if not regions:
            return

        all_xs = []
        all_ys = []
        all_rights = []
        all_bottoms = []

        for region in regions:
            if region.boundingBox:
                all_xs.append(region.boundingBox.x)
                all_ys.append(region.boundingBox.y)
                all_rights.append(region.boundingBox.x + region.boundingBox.width)
                all_bottoms.append(region.boundingBox.y + region.boundingBox.height)

            for line in region.lines:
                if line.boundingBox:
                    all_xs.append(line.boundingBox.x)
                    all_ys.append(line.boundingBox.y)
                    all_rights.append(line.boundingBox.x + line.boundingBox.width)
                    all_bottoms.append(line.boundingBox.y + line.boundingBox.height)

                for word in line.words:
                    if word.boundingBox:
                        all_xs.append(word.boundingBox.x)
                        all_ys.append(word.boundingBox.y)
                        all_rights.append(word.boundingBox.x + word.boundingBox.width)
                        all_bottoms.append(word.boundingBox.y + word.boundingBox.height)

        if all_xs and all_ys and all_rights and all_bottoms:
            self.page_width = max(all_rights) - min(all_xs)
            self.page_height = max(all_bottoms) - min(all_ys)

    # ====== 布局常量估计与持久化 ======
    def _contains_cjk(self, s: str) -> bool:
        """是否包含中日韩统一表意文字（用于估计正文汉字高度）"""
        for ch in s:
            code = ord(ch)
            if (
                0x4E00 <= code <= 0x9FFF or
                0x3400 <= code <= 0x4DBF or
                0x20000 <= code <= 0x2A6DF or
                0x2A700 <= code <= 0x2B73F or
                0x2B740 <= code <= 0x2B81F or
                0x2B820 <= code <= 0x2CEAF
            ):
                return True
        return False

    def _robust_median(self, values: List[float]) -> float:
        if not values:
            return 0.0
        try:
            return float(statistics.median(values))
        except statistics.StatisticsError:
            return float(values[0])

    def estimate_layout_constants(self, regions: List['Region']) -> Tuple[float, float, Dict[str, int]]:
        """返回用户设置的布局参数

        参数在初始化时设置，不再进行自动估算

        返回: (char_height_px, line_height_multiplier, sample_counts)
        """
        # print(f" 使用布局参数: 字符高度={self.char_height:.2f}, 行高倍数={self.line_height_multiplier:.3f}, DPI={self.dpi}")
        return self.char_height, self.line_height_multiplier, {'char': 0, 'line': 0}

    def convert_regions_to_text_lines(self, regions: List[Region], char_height: float, line_height_multiplier: float) -> List[str]:
        """将区域列表转换为纯文本行（跨 region 同行合并、行首缩进与行间空行）"""
        text_lines: List[str] = []

        # 1) 处理水平文本：收集所有行分片
        fragments = self._collect_horizontal_fragments(regions)
        if fragments:
            line_spacing = max(1.0, char_height * line_height_multiplier)
            grouped = self._group_fragments_by_line(fragments, line_spacing, self.same_line_threshold_ratio)

            # 确定文字区域边界
            text_area_bounds = self._determine_text_area_bounds(fragments)

            # 文字区域左边界（全局最小 x）
            base_left = text_area_bounds['left']
            # 文字区域右边界
            base_right = text_area_bounds['right']

            # 合并每一行的分片，按像素间距 → 空格数（两个空格≈一个正文汉字高度）
            prev_row: Optional[List[Dict[str, Any]]] = None
            for row in grouped:
                # 应用行级过滤器
                if not self._apply_row_box_filters(row, {'page_width': self.page_width, 'page_height': self.page_height}):
                    continue

                # 行间距 → 满行空格
                if prev_row is not None:
                    blanks = self._compute_blank_lines_between(prev_row, row, line_spacing)
                    if blanks > 0:
                        # 优先使用页面宽度计算每行字符数，确保空行填充足够
                        if hasattr(self, 'page_width') and self.page_width > 0:
                            chars_per_line = self._compute_chars_per_line_with_page_width(char_height)
                        else:
                            # 回退到基于文字区域宽度的计算
                            chars_per_line = self._compute_chars_per_line(text_area_bounds, char_height)
                        for _ in range(blanks):
                            text_lines.append(' ' * chars_per_line)
                # 行首缩进：行头到文字区域左边界的距离以空格填充
                indent_spaces = self._compute_row_indent_spaces(row, base_left, char_height)
                joined = self._join_fragments_with_spacing(row, char_height, base_right)
                # 只移除行首空格，保留行末空格（包括边界填充）
                stripped = joined.lstrip()
                if not stripped:
                    continue
                text_lines.append((' ' * indent_spaces) + stripped)
                prev_row = row

        # 2) 垂直文本：保持原有处理，作为引用
        vertical_regions = [r for r in regions if r.dir == TextDirection.VERTICAL.value]
        if vertical_regions:
            vertical_regions = sorted(vertical_regions, key=lambda r: r.boundingBox.x)
            for region in vertical_regions:
                # 将垂直文本直接按普通文本输出（不加 markdown 引用符号）
                sorted_lines = sorted(region.lines, key=lambda l: l.boundingBox.x)
                for line in sorted_lines:
                    # 准备box数据用于过滤
                    if line.boundingBox:
                        box_data = {
                            'text': line.text.strip() if line.text else '',
                            'x': int(line.boundingBox.x),
                            'y': int(line.boundingBox.y),
                            'width': int(line.boundingBox.width),
                            'height': int(line.boundingBox.height),
                            'bbox': line.boundingBox,
                            'line': line,
                            'region': region
                        }

                        # 准备页面信息用于过滤
                        page_info = {
                            'page_width': self.page_width,
                            'page_height': self.page_height
                        }

                        # 应用用户自定义过滤器
                        if not self._apply_box_filters(box_data, page_info):
                            continue

                    text = (line.text or '').strip()
                    if text:
                        text_lines.append(text)

        return text_lines

    def _compute_row_indent_spaces(self, row: List[Dict[str, Any]], base_left: int, char_height: float) -> int:
        """计算一行行头相对文字区域左边界的空格数（两个空格≈一个汉字高度）"""
        if not row:
            return 0
        if char_height <= 0:
            raise ValueError("char_height必须大于0，请通过set_layout_params设置有效的字符高度")
        left_x = min(item['x'] for item in row)
        indent_px = max(0, left_x - int(base_left or 0))
        # 根据OCR格式调整系数：pymupdf需要更多空格，RapidOCR需要减少
        # 横向空格：pymupdf使用1.14倍，其他格式使用0.8倍
        # spacing_factor = 1 if hasattr(self, '_is_pymupdf') and self._is_pymupdf else 1
        spacing_factor = 1
        spaces = int(round((indent_px / char_height) * 2 * spacing_factor))
        return max(0, spaces)

    def _compute_blank_lines_between(self, prev_row: List[Dict[str, Any]], curr_row: List[Dict[str, Any]], line_spacing: float) -> int:
        """根据两行的垂直间距，折算为空行数量并返回。
        以上一行的下边界与下一行的上边界的像素差为基准：
        blanks = floor(gap_px / line_spacing)
        """
        if not prev_row or not curr_row or line_spacing <= 0:
            return 0
        prev_bottom = max(item['y'] + item['height'] for item in prev_row)
        curr_top = min(item['y'] for item in curr_row)
        gap_px = max(0.0, float(curr_top - prev_bottom))
        # # 根据OCR格式调整系数：pymupdf需要减少空行，其他格式需要增加空行
        # # 空行空格：pymupdf使用0.5倍，其他格式使用2.0倍
        # spacing_factor = 1.3 if hasattr(self, '_is_pymupdf') and self._is_pymupdf else 1.3
        spacing_factor = 1
        blanks = int((gap_px / line_spacing) * spacing_factor)
        return max(0, blanks)

    def _collect_horizontal_fragments(self, regions: List[Region]) -> List[Dict[str, Any]]:
        """从所有 region 收集水平文本分片（以行 bbox 为准）。
        返回的分片包含: text, x, y, width, height
        """
        fragments: List[Dict[str, Any]] = []

        # 更新页面尺寸信息，用于过滤器
        self._update_page_dimensions(regions)

        for region in regions:
            if region.dir != TextDirection.HORIZONTAL.value:
                continue
            for line in region.lines:
                if not line or not line.text:
                    continue
                bbox = line.boundingBox or region.boundingBox
                if not bbox:
                    continue

                # 准备box数据用于过滤
                box_data = {
                    'text': line.text.strip(),
                    'x': int(bbox.x),
                    'y': int(bbox.y),
                    'width': int(bbox.width),
                    'height': int(bbox.height),
                    'bbox': bbox,
                    'line': line,
                    'region': region
                }

                # 准备页面信息用于过滤
                page_info = {
                    'page_width': self.page_width,
                    'page_height': self.page_height
                }

                # 应用用户自定义过滤器
                if self._apply_box_filters(box_data, page_info):
                    fragments.append({
                        'text': line.text.strip(),
                        'x': int(bbox.x),
                        'y': int(bbox.y),
                        'width': int(bbox.width),
                        'height': int(bbox.height),
                    })

        return fragments

    def _group_fragments_by_line(self, fragments: List[Dict[str, Any]], line_spacing: float, ratio: float) -> List[List[Dict[str, Any]]]:
        """按 y 中心与行距的比例阈值聚类为同一行。"""
        if not fragments:
            return []
        # 以 y 中心排序，便于顺序聚类
        for frag in fragments:
            frag['y_mid'] = frag['y'] + frag['height'] / 2.0
        fragments.sort(key=lambda frag: frag['y_mid'])

        threshold = max(1.0, ratio * line_spacing)
        groups: List[List[Dict[str, Any]]] = []
        current_group: List[Dict[str, Any]] = []
        current_mid: Optional[float] = None

        for item in fragments:
            if current_group and current_mid is not None:
                if abs(item['y_mid'] - current_mid) <= threshold:
                    current_group.append(item)
                    # 更新组中心（滚动平均）
                    current_mid = (current_mid * (len(current_group) - 1) + item['y_mid']) / len(current_group)
                else:
                    # 关闭当前组
                    groups.append(sorted(current_group, key=lambda frag: frag['x']))
                    current_group = [item]
                    current_mid = item['y_mid']
            else:
                current_group = [item]
                current_mid = item['y_mid']

        if current_group:
            groups.append(sorted(current_group, key=lambda frag: frag['x']))

        return groups

    def _join_fragments_with_spacing(self, row: List[Dict[str, Any]], char_height: float, text_area_right: int) -> str:
        """按片段的左右间距，以"两个空格≈一个汉字高度"的换算插入空格，并在行末添加边界填充"""
        if not row:
            return ''
        if char_height <= 0:
            raise ValueError("char_height必须大于0，请通过set_layout_params设置有效的字符高度")
        parts: List[str] = []
        prev_right = None
        for frag in row:
            if prev_right is None:
                parts.append(frag['text'])
                prev_right = frag['x'] + frag['width']
                continue
            gap_px = max(0, frag['x'] - prev_right)
            # 根据OCR格式调整系数：pymupdf需要更多空格，RapidOCR需要减少
            # 行内空格：pymupdf使用1.14倍，其他格式使用0.8倍
            # spacing_factor = 1.14 if hasattr(self, '_is_pymupdf') and self._is_pymupdf else 0.8
            spacing_factor = 1
            spaces = int(round((gap_px / char_height) * 2 * spacing_factor))
            if spaces > 0:
                parts.append(' ' * spaces)
            parts.append(frag['text'])
            prev_right = frag['x'] + frag['width']

        # 行末边界填充：最后一个box后按照其与右边界的距离填充空格
        if row and text_area_right > 0:
            last_frag = row[-1]
            last_right = last_frag['x'] + last_frag['width']
            end_gap_px = max(0, text_area_right - last_right)
            # 根据OCR格式调整系数：pymupdf需要更多空格，RapidOCR需要减少
            # 行末空格：pymupdf使用1.14倍，其他格式使用0.8倍
            # spacing_factor = 1.14 if hasattr(self, '_is_pymupdf') and self._is_pymupdf else 0.8
            spacing_factor = 1
            end_spaces = int(round((end_gap_px / char_height) * 2 * spacing_factor))
            if end_spaces > 0:
                parts.append(' ' * end_spaces)

        return ''.join(parts)

    def _determine_text_area_bounds(self, fragments: List[Dict[str, Any]]) -> Dict[str, int]:
        """确定文字区域的边界（左、右、上、下）"""
        if not fragments:
            return {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}

        # 完全基于实际文本片段计算边界
        left = min(frag['x'] for frag in fragments)
        right = max(frag['x'] + frag['width'] for frag in fragments)
        top = min(frag['y'] for frag in fragments)
        bottom = max(frag['y'] + frag['height'] for frag in fragments)

        return {
            'left': left,
            'right': right,
            'top': top,
            'bottom': bottom
        }

    def _compute_chars_per_line(self, text_area_bounds: Dict[str, int], char_height: float) -> int:
        """计算每行应该有多少个字符（基于文字区域宽度）"""
        if not text_area_bounds or char_height <= 0:
            return 80  # 默认值

        # 文字区域宽度
        text_width = text_area_bounds['right'] - text_area_bounds['left']

        # 两个空格≈一个汉字高度，所以一个汉字≈两个空格
        # 每行字符数 = 文字区域宽度 / 汉字宽度
        chars_per_line = int(round((text_width / char_height) * 2))

        # 确保至少有一些字符，避免过短
        return max(20, chars_per_line)

    def _compute_chars_per_line_with_page_width(self, char_height: float) -> int:
        """基于页面宽度计算每行应该有多少个字符"""
        if not hasattr(self, 'page_width') or self.page_width <= 0 or char_height <= 0:
            return 80  # 默认值

        # 使用页面宽度计算
        chars_per_line = int(round((self.page_width / char_height) * 2))

        # 确保至少有一些字符，避免过短
        return max(20, chars_per_line)

    def convert_youdao_json_to_text(self, ocr_json: Dict[str, Any]) -> str:
        """将有道智云OCR JSON结果转换为纯文本（带空格/空行）"""
        try:
            # 解析JSON数据
            if 'Result' not in ocr_json:
                raise ValueError("JSON数据中缺少'Result'字段")

            result = ocr_json['Result']
            regions_data = result.get('regions', [])

            # 转换为Region对象
            regions = [Region.from_dict(region_data) for region_data in regions_data]

            # 估计布局常量
            char_h, line_mul, _ = self.estimate_layout_constants(regions)

            # 转换为纯文本行
            lines = self.convert_regions_to_text_lines(regions, char_h, line_mul)
            return '\n'.join(lines)

        except (KeyError, TypeError, ValueError) as e:
            return f"转换失败: {str(e)}"

    def convert_rapidocr_json_to_text(self, ocr_json: List[Dict[str, Any]]) -> str:
        """将RapidOCR JSON结果转换为纯文本（带空格/空行）"""
        try:
            # RapidOCR返回的是数组格式，每个元素包含box和txt字段
            if not isinstance(ocr_json, list):
                raise ValueError("RapidOCR JSON数据应该是数组格式")

            # 将RapidOCR格式转换为Region对象
            regions = self._convert_rapidocr_to_regions(ocr_json)

            # 估计布局常量
            char_h, line_mul, _ = self.estimate_layout_constants(regions)

            # 转换为纯文本行
            lines = self.convert_regions_to_text_lines(regions, char_h, line_mul)
            return '\n'.join(lines)

        except (KeyError, TypeError, ValueError) as e:
            return f"转换失败: {str(e)}"

    def convert_pymupdf_json_to_text(self, ocr_json: List[Dict[str, Any]]) -> str:
        """将pymupdf导出的JSON结果转换为纯文本（带空格/空行）"""
        try:
            # pymupdf返回的是页面列表，每个页面包含blocks
            if not isinstance(ocr_json, list):
                raise ValueError("pymupdf JSON数据应该是页面列表格式")

            # 设置pymupdf格式标识
            self._is_pymupdf = True

            # 将pymupdf格式转换为Region对象
            regions = self._convert_pymupdf_to_regions(ocr_json)

            # 估计布局常量
            char_h, line_mul, _ = self.estimate_layout_constants(regions)

            # 转换为纯文本行
            lines = self.convert_regions_to_text_lines(regions, char_h, line_mul)

            # 清除格式标识
            self._is_pymupdf = False

            return '\n'.join(lines)

        except (KeyError, TypeError, ValueError) as e:
            # 确保清除格式标识
            self._is_pymupdf = False
            return f"转换失败: {str(e)}"

    def _convert_rapidocr_to_regions(self, ocr_items: List[Dict[str, Any]]) -> List[Region]:
        """将RapidOCR的识别结果转换为Region对象列表"""
        if not ocr_items:
            return []

        # 创建临时的Line对象列表
        temp_lines: List[Line] = []

        for item in ocr_items:
            if not isinstance(item, dict) or 'txt' not in item or 'box' not in item:
                continue

            text = item.get('txt', '').strip()
            if not text:
                continue

            # 解析四点坐标
            box = item.get('box', [])
            if len(box) != 4 or not all(len(point) == 2 for point in box):
                continue

            # 计算边界框
            xs = [point[0] for point in box]
            ys = [point[1] for point in box]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            # 创建BoundingBox
            bbox = BoundingBox(
                x=int(min_x),
                y=int(min_y),
                width=int(max_x - min_x),
                height=int(max_y - min_y)
            )

            # 准备box数据用于过滤
            box_data = {
                'text': text,
                'x': int(min_x),
                'y': int(min_y),
                'width': int(max_x - min_x),
                'height': int(max_y - min_y),
                'bbox': bbox,
                'rapidocr_item': item
            }

            # 准备页面信息用于过滤（RapidOCR情况下可能还没有页面尺寸信息）
            page_info = {
                'page_width': self.page_width,
                'page_height': self.page_height
            }

            # 应用用户自定义过滤器
            if not self._apply_box_filters(box_data, page_info):
                continue

            # 创建Word对象（RapidOCR没有单词级别，将整行作为一个word）
            word = Word(word=text, boundingBox=bbox)

            # 创建Line对象
            line = Line(
                text=text,
                words=[word],
                boundingBox=bbox,
                text_height=bbox.height,
                style=''
            )

            temp_lines.append(line)

        # 按y坐标排序，确保文本顺序正确
        temp_lines.sort(key=lambda line: line.boundingBox.y)

        # 创建单个Region对象，包含所有行
        if temp_lines:
            # 计算整个区域的边界框
            all_xs = [line.boundingBox.x for line in temp_lines]
            all_ys = [line.boundingBox.y for line in temp_lines]
            all_rights = [line.boundingBox.x + line.boundingBox.width for line in temp_lines]
            all_bottoms = [line.boundingBox.y + line.boundingBox.height for line in temp_lines]

            region_bbox = BoundingBox(
                x=min(all_xs),
                y=min(all_ys),
                width=max(all_rights) - min(all_xs),
                height=max(all_bottoms) - min(all_ys)
            )

            region = Region(
                lang='zh',  # RapidOCR主要用于中文
                dir='h',    # 假设为水平文本
                lines=temp_lines,
                boundingBox=region_bbox
            )

            return [region]

        return []

    def _convert_pymupdf_to_regions(self, pages: List[Dict[str, Any]]) -> List[Region]:
        """将pymupdf的识别结果转换为Region对象列表"""
        if not pages:
            return []

        regions = []

        # DPI转换：pymupdf是72dpi，其他OCR通常是用户设置的DPI
        # 需要将pymupdf的坐标和尺寸放大到用户设置的DPI
        dpi_scale_factor = self.dpi / 72.0

        # 记录页面尺寸信息，用于后续的空格填充计算
        max_page_width = 0
        max_page_height = 0

        for page in pages:
            if not isinstance(page, dict) or 'blocks' not in page:
                continue

            # 获取页面尺寸信息 - 修复：使用正确的字段名
            # 应用DPI转换：将72dpi转换为用户设置的DPI
            page_width = int(page.get('width', 0) * dpi_scale_factor)
            page_height = int(page.get('height', 0) * dpi_scale_factor)

            # 如果页面尺寸为0，尝试从页面内容推断
            if page_width <= 0 or page_height <= 0:
                # 从所有文本块的坐标推断页面尺寸
                all_xs = []
                all_ys = []
                all_rights = []
                all_bottoms = []

                for block in page.get('blocks', []):
                    if isinstance(block, dict) and block.get('type') == 0:  # 文本块
                        for line_data in block.get('lines', []):
                            if isinstance(line_data, dict) and 'spans' in line_data:
                                for span in line_data.get('spans', []):
                                    if isinstance(span, dict) and 'bbox' in span:
                                        span_bbox = span.get('bbox', [])
                                        if len(span_bbox) == 4:
                                            x, y, w, h = span_bbox
                                            all_xs.append(x)
                                            all_ys.append(y)
                                            all_rights.append(w)
                                            all_bottoms.append(h)

                if all_xs and all_ys and all_rights and all_bottoms:
                    # 应用DPI转换：将72dpi转换为用户设置的DPI
                    inferred_width = (max(all_rights) - min(all_xs)) * dpi_scale_factor
                    inferred_height = (max(all_bottoms) - min(all_ys)) * dpi_scale_factor
                    # 添加一些边距
                    page_width = max(page_width, inferred_width + 100)
                    page_height = max(page_height, inferred_height + 100)

            # 更新最大页面尺寸
            max_page_width = max(max_page_width, page_width)
            max_page_height = max(max_page_height, page_height)

            # 处理页面中的文本块
            text_blocks = []
            for block in page.get('blocks', []):
                if not isinstance(block, dict):
                    continue

                # 只处理文本类型的块 (type == 0)
                if block.get('type') != 0:
                    continue

                # 处理文本块中的行
                lines_data = block.get('lines', [])
                if not lines_data:
                    continue

                # 创建Line对象列表
                lines = []
                for line_data in lines_data:
                    if not isinstance(line_data, dict) or 'spans' not in line_data:
                        continue

                    # 处理行中的文本片段
                    spans = line_data.get('spans', [])
                    if not spans:
                        continue

                    # 合并同一行的所有文本片段
                    line_text = ''
                    line_words = []
                    line_bbox = None

                    for span in spans:
                        if not isinstance(span, dict) or 'text' not in span:
                            continue

                        text = span.get('text', '').strip()
                        if not text:
                            continue

                        line_text += text

                        # 创建Word对象
                        span_bbox = span.get('bbox', [])
                        if len(span_bbox) == 4:
                            # 应用DPI转换：将72dpi转换为用户设置的DPI
                            x, y, w, h = span_bbox
                            word_bbox = BoundingBox(
                                x=int(x * dpi_scale_factor),
                                y=int(y * dpi_scale_factor),
                                width=int((w - x) * dpi_scale_factor),
                                height=int((h - y) * dpi_scale_factor)
                            )
                            word = Word(word=text, boundingBox=word_bbox)
                            line_words.append(word)

                            # 更新行的边界框
                            if line_bbox is None:
                                line_bbox = word_bbox
                            else:
                                # 合并边界框
                                min_x = min(line_bbox.x, word_bbox.x)
                                min_y = min(line_bbox.y, word_bbox.y)
                                max_x = max(line_bbox.x + line_bbox.width, word_bbox.x + word_bbox.width)
                                max_y = max(line_bbox.y + line_bbox.height, word_bbox.y + word_bbox.height)
                                line_bbox = BoundingBox(
                                    x=min_x,
                                    y=min_y,
                                    width=max_x - min_x,
                                    height=max_y - min_y
                                )

                    if line_text and line_bbox:
                        # 创建Line对象
                        line = Line(
                            text=line_text,
                            words=line_words,
                            boundingBox=line_bbox,
                            text_height=line_bbox.height
                        )
                        lines.append(line)

                if lines:
                    # 计算文本块的边界框
                    if lines:
                        min_x = min(line.boundingBox.x for line in lines)
                        min_y = min(line.boundingBox.y for line in lines)
                        max_x = max(line.boundingBox.x + line.boundingBox.width for line in lines)
                        max_y = max(line.boundingBox.y + line.boundingBox.height for line in lines)

                        block_bbox = BoundingBox(
                            x=min_x,
                            y=min_y,
                            width=max_x - min_x,
                            height=max_y - min_y
                        )

                        # 创建Region对象
                        region = Region(
                            lang='zh',  # 默认中文
                            dir='h',    # 默认水平方向
                            lines=lines,
                            boundingBox=block_bbox
                        )
                        regions.append(region)

        # 更新转换器的页面尺寸信息，用于空格填充计算
        if max_page_width > 0 and max_page_height > 0:
            self.page_width = max_page_width
            self.page_height = max_page_height
            # print(f"[DEBUG] 设置页面尺寸: {max_page_width} x {max_page_height}")

        return regions

    def convert_json_to_text(self, ocr_json: Any) -> str:
        """将OCR JSON结果转换为纯文本（带空格/空行）"""
        # 自动识别JSON格式
        if isinstance(ocr_json, list):
            # 检查是否为pymupdf格式（页面列表，每个页面有width/height和blocks）
            if (len(ocr_json) > 0 and
                isinstance(ocr_json[0], dict) and
                'width' in ocr_json[0] and
                'height' in ocr_json[0] and
                'blocks' in ocr_json[0]):
                print(f"转换pymupdf格式")
                return self.convert_pymupdf_json_to_text(ocr_json)
            else:
                # RapidOCR格式：直接是文本块数组
                print(f"转换RapidOCR格式")
                return self.convert_rapidocr_json_to_text(ocr_json)
        elif isinstance(ocr_json, dict):
            if 'Result' in ocr_json:
                # 有道智云格式
                print(f"转换有道智云格式")
                return self.convert_youdao_json_to_text(ocr_json)
            else:
                raise ValueError("不支持的JSON格式")
        else:
            raise ValueError("不支持的JSON格式")

def convert_json_to_text(json_path: str, out_path: str='', box_filter_functions: List[callable]=None, row_filter_functions: List[callable]=None, dpi: int=300, char_height: float=50.0, line_height_multiplier: float=1.5) -> str:
    """将OCR JSON结果转换为纯文本（带空格/空行）"""
    if not out_path:
        out_path = re.sub(r'\.[^\.]+$', '.txt', json_path)
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        tl_conv = OCRJsonToTextLine(dpi=dpi, char_height=char_height, line_height_multiplier=line_height_multiplier)  # 使用初始化参数
        if box_filter_functions:
            tl_conv.boxFilter(*box_filter_functions)
        if row_filter_functions:
            tl_conv.rowBoxFilter(*row_filter_functions)
        text = tl_conv.convert_json_to_text(json_data)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)

def convert_jsons_to_text(json_dir: str, out_dir: str='', box_filter_functions: List[callable]=None, row_filter_functions: List[callable]=None, dpi: int=300, char_height: float=50.0, line_height_multiplier: float=1.5) -> str:
    """将文件夹中的OCR JSON结果转换为纯文本（带空格/空行），支持递归处理"""
    
    # 检查输入文件夹是否存在
    input_dir_obj = pathlib.Path(json_dir)
    if not input_dir_obj.exists():
        print(f"输入文件夹不存在: {json_dir}")
        return
    
    # 如果输出目录为空，则使用输入目录
    if not out_dir:
        output_dir_obj = input_dir_obj
    else:
        output_dir_obj = pathlib.Path(out_dir)
        output_dir_obj.mkdir(parents=True, exist_ok=True)
    
    # 递归查找所有JSON文件
    json_files = list(input_dir_obj.rglob("*.json"))
    
    total_files = len(json_files)
    if total_files == 0:
        print("未找到JSON文件")
        return
    
    print(f"共找到 {total_files} 个JSON文件，开始处理……")
    
    for idx, json_path in enumerate(sorted(json_files), 1):
        print(f"[{idx}/{total_files}] processing: {json_path}")
        
        try:
            # 保持完整的相对路径结构
            relative_path = json_path.relative_to(input_dir_obj)
            output_subdir = output_dir_obj / relative_path.parent
            output_subdir.mkdir(parents=True, exist_ok=True)
            
            # 生成输出文件路径
            output_file = output_subdir / (relative_path.stem + '.txt')
            
            # 调用convert_json_to_text处理单个文件
            convert_json_to_text(str(json_path), str(output_file), box_filter_functions, row_filter_functions, dpi, char_height, line_height_multiplier)
            
        except Exception as e:
            print(f"处理文件 {json_path} 时出错: {e}")
    
    print("批量JSON转换处理完成！")

if __name__ == "__main__":

    from ocr_json_filters import box_filters, row_filters

    # files = [
    #     'tests/assets/img_0_toc.json',
    #     'tests/assets/pymupdf.json',
    #     'tests/assets/rapidocr.json',
    #     'tests/assets/youdao.json',
    # ]
    # for file in files:
    #     # 转换单个JSON文件
    #     convert_json_to_text(
    #         file,
    #         box_filter_functions=box_filters,
    #         row_filter_functions=row_filters,
    #         dpi=300,
    #         char_height=50.0,
    #         line_height_multiplier=1.5
    #         )

    # # 转换文件夹中的所有JSON文件
    convert_jsons_to_text(
        'E:/语文出版社/2025/人教教师教学用书语文一年级上册-集团质检/img_preprocessed/',
        box_filter_functions=box_filters,
        row_filter_functions=row_filters,
        dpi=300,
        char_height=50.0,
        line_height_multiplier=1.5
    )
