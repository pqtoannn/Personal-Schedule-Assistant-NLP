from datetime import datetime, timedelta
from .constants import REMINDER_PATTERN, LOCATION_PATTERN, RELATIVE_FUTURE_PATTERN

def extract_reminder(text):
    match = REMINDER_PATTERN.search(text)
    minutes = 0
    matched_text = ""
    
    if match:
        val = int(match.group(4))
        unit = match.group(5).lower()
        
        # [UPDATED] Check thêm gio, tieng
        if unit in ['giờ', 'h', 'tiếng', 'gio', 'tieng']:
            minutes = val * 60
        # [UPDATED] Check thêm ngay
        elif unit in ['ngày', 'ngay']: 
            minutes = val * 1440 
        else:
            minutes = val
            
        matched_text = match.group(0)
    return minutes, matched_text

def extract_location(text):
    match = LOCATION_PATTERN.search(text)
    location = None
    matched_text = ""
    
    if match:
        matched_text = match.group(0)
        prefix = match.group(1).strip() # Lấy từ khóa (vd: tai, o, san, sieu thi)
        raw_loc = match.group(2).strip()
        
        # [UPDATED] Danh sách các Prefix là Danh từ (cần giữ lại để thành tên địa điểm hoàn chỉnh)
        # Fix lỗi: "Sân số 7" -> bị cắt thành "số 7"
        NOUN_PREFIXES = [
            'phòng', 'phong', 'sân', 'san', 'nhà hàng', 'nha hang', 
            'quán', 'quan', 'trường', 'truong', 'bệnh viện', 'benh vien',
            'trung tâm', 'trung tam', 'công ty', 'cong ty', 'siêu thị', 'sieu thi',
            'tiệm', 'tiem', 'hồ bơi', 'ho boi'
        ]
        
        # Nếu Prefix là danh từ, nối nó vào kết quả
        if prefix.lower() in NOUN_PREFIXES:
            full_loc = f"{prefix} {raw_loc}"
        else:
            full_loc = raw_loc

        if len(full_loc) > 1:
            if full_loc.islower():
                location = full_loc.title()
            else:
                location = full_loc
        else:
            matched_text = "" 
            
    return location, matched_text

def extract_future_time(text):
    """
    Xử lý: 'sau 30 phut', 'trong 2 tieng'
    """
    match = RELATIVE_FUTURE_PATTERN.search(text)
    future_time = None
    matched_text = ""
    
    if match:
        val = int(match.group(2))
        unit = match.group(3).lower()
        
        now = datetime.now()
        # [UPDATED] Check thêm phut
        if unit in ['phút', 'p', 'phut']:
            future_time = now + timedelta(minutes=val)
        # [UPDATED] Check thêm gio, tieng
        elif unit in ['tiếng', 'h', 'giờ', 'gio', 'tieng']:
            future_time = now + timedelta(hours=val)
        # [UPDATED] Check thêm ngay
        elif unit in ['ngày', 'ngay']:
            future_time = now + timedelta(days=val)
            future_time = future_time.replace(hour=8, minute=0, second=0)
            
        matched_text = match.group(0)
        
    return future_time, matched_text