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
st.markdown("---")

# ==========================================
# 3. ส่วนการรับข้อมูล (ตาราง Field Book)
# ==========================================
st.subheader("1. ข้อมูลสมุดจดงานระดับ (Field Book)")

# แบ่งคอลัมน์เพื่อความสวยงาม
col1, col2 = st.columns([1, 2])
with col1:
    bm_elev = st.number_input("ค่าระดับจุดเริ่มต้น BM.1 (First Elev.):", value=100.000, format="%.3f")
with col2:
    st.info("💡 สามารถคัดลอกข้อมูลจาก Excel มาวาง (Ctrl+V) ลงในตารางด้านล่างได้โดยตรง")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Sta.': ['BM.1', '0+000', '0+025', '0+050', '0+075', '0+100', 'TP.1', '0+125', '0+150', '0+175', '0+200', '0+225', '0+250', 'BM.2'],
        'B.S.': [2.910, None, None, None, None, None, 0.911, None, None, None, None, None, None, None],
        'I.F.S.': [None, 2.220, 1.670, 2.250, 2.890, 2.500, None, 0.190, 0.210, 0.630, 1.960, 2.610, 2.880, None],
        'F.S.': [None, None, None, None, None, None, 1.171, None, None, None, None, None, None, 1.713],
        'Design Elev.': [None, 100.500, 101.000, 100.500, 100.000, 100.200, None, 102.000, 102.500, 102.000, 102.500, 100.500, 100.000, None],
        'Remark': ['สมมุติ', '', '', '', '', '', '', '', '', '', '', '', '', '']
    })

# ปรับขนาดความสูงตารางให้เหมาะสม
edited_df = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True, height=350)

# ปุ่มประมวลผลขนาดใหญ่
st.markdown("<br>", unsafe_allow_html=True)
calculate_btn = st.button("ประมวลผลคำนวณค่าระดับ และสร้างรูปตัด", type="primary", use_container_width=True)
st.markdown("---")

# ==========================================
# 4. ปุ่มประมวลผลและการคำนวณ
# ==========================================
if calculate_btn:
    df = edited_df.copy()
    
    df['H.I.'] = np.nan
    df['Elev.'] = np.nan
    current_hi = np.nan
    
    for idx, row in df.iterrows():
        bs = float(row['B.S.']) if pd.notna(row['B.S.']) and str(row['B.S.']).strip() != '' else np.nan
        ifs = float(row['I.F.S.']) if pd.notna(row['I.F.S.']) and str(row['I.F.S.']).strip() != '' else np.nan
        fs = float(row['F.S.']) if pd.notna(row['F.S.']) and str(row['F.S.']).strip() != '' else np.nan
        
        if idx == 0:
            df.at[idx, 'Elev.'] = bm_elev
        else:
            if pd.notna(ifs):
                df.at[idx, 'Elev.'] = current_hi - ifs
            elif pd.notna(fs):
                df.at[idx, 'Elev.'] = current_hi - fs
                
        if pd.notna(bs):
            current_hi = df.at[idx, 'Elev.'] + bs
            df.at[idx, 'H.I.'] = current_hi

    # ==========================================
    # 5. แสดงตารางผลลัพธ์
    # ==========================================
    st.subheader("2. ตารางผลการคำนวณ (Completed Field Book)")
    
    display_df = df[['Sta.', 'B.S.', 'H.I.', 'I.F.S.', 'F.S.', 'Elev.', 'Remark']].copy()
    for col in ['B.S.', 'H.I.', 'I.F.S.', 'F.S.', 'Elev.']:
        display_df[col] = display_df[col].map(lambda x: f"{x:.3f}" if pd.notna(x) else "")
        
    st.dataframe(display_df, use_container_width=True)

    # ==========================================
    # 6. กล่องตรวจสอบความคลาดเคลื่อน (Error Check)
    # ==========================================
    st.subheader("การตรวจสอบความคลาดเคลื่อน (Error Check)")
    
    sum_bs = df['B.S.'].astype(float).sum()
    sum_fs = df['F.S.'].astype(float).sum()
    first_elev = df['Elev.'].iloc[0]
    last_elev = df['Elev.'].dropna().iloc[-1]
    
    diff_bs_fs = sum_bs - sum_fs
    diff_elev = last_elev - first_elev
    is_correct = round(diff_bs_fs, 3) == round(diff_elev, 3)
    
    # แสดงผลแบบ Metric Cards
    col_err1, col_err2, col_err3 = st.columns(3)
    with col_err1:
        st.metric(label="ΣB.S. - ΣF.S.", value=f"{diff_bs_fs:.3f}")
    with col_err2:
        st.metric(label="Last Elev. - First Elev.", value=f"{diff_elev:.3f}")
    with col_err3:
        if is_correct:
            st.success("✅ คำนวณถูกต้อง (Passed)")
        else:
            st.error("❌ ข้อมูลคลาดเคลื่อน (Failed)")

    st.markdown("---")

    # ==========================================
   if len(plot_df) > 1:
        # 1. กำหนดขนาดหน้ากระดาษ A4 แนวนอน (11.69 x 8.27 นิ้ว) ความละเอียด 300 DPI สำหรับงานพิมพ์
        fig = plt.figure(figsize=(11.69, 8.27), dpi=300)
        
        # 2. แบ่งสัดส่วนหน้ากระดาษ: ซ้าย 80% (กราฟ+Data Band), ขวา 20% (Title Block)
        ax = fig.add_axes([0.08, 0.35, 0.70, 0.55]) # [left, bottom, width, height]
        
        # วาดเส้นระดับดินเดิม และระดับก่อสร้าง
        ax.plot(plot_df['Distance (m)'], plot_df['Elev.'], color='blue', linewidth=1.5, label='ระดับดินเดิม (Existing Ground)')
        
        if plot_df['Design Elev.'].notna().any():
            ax.plot(plot_df['Distance (m)'], plot_df['Design Elev.'], color='red', linewidth=1.5, label='ระดับก่อสร้าง (Design Grade)')
            
            elev_array = np.array(plot_df['Elev.'], dtype=float)
            design_array = np.array(plot_df['Design Elev.'], dtype=float)
            dist_array = np.array(plot_df['Distance (m)'], dtype=float)
            
            # แรเงาดินตัด-ดินถม
            ax.fill_between(dist_array, elev_array, design_array, 
                            where=(design_array > elev_array), 
                            color='red', alpha=0.15, hatch='//')
            ax.fill_between(dist_array, elev_array, design_array, 
                            where=(design_array < elev_array), 
                            color='blue', alpha=0.15, hatch='\\\\')

        ax.set_title('รูปตัดตามยาวโครงการสร้างทาง (Longitudinal Road Profile)', fontsize=18, pad=15)
        ax.set_ylabel('ค่าระดับความสูง (m)', fontsize=12)
        ax.set_xticks(plot_df['Distance (m)'])
        ax.set_xticklabels([]) # ซ่อน tick เดิม เพื่อไปใช้ Data Band ด้านล่าง
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
        
        # 3. สร้าง Data Band (ตารางข้อมูลใต้กราฟ)
        table_data = [
            plot_df['Sta.'].tolist(),
            plot_df['Elev.'].map(lambda x: f"{x:.3f}").tolist(),
            plot_df['Design Elev.'].map(lambda x: f"{x:.3f}" if pd.notna(x) else "").tolist()
        ]
        row_labels = ['ระยะทาง / สถานี (STA)', 'ระดับดินเดิม\n(Existing Ground Level)', 'ระดับออกแบบ\n(Design Grade Level)']
        
        data_table = ax.table(cellText=table_data, rowLabels=row_labels, 
                              loc='bottom', bbox=[0, -0.4, 1, 0.35], cellLoc='center')
        data_table.auto_set_font_size(False)
        data_table.set_fontsize(10)
        data_table.scale(1, 2)

        # 4. สร้างกรอบ Title Block ด้านขวามือ
        ax_title = fig.add_axes([0.80, 0.05, 0.15, 0.85]) # พื้นที่ Title Block
        ax_title.axis('off') # ซ่อนเส้นกราฟ
        
        # ข้อมูลใน Title Block หน่วยงาน
        tb_text = (
            "รูปตัดตามยาว\nโครงการก่อสร้างทาง\n(Longitudinal Road Profile)\n\n"
            "--------------------------\n"
            "Horizontal Scale 1:1000\n"
            "Vertical Scale 1:100\n"
            "--------------------------\n"
            "สำรวจ / ออกแบบ:\n"
            "นายอุดมพงศ์ วะชุม\n"
            "วิศวกรโยธา\n\n"
            "ตรวจสอบ:\n"
            "........................\n\n"
            "อนุมัติ:\n"
            "........................\n"
            "--------------------------\n"
            "องค์การบริหารส่วนตำบลนาหว้า\n"
            "อ.นาหว้า จ.นครพนม\n"
            "--------------------------\n"
            "แผ่นที่: 1 / 1"
        )
        
        # ตีกรอบล้อมรอบ Title Block
        rect = plt.Rectangle((0, 0), 1, 1, fill=False, edgecolor='black', linewidth=1, transform=ax_title.transAxes)
        ax_title.add_patch(rect)
        ax_title.text(0.5, 0.5, tb_text, transform=ax_title.transAxes, fontsize=11, 
                      ha='center', va='center', multialignment='center')

        # 5. แสดงผลบนเว็บแอปพลิเคชัน
        st.pyplot(fig, use_container_width=False)
        
        # 6. ปุ่มดาวน์โหลด PDF ที่ Scale ถูกต้อง
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format="pdf", bbox_inches='tight')
        st.download_button(
            label="📄 ดาวน์โหลดแบบ A4 (PDF)",
            data=buf.getvalue(),
            file_name="Road_Profile_NaWa.pdf",
            mime="application/pdf"
        )
