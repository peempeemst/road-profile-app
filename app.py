import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# 1. โหลดฟอนต์ภาษาไทยสำหรับการวาดแบบบนระบบ Cloud
@st.cache_resource
def load_thai_font():
    font_path = "THSarabunNew.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve("https://github.com/Phonbopit/sarabun-webfont/raw/master/fonts/thsarabunnew-webfont.ttf", font_path)
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'TH Sarabun New'
    plt.rcParams['font.size'] = 14

load_thai_font()

# 2. ตั้งค่าหน้าต่างโปรแกรม
st.set_page_config(page_title="โปรแกรมงานสำรวจและวาดรูปตัด", layout="wide")
st.title("โปรแกรมคำนวณและวาดรูปตัดตามยาว (Longitudinal Road Profile)")

# 3. ส่วนการรับข้อมูล
st.subheader("1. ตารางข้อมูลงานสำรวจและระดับออกแบบ")
bm_elev = st.number_input("ค่าระดับ Benchmark เริ่มต้น (m):", value=100.000, format="%.3f")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'STA (กม.)': ['0+000', '0+025', '0+050', '0+075', '0+100'],
        'Distance (m)': [0, 25, 50, 75, 100],
        'B.S.': [1.500, None, None, None, None],
        'I.S.': [None, 1.200, 2.500, 1.200, 0.900],
        'F.S.': [None, None, None, None, None],
        'Design Elev.': [100.500, 100.400, 100.100, 100.100, 100.300]
    })

# ตารางที่สามารถกรอกค่าได้ทันที
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)

# 4. ส่วนประมวลผลและวาดแบบ
if st.button("ประมวลผลและสร้างรูปตัด", type="primary"):
    df = edited_df.copy()
    df['H.I.'] = np.nan
    df['Existing Elev.'] = np.nan
    
    current_hi = np.nan
    
    # อัลกอริทึมคำนวณระดับดินเดิม
    for idx, row in df.iterrows():
        if idx == 0:
            df.at[idx, 'Existing Elev.'] = bm_elev
            
        if pd.notna(row['I.S.']):
            df.at[idx, 'Existing Elev.'] = current_hi - float(row['I.S.'])
        if pd.notna(row['F.S.']):
            df.at[idx, 'Existing Elev.'] = current_hi - float(row['F.S.'])
            
        if pd.notna(row['B.S.']):
            current_hi = df.at[idx, 'Existing Elev.'] + float(row['B.S.'])
            df.at[idx, 'H.I.'] = current_hi

    st.subheader("2. ตารางผลการคำนวณค่าระดับดินเดิม")
    st.dataframe(df[['STA (กม.)', 'B.S.', 'H.I.', 'I.S.', 'F.S.', 'Existing Elev.', 'Design Elev.']], use_container_width=True)
# บังคับแปลงข้อมูลในคอลัมน์กราฟให้เป็นตัวเลขทั้งหมด
    df['Distance (m)'] = pd.to_numeric(df['Distance (m)'], errors='coerce')
    df['Existing Elev.'] = pd.to_numeric(df['Existing Elev.'], errors='coerce')
    df['Design Elev.'] = pd.to_numeric(df['Design Elev.'], errors='coerce')
    st.subheader("3. รูปตัดตามยาวโครงการ (Longitudinal Profile)")
    fig, ax = plt.subplots(figsize=(15, 6))
    
    # วาดเส้นระดับดินเดิมและระดับก่อสร้าง
    ax.plot(df['Distance (m)'], df['Existing Elev.'], color='blue', linewidth=2, label='ระดับดินเดิม')
    ax.plot(df['Distance (m)'], df['Design Elev.'], color='red', linewidth=2, label='ระดับก่อสร้าง')
    
    # คำนวณและแรเงางานดินตัด-ดินถม
    ax.fill_between(df['Distance (m)'], df['Existing Elev.'], df['Design Elev.'], 
                    where=(df['Design Elev.'] > df['Existing Elev.']), 
                    interpolate=True, color='red', alpha=0.15, hatch='//', label='ดินถม (Fill)')
    ax.fill_between(df['Distance (m)'], df['Existing Elev.'], df['Design Elev.'], 
                    where=(df['Design Elev.'] < df['Existing Elev.']), 
                    interpolate=True, color='blue', alpha=0.15, hatch='\\\\', label='ดินตัด (Cut)')

    # ปรับแต่งรายละเอียดรูปตัดตามยาว
    ax.set_title('รูปตัดตามยาวโครงการสร้างทาง (Longitudinal Road Profile)', fontsize=18)
    ax.set_ylabel('ค่าระดับความสูง (m)')
    ax.set_xticks(df['Distance (m)'])
    ax.set_xticklabels(df['STA (กม.)'])
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(loc='upper right')
    
    # สร้าง Data Band (ตารางข้อมูลด้านล่างแบบ)
    table_data = [df['STA (กม.)'].tolist(), 
                  df['Existing Elev.'].round(3).tolist(), 
                  df['Design Elev.'].round(3).tolist()]
    table_row_labels = ['ระยะทาง (STA)', 'ระดับดินเดิม', 'ระดับออกแบบ']
    table = ax.table(cellText=table_data, rowLabels=table_row_labels, loc='bottom', bbox=[0, -0.4, 1, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    
    plt.subplots_adjust(bottom=0.3)
    st.pyplot(fig)
