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
    print(f'Processing {in_path.name}')
    
    try:
        image = io.imread(in_path)
        grayscale = rgb2gray(image)
        angle = determine_skew(grayscale)
        
        # 检查angle是否为None
        if angle is None:
            print(f'  Warning: Could not determine skew angle for {in_path}, take it as 0...')
            angle = 0
        
        print(f'  Rotating by {angle:.3f}°')
        rotated = rotate(image, angle, resize=True) * 255
        io.imsave(out_path, rotated.astype(np.uint8))
            
        print(f'  Saved to {out_path}')
        
    except Exception as e:
        print(f'  Error processing {in_path}: {e}')
        return

def deskew_images(in_dir, out_dir=''):
    """旋正倾斜图片，并保存"""
    in_dir = Path(in_dir)
    image_files = list(in_dir.rglob('*.png')) + list(in_dir.rglob('*.jpg'))
    
    if not image_files:
        print(f'No image files found in {in_dir}')
        return
    
    print(f'Found {len(image_files)} image files to process')
    
    success_count = 0
    error_count = 0
    
    for i, in_path in enumerate(image_files, 1):
        print(f'\n[{i}/{len(image_files)}] Processing image in {in_path.parent.name}')
        try:
            deskew_image(in_path, out_dir)
            success_count += 1
        except Exception as e:
            print(f'  Failed to process {in_path}: {e}')
            error_count += 1
    
    print(f'\nProcessing complete!')
    print(f'Success: {success_count}, Errors: {error_count}')


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
