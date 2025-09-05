"""
版心检测算法 - 基于滑动窗口和梯度变化的方法
使用滑动窗口检测黑色像素分布变化，精确定位版心边界
"""

import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import statistics
from pathlib import Path

# 尝试导入图像处理库
try:
    import cv2
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("警告: 未安装OpenCV，将使用PIL进行图像处理")

try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("警告: 未安装PIL，图像处理功能将受限")

@dataclass
class PageMargin:
    """页面边距信息"""
    left: int
    right: int
    top: int
    bottom: int
    confidence: float = 0.0

class PageBodyDetector:
    """版心检测器 - 基于滑动窗口和梯度变化"""
    
    def __init__(self, 
                 body_ratio_width: float = 0.8, 
                 body_ratio_height: float = 0.8,
                 window_size: int = 20,
                 gradient_threshold: float = 0.1):
        """
        初始化版心检测器
        
        Args:
            body_ratio_width: 版心宽度占页面宽度的比例，默认0.8
            body_ratio_height: 版心高度占页面高度的比例，默认0.8
            window_size: 滑动窗口大小，默认20像素
            gradient_threshold: 梯度变化阈值，默认0.1
        """
        self.body_ratio_width = body_ratio_width
        self.body_ratio_height = body_ratio_height
        self.window_size = window_size
        self.gradient_threshold = gradient_threshold
        self.debug = True
    
    def detect_from_image(self, image_path: str) -> PageMargin:
        """
        基于图像处理检测版心
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PageMargin: 版心边界信息
        """
        if HAS_OPENCV:
            return self._detect_with_opencv(image_path)
        elif HAS_PIL:
            return self._detect_with_pil(image_path)
        else:
            raise ValueError("需要安装OpenCV或PIL库进行图像处理")
    
    def _detect_with_opencv(self, image_path: str) -> PageMargin:
        """使用OpenCV进行检测"""
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        height, width = image.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 使用滑动窗口方法检测版心
        left_margin, right_margin = self._detect_horizontal_margins(binary, width)
        top_margin, bottom_margin = self._detect_vertical_margins(binary, height)
        
        # 计算置信度
        confidence = self._calculate_confidence(binary, left_margin, right_margin, top_margin, bottom_margin)
        
        return PageMargin(
            left=left_margin,
            right=right_margin,
            top=top_margin,
            bottom=bottom_margin,
            confidence=confidence
        )
    
    def _detect_with_pil(self, image_path: str) -> PageMargin:
        """使用PIL进行检测"""
        # 读取图像
        image = Image.open(image_path)
        width, height = image.size
        
        # 转换为灰度图
        gray = image.convert('L')
        
        # 转换为numpy数组
        img_array = np.array(gray)
        
        # 简单的二值化
        threshold = np.mean(img_array)
        binary = (img_array < threshold).astype(np.uint8) * 255
        
        # 使用滑动窗口方法检测版心
        left_margin, right_margin = self._detect_horizontal_margins(binary, width)
        top_margin, bottom_margin = self._detect_vertical_margins(binary, height)
        
        # 计算置信度
        confidence = self._calculate_confidence(binary, left_margin, right_margin, top_margin, bottom_margin)
        
        return PageMargin(
            left=left_margin,
            right=right_margin,
            top=top_margin,
            bottom=bottom_margin,
            confidence=confidence
        )
    
    def _detect_horizontal_margins(self, binary: np.ndarray, width: int) -> Tuple[int, int]:
        """
        使用滑动窗口检测水平边距
        
        Args:
            binary: 二值化图像
            width: 图像宽度
            
        Returns:
            (left_margin, right_margin)
        """
        height = binary.shape[0]
        
        # 计算初始版心区域
        initial_left = int(width * (1 - self.body_ratio_width) / 2)
        initial_right = int(width * (1 + self.body_ratio_width) / 2)
        
        if self.debug:
            print(f"初始版心区域: 左{initial_left}, 右{initial_right}")
        
        # 检测左边界
        left_margin = self._detect_boundary_sliding_window(
            binary, initial_left, 'left', width, height
        )
        
        # 检测右边界
        right_margin = self._detect_boundary_sliding_window(
            binary, initial_right, 'right', width, height
        )
        
        if self.debug:
            print(f"检测结果: 左{left_margin}, 右{right_margin}")
        
        return left_margin, right_margin
    
    def _detect_vertical_margins(self, binary: np.ndarray, height: int) -> Tuple[int, int]:
        """
        使用滑动窗口检测垂直边距
        
        Args:
            binary: 二值化图像
            height: 图像高度
            
        Returns:
            (top_margin, bottom_margin)
        """
        width = binary.shape[1]
        
        # 计算初始版心区域
        initial_top = int(height * (1 - self.body_ratio_height) / 2)
        initial_bottom = int(height * (1 + self.body_ratio_height) / 2)
        
        if self.debug:
            print(f"初始版心区域: 上{initial_top}, 下{initial_bottom}")
        
        # 检测上边界
        top_margin = self._detect_boundary_sliding_window(
            binary, initial_top, 'top', width, height
        )
        
        # 检测下边界
        bottom_margin = self._detect_boundary_sliding_window(
            binary, initial_bottom, 'bottom', width, height
        )
        
        if self.debug:
            print(f"检测结果: 上{top_margin}, 下{bottom_margin}")
        
        return top_margin, bottom_margin
    
    def _detect_boundary_sliding_window(self, 
                                      binary: np.ndarray, 
                                      initial_pos: int, 
                                      direction: str, 
                                      width: int, 
                                      height: int) -> int:
        """
        使用滑动窗口检测单个边界
        
        Args:
            binary: 二值化图像
            initial_pos: 初始位置
            direction: 检测方向 ('left', 'right', 'top', 'bottom')
            width: 图像宽度
            height: 图像高度
            
        Returns:
            检测到的边界位置
        """
        # 根据方向确定搜索范围和步长
        if direction in ['left', 'top']:
            # 向内搜索（减小位置值）
            search_range = range(initial_pos, 0, -1)
            step = -1
        else:
            # 向外搜索（增大位置值）
            search_range = range(initial_pos, width if direction in ['right', 'bottom'] else height)
            step = 1
        
        # 计算黑色像素密度变化
        densities = []
        positions = []
        
        for pos in search_range:
            if direction in ['left', 'right']:
                # 水平方向检测
                if pos < self.window_size or pos > width - self.window_size:
                    continue
                density = self._calculate_black_density_horizontal(binary, pos, height)
            else:
                # 垂直方向检测
                if pos < self.window_size or pos > height - self.window_size:
                    continue
                density = self._calculate_black_density_vertical(binary, pos, width)
            
            densities.append(density)
            positions.append(pos)
        
        if len(densities) < 3:
            return initial_pos
        
        # 计算密度梯度
        gradients = self._calculate_gradients(densities)
        
        # 找到梯度变化最大的位置
        boundary_pos = self._find_gradient_peak(positions, gradients, direction)
        
        if self.debug:
            print(f"{direction}方向检测: 初始位置{initial_pos}, 检测位置{boundary_pos}")
        
        return boundary_pos
    
    def _calculate_black_density_horizontal(self, binary: np.ndarray, x_pos: int, height: int) -> float:
        """
        计算水平位置处的黑色像素密度
        
        Args:
            binary: 二值化图像
            x_pos: x坐标位置
            height: 图像高度
            
        Returns:
            黑色像素密度 (0-1)
        """
        # 定义窗口范围
        x_start = max(0, x_pos - self.window_size // 2)
        x_end = min(binary.shape[1], x_pos + self.window_size // 2)
        
        # 提取窗口区域
        window = binary[:, x_start:x_end]
        
        # 计算黑色像素密度
        black_pixels = np.sum(window == 0)
        total_pixels = window.size
        
        return black_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_black_density_vertical(self, binary: np.ndarray, y_pos: int, width: int) -> float:
        """
        计算垂直位置处的黑色像素密度
        
        Args:
            binary: 二值化图像
            y_pos: y坐标位置
            width: 图像宽度
            
        Returns:
            黑色像素密度 (0-1)
        """
        # 定义窗口范围
        y_start = max(0, y_pos - self.window_size // 2)
        y_end = min(binary.shape[0], y_pos + self.window_size // 2)
        
        # 提取窗口区域
        window = binary[y_start:y_end, :]
        
        # 计算黑色像素密度
        black_pixels = np.sum(window == 0)
        total_pixels = window.size
        
        return black_pixels / total_pixels if total_pixels > 0 else 0
    
    def _calculate_gradients(self, densities: List[float]) -> List[float]:
        """
        计算密度梯度
        
        Args:
            densities: 密度列表
            
        Returns:
            梯度列表
        """
        if len(densities) < 2:
            return [0] * len(densities)
        
        gradients = []
        for i in range(len(densities)):
            if i == 0:
                gradients.append(densities[i+1] - densities[i])
            elif i == len(densities) - 1:
                gradients.append(densities[i] - densities[i-1])
            else:
                # 使用中心差分
                gradients.append((densities[i+1] - densities[i-1]) / 2)
        
        return gradients
    
    def _find_gradient_peak(self, positions: List[int], gradients: List[float], direction: str) -> int:
        """
        找到梯度变化最大的位置
        
        Args:
            positions: 位置列表
            gradients: 梯度列表
            direction: 检测方向
            
        Returns:
            边界位置
        """
        if not positions or not gradients:
            return positions[0] if positions else 0
        
        # 计算梯度的绝对值
        abs_gradients = [abs(g) for g in gradients]
        
        # 找到最大梯度位置
        max_grad_idx = np.argmax(abs_gradients)
        
        # 如果梯度变化超过阈值，使用该位置
        if abs_gradients[max_grad_idx] > self.gradient_threshold:
            return positions[max_grad_idx]
        
        # 否则返回初始位置
        return positions[0]
    
    def _calculate_confidence(self, binary: np.ndarray, left: int, right: int, top: int, bottom: int) -> float:
        """
        计算检测置信度
        
        Args:
            binary: 二值化图像
            left, right, top, bottom: 版心边界
            
        Returns:
            置信度 (0-1)
        """
        if left >= right or top >= bottom:
            return 0.0
        
        # 计算版心区域
        body_width = right - left
        body_height = bottom - top
        total_width = binary.shape[1]
        total_height = binary.shape[0]
        
        # 计算版心比例
        width_ratio = body_width / total_width
        height_ratio = body_height / total_height
        
        # 理想比例应该在0.6-0.9之间
        ideal_ratio = 0.75
        width_score = 1.0 - abs(width_ratio - ideal_ratio) / ideal_ratio
        height_score = 1.0 - abs(height_ratio - ideal_ratio) / ideal_ratio
        
        # 综合评分
        confidence = (width_score + height_score) / 2
        return max(0.0, min(1.0, confidence))
    
    def visualize_detection(self, image_path: str, margin: PageMargin, output_path: str = None):
        """可视化检测结果"""
        if HAS_OPENCV:
            return self._visualize_with_opencv(image_path, margin, output_path)
        elif HAS_PIL:
            return self._visualize_with_pil(image_path, margin, output_path)
        else:
            print("无法可视化：需要OpenCV或PIL库")
            return None
    
    def _visualize_with_opencv(self, image_path: str, margin: PageMargin, output_path: str = None):
        """使用OpenCV可视化"""
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # 绘制版心边界
        cv2.rectangle(image, 
                     (margin.left, margin.top), 
                     (margin.right, margin.bottom), 
                     (0, 255, 0), 2)
        
        # 添加标签
        cv2.putText(image, f"Left: {margin.left}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Right: {margin.right}", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(image, f"Confidence: {margin.confidence:.2f}", (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        if output_path:
            cv2.imwrite(output_path, image)
        
        return image
    
    def _visualize_with_pil(self, image_path: str, margin: PageMargin, output_path: str = None):
        """使用PIL可视化"""
        from PIL import ImageDraw, ImageFont
        
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # 绘制版心边界
        draw.rectangle([margin.left, margin.top, margin.right, margin.bottom], 
                      outline=(0, 255, 0), width=2)
        
        # 添加标签（PIL的文本绘制比较简单）
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((10, 10), f"Left: {margin.left}", fill=(0, 255, 0), font=font)
        draw.text((10, 30), f"Right: {margin.right}", fill=(0, 255, 0), font=font)
        draw.text((10, 50), f"Confidence: {margin.confidence:.2f}", fill=(0, 255, 0), font=font)
        
        if output_path:
            image.save(output_path)
        
        return image

def main():
    """测试版心检测功能"""
    # 测试不同的参数组合
    test_configs = [
        {"body_ratio_width": 0.7, "body_ratio_height": 0.7, "window_size": 15},
        {"body_ratio_width": 0.8, "body_ratio_height": 0.8, "window_size": 20},
        {"body_ratio_width": 0.85, "body_ratio_height": 0.85, "window_size": 25},
    ]
    
    # 测试图像
    img_path = "tests/assets/detect_body.jpg"
    
    print("=== 新版心检测算法测试（滑动窗口方法）===\n")
    
    for i, config in enumerate(test_configs):
        print(f"--- 配置 {i+1}: {config} ---")
        detector = PageBodyDetector(**config)
        
        try:
            margin = detector.detect_from_image(img_path)
            print(f"检测结果:")
            print(f"  左边界: {margin.left}")
            print(f"  右边界: {margin.right}")
            print(f"  上边界: {margin.top}")
            print(f"  下边界: {margin.bottom}")
            print(f"  置信度: {margin.confidence:.2f}")
            
            # 计算版心宽度和高度
            body_width = margin.right - margin.left
            body_height = margin.bottom - margin.top
            print(f"  版心宽度: {body_width}px")
            print(f"  版心高度: {body_height}px")
            
            # 可视化结果
            output_path = f"tests/assets/detect_body_sliding_{i+1}.jpg"
            detector.visualize_detection(img_path, margin, output_path)
            print(f"  可视化结果已保存到 {output_path}")
            
        except Exception as e:
            print(f"检测失败: {e}")
        
        print()

if __name__ == "__main__":
    main()
