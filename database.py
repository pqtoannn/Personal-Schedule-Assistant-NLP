import sqlite3
import os

# --- CẤU HÌNH ĐƯỜNG DẪN TUYỆT ĐỐI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "scheduler.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_table():
    conn = get_connection()
    c = conn.cursor()
    # --- CẬP NHẬT: Thêm cột end_time ---
    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,      -- Cột mới lưu thời gian kết thúc
            location TEXT,
            reminder_minutes INTEGER DEFAULT 0,
            raw_input TEXT      -- Lưu câu lệnh gốc
        )
    """)
    conn.commit()
    conn.close()

# --- CẬP NHẬT: Thêm tham số end_time vào hàm ---
def add_event(event, start_time, end_time, location, reminder_minutes, raw_input=""):
    conn = get_connection()
    c = conn.cursor()
    # Insert đủ 6 trường dữ liệu (trừ ID tự tăng)
    c.execute("""
        INSERT INTO events (event, start_time, end_time, location, reminder_minutes, raw_input) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event, start_time, end_time, location, reminder_minutes, raw_input))
    conn.commit()
    conn.close()

def get_all_events():
    conn = get_connection()
    c = conn.cursor()
    # Thứ tự trả về: 0:id, 1:event, 2:start, 3:end, 4:loc, 5:remind, 6:raw
    c.execute("SELECT * FROM events ORDER BY start_time ASC")
    data = c.fetchall()
    conn.close()
    return data

def delete_event(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    
# [Thêm vào cuối file database.py]
def update_event(event_id, new_event, new_start, new_end, new_location, new_remind):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE events 
        SET event=?, start_time=?, end_time=?, location=?, reminder_minutes=?
        WHERE id=?
    """, (new_event, new_start, new_end, new_location, new_remind, event_id))
    conn.commit()
    conn.close()

# Hàm lấy chi tiết 1 sự kiện để điền vào form sửa
def get_event_by_id(event_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM events WHERE id=?", (event_id,))
    data = c.fetchone()
    conn.close()
    return data

# Chạy tạo bảng (Nếu chưa có file db thì sẽ tạo mới)
create_table()