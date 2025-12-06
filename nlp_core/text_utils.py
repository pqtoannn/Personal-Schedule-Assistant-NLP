import re
from underthesea import text_normalize
from .constants import STOPWORDS, CLEANUP_TIME_PATTERN, CLEANUP_DATE_PATTERN

def preprocess_text(text):
    return text_normalize(text)

def clean_event_title(text, location_str=None):
    if location_str:
        text = text.replace(location_str, "")
        
    # 1. Cắt cụm Thời gian (Regex CLEANUP_TIME_PATTERN trong constants đã được update rồi nên dòng này OK)
    text = CLEANUP_TIME_PATTERN.sub(' ', text)
    
    # 2. Cắt cụm Ngày tháng (Tương tự, đã update constants)
    text = CLEANUP_DATE_PATTERN.sub(' ', text)
    
    # 3. Dọn rác [UPDATED]
    text = re.sub(r'\b\d{1,2}\s*:\s*\d{2}\b', ' ', text)
    # [UPDATED] Thêm gio, phut, tieng vào regex xóa đơn vị lẻ
    text = re.sub(r'\b\d{1,2}\s*(h|g|giờ|gio|phút|p|phut|tiếng|tieng)\b', ' ', text, flags=re.IGNORECASE)
    
    # 4. Xóa Stopwords
    for word in STOPWORDS:
        text = re.sub(r'\b' + word + r'\b', ' ', text, flags=re.IGNORECASE)
        
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.strip(".,- ")
    
    return text.capitalize() if text else "Sự kiện mới"