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
