"""旋正倾斜图片，并保存
"""
import re
import numpy as np
from pymupdf import os
from skimage import io
from skimage.color import rgb2gray
from skimage.transform import rotate

from deskew import determine_skew

def deskew_image(in_path, out_path=''):
    """旋正倾斜图片，并保存"""
    if not out_path:
        out_path = re.sub(r'\.[^\.]+$', '_dsk.jpg', in_path)
    image = io.imread(in_path)
    grayscale = rgb2gray(image)
    angle = determine_skew(grayscale)
    rotated = rotate(image, angle, resize=True) * 255
    io.imsave(out_path, rotated.astype(np.uint8))

def deskew_images(in_dir, out_dir=''):
    """旋正倾斜图片，并保存"""
    # 创建输出目录
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for in_path in os.listdir(in_dir):
        if in_path.endswith('.jpg'):
            deskew_image(os.path.join(in_dir, in_path), os.path.join(out_dir, in_path))


if __name__ == "__main__":
    # 
    # 旋正单张图片
    # 
    IN_PATH = 'tests/assets/img_0.jpg'
    deskew_image(IN_PATH)

    # 
    # 旋正多个图片
    # 
    # deskew_images('img', 'img_dsk')
