from PIL import Image
import pytesseract

def ocr_analyze(path):
    text = pytesseract.image_to_string(Image.open(path), lang="chi_tra+eng")
    return f"OCR 讀取結果：\n{text}"