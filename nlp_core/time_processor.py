import re
from datetime import datetime, timedelta
from dateparser.search import search_dates
# Import đầy đủ các pattern từ constants (bao gồm pattern MỚI)
from .constants import (
    TIME_PATTERN_HHMM, TIME_PATTERN_HH_SESSION, TIME_PATTERN_HH_ONLY, 
    TIME_PATTERN_PREFIX, TIME_PATTERN_IMPLICIT, 
    TIME_PATTERN_COMPACT, TIME_RANGE_PATTERN
)

# Map ngữ cảnh sang giờ cụ thể
CONTEXT_MAPPING = {
    "sáng mai": "08:00 ngày mai", "sang mai": "08:00 ngày mai",
    "trưa mai": "12:00 ngày mai", "trua mai": "12:00 ngày mai",
    "chiều mai": "14:00 ngày mai", "chieu mai": "14:00 ngày mai",
    "tối mai": "19:00 ngày mai", "toi mai": "19:00 ngày mai",
    "sáng nay": "08:00 hôm nay", "sang nay": "08:00 hôm nay",
    "trưa nay": "12:00 hôm nay", "trua nay": "12:00 hôm nay",
    "chiều nay": "14:00 hôm nay", "chieu nay": "14:00 hôm nay",
    "tối nay": "19:00 hôm nay", "toi nay": "19:00 hôm nay",
    "đêm nay": "22:00 hôm nay", "dem nay": "22:00 hôm nay",
}

DEFAULT_HOURS = {
    "sáng": 8, "sang": 8, "trưa": 12, "trua": 12,
    "chiều": 14, "chieu": 14, "tối": 19, "toi": 19,
    "đêm": 22, "dem": 22, "khuya": 23
}

def replace_vietnamese_relative_terms(text):
    text = text.lower()
    
    if any(x in text for x in ["âm lịch", "am lich", "tháng chạp", "thang chap"]):
        text = re.sub(r'\d{1,2}\s*(?:âm|am)\s*lịch', '', text)
        return text, False

    # FIX LỖI: Tránh thay thế nhầm nếu đã có giờ cụ thể đứng trước (ví dụ: 10 gio sang mai)
    for key, val in CONTEXT_MAPPING.items():
        if key in text:
            # [UPDATED] Thêm 'gio' vào regex check để hỗ trợ không dấu
            if not re.search(r'\d{1,2}\s*(h|g|:|giờ|gio)', text):
                text = text.replace(key, val)

    def replace_kem(match):
        h = int(match.group(1))
        m = int(match.group(2))
        new_m = 60 - m
        new_h = h - 1
        return f"{new_h}:{new_m}"
    # [UPDATED] Thêm 'gio' cho trường hợp kém
    text = re.sub(r'(\d{1,2})\s*(?:h|g|giờ|gio)?\s*kém\s*(\d{1,2})', replace_kem, text)

    text = re.sub(r'(\d{1,2})[:h]\s*rưỡi', r'\1:30', text)
    text = re.sub(r'(\d{1,2})\s*rưỡi', r'\1:30', text)

    next_year = datetime.now().year + 1
    text = re.sub(r'\b(nam sau|năm sau)\b', str(next_year), text)

    # --- [FIX QUAN TRỌNG] XỬ LÝ NGÀY THÁNG TIẾNG VIỆT ---
    # 1. Dạng DD-MM-YYYY hoặc DD.MM.YYYY -> DD/MM/YYYY
    text = re.sub(r'(\d{1,2})[-.](\d{1,2})[-.](\d{4})', r'\1/\2/\3', text)
    
    # 2. [MỚI - Fix lỗi case 44] Dạng "20 thang 10" hoặc "20 thang 10" -> "20/10"
    text = re.sub(r'(\d{1,2})\s*(?:tháng|thang)\s*(\d{1,2})', r'\1/\2', text)
    
    # 3. Dạng "ngay 20 10" -> "20/10"
    text = re.sub(r'(ngày|ngay)\s+(\d{1,2})\s+(\d{1,2})', r'\1 \2/\3', text)
    
    # 4. Dạng rút gọn "20 10" (chỉ chạy khi các regex trên không bắt được và context phù hợp)
    text = re.sub(r'\b(\d{1,2})\s+(\d{1,2})\b', r'\1/\2', text)

    target_date_mot = (datetime.now() + timedelta(days=2)).strftime("%d/%m")
    replacements = {
        "mốt": f"ngày {target_date_mot}", "ngày kia": f"ngày {target_date_mot}", "mot": f"ngày {target_date_mot}",
        "hôm kia": "2 ngày trước", "hom kia": "2 ngày trước",
        "tuần tới": "tuần sau", "cn": "chủ nhật", "tuan toi": "tuần sau",
        "t2": "thứ 2", "t3": "thứ 3", "t4": "thứ 4", 
        "t5": "thứ 5", "t6": "thứ 6", "t7": "thứ 7"
    }
    for k, v in replacements.items():
        text = re.sub(r'\b' + k + r'\b', v, text)
    return text, True

def normalize_time_string(text):
    text, should_parse = replace_vietnamese_relative_terms(text)
    if not should_parse: return text, False 

    lower_text = text.lower()
    found_time = False 

    def convert_to_24h_str(h, m, session):
        if session:
            session = session.lower().split()[0]
            if session in ['chiều', 'tối', 'đêm', 'pm', 'chieu', 'toi', 'dem'] and h < 12:
                h += 12
            elif session in ['sáng', 'am', 'sang', 'khuya'] and h == 12:
                h = 0
        return f" {h:02}:{m:02} "

    def wrapper(match, func):
        nonlocal found_time
        found_time = True
        return func(match)

    # 1. Ưu tiên xử lý Compact Time (19h30 -> 19:30)
    lower_text = TIME_PATTERN_COMPACT.sub(lambda m: wrapper(m, lambda x: convert_to_24h_str(int(x.group(1)), int(x.group(2)), None)), lower_text)

    # 2. Xử lý các pattern khác
    lower_text = TIME_PATTERN_PREFIX.sub(lambda m: wrapper(m, lambda x: convert_to_24h_str(int(x.group(2)), int(x.group(3)) if x.group(3) else 0, x.group(1))), lower_text)
    lower_text = TIME_PATTERN_IMPLICIT.sub(lambda m: wrapper(m, lambda x: convert_to_24h_str(int(x.group(1)), 0, x.group(2))), lower_text)
    lower_text = TIME_PATTERN_HHMM.sub(lambda m: wrapper(m, lambda x: convert_to_24h_str(int(x.group(1)), int(x.group(2)), x.group(3))), lower_text)
    lower_text = TIME_PATTERN_HH_SESSION.sub(lambda m: wrapper(m, lambda x: convert_to_24h_str(int(x.group(1)), 0, x.group(2))), lower_text)
    lower_text = TIME_PATTERN_HH_ONLY.sub(lambda m: wrapper(m, lambda x: f" {int(x.group(1)):02}:00 "), lower_text)
    
    if not found_time:
        found_time = bool(re.search(r' \d{2}:\d{2} ', lower_text))
    
    return lower_text, found_time

# --- HÀM XỬ LÝ RANGE (START - END) ---
def parse_simple_hour(time_str):
    """Parse giờ đơn giản từ chuỗi đã regex"""
    time_str = time_str.lower().strip()
    h, m = 0, 0
    # Dạng 10h30, 10:30
    match_full = re.search(r'(\d{1,2})[:hg](\d{2})', time_str)
    if match_full:
        h, m = int(match_full.group(1)), int(match_full.group(2))
    else:
        # Dạng 10h, 10g
        match_h = re.search(r'(\d{1,2})', time_str)
        if match_h:
            h = int(match_h.group(1))
    return h, m

def extract_time_range_explicit(text, original_raw_text):
    """
    Xử lý: 'từ 10h đến 12h', '10g-12g'
    Trả về Dict full nếu bắt được, None nếu không
    """
    match = TIME_RANGE_PATTERN.search(original_raw_text)
    if match:
        start_str = match.group(1)
        end_str = match.group(2)
        
        h_start, m_start = parse_simple_hour(start_str)
        h_end, m_end = parse_simple_hour(end_str)
        
        # Heuristic: Nếu End < Start (VD: 10h đến 2h), giả định End là chiều (+12h)
        if h_end < h_start:
            h_end += 12

        # Để tìm Ngày, ta xóa cụm giờ đi và dùng logic cũ để quét ngày còn lại trong câu
        clean_text_for_date = TIME_RANGE_PATTERN.sub(' ', text) 
        
        # Gọi đệ quy logic date cũ (nhưng chỉ để lấy ngày)
        res_date = extract_datetime(clean_text_for_date, clean_text_for_date)
        
        if res_date['start_time']:
            base_date = datetime.strptime(res_date['start_time'], "%Y-%m-%dT%H:%M:%S")
        else:
            base_date = datetime.now() # Fallback hôm nay nếu không nói ngày
            
        start_dt = base_date.replace(hour=h_start, minute=m_start, second=0)
        end_dt = base_date.replace(hour=h_end, minute=m_end, second=0)
        
        return {
            "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "is_all_day": False,
            "error": None
        }
    return None

def process_weekend_logic(text):
    if "cuối tuần" in text.lower() or "cuoi tuan" in text.lower():
        now = datetime.now()
        days_ahead = 5 - now.weekday()
        if days_ahead < 0: days_ahead += 7
        start_date = now + timedelta(days=days_ahead)
        end_date = start_date + timedelta(days=1)
        start_dt = start_date.replace(hour=8, minute=0, second=0)
        end_dt = end_date.replace(hour=21, minute=0, second=0)
        return start_dt, end_dt, True 
    return None, None, False

def extract_datetime(text, original_raw_text):
    # 0. Check Range Explicit (Ưu tiên cao nhất)
    range_result = extract_time_range_explicit(text, original_raw_text)
    if range_result:
        return range_result

    # 1. Weekend
    wk_start, wk_end, wk_allday = process_weekend_logic(original_raw_text)
    if wk_start:
        return {"start_time": wk_start.strftime("%Y-%m-%dT%H:%M:%S"), "end_time": wk_end.strftime("%Y-%m-%dT%H:%M:%S"), "is_all_day": True, "error": None}

    # 2. Normalize
    time_text, has_explicit_time = normalize_time_string(text)
    original_lower = original_raw_text.lower()
    
    # Check context words (sáng, chiều...)
    default_hour = None
    if not has_explicit_time:
        for session, hour in DEFAULT_HOURS.items():
            if session in original_lower:
                default_hour = hour
                break
    
    date_keywords = ['ngày', 'mai', 'thứ', 'qua', 'tuần', 'hôm', 'mốt', 'kia', '/', '-', 'tháng', 'năm']
    has_date_keyword = any(kw in original_lower for kw in date_keywords) or bool(re.search(r'\d{1,2}\s+\d{1,2}', original_lower))
    is_now = any(kw in original_lower for kw in ['ngay bây giờ', 'ngay lúc này'])

    if not has_explicit_time and not default_hour and not has_date_keyword and not is_now:
        return {"start_time": None, "end_time": None, "is_all_day": False, "error": None}

    settings = {'TIMEZONE': 'Asia/Ho_Chi_Minh', 'DATE_ORDER': 'DMY', 'PARSERS': ['absolute-time', 'relative-time']}
    if not any(k in original_lower for k in ['nay', 'hôm nay', 'bây giờ']):
        settings['PREFER_DATES_FROM'] = 'future'

    dates = search_dates(time_text, languages=['vi'], settings=settings)
    
    if dates:
        best_match = max(dates, key=lambda x: len(x[0]))
        dt_obj = best_match[1]
        
        is_all_day = False
        if not has_explicit_time and default_hour is not None:
            dt_obj = dt_obj.replace(hour=default_hour, minute=0, second=0)
            is_all_day = True
        elif not has_explicit_time and not is_now:
            dt_obj = dt_obj.replace(hour=8, minute=0, second=0)
            is_all_day = True

        current_now = datetime.now()
        is_explicit_date = bool(re.search(r'\d{1,2}[/.-]\d{1,2}', original_lower)) or "ngày" in original_lower
        
        # --- LOGIC QUÁ KHỨ V27 ---
        if dt_obj < current_now:
            has_year = bool(re.search(r'\b20\d{2}\b', original_lower))
            if has_year:
                 return {"start_time": None, "end_time": None, "is_all_day": False, "error": "Thời gian đã qua"}

            if is_explicit_date and not any(k in original_lower for k in ['nay', 'hôm nay']):
                 if (current_now - dt_obj).days > 180: 
                     dt_obj = dt_obj.replace(year=dt_obj.year + 1)
                 else:
                     return {"start_time": None, "end_time": None, "is_all_day": False, "error": "Thời gian đã qua"}
            
            if not is_explicit_date and any(k in original_lower for k in ['thứ', 't2', 't3', 't4', 't5', 't6', 't7', 'cn']):
                dt_obj += timedelta(days=7)

        return {
            "start_time": dt_obj.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": None, 
            "is_all_day": is_all_day,
            "error": None
        }
    
    return {"start_time": None, "end_time": None, "is_all_day": False, "error": None}