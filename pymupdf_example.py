"""转换pdf为image"""
import os
import pymupdf

def pdf_to_image(pdf_path, img_dir, dpi=300):
    """转换pdf为image"""
    ZOOM_FACTOR = dpi / 72.0
    mat = pymupdf.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    doc = pymupdf.open(pdf_path)
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(matrix=mat)
        pix.save(f"{img_dir}/img-{page_number + 1}.jpg")
    doc.close()

def pdfs_to_image(pdf_dir, img_dir, dpi=300):
    """转换多个pdf为image"""
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    for pdf_path in os.listdir(pdf_dir):
        if pdf_path.endswith('.pdf'):
            # 用pdf文件名建立子目录
            sub_dir = os.path.join(img_dir, pdf_path.replace('.pdf', ''))
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)
            pdf_to_image(os.path.join(pdf_dir, pdf_path), sub_dir, dpi)

if __name__ == "__main__":
    # 转换单个pdf为image
    # PDF_PATH = "D:/OneDrive163/OneDrive/同步练习题库/长江作业本四上.pdf"
    # IMG_DIR = "img"
    # pdf_to_image(PDF_PATH, IMG_DIR)

    # 转换多个pdf为image
    pdfs_to_image('pdf', 'img')
