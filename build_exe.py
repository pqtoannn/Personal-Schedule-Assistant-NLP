import PyInstaller.__main__
import os
import shutil

APP_NAME = "PersonalAssistant_v7"

# --- DANH SÁCH FILE CẦN GÓI ---
datas = [
    ('app.py', '.'),
    ('database.py', '.'),
    ('nlp_engine.py', '.'),
    ('nlp_core', 'nlp_core'),      # Folder NLP
    ('assets', 'assets'),          # Folder Âm thanh
    ('test_cases.csv', '.'),       # File Test
    ('scheduler.db', '.'),         # File Data
]

datas_str = []
for src, dest in datas:
    if os.path.isdir(src):
        if os.name == 'nt': datas_str.append(f'--add-data={src}{os.pathsep}{dest}')
        else: datas_str.append(f'--add-data={src}:{dest}')
    else:
        if os.path.exists(src):
            if os.name == 'nt': datas_str.append(f'--add-data={src}{os.pathsep}.')
            else: datas_str.append(f'--add-data={src}:.')
        else: print(f"⚠️ Warning: {src} not found.")

print("🚀 Đang đóng gói (Chế độ Thư mục - Nhanh & Admin)... Vui lòng đợi...")

PyInstaller.__main__.run([
    'run.py',                       
    f'--name={APP_NAME}',           
    
    '--onedir',                     # <-- Chế độ THƯ MỤC (Khởi động nhanh)
    '--uac-admin',                  # <-- Yêu cầu quyền Admin
    '--console',                    # <-- Hiện cửa sổ đen thông báo
    
    '--clean',                      
    
    # --- Fix lỗi thiếu thư viện ---
    '--hidden-import=streamlit_autorefresh',
    '--hidden-import=dateparser',
    '--hidden-import=babel.numbers',
    
    # --- Thu thập tài nguyên ---
    '--collect-all=streamlit',              
    '--collect-all=underthesea',
    '--collect-all=dateparser',
    '--collect-all=streamlit_calendar',
    '--collect-all=streamlit_option_menu',
    '--collect-all=streamlit_autorefresh',
    '--collect-all=pandas',
    
    *datas_str,
])

print(f"✅ Xong! Kiểm tra thư mục 'dist/{APP_NAME}'")