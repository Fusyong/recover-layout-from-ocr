"""旋正倾斜图片，并保存
"""
from pathlib import Path
import numpy as np
from skimage import io
from skimage.color import rgb2gray
from skimage.transform import rotate

from deskew import determine_skew

def deskew_image(in_path, out_path=''):
    """旋正倾斜图片，并保存"""
    in_path = Path(in_path)
    if not out_path:
        # 如果out_path为空，则使用in_path的文件名加后缀作为out_path
        out_path = in_path.with_suffix('.dsk.png')
    else:
        if Path(out_path).is_dir():
            # 如果out_path是目录，则使用in_path的文件名作为out_path的文件名
            out_path = Path(out_path) / in_path.with_suffix('.dsk.png').name
            out_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 如果out_path是文件，则使用out_path作为out_path
            out_path = Path(out_path)
    print(f'Processing {in_path}')
    image = io.imread(in_path)
    grayscale = rgb2gray(image)
    angle = determine_skew(grayscale)
    rotated = rotate(image, angle, resize=True) * 255
    io.imsave(out_path, rotated.astype(np.uint8))

def deskew_images(in_dir, out_dir=''):
    """旋正倾斜图片，并保存"""
    in_dir = Path(in_dir)
    for in_path in in_dir.rglob('*'):  # 递归遍历所有子文件夹和文件
        if in_path.suffix in ['.png', '.jpg']:
            deskew_image(in_path, out_dir)


if __name__ == "__main__":
    # 
    # 旋正单张图片
    # 
    # IN_PATH = 'D:/语文出版社/2025/同步练习题库/2顺序拼接PDF/一本自主测评卷五下-h/img-1.png'
    # deskew_image(IN_PATH)

    # 
    # 旋正多个图片
    # 
    deskew_images('D:/语文出版社/2025/同步练习题库/2顺序拼接PDF')
