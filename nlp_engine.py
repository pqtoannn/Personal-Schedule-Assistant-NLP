from nlp_core.text_utils import preprocess_text, clean_event_title
from nlp_core.extractors import extract_reminder, extract_location, extract_future_time
from nlp_core.time_processor import extract_datetime

class NLPEngine:
    def __init__(self):
        pass

    def process(self, text):
        raw_text = text 
        text = preprocess_text(text)
        
        # 1. Trích xuất Nhắc nhở
        reminder_minutes, reminder_str = extract_reminder(text)
        if reminder_str: 
            text = text.replace(reminder_str, "")
        else:
            # [UPDATED] Nếu không có reminder trong câu, mặc định là 15 phút
            reminder_minutes = 15
            
        # 2. Trích xuất Địa điểm
        location, location_str = extract_location(text)
        if location_str: text = text.replace(location_str, "")
        
        time_result = {"start_time": None, "end_time": None, "is_all_day": False, "error": None}
        
        # 3. Check Tương lai gần (Relative Future)
        future_time, future_str = extract_future_time(text)
        if future_time:
            time_result["start_time"] = future_time.strftime("%Y-%m-%dT%H:%M:%S")
            text = text.replace(future_str, "")
        else:
            # 4. Check Dateparser (Time Processor)
            time_result = extract_datetime(text, raw_text)

        # 5. Làm sạch tiêu đề sự kiện
        event_name = clean_event_title(text, location_str=None) 
        
        return {
            "event": event_name,
            "start_time": time_result["start_time"],
            "end_time": time_result["end_time"],
            "is_all_day": time_result["is_all_day"],
            "error": time_result.get("error"),
            "location": location,
            "reminder_minutes": reminder_minutes,
            "original_input": raw_text
        }