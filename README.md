# 📅 Trợ Lý Lịch Trình Cá Nhân (Personal Schedule Assistant)

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red.svg)
![NLP](https://img.shields.io/badge/NLP-Underthesea-green.svg)

Ứng dụng Desktop quản lý lịch trình cá nhân thông minh, cho phép nhập liệu bằng ngôn ngữ tự nhiên tiếng Việt, tự động trích xuất thông tin và nhắc nhở sự kiện.

## ✨ Tính năng nổi bật

* **Xử lý ngôn ngữ tự nhiên (NLP):**
    * Hiểu câu lệnh tiếng Việt: *"Họp team lúc 9h sáng mai ở phòng 302"*.
    * Tự động trích xuất: Tên sự kiện, Thời gian, Địa điểm, Nhắc nhở.
    * Xử lý thời gian linh hoạt: *"tuần sau", "ngày mốt", "kém 15", "sau 30 phút nữa"*.
* **Quản lý lịch trình:** Xem lịch theo Tháng/Tuần/Ngày, tìm kiếm và chỉnh sửa sự kiện.
* **Hệ thống nhắc nhở:** Chạy ngầm, phát âm thanh và hiện thông báo Popup khi đến giờ hẹn.
* **Hoạt động Offline:** Sử dụng SQLite, không cần Internet, đảm bảo riêng tư.

## 🛠️ Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.10
* **Giao diện:** Streamlit
* **NLP Engine:** Underthesea, Dateparser, Regex
* **Database:** SQLite3
* **Đóng gói:** PyInstaller

## 🚀 Hướng dẫn Cài đặt & Chạy (Dành cho Developer)

Nếu bạn muốn tham khảo mã nguồn hoặc phát triển tiếp:

### 1. Clone dự án
```bash
git clone [https://github.com/pqtoannn/Personal-Schedule-Assistant-NLP.git](https://github.com/pqtoannn/Personal-Schedule-Assistant-NLP.git)
cd Personal-Schedule-Assistant-NLP
```
2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```
3. Chạy ứng dụng
```bash
streamlit run app.py

```
Tải xuống (Dành cho Người dùng cuối)
Nếu bạn chỉ muốn tải ứng dụng về dùng ngay (không cần cài Python), vui lòng truy cập mục Releases để tải file .exe đã đóng gói.

📂 Cấu trúc dự án
Personal-Schedule-Assistant-NLP/
├── assets/              # Tài nguyên (Âm thanh, icon)
├── nlp_core/            # Các module xử lý ngôn ngữ
│   ├── extractors.py    # Trích xuất thực thể
│   ├── text_utils.py    # Tiền xử lý
│   └── time_processor.py# Logic xử lý thời gian
├── app.py               # Giao diện chính (Streamlit)
├── database.py          # Xử lý SQLite
├── nlp_engine.py        # Bộ điều phối trung tâm
├── constants.py         # Định nghĩa Regex & Hằng số
└── requirements.txt     # Danh sách thư viện