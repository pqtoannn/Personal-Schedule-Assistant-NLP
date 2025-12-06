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

## 📂 Cấu trúc dự án

Dự án được tổ chức theo cấu trúc phân lớp (Layered Architecture) rõ ràng, với các module NLP được nhóm lại trong thư mục chuyên biệt:

```text
Personal-Schedule-Assistant-NLP/
├── assets/              # Tài nguyên (Âm thanh, icon)
├── nlp_core/            # Module Xử lý Ngôn ngữ Lõi
│   ├── constants.py     # Định nghĩa các Regex và Hằng số (Đã chuyển vào nlp_core)
│   ├── extractors.py    # Logic trích xuất thực thể (Reminder, Location)
│   ├── text_utils.py    # Tiền xử lý văn bản (Chuẩn hóa, xóa Stopwords)
│   └── time_processor.py# Logic phân tích thời gian chuyên sâu
├── .gitignore           # Luật bỏ qua file (venv, dist, build)
├── README.md            # Mô tả dự án này
├── app.py               # Giao diện chính và Logic điều khiển Streamlit
├── build_exe.py         # Script đóng gói ứng dụng (.exe)
├── database.py          # Module kết nối và thao tác SQLite
├── nlp_engine.py        # Bộ điều phối trung tâm NLP
├── requirements.txt     # Danh sách thư viện Python
├── run.py               # Script khởi chạy (được gọi bởi build_exe)
├── scheduler.db         # [IGNORE] File Database SQLite cục bộ
└── test_cases_final.csv # File dữ liệu kiểm thử (30 câu lệnh)

```text
📖 Hướng dẫn Sử dụng (Chi tiết)
Sau khi khởi chạy ứng dụng thành công, người dùng có thể tương tác qua 4 tab chức năng chính:

1. Thêm Sự kiện Thông minh (Tab "Thêm Sự Kiện (AI)")
Đây là chức năng cốt lõi sử dụng Module NLP để tạo lịch trình nhanh nhất.

Nhập lệnh: Gõ câu lệnh tiếng Việt tự nhiên vào ô nhập liệu. Ví dụ: "Khám răng lúc 8h sáng mai tại bệnh viện Hoàn Mỹ, nhắc trước 30 phút".

Phân tích: Nhấn nút "🚀 Phân Tích". Ứng dụng sẽ trích xuất và hiển thị các trường thông tin (Sự kiện, Thời gian, Địa điểm) vào các thẻ (Card).

Lưu trữ: Kiểm tra kết quả phân tích. Nếu chính xác, nhấn "💾 LƯU VÀO LỊCH" để ghi sự kiện vào Database. Nếu lỗi, nhập lại câu lệnh.

2. Tương tác với Lịch trình (Tab "Xem Lịch Trình")
Tab này cung cấp giao diện trực quan dưới dạng lịch (Calendar View).

Mở xem Ngày: Để xem toàn bộ sự kiện chi tiết của một ngày, bạn hãy click đúp vào ngày đó trên lịch tháng. Giao diện sẽ chuyển sang dạng ngày (timeGridDay) và liệt kê chi tiết các sự kiện theo giờ.

Xem chi tiết Sự kiện: Nhấp vào tiêu đề một sự kiện trên lịch để xem card chi tiết có chứa Địa điểm và Câu lệnh gốc.

Quay lại: Nhấn nút "⬅️ Về Xem Tháng" ở góc trên bên trái để trở về chế độ xem tổng quan.

3. Quản lý (Sửa, Xóa, Tìm kiếm) (Tab "Danh Sách")
Phần này dùng để quản trị dữ liệu, đảm bảo tính năng Sửa/Xóa (CRUD) hoạt động ổn định.

Tìm kiếm: Nhập từ khóa (tên sự kiện hoặc địa điểm) vào ô "🔍 Tìm nhanh". Bảng hiển thị bên trái sẽ được lọc theo thời gian thực.

Chọn ID:

Nếu không tìm kiếm: Selectbox sẽ hiển thị toàn bộ ID hiện có.

Nếu đã tìm kiếm: Selectbox chỉ hiển thị các ID đang hiển thị trên bảng đã lọc.

Chỉnh sửa: Sau khi chọn ID, chuyển sang tab con "✏️ SỬA ĐỔI". Cập nhật các trường thông tin (tên, ngày, giờ) và nhấn "💾 LƯU THAY ĐỔI".

Xóa bỏ: Chuyển sang tab con "🗑 XÓA BỎ" và nhấn nút xác nhận để xóa sự kiện vĩnh viễn.

4. Hệ thống Nhắc nhở & Kiểm thử
Báo thức: Hệ thống hoạt động ngầm. Khi đến giờ hẹn (trừ đi thời gian nhắc nhở), ứng dụng sẽ tự động phát âm thanh và hiện thông báo Popup. Nhấn "🔕 TẮT NGAY" để dừng báo thức.

Kiểm thử Batch: Tab "Kiểm Thử & Import" cho phép tải lên file CSV (có cột input) và chạy phân tích hàng loạt trên Module NLP để kiểm tra độ chính xác.

