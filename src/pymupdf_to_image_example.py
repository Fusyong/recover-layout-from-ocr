"""转换pdf为image"""
import pymupdf
from pathlib import Path

def pdf_to_image(pdf_path, img_dir="", dpi=300):
    """转换pdf为image"""
    ZOOM_FACTOR = dpi / 72.0
    mat = pymupdf.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
    # 如果img_dir为空，则使用pdf_path(去掉扩展名)作为img_dir    
    PDF_PATH = Path(pdf_path)
    if not img_dir:
        img_dir = str(PDF_PATH.with_suffix(''))
    IMG_PATH = Path(img_dir)
    if not IMG_PATH.exists():
        IMG_PATH.mkdir(parents=True, exist_ok=True)
    print(f'Processing {PDF_PATH.name} to {IMG_PATH}')
    doc = pymupdf.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(matrix=mat)
        img_path = IMG_PATH / f"img-{page_number + 1}.png"
        pix.save(img_path)
    doc.close()

def pdfs_to_image(pdf_dir, img_dir="", dpi=300):
    """转换多个pdf为image"""
    # 如果img_dir为空，则使用pdf_path作为img_dir
    if not img_dir:
        img_dir = pdf_dir
    for pdf_path in Path(pdf_dir).iterdir():
        if pdf_path.suffix == '.pdf':
            # 用pdf文件名建立子目录
            sub_dir = Path(img_dir) / pdf_path.stem
            if not sub_dir.exists():
                sub_dir.mkdir(parents=True, exist_ok=True)
            pdf_to_image(pdf_path, str(sub_dir), dpi)

if __name__ == "__main__":
    # 
    # 转换单个pdf为image
    # 
    # PDF_PATH = "D:/语文出版社/2025/同步练习题库/2顺序拼接PDF/五三天天练测评卷四下-h.pdf"
    # pdf_to_image(PDF_PATH)

    # 
    # 转换多个pdf为image
    # 
    pdfs_to_image('D:/语文出版社/2025/同步练习题库/2顺序拼接PDF')
