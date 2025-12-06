import streamlit as st
import pandas as pd
import time
import threading
import os
import base64
from datetime import datetime, timedelta
from streamlit_calendar import calendar 
from streamlit_option_menu import option_menu 
from streamlit_autorefresh import st_autorefresh 
from database import add_event, get_all_events, delete_event, update_event

from nlp_engine import NLPEngine

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Trợ Lý Cá Nhân", 
    page_icon="📅", 
    layout="wide"
)

# Tự động làm mới trang mỗi 10 giây
count = st_autorefresh(interval=10000, limit=None, key="fizzbuzzcounter")

# --- 2. CSS & STYLES ---
st.markdown("""
<style>
    /* Card thông tin */
    .info-card { background-color: rgba(128, 128, 128, 0.05); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 10px; padding: 15px; margin-bottom: 10px; height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .card-label { font-size: 0.85rem; color: #888; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }
    .card-value { font-size: 1.1rem; font-weight: 700; word-wrap: break-word; color: inherit; }

    /* Custom Calendar */
    .fc .fc-toolbar-title { color: inherit !important; }
    .fc .fc-col-header-cell-cushion { color: inherit !important; }
    .fc .fc-daygrid-day-number { color: inherit !important; text-decoration: none !important; }
    .fc .fc-button { background-color: #262730; border-color: #4e4e4e; color: white; text-transform: capitalize; }
    .fc .fc-button-primary:not(:disabled).fc-button-active { background-color: #ff4b4b; border-color: #ff4b4b; }
    .fc-theme-standard td, .fc-theme-standard th { border-color: #444 !important; }
    
    /* Event Card */
    .event-card { background-color: #262730; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    
    /* CSS cho nút tắt nổi */
    div.floating-dismiss-container {
        position: fixed; bottom: 30px; right: 30px; z-index: 99999;
        background-color: white; padding: 10px; border-radius: 10px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.5); border: 2px solid #FF4B4B;
    }
    div.floating-dismiss-container button {
        background-color: #FF4B4B !important; color: white !important;
        border: none !important; font-weight: bold !important;
        padding: 10px 20px !important; font-size: 1.2rem !important;
    }
    div.floating-dismiss-container button:hover { background-color: #ff1c1c !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS & STATE ---

# Load NLP Engine
@st.cache_resource
def load_nlp():
    return NLPEngine()

with st.spinner("Đang khởi động AI Engine..."):
    nlp = load_nlp()

# Thread nhắc nhở 
@st.cache_resource
def start_reminder_thread():
    def check_reminders():
        while True:
            time.sleep(60)     
    t = threading.Thread(target=check_reminders, daemon=True)
    t.start()
    return t

start_reminder_thread()

# Đọc file âm thanh
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE_PATH = os.path.join(BASE_DIR, "assets", "alarm.mp3")

def get_base64_audio(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# State Management
if "audio_permission" not in st.session_state:
    st.session_state.audio_permission = False
if "browser_noti_permission" not in st.session_state:
    st.session_state.browser_noti_permission = False
if "dismissed_events" not in st.session_state:
    st.session_state.dismissed_events = []
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = 0 

def enable_audio():
    st.session_state.audio_permission = True

def request_browser_notification():
    # Hàm này chỉ đánh dấu state, việc gọi JS sẽ thực hiện ở Sidebar
    st.session_state.browser_noti_permission = True

def dismiss_alarm(evt_id):
    st.session_state.dismissed_events.append(evt_id)

# --- 4. LOGIC DỮ LIỆU ---
events_db = get_all_events() 
df = pd.DataFrame(events_db, columns=["ID", "Sự kiện", "Bắt đầu", "Kết thúc", "Địa điểm", "Nhắc trước", "Câu lệnh gốc"])

# --- 5. HỆ THỐNG KIỂM TRA BÁO THỨC (CORE) ---
active_alarm_id = None
active_alarm_name = ""
active_alarm_time = ""
current_alarm_html = ""
js_notification_code = "" # Mã JS để đẩy thông báo hệ thống

now = datetime.now()

for e in events_db:
    try:
        e_id = e[0]
        if e_id in st.session_state.dismissed_events:
            continue

        try:
            start_t = datetime.strptime(e[2], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            start_t = datetime.strptime(e[2], "%Y-%m-%d %H:%M:%S")
            
        remind_time = start_t - timedelta(minutes=e[5]) 
        
        # Check window 60s
        if remind_time <= now <= remind_time + timedelta(seconds=60):
            active_alarm_id = e_id
            active_alarm_name = e[1]
            active_alarm_time = e[2].split("T")[1][:5] if "T" in e[2] else e[2].split(" ")[1][:5]
            
            # 1. Tạo Âm thanh (Nếu đã bật quyền Audio)
            if st.session_state.audio_permission:
                audio_base64 = get_base64_audio(SOUND_FILE_PATH)
                if audio_base64:
                    current_alarm_html = f"""
                    <audio autoplay="true" id="audio-{e_id}">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg">
                    </audio>
                    <script>
                        var audio = document.getElementById("audio-{e_id}");
                        if(audio) {{
                            audio.volume = 1.0;
                            audio.play().catch(e => console.log("Audio block: " + e));
                            setTimeout(function() {{ audio.pause(); }}, 15000); 
                        }}
                    </script>
                    """
            
            # 2. Tạo Thông báo Hệ thống (Nếu đã bật quyền Browser Notification)
            # Đây là phần quan trọng để hiện thông báo khi ẩn tab
            js_notification_code = f"""
            <script>
                if (Notification.permission === "granted") {{
                    new Notification("⏰ BÁO THỨC: {active_alarm_name}", {{
                        body: "Đã đến giờ: {active_alarm_time}. Địa điểm: {e[4] if e[4] else 'Không có'}",
                        icon: "https://cdn-icons-png.flaticon.com/512/2693/2693507.png",
                        requireInteraction: true
                    }});
                }}
            </script>
            """
            
            break 
    except: continue

# --- 6. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🤖 Trợ Lý Cá Nhân")
    st.caption("v7.0 - Background Notification")
    
    # [NÚT CẤP QUYỀN TRÌNH DUYỆT]
    if not st.session_state.browser_noti_permission:
        st.warning("⚠️ Chưa bật thông báo nền")
        if st.button("🔔 BẬT THÔNG BÁO DESKTOP", on_click=request_browser_notification, use_container_width=True):
            # Inject JS để xin quyền ngay lập tức
            st.markdown("""
                <script>
                    Notification.requestPermission().then(function(permission) {
                        if(permission === 'granted') {
                            console.log('Notification granted');
                        }
                    });
                </script>
            """, unsafe_allow_html=True)
            st.toast("Đã gửi yêu cầu cấp quyền!", icon="✅")
    else:
        st.success("🔔 Thông báo nền: Đã bật")

    # Nút bật âm thanh (như cũ)
    if not st.session_state.audio_permission:
        if st.button("🔊 KÍCH HOẠT ÂM THANH", on_click=enable_audio, use_container_width=True):
            st.toast("Đã kích hoạt âm thanh!", icon="✅")
    
    st.divider()
    
    options_list = ["Thêm Sự Kiện (AI)", "Xem Lịch Trình", "Danh Sách", "Kiểm Thử & Import"]
    def on_change_tab(key):
        selection = st.session_state[key]
        if selection in options_list:
            st.session_state.selected_tab = options_list.index(selection)

    selected = option_menu(
        menu_title=None, 
        options=options_list,
        icons=["stars", "calendar-date", "list-check", "database-add"],
        default_index=st.session_state.selected_tab,
        on_change=on_change_tab,
        key='main_menu_nav',
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#333"},
            "nav-link-selected": {"background-color": "#FF4B4B"},
        }
    )
    
    st.divider()
    
    # Thống kê
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_count = sum(1 for e in events_db if today_str in e[2])
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Tổng", len(events_db))
    col_s2.metric("Hôm nay", today_count)
    
    if not df.empty:
        json_data = df.to_json(orient="records", force_ascii=False)
        st.download_button("📥 Backup JSON", json_data, f"backup_{today_str}.json", "application/json", use_container_width=True)

# --- 7. MAIN CONTENT ---

# [XỬ LÝ BÁO THỨC]
if active_alarm_id is not None:
    # 1. Phát âm thanh (ẩn)
    if current_alarm_html:
        st.markdown(current_alarm_html, unsafe_allow_html=True)
    
    # 2. Bắn thông báo hệ thống (Desktop Notification)
    if js_notification_code:
        st.components.v1.html(js_notification_code, height=0, width=0)
    
    # 3. Toast trong app
    st.toast(f"⏰ **BÁO THỨC:** {active_alarm_name} ({active_alarm_time})", icon="🔔")
    
    # 4. Nút Tắt Nổi
    with st.container():
        st.markdown('<div class="floating-dismiss-container">', unsafe_allow_html=True)
        st.write(f"**🔔 {active_alarm_name}**")
        st.button("🔕 TẮT NGAY", type="primary", on_click=dismiss_alarm, args=(active_alarm_id,), key=f"dismiss_{active_alarm_id}")
        st.markdown('</div>', unsafe_allow_html=True)

# === TAB 1: THÊM SỰ KIỆN ===
if selected == "Thêm Sự Kiện (AI)":
    st.markdown("## ✨ Thêm Sự Kiện Thông Minh")
    st.caption("Nhập yêu cầu bằng tiếng Việt, AI sẽ tự động trích xuất thông tin.")

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_input = st.text_input("Nhập lệnh:", placeholder="VD: Họp team từ 9h đến 11h sáng mai ở phòng 302...", key="nlp_in")
    with col_btn:
        st.write("") 
        st.write("") 
        process_btn = st.button("🚀 Phân Tích", type="primary", use_container_width=True)

    if process_btn and user_input:
        with st.spinner("🤖 AI đang suy nghĩ..."):
            try:
                res = nlp.process(user_input)
                st.session_state['nlp_result'] = res
                st.session_state['nlp_last_input'] = user_input
            except Exception as e:
                st.error(f"Lỗi xử lý: {e}")

    if 'nlp_result' in st.session_state:
        res = st.session_state['nlp_result']
        last_in = st.session_state.get('nlp_last_input', '')

        st.divider()
        st.markdown(f"**🗣️ Câu lệnh gốc:**")
        st.info(last_in)
        
        # Kiểm tra kết quả hợp lệ để hiển thị tiêu đề
        if res.get('start_time'):
            st.success("✅ Kết quả phân tích hợp lệ:")
        else:
            st.error("⚠️ Không tìm thấy thời gian cụ thể!")

        def draw_card(label, value, icon):
            return f"""<div class="info-card"><div class="card-label">{icon} {label}</div><div class="card-value">{value}</div></div>"""

        c1, c2, c3, c4, c5 = st.columns(5)
        
        start_disp = res['start_time'].replace('T', ' ') if res['start_time'] else "---"
        end_disp = res['end_time'].replace('T', ' ') if res['end_time'] else "---"
        
        with c1: st.markdown(draw_card("Sự Kiện", res['event'], "📝"), unsafe_allow_html=True)
        with c2: st.markdown(draw_card("Bắt Đầu", start_disp, "⏰"), unsafe_allow_html=True)
        with c3: st.markdown(draw_card("Kết Thúc", end_disp, "🏁"), unsafe_allow_html=True)
        with c4: st.markdown(draw_card("Địa Điểm", res['location'] or "---", "📍"), unsafe_allow_html=True)
        with c5: st.markdown(draw_card("Nhắc Trước", f"{res['reminder_minutes']} phút", "⏳"), unsafe_allow_html=True)
            
        st.write("")
        btn1, btn2 = st.columns([1, 4])
        
        # [CẬP NHẬT QUAN TRỌNG] Chỉ cho phép lưu nếu có start_time
        if res.get('start_time'):
            if btn1.button("💾 LƯU VÀO LỊCH", type="primary"):
                add_event(res['event'], res['start_time'], res['end_time'], res['location'], res['reminder_minutes'], last_in)
                st.toast("Đã lưu sự kiện thành công!", icon="🎉")
                del st.session_state['nlp_result']
                del st.session_state['nlp_last_input']
                time.sleep(1)
                st.rerun()
        else:
            # Nếu lỗi, hiển thị thông báo thay vì nút Lưu
            error_msg = res.get('error') if res.get('error') else "Thiếu thông tin thời gian"
            btn1.warning(f"⛔ Không thể lưu: {error_msg}")

        if btn2.button("❌ Hủy bỏ/Nhập lại"):
            del st.session_state['nlp_result']
            del st.session_state['nlp_last_input']
            st.rerun()

# === TAB 2: LỊCH TRÌNH ===
elif selected == "Xem Lịch Trình":
    if 'cal_view' not in st.session_state: st.session_state['cal_view'] = 'dayGridMonth'
    if 'cal_date' not in st.session_state: st.session_state['cal_date'] = datetime.now().strftime("%Y-%m-%d")
    if 'cal_uid' not in st.session_state: st.session_state['cal_uid'] = 0

    st.markdown("## 🗓 Lịch Trình Của Bạn")
    
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("⬅️ Về Xem Tháng", use_container_width=True):
            st.session_state['cal_view'] = 'dayGridMonth'
            st.session_state['cal_date'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state['cal_uid'] += 1
            st.rerun()

    calendar_events = []
    for e in events_db:
        try:
            try: dt_obj = datetime.strptime(e[2], "%Y-%m-%dT%H:%M:%S")
            except ValueError: dt_obj = datetime.strptime(e[2], "%Y-%m-%d %H:%M:%S")
            iso_start = dt_obj.isoformat()
            if e[3]:
                try: iso_end = datetime.strptime(e[3], "%Y-%m-%dT%H:%M:%S").isoformat()
                except: iso_end = (dt_obj + timedelta(minutes=60)).isoformat()
            else: iso_end = (dt_obj + timedelta(minutes=60)).isoformat()
            
            bg_color = "#3788d8"
            if "họp" in e[1].lower(): bg_color = "#e74c3c"
            elif "chơi" in e[1].lower(): bg_color = "#27ae60"

            calendar_events.append({
                "title": f"{e[1]}", "start": iso_start, "end": iso_end,
                "backgroundColor": bg_color, "borderColor": bg_color,
                "extendedProps": {"location": e[4] if e[4] else "Không có", "remind": e[5], "raw": e[6], "id": e[0]}
            })
        except ValueError: continue

    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek,timeGridDay,listDay", 
        },
        "initialView": st.session_state['cal_view'], "initialDate": st.session_state['cal_date'],
        "timeZone": 'Asia/Ho_Chi_Minh', "locale": 'vi', "height": 700,
        "selectable": True, "navLinks": False, "editable": False, "dayMaxEvents": True,
    }
    
    cal_key = f"calendar_{st.session_state['cal_uid']}"
    cal_state = calendar(events=calendar_events, options=calendar_options, key=cal_key, callbacks=['dateClick', 'eventClick'])
    
    if cal_state.get("dateClick"):
        click_data = cal_state["dateClick"]
        date_clicked = click_data.get("dateStr")
        if not date_clicked and "date" in click_data: date_clicked = click_data["date"].split("T")[0]
        if date_clicked and st.session_state['cal_view'] == 'dayGridMonth':
            st.session_state['cal_view'] = 'timeGridDay'
            st.session_state['cal_date'] = date_clicked
            st.session_state['cal_uid'] += 1
            st.rerun()

    if cal_state.get("eventClick"):
        event_data = cal_state["eventClick"]["event"]
        props = event_data.get("extendedProps", {})
        st.write("---")
        st.subheader("📌 Chi Tiết Sự Kiện")
        st.markdown(f"""
        <div class="event-card" style="border-left: 5px solid {event_data.get('backgroundColor', '#3788d8')};">
            <h3 style="margin-top:0; color: white;">{event_data['title']}</h3>
            <p style="font-size: 1.1em; color: #ffbd45;">⏰ {event_data['start'].replace('T', ' ')[:16]} ➔ {event_data['end'].replace('T', ' ')[:16] if event_data['end'] else '...'}</p>
            <div style="display: flex; gap: 20px; color: #ddd;">
                <p>📍 {props.get('location')}</p> <p>🔔 {props.get('remind')} phút</p>
            </div>
            <p style="font-style: italic; color: #888; font-size: 0.9em; margin-bottom: 0;">Origin: "{props.get('raw')}"</p>
        </div>""", unsafe_allow_html=True)

    if st.session_state['cal_view'] in ['timeGridDay', 'listDay', 'timeGridWeek']:
        target_date = st.session_state['cal_date']
        if "T" in target_date: target_date = target_date.split("T")[0]
        st.divider()
        st.markdown(f"### 📋 Danh sách ngày: **{target_date}**")
        day_events = [e for e in events_db if target_date in e[2]]
        if day_events:
            for ev in day_events:
                t_start = ev[2].split("T")[1][:5] if "T" in ev[2] else ev[2].split(" ")[1][:5]
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="background-color: #FF4B4B; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">{t_start}</span>
                        <div><div style="font-size: 1.1em; font-weight: 600; color: #fff;">{ev[1]}</div>
                        <div style="font-size: 0.9em; color: #aaa;">📍 {ev[4] if ev[4] else "---"}</div></div>
                    </div>
                    <div style="text-align: right;"><span style="font-size: 0.85em; background: #333; padding: 4px 8px; border-radius: 10px; color: #ddd;">🔔 {ev[5]}p</span></div>
                </div>""", unsafe_allow_html=True)
        else: st.info("Trống lịch! 🎉")

# === TAB 3: DANH SÁCH & QUẢN LÝ (ĐÃ FIX TOÀN BỘ LOGIC VÀ LỖI PANDAS) ===
elif selected == "Danh Sách":
    st.markdown("## 📋 Quản Lý Danh Sách Sự Kiện")
    
    # 1. Cập nhật dữ liệu từ DB (Toàn bộ)
    events_db = get_all_events()
    df_full = pd.DataFrame(events_db, columns=["ID", "Sự kiện", "Bắt đầu", "Kết thúc", "Địa điểm", "Nhắc trước", "Câu lệnh gốc"])
    
    if df_full.empty:
        st.info("Chưa có dữ kiện nào. Hãy sang tab 'Thêm Sự Kiện' để bắt đầu.")
        st.stop() # Thoát nếu DB rỗng

    # --- 2. Lọc dữ liệu theo Search Term ---
    # Bắt đầu với DataFrame đã lọc (cho bảng hiển thị)
    df_filtered = df_full.copy()
    
    col_search, col_space = st.columns([2, 1])
    with col_search:
        search_term = st.text_input("🔍 Tìm nhanh:", placeholder="Nhập tên sự kiện hoặc địa điểm...")
    
    if search_term:
        # Áp dụng bộ lọc cho DataFrame hiển thị
        df_filtered = df_filtered[df_filtered['Sự kiện'].str.contains(search_term, case=False) | df_filtered['Địa điểm'].str.contains(search_term, case=False)]
    
    
    # --- 3. GIAO DIỆN CHÍNH (Hiển thị Bảng) ---
    col_table, col_action = st.columns([2, 1])
    
    with col_table:
        st.markdown("### 🗃️ Dữ liệu hiện tại")
        st.dataframe(
            df_filtered.drop(columns=["Câu lệnh gốc"]), 
            use_container_width=True, 
            hide_index=True,
            height=400
        )

    # --- 4. Lấy ID và Xử lý Form ---
    with col_action:
        st.markdown("### 🛠️ Thao tác")
        
        # Nếu bảng hiển thị rỗng sau khi lọc
        if df_filtered.empty:
            st.info("Không tìm thấy sự kiện nào khớp với tìm kiếm.")
            st.stop() # Thoát khỏi phần hiển thị form
            
        list_ids = df_filtered['ID'].tolist()
        
        # Selectbox chọn ID (sử dụng Key để Streamlit theo dõi giá trị)
        # Sử dụng df_filtered để populate list_ids
        selected_id = st.selectbox("Chọn Sự Kiện (ID):", 
                                   list_ids, 
                                   format_func=lambda x: f"ID {x}", 
                                   key="select_id_detail"
                                   )
        
        # --- BẮT ĐẦU FIX INDEX ERROR VÀ LỖI STATE ---
        # Lấy thông tin chi tiết từ DataFrame GỐC (df_full)
        event_row = df_full[df_full['ID'] == selected_id]
        
        # FIX: Kiểm tra nếu ID được chọn không còn tồn tại
        if event_row.empty:
            st.error(f"⚠️ Lỗi: Sự kiện ID {selected_id} không tìm thấy.")
            st.stop()

        current_event = event_row.iloc[0] # Truy cập an toàn
        # --- KẾT THÚC FIX LOGIC ---


        tab_edit, tab_delete = st.tabs(["✏️ SỬA ĐỔI", "🗑 XÓA BỎ"])
        
        # --- TAB CON: SỬA ---
        with tab_edit:
            with st.form(key="edit_form"):
                # Dữ liệu form lấy từ current_event đã được xác thực
                st.caption(f"Đang sửa: **{current_event['Sự kiện']}** (ID: {current_event['ID']})")
                
                # 1. Tên sự kiện
                new_name = st.text_input("Tên sự kiện:", value=current_event['Sự kiện'])
                
                # 2. Địa điểm
                new_loc = st.text_input("Địa điểm:", value=current_event['Địa điểm'] if current_event['Địa điểm'] else "")
                
                # 3. Xử lý thời gian (Tách ngày/giờ để hiển thị lên widget)
                try:
                    dt_start = datetime.strptime(current_event['Bắt đầu'], "%Y-%m-%dT%H:%M:%S")
                except:
                    dt_start = datetime.now() 
                    
                c_date, c_time = st.columns(2)
                d_input = c_date.date_input("Ngày:", value=dt_start.date())
                t_input = c_time.time_input("Giờ:", value=dt_start.time())
                
                # 4. Nhắc nhở
                new_remind = st.number_input("Nhắc trước (phút):", min_value=0, value=int(current_event['Nhắc trước']))
                
                # Submit button
                if st.form_submit_button("💾 LƯU THAY ĐỔI", type="primary"):
                    new_start_dt = datetime.combine(d_input, t_input)
                    new_start_str = new_start_dt.strftime("%Y-%m-%dT%H:%M:%S")
                    new_end_str = (new_start_dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")

                    # Gọi hàm Update DB
                    update_event(current_event['ID'], new_name, new_start_str, new_end_str, new_loc, new_remind)
                    
                    st.toast("Cập nhật thành công!", icon="✅")
                    time.sleep(1)
                    st.rerun()

        # --- TAB CON: XÓA ---
        with tab_delete:
            st.warning("Hành động này không thể hoàn tác.")
            st.write(f"Bạn chắc chắn muốn xóa: **{current_event['Sự kiện']}** (ID: {current_event['ID']})?")
            if st.button("Xác nhận Xóa", type="primary"):
                delete_event(current_event['ID'])
                st.toast("Đã xóa sự kiện!", icon="🗑")
                time.sleep(1)
                st.rerun()

# === TAB 4: TEST & IMPORT ===
elif selected == "Kiểm Thử & Import":
    st.markdown("## 🧪 Kiểm Thử Batch")
    uploaded_file = st.file_uploader("Chọn file CSV:", type=["csv"])
    if 'batch_results' not in st.session_state: st.session_state['batch_results'] = None
    if uploaded_file:
        try:
            df_test = pd.read_csv(uploaded_file)
            if "input" in df_test.columns:
                if st.button("▶️ Chạy Phân Tích", type="primary"):
                    results = []
                    progress_bar = st.progress(0)
                    total_rows = len(df_test)
                    with st.spinner("Đang xử lý..."):
                        for i, row in df_test.iterrows():
                            raw = str(row['input'])
                            try:
                                out = nlp.process(raw)
                                stat = "✅ Hợp lệ"
                                if out['error']: stat = "❌ Lỗi Logic"
                                elif out['start_time'] is None: stat = "❌ Bỏ qua"
                                results.append({
                                    "Câu lệnh gốc": raw, "Sự kiện": out['event'],
                                    "Bắt đầu": out['start_time'], "Kết thúc": out['end_time'],
                                    "Địa điểm": out['location'], "Nhắc": out['reminder_minutes'],
                                    "Trạng thái": stat, "_raw_start": out['start_time'], "_raw_end": out['end_time']
                                })
                            except: pass
                            progress_bar.progress((i + 1) / total_rows)
                    st.session_state['batch_results'] = results
                    st.success("Xong!")
            else: st.error("Thiếu cột 'input'")
        except: st.error("Lỗi file")

    if st.session_state['batch_results']:
        res_df = pd.DataFrame(st.session_state['batch_results'])
        def hl(v): return 'background-color: #d4edda; color: #155724' if v == '✅ Hợp lệ' else 'background-color: #f8d7da; color: #721c24'
        st.dataframe(res_df.style.map(hl, subset=['Trạng thái']), use_container_width=True)
        if st.button("💾 LƯU SỰ KIỆN HỢP LỆ", type="primary"):
            c = 0
            for it in st.session_state['batch_results']:
                if it['_raw_start']:
                    add_event(it['Sự kiện'], it['_raw_start'], it['_raw_end'], it['Địa điểm'], it['Nhắc'], it['Câu lệnh gốc'])
                    c += 1
            st.toast(f"Lưu thành công {c} mục!", icon="🎉")
            del st.session_state['batch_results']
            time.sleep(1.5)
            st.rerun()