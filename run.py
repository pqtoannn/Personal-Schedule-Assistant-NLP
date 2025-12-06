import streamlit.web.cli as stcli
import os, sys
import time

def resolve_path(path):
    # Hàm này giúp tìm đường dẫn file khi đã đóng gói vào exe
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.join(os.path.abspath("."), path)

if __name__ == "__main__":
    # --- PHẦN THÔNG BÁO KHỞI ĐỘNG ---
    os.system('cls' if os.name == 'nt' else 'clear') # Xóa rác màn hình nếu có
    
    print("\n" * 2)
    print("="*60)
    print("      🚀  TRỢ LÝ CÁ NHÂN ĐANG KHỞI ĐỘNG...      ")
    print("="*60)
    print("\n[INFO] Đang tải thư viện và dữ liệu...")
    print("[INFO] Vui lòng không tắt cửa sổ này.")
    print("[INFO] Trình duyệt sẽ tự động mở sau vài giây.")
    print("\n" + "-"*60 + "\n")
    
    # --- KẾT THÚC PHẦN THÔNG BÁO ---

    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())