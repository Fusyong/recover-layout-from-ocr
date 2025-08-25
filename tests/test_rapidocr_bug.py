from rapidocr import RapidOCR

engine = RapidOCR()

img_url = "https://github.com/RapidAI/RapidOCR/blob/main/python/tests/test_files/ch_en_num.jpg?raw=true"
result = engine(img_url)
print(result)

result.vis("vis_result.jpg")           # 看到正确输出的文件
result.vis("视觉化结果_vis_result.jpg") # 看到文件名乱码的输出文件：瑙嗚鍖栫粨鏋淿vis_result.jpg
result.vis("视觉化结果/vis_result.jpg") # “视觉化结果”文件夹下没有输出文件

# 输出日志没有异常：
# [INFO] 2025-08-21 12:33:45,751 [RapidOCR] vis_res.py:49: Using D:\ah21\recover-layout-from-ocr\.venv\Lib\site-packages\rapidocr\models\FZYTK.TTF to visualize results.
# [INFO] 2025-08-21 12:33:45,761 [RapidOCR] output.py:62: Visualization saved as vis_result.jpg
# [INFO] 2025-08-21 12:33:45,761 [RapidOCR] vis_res.py:49: Using D:\ah21\recover-layout-from-ocr\.venv\Lib\site-packages\rapidocr\models\FZYTK.TTF to visualize results.
# [INFO] 2025-08-21 12:33:45,770 [RapidOCR] output.py:62: Visualization saved as 视觉化结果_vis_result.jpg
# [INFO] 2025-08-21 12:33:45,770 [RapidOCR] vis_res.py:49: Using D:\ah21\recover-layout-from-ocr\.venv\Lib\site-packages\rapidocr\models\FZYTK.TTF to visualize results.
# [INFO] 2025-08-21 12:33:45,776 [RapidOCR] output.py:62: Visualization saved as 视觉化结果/vis_result.jpg