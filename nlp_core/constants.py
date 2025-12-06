import re

# 1. Regex Nhắc nhở [UPDATED V30]
# Thêm (?!\s*(?:sáng|trưa...)) để tránh bắt nhầm "trước 5h chiều" thành nhắc nhở
REMINDER_PATTERN = re.compile(
    r"\b(nhắc nhở|nhắc|nhac nho|nhac|báo(?!\s*thức)|bao|thông báo|thong bao|alarm|remind|nhớ|nho)\s*(tôi|mình|nhé|giúp|dùm|ngay)?\s*(trước|sớm|sau|truoc|som)?\s*(\d+)\s*(phút|p|phut|giờ|h|tiếng|tieng|ngày|ngay|gio)(?!\s*(?:sáng|trưa|chiều|tối|đêm|khuya|sang|trua|chieu|toi|dem))", 
    re.IGNORECASE
)

# 2. Regex Thời gian Tương lai
RELATIVE_FUTURE_PATTERN = re.compile(
    r"\b(sau|trong|tầm|khoảng|khoang)\s+(\d+)\s+(phút|p|phut|tiếng|tieng|h|giờ|gio|ngày|ngay)\s*(nữa|tới|toi|tiếp theo|tiep theo)?",
    re.IGNORECASE
)

# 3. Regex Địa điểm
LOCATION_PATTERN = re.compile(
    r"\b("
        r"tại|ở|o|trong|khu vực|khu vuc|phòng|phong|sân|san|"
        r"nhà hàng|nha hang|quán|quan|trường|truong|bệnh viện|benh vien|"
        r"trung tâm|trung tam|công ty|cong ty|siêu thị|sieu thi|tiệm|tiem|hồ bơi|ho boi|"
        r"tai(?!\s*(?:chinh|khoan|nan|lieu|san)\b)" 
    r")\s+"
    r"([\w\s,Đđ/-]+?)"
    r"(?=\s+("
        r"lúc|luc|vào|vao|ngày|ngay|hôm|hom|sáng|sang|trưa|trua|chiều|chieu|tối|toi|đêm|dem|khuya|bây giờ|bay gio|"
        r"\d{1,2}\s*[:hg]|\d{1,2}\s*giờ|\d{1,2}\s*gio|"
        r"họp|hop|làm|lam|đi|di|gặp|gap|đá|da|mua|báo|bao|gọi|goi|nộp|nop|bắt đầu|bat dau|sau|trong|"
        r"nhắc|nhac|báo|bao|nhớ|nho" 
    r")|$)", 
    re.IGNORECASE
)

# --- CÁC REGEX TIME (Giữ nguyên V29) ---
TIME_PATTERN_COMPACT = re.compile(r'\b(\d{1,2})[hg:](\d{2})\b', re.IGNORECASE)
TIME_RANGE_PATTERN = re.compile(
    r'\b(?:từ|tu)?\s*(\d{1,2}(?:[:hg]\d{2}|[:hg]|\s*giờ|\s*gio|\s*h|\s*g))\s*(?:đến|den|tới|toi|-)\s*(\d{1,2}(?:[:hg]\d{2}|[:hg]|\s*giờ|\s*gio|\s*h|\s*g))\b',
    re.IGNORECASE
)
TIME_PATTERN_HHMM = re.compile(r'\b(\d{1,2})\s*(?:[:hg]|giờ|gio|p|phút|phut)\s*(\d{1,2})\s*(sáng|trưa|chiều|tối|đêm|am|pm|khuya|sang|trua|chieu|toi|dem)?\b', re.IGNORECASE)
TIME_PATTERN_HH_SESSION = re.compile(r'\b(\d{1,2})\s*(?:h|g|giờ|gio)\s*(sáng|trưa|chiều|tối|đêm|am|pm|khuya|sang|trua|chieu|toi|dem)(?:\s+nay)?\b', re.IGNORECASE)
TIME_PATTERN_HH_ONLY = re.compile(r'\b(\d{1,2})\s*(?:h|g|giờ|gio)\b(?![:\d])', re.IGNORECASE)
TIME_PATTERN_PREFIX = re.compile(r'\b(sáng|trưa|chiều|tối|đêm|khuya|sang|trua|chieu|toi|dem)(?:\s+nay)?\s*[,.]?\s*(\d{1,2})\s*(?:h|g|:|giờ|gio)?\s*(\d{1,2})?\b', re.IGNORECASE)
TIME_PATTERN_IMPLICIT = re.compile(r'\b(\d{1,2})\s+(chiều|tối|đêm|khuya|chieu|toi|dem)(?:\s+nay)?\b', re.IGNORECASE)

# 5. Cleanup Regex (Giữ nguyên)
CLEANUP_DATE_PATTERN = re.compile(
    r'\b(vào|vao|trong|ngay|ngày|thứ|thu|t|cn|chủ nhật|trước|truoc|sau|tới|toi|đến|den|dự kiến|du kien|hạn|han|deadline)?\s*'
    r'('
        r'\d{1,2}[-./\s]\d{1,2}([-./\s]\d{2,4})?' 
        r'|\d{1,2}\s*(?:âm|am)\s*lịch'
        r'|\d{1,2}\s*(?:tháng|thang)\s*(?:chạp|giêng|chap|gieng|\d{1,2})'
        r'|[2-7]'
        r'|\b(nay|mai|kia|mốt|mot|qua)\b'
        r'|mỗi ngày|moi ngay|hàng ngày|hang ngay|hằng ngày'
        r'|cuối tuần|cuoi tuan'
    r')\s*'
    r'(tuan sau|tuần sau|tới|toi|năm sau|nam sau|âm lịch|am lich|lịch|lich)?', 
    re.IGNORECASE
)
CLEANUP_TIME_PATTERN = re.compile(
    r'\b(từ|tu|lúc|luc|vào|vao|trước|truoc|sau|khoảng|khoang|deadline|hạn|trong)?\s*'
    r'('
        r'\d{1,2}\s*(?:giờ|gio|[:hg]|phút|p|phut)\s*\d{0,2}'       
        r'\s*(?:sáng|trưa|chiều|tối|đêm|am|pm|khuya|sang|trua|chieu|toi|dem)?'            
        r'\s*(?:\b(?:nay|mai|kia|mốt|mot|qua)\b)?'
        r'|\d{1,2}[:h]?\s*rưỡi'
        r'|\d{1,2}[:h]?\s*kém\s*\d{1,2}'
        r'|\d{1,2}[hg:]\d{2}' 
        r'|\d{1,2}\s*(?:[:hg]|\s*h|\s*g|\s*giờ|\s*gio).*?(?:đến|den|tới|toi|-).*?\d{1,2}\s*(?:[:hg]|\s*h|\s*g|\s*giờ|\s*gio)'
    r'|'
        r'(?:sáng|trưa|chiều|tối|đêm|khuya|sang|trua|chieu|toi|dem)\s*(?:\b(?:nay|mai|kia|mốt|mot)\b)?\s*\d{1,2}?'  
    r')'
    r'(?:\s*(?:đến|den)\s*\d{1,2}\s*(?:[:hg]|giờ|gio|p|phút|phut)\s*\d{0,2}\s*(?:sáng|trưa|chiều|tối|đêm|am|pm|khuya|sang|trua|chieu|toi|dem)?)?', 
    re.IGNORECASE
)

# 7. Stopwords [UPDATED V30]
# ĐÃ XÓA "tai", "o", "trong" để tránh xóa nhầm từ trong Event
STOPWORDS = [
    "nhắc nhở", "nhắc tôi", "hãy nhắc", "nhắc", "nhở", "nhac nho", "nhac toi", "hay nhac", "nhac", "nho", "bao thuc",
    "đặt lịch", "tạo", "dat lich", "tao",
    "vào lúc", "lúc", "vào", "khoảng", "dự kiến", "ở", "tại", "trong", "vao luc", "luc", "vao", "khoang", "du kien", 
    "bây giờ", "ngay", "deadline", "bay gio",
    "luc", "vao", "truoc", "sau", "tuần sau", "tuan sau",
    "t2", "t3", "t4", "t5", "t6", "t7", "cn", "chủ nhật", "chu nhat",
    "cuối tuần", "cuoi tuan"
]