import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# ==========================================
# 1. โหลดฟอนต์ภาษาไทยสำหรับการวาดแบบ
# ==========================================
@st.cache_resource
def load_thai_font():
    font_path = "THSarabunNew.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve("https://github.com/Phonbopit/sarabun-webfont/raw/master/fonts/thsarabunnew-webfont.ttf", font_path)
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'TH Sarabun New'
    plt.rcParams['font.size'] = 14

load_thai_font()

# ==========================================
# 2. ตั้งค่าหน้าต่างโปรแกรม
# ==========================================
st.set_page_config(page_title="โปรแกรมงานระดับมาตรฐาน", layout="wide")
st.title("โปรแกรมคำนวณงานระดับและวาดรูปตัด (Profile Leveling)")

# ==========================================
# 3. ส่วนการรับข้อมูล (ตาราง Field Book)
# ==========================================
st.subheader("1. กรอกข้อมูลสมุดจดงานระดับ (Field Book)")
bm_elev = st.number_input("ค่าระดับจุดเริ่มต้น BM.1 (First Elev.):", value=100.000, format="%.3f")

# จำลองข้อมูลเริ่มต้นให้เหมือนในรูปตัวอย่างเป๊ะๆ
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Sta.': ['BM.1', '0+000', '0+025', '0+050', '0+075', '0+100', 'TP.1', '0+125', '0+150', '0+175', '0+200', '0+225', '0+250', 'BM.2'],
        'B.S.': [2.910, None, None, None, None, None, 0.911, None, None, None, None, None, None, None],
        'I.F.S.': [None, 2.220, 1.670, 2.250, 2.890, 2.500, None, 0.190, 0.210, 0.630, 1.960, 2.610, 2.880, None],
        'F.S.': [None, None, None, None, None, None, 1.171, None, None, None, None, None, None, 1.713],
        'Design Elev.': [None, 100.500, 101.000, 100.500, 100.000, 100.200, None, 102.000, 102.500, 102.000, 102.500, 100.500, 100.000, None],
        'Remark': ['สมมุติ', '', '', '', '', '', '', '', '', '', '', '', '', '']
    })

# แสดงตารางให้ผู้ใช้งานกรอก (ซ่อนคอลัมน์คำนวณไว้ก่อน)
st.write("📝 *ตารางนี้สามารถคัดลอกข้อมูลจาก Excel มาวาง (Ctrl+V) หรือพิมพ์ตัวเลขลงไปได้โดยตรง*")
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)

# ==========================================
# 4. ปุ่มประมวลผลและการคำนวณ
# ==========================================
if st.button("ประมวลผลคำนวณค่าระดับ และวาดแบบ", type="primary"):
    df = edited_df.copy()
    
    # สร้างคอลัมน์เก็บผลลัพธ์
    df['H.I.'] = np.nan
    df['Elev.'] = np.nan
    current_hi = np.nan
    
    # อัลกอริทึมคำนวณแบบวิ่งทีละแถว (เหมือนช่างสำรวจกดเครื่องคิดเลข)
    for idx, row in df.iterrows():
        # แปลงค่าให้เป็นตัวเลขอย่างปลอดภัย (ป้องกันผู้ใช้พิมพ์ช่องว่าง)
        bs = float(row['B.S.']) if pd.notna(row['B.S.']) and str(row['B.S.']).strip() != '' else np.nan
        ifs = float(row['I.F.S.']) if pd.notna(row['I.F.S.']) and str(row['I.F.S.']).strip() != '' else np.nan
        fs = float(row['F.S.']) if pd.notna(row['F.S.']) and str(row['F.S.']).strip() != '' else np.nan
        
        # ก. การหาค่า Elev.
        if idx == 0:
            df.at[idx, 'Elev.'] = bm_elev # แถวแรกรับค่าเริ่มต้น
        else:
            if pd.notna(ifs):
                df.at[idx, 'Elev.'] = current_hi - ifs
            elif pd.notna(fs):
                df.at[idx, 'Elev.'] = current_hi - fs
                
        # ข. การหาค่า H.I. (ตั้งกล้องใหม่)
        if pd.notna(bs):
            current_hi = df.at[idx, 'Elev.'] + bs
            df.at[idx, 'H.I.'] = current_hi

    # ==========================================
    # 5. แสดงตารางผลลัพธ์ฉบับสมบูรณ์
    # ==========================================
    st.subheader("2. ตารางผลการคำนวณ (Completed Field Book)")
    
    # จัดรูปแบบตารางให้แสดงทศนิยม 3 ตำแหน่ง
    display_df = df[['Sta.', 'B.S.', 'H.I.', 'I.F.S.', 'F.S.', 'Elev.', 'Remark']].copy()
    for col in ['B.S.', 'H.I.', 'I.F.S.', 'F.S.', 'Elev.']:
        display_df[col] = display_df[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "")
        
    st.dataframe(display_df, use_container_width=True)

    # ==========================================
    # 6. กล่องตรวจสอบความคลาดเคลื่อน (Error Check)
    # ==========================================
    sum_bs = df['B.S.'].astype(float).sum()
    sum_fs = df['F.S.'].astype(float).sum()
    first_elev = df['Elev.'].iloc[0]
    last_elev = df['Elev.'].dropna().iloc[-1]
    
    diff_bs_fs = sum_bs - sum_fs
    diff_elev = last_elev - first_elev
    
    # เช็คว่าผลต่างเท่ากันหรือไม่ (เผื่อทศนิยมคลาดเคลื่อนเล็กน้อย ใช้ round เช็ค)
    is_correct = round(diff_bs_fs, 3) == round(diff_elev, 3)
    
    st.subheader("ตรวจสอบการคำนวณ")
    if is_correct:
        st.success(f"""
        **ผลรวม ΣB.S. - ΣF.S. = Last Elev. - First Elev.**  ✅ (คำนวณถูกต้อง)
        
        * {sum_bs:.3f} - {sum_fs:.3f} = **{diff_bs_fs:.3f}**
        * {last_elev:.3f} - {first_elev:.3f} = **{diff_elev:.3f}**
        """)
    else:
        st.error(f"""
        **มีข้อผิดพลาดในการคำนวณ หรือจดค่าผิดพลาด** ❌
        
        * ΣB.S. - ΣF.S. = **{diff_bs_fs:.3f}**
        * Last Elev. - First Elev. = **{diff_elev:.3f}**
        """)

    # ==========================================
    # 7. วาดรูปตัดตามยาว (กรองเฉพาะ Sta. ที่เป็นตัวเลข)
    # ==========================================
    st.subheader("3. รูปตัดตามยาวโครงการ (Longitudinal Profile)")
    
    # ฟังก์ชันแปลง '0+025' เป็นระยะทาง 25 สำหรับพล็อตกราฟ (ละเว้น BM และ TP อัตโนมัติ)
    def parse_sta(sta_str):
        if isinstance(sta_str, str) and '+' in sta_str:
            parts = sta_str.split('+')
            try:
                return float(parts[0]) * 1000 + float(parts[1])
            except:
                return np.nan
        return np.nan
        
    df['Distance (m)'] = df['Sta.'].apply(parse_sta)
    
    # ดึงเฉพาะข้อมูลเส้นทางหลัก (ตัด BM, TP ออกไปจากการวาดกราฟ)
    plot_df = df.dropna(subset=['Distance (m)', 'Elev.']).copy()
    plot_df['Design Elev.'] = pd.to_numeric(plot_df['Design Elev.'], errors='coerce')
    
    if len(plot_df) > 1:
        fig, ax = plt.subplots(figsize=(15, 6))
        
        # วาดกราฟ
        ax.plot(plot_df['Distance (m)'], plot_df['Elev.'], color='blue', linewidth=2, label='ระดับดินเดิม')
        
        # วาดระดับออกแบบ และแรเงา (ถ้ามีการกรอก Design Elev.)
        if plot_df['Design Elev.'].notna().any():
            ax.plot(plot_df['Distance (m)'], plot_df['Design Elev.'], color='red', linewidth=2, label='ระดับก่อสร้าง')
            
            # บังคับข้อมูลเป็นตัวเลขสำหรับการแรเงา
            elev_array = np.array(plot_df['Elev.'], dtype=float)
            design_array = np.array(plot_df['Design Elev.'], dtype=float)
            dist_array = np.array(plot_df['Distance (m)'], dtype=float)
            
            ax.fill_between(dist_array, elev_array, design_array, 
                            where=(design_array > elev_array), 
                            interpolate=True, color='red', alpha=0.15, hatch='//', label='ดินถม (Fill)')
            ax.fill_between(dist_array, elev_array, design_array, 
                            where=(design_array < elev_array), 
                            interpolate=True, color='blue', alpha=0.15, hatch='\\\\', label='ดินตัด (Cut)')

        ax.set_title('รูปตัดตามยาวโครงการสร้างทาง', fontsize=18)
        ax.set_ylabel('ค่าระดับความสูง (m)')
        ax.set_xticks(plot_df['Distance (m)'])
        ax.set_xticklabels(plot_df['Sta.'])
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='upper right')
        
        st.pyplot(fig)
    else:
        st.info("ระบุข้อมูลระยะทาง (Sta.) ในรูปแบบ 0+000 ให้ครบถ้วนเพื่อแสดงกราฟ")
```eof

### สิ่งที่อัปเดตเพิ่มเติมในเวอร์ชันนี้:
1.  **คอลัมน์ตรงเป๊ะ:** เปลี่ยนหัวตารางเป็น `Sta.`, `B.S.`, `I.F.S.`, `F.S.` แบบที่ช่างสำรวจคุ้นเคย
2.  **รองรับ TP.1 และ BM.2:** สามารถใส่จุด Turning Point ตรงไหนก็ได้ในตาราง โปรแกรมจะคำนวณ F.S. ตัดระดับก่อน แล้วหา H.I. ใหม่ทันทีในบรรทัดเดียวกันให้โดยอัตโนมัติ
3.  **กล่องสีเขียวตรวจสอบ Error:** เพิ่มระบบเช็ค `ΣBS - ΣFS = Last Elev - First Elev` ตอนท้ายตาราง หากตัวเลขตรงกัน จะขึ้นกล่องสีเขียวแจ้งว่า "คำนวณถูกต้อง ✅" แต่ถ้าจดค่ามาผิด จะขึ้นกล่องสีแดง ❌ 
4.  **ความฉลาดในการวาดกราฟ:** กราฟจะวาดเฉพาะจุดที่เป็น Station (เช่น 0+000) โดยจะ **ข้าม** จุด TP และ BM ให้เองอัตโนมัติ ทำให้รูปวาดที่ได้มีความถูกต้องตามมาตรฐานงานวิศวกรรม

**วิธีอัปเดตเข้าโปรแกรมของคุณ:**
1. ไปที่ GitHub ของคุณ เปิดไฟล์ `app.py`
2. กดไอคอน ✏️ (รูปดินสอ) มุมขวาบนเพื่อแก้ไขไฟล์
3. ลบโค้ดเดิมทิ้งทั้งหมด แล้วก๊อปปี้โค้ดด้านบนนี้ไปวางแทน
4. เลื่อนลงมากดปุ่มสีเขียว **Commit changes**
5. รอ 1 นาที แล้วกลับไปหน้าเว็บโปรแกรมของคุณ กด F5 (Refresh) การเปลี่ยนแปลงใหม่ทั้งหมดจะแสดงขึ้นมาทันทีครับ!
