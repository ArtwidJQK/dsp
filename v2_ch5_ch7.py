# -*- coding: utf-8 -*-
"""
Module: Chapter 5 (Experimental Results), Chapter 6 (Discussion & Limitations),
Chapter 7 (Conclusion & Future Work), References, and Appendices A, B, C
for LeTanDung_24150654_v2.docx

Strictly restored according to original LeTanDung_24150654.docx (Single Source of Truth):
- Table 5.1: Exactly 5 verified notes (A4, C4, C5, D3, E3) with 100% correct detection rate.
  Target, Mean, Std, MAE (Hz), MAE (cent) [derived via 1200*log2(1+MAE/f_target), noted as derived],
  Max error, 100% correct rate, Estimator = [CẦN BỔ SUNG].
- Table 5.2: Inharmonicity table from original (f1, f2/2, f3/3, dev2, dev3). All text on 'two runs' deleted.
- E2 register: 15% (3/20 frames), mean 83.160 Hz, std 0.137, MAE 0.750; 85% frames misidentified as E3.
  Table 5.4: Spectrum of E2 (f0 1.5–7.3; m=2 15.9–28.4; m=3 22.0–46.4; m=4 12.4–25.1).
- Processing Latency: 23.56–25.37 ms, CPU load ≈18.5%, Hop 128 ms, Frame 256 ms, Fast Lock 256 ms,
  Web Polling 125 ms, Total latency 150–280 ms. Fabricated 10.5+2.1+4.2 = 16.8 ms breakdown deleted.
- Frontend testing: Chrome headless CDP, 0 JS errors, 8 viewports passed, 'chưa xác minh trên điện thoại vật lý'.
- Deleted Table 5.6 (bandwidth/RTT/packet loss).
- Table 6.1: Qualitative comparison only (no fabricated ms values).
- WebSocket noted strictly as future work. Deleted Safari/Firefox/375x667.
"""

import math
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

import v2_helpers as vh

def build_ch5_ch7(doc):
    # =========================================================================
    # CHƯƠNG 5 — KIỂM THỬ VÀ PHÂN TÍCH KẾT QUẢ THỰC TẾ
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 5 — KIỂM THỬ VÀ PHÂN TÍCH KẾT QUẢ THỰC TẾ", is_chapter=True)

    # 5.1 Phương pháp luận và quy trình kiểm thử
    vh.add_heading_2(doc, "5.1. Phương pháp luận và quy trình kiểm thử")
    vh.add_p(doc, 
        "Để đánh giá khách quan, khoa học và minh bạch năng lực của thiết bị, toàn bộ các bài kiểm thử thực nghiệm "
        "được tiến hành thu âm trực tiếp từ đàn piano cơ thật (acoustic piano). Quá trình đo đạc tuân thủ nghiêm ngặt "
        "nguyên tắc nghiên cứu thực chứng (REAL-DATA ONLY): tuyệt đối không sử dụng dữ liệu tự tạo, không làm tròn số liệu "
        "chủ quan và phân định rõ ràng giữa các kết quả đã được xác minh thực tế với các giới hạn kỹ thuật chưa được kiểm chứng.", indent=0.394)

    vh.add_p(doc, 
        "Bố trí thực nghiệm bao gồm: Bo mạch vi điều khiển ESP32-S3 kết hợp microphone MEMS kỹ thuật số I2S INMP441, "
        "đặt tại khoảng cách 15–20\u00A0cm so với soundboard và dây đàn piano, hướng trực diện vào khu vực búa gõ phím. "
        "Các thông số môi trường phòng đo cần được tác giả ghi chép đầy đủ: [CẦN BỔ SUNG: hãng và model đàn piano (upright hay grand), "
        "ngày lên dây gần nhất, địa điểm và đặc điểm âm học phòng đo, nhiệt độ môi trường (°C), mức ồn nền phòng đo (dBA), "
        "số lần gõ phím cho mỗi nốt, quy trình thu nhận 20 khung liên tục trong một lần gõ hay gõ lặp lại].", indent=0.394)

    vh.add_placeholder_box(doc, 
        "Ảnh chụp bố trí thực nghiệm thực tế: Đàn piano acoustic, vị trí đặt vi điều khiển ESP32-S3 và microphone INMP441",
        "Hình 5.1: Bố trí thực nghiệm đo đạc âm thanh thực tế trên đàn piano acoustic")

    vh.add_placeholder_box(doc, 
        "Ảnh chụp màn hình giao diện web thực tế khi thiết bị đang nhận diện phím đàn piano",
        "Hình 5.2: Giao diện web hiển thị kết quả phân tích cao độ và trạng thái cân chỉnh thực tế")

    # 5.2 Kiểm chứng trên tín hiệu mô phỏng số học
    vh.add_heading_2(doc, "5.2. Kiểm chứng độ chính xác thuật toán trên tín hiệu mô phỏng số học")
    vh.add_p(doc, 
        "Trước khi thử nghiệm trên nhạc cụ cơ học, chuỗi thuật toán xử lý tín hiệu (cửa sổ Hann tuần hoàn, biến đổi FFT radix-2 "
        "và nội suy parabol bậc hai) đã được kiểm chứng độ chính xác số học thông qua mô phỏng tín hiệu sóng sin thuần túy trên Python "
        "với các tham số tương đồng firmware: F_s = 16\u00A0000\u00A0Hz, N = 4\u00A0096 mẫu (độ phân giải bin phổ Δf = 3.90625\u00A0Hz/bin), "
        "tần số thử nghiệm f_test = 440.000\u00A0Hz.", indent=0.394)

    vh.add_p(doc, 
        "Kết quả mô phỏng ghi nhận: Đỉnh phổ rời rạc rơi vào bin k = 113 (tần số trung tâm bin 441.40625\u00A0Hz). "
        "Khi áp dụng thuật toán nội suy parabol bậc hai trên biên độ tuyến tính, độ lệch đỉnh tính được là p = −0.3102 bin, "
        "cho tần số ước tính f_interp = (113 − 0.3102) × 3.90625 = 440.1945\u00A0Hz (độ lệch +0.1945\u00A0Hz). "
        "Khi quét lệch tần số liên tục trên toàn bộ độ rộng một bin phổ (±Δf/2), sai số lớn nhất của phương pháp nội suy parabol tuyến tính "
        "đạt xấp xỉ 0.2062\u00A0Hz. Trong khi đó, nếu áp dụng nội suy parabol trên log-biên độ, độ lệch tính được là p = −0.3745 bin, "
        "cho tần số f_log = 439.9432\u00A0Hz (sai số −0.0568\u00A0Hz) và sai số quét lớn nhất chỉ là 0.0625\u00A0Hz.", indent=0.394)

    vh.add_p(doc, 
        "Nhận xét kỹ thuật: Kết quả mô phỏng chứng minh rằng phương pháp nội suy parabol bậc hai trên biên độ tuyến tính tồn tại độ lệch bias "
        "toán học cố hữu (khoảng 0.19–0.21\u00A0Hz đối với cửa sổ Hann). Một phần sai số MAE của nốt A4 ghi nhận trong thực nghiệm đàn cơ (0.281\u00A0Hz) "
        "chính là xuất phát từ độ lệch bias thuật toán này, bên cạnh dao động cơ học của dây đàn.", indent=0.394)

    # 5.3 Kết quả thực nghiệm định lượng trên 5 nốt kiểm chứng (Bảng 5.1)
    vh.add_heading_2(doc, "5.3. Kết quả đo đạc thống kê cao độ trên đàn piano cơ thật (Bảng 5.1)")
    vh.add_p(doc, 
        "Thử nghiệm đo đạc định lượng được thực hiện trên 5 nốt đại diện thuộc dải trung âm và cận trầm: A4 (440.00\u00A0Hz - nốt chuẩn quốc tế), "
        "C4 (261.63\u00A0Hz - nốt Đô trung), C5 (523.25\u00A0Hz - nốt Đô cao), D3 (146.83\u00A0Hz - dải cận trầm) và E3 (164.81\u00A0Hz - dải cận trầm). "
        "Tại mỗi nốt, hệ thống thu thập chuỗi 20 khung phân tích hợp lệ liên tiếp (VALID frames) khi gõ phím đàn.", indent=0.394)

    # BẢNG 5.1 KHÔI PHỤC NGUYÊN VĂN BẢN GỐC
    vh.add_caption(doc, "Bảng 5.1: Kết quả đo đạc thống kê cao độ trên đàn piano cơ thật (20 khung VALID liên tiếp/nốt)", is_table=True)
    tbl_51 = doc.add_table(rows=1, cols=9)
    tbl_51.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_51.autofit = False
    vh.set_table_borders(tbl_51)

    t51_dxa = [650, 1050, 1150, 950, 950, 1050, 950, 1050, 1272]
    
    # Fixed tblLayout & tblGrid (9072 dxa total)
    tblPr = tbl_51._tbl.tblPr
    tblPr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'))
    tblW = tblPr.find(qn('w:tblW'))
    if tblW is not None:
        tblW.set(qn('w:w'), '9072')
        tblW.set(qn('w:type'), 'dxa')
    else:
        tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="9072" w:type="dxa"/>'))

    tblGrid = OxmlElement('w:tblGrid')
    for w in t51_dxa:
        col = OxmlElement('w:gridCol')
        col.set(qn('w:w'), str(w))
        tblGrid.append(col)
    tbl_51._tbl.insert(tbl_51._tbl.index(tblPr) + 1, tblGrid)

    t51_hdrs = [
        "Nốt nhạc", "Tần số chuẩn\n(Hz)", "Trung bình đo\n(Mean, Hz)", "Độ lệch chuẩn\n(Std, Hz)", 
        "Sai số MAE\n(Hz)", "MAE (cent)\n[suy ra]*", "Sai số Max\n(Hz)", "Tỷ lệ đúng\n(%)", "Bộ ước lượng\n(Estimator)"
    ]
    for idx, text in enumerate(t51_hdrs):
        c = tbl_51.rows[0].cells[idx]
        c.width = Inches(t51_dxa[idx] / 1440.0)
        tcPr = c._tc.get_or_add_tcPr()
        tcW = tcPr.find(qn('w:tcW'))
        if tcW is not None:
            tcW.set(qn('w:w'), str(t51_dxa[idx]))
            tcW.set(qn('w:type'), 'dxa')
        else:
            tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{t51_dxa[idx]}" w:type="dxa"/>'))
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=40, bottom=40, left=10, right=10)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.left_indent = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(8.0)
        r.bold = True

    # Exact numbers strictly preserved from original Table 5.1 (Table 44 in LeTanDung_24150654.docx)
    # MAE (cent) derived via formula: 1200 * log2(1 + MAE/f_target)
    # A4: 1200*log2(1 + 0.281/440.000) = 1.10 cent
    # C4: 1200*log2(1 + 0.065/261.626) = 0.43 cent
    # C5: 1200*log2(1 + 0.188/523.251) = 0.62 cent
    # D3: 1200*log2(1 + 0.060/146.832) = 0.71 cent
    # E3: 1200*log2(1 + 0.054/164.814) = 0.57 cent
    t51_data = [
        ("A4", "440.000 Hz", "440.281 Hz", "0.096 Hz", "0.281 Hz", "1.10 cent", "0.680 Hz", "100.0%", "[CẦN BỔ SUNG]"),
        ("C4", "261.626 Hz", "261.674 Hz", "0.064 Hz", "0.065 Hz", "0.43 cent", "0.140 Hz", "100.0%", "[CẦN BỔ SUNG]"),
        ("C5", "523.251 Hz", "523.438 Hz", "0.020 Hz", "0.188 Hz", "0.62 cent", "0.260 Hz", "100.0%", "[CẦN BỔ SUNG]"),
        ("D3", "146.832 Hz", "146.797 Hz", "0.074 Hz", "0.060 Hz", "0.71 cent", "0.270 Hz", "100.0%", "[CẦN BỔ SUNG]"),
        ("E3", "164.814 Hz", "164.787 Hz", "0.065 Hz", "0.054 Hz", "0.57 cent", "0.133 Hz", "100.0%", "[CẦN BỔ SUNG]"),
    ]
    for r_data in t51_data:
        row = tbl_51.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = Inches(t51_dxa[idx] / 1440.0)
            tcPr = c._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn('w:tcW'))
            if tcW is not None:
                tcW.set(qn('w:w'), str(t51_dxa[idx]))
                tcW.set(qn('w:type'), 'dxa')
            else:
                tcPr.append(parse_xml(f'<w:tcW {nsdecls("w")} w:w="{t51_dxa[idx]}" w:type="dxa"/>'))
            tcPr.append(parse_xml(f'<w:noWrap {nsdecls("w")}/>'))
            vh.set_cell_margins(c, top=25, bottom=25, left=10, right=10)
            p = c.paragraphs[0]
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.left_indent = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            if idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif idx in [1, 2, 3, 4, 5, 6]:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.0)
            if idx == 0:
                r.bold = True
            if idx == 8 and "[CẦN BỔ SUNG]" in text:
                r.bold = True
                r.font.color.rgb = RGBColor(180, 20, 20)

    vh.make_table_responsive(tbl_51)

    p_note51 = doc.add_paragraph()
    p_note51.paragraph_format.space_before = Pt(2)
    p_note51.paragraph_format.space_after = Pt(6)
    r_n = p_note51.add_run(
        "(* Ghi chú minh bạch: Cột 'MAE (cent)' được suy ra bằng công thức toán học c = 1200·log₂(1 + MAE/f_target); "
        "cột 'Bộ ước lượng' ghi nhận [CẦN BỔ SUNG] chờ tác giả đối chiếu lại log runtime từ firmware ESP32-S3)."
    )
    r_n.font.name = "Times New Roman"
    r_n.font.size = Pt(9.5)
    r_n.font.italic = True
    r_n.font.color.rgb = RGBColor(80, 80, 80)

    # 5.4 Phân tích chi tiết từng nốt kiểm chứng
    vh.add_heading_2(doc, "5.4. Phân tích chi tiết các nốt nhạc kiểm chứng")
    vh.add_p(doc, 
        "• Nốt A4 (440.000 Hz - Chuẩn cao độ quốc tế): Năng lượng tập trung rất mạnh tại Bin 113. "
        "Thuật toán đạt tần số trung bình 440.281 Hz, độ lệch chuẩn std = 0.096 Hz, sai số tuyệt đối MAE chỉ 0.281 Hz (1.10 cent). "
        "Sai số cực đại trong 20 khung ghi nhận là 0.680 Hz. Tỷ lệ bắt đúng nốt đạt 100.0%.", indent=0.394)

    vh.add_p(doc, 
        "• Nốt C4 (261.626 Hz - Middle C): Đỉnh phổ nằm tại Bin 67. Kết quả đo đạt độ chính xác rất cao: "
        "Trung bình đo đạt 261.674 Hz, độ lệch chuẩn 0.064 Hz, sai số MAE chỉ 0.065 Hz (0.43 cent), sai số cực đại chỉ 0.140 Hz.", indent=0.394)

    vh.add_p(doc, 
        "• Nốt C5 (523.251 Hz - Quãng cao Treble): Năng lượng f_1 rất tập trung tại Bin 134 (biên độ ~45.0), độ biến thiên giữa các khung "
        "cực thấp với độ lệch chuẩn nhỏ nhất trong toàn bộ tập mẫu (std = 0.020 Hz). Tần số trung bình đo được là 523.438 Hz, MAE đạt 0.188 Hz (0.62 cent).", indent=0.394)

    vh.add_p(doc, 
        "• Nốt D3 (146.832 Hz) và E3 (164.814 Hz - Dải cận trầm): Tại nốt D3, f_1 (Bin 38) suy giảm xuống biên độ ~3.8 trong khi họa âm bậc 3 "
        "(440.92 Hz) lên tới ~35.0; thuật toán giả thuyết họa âm đã bắt đúng tần số cơ bản 146.797 Hz, MAE đạt 0.060 Hz (0.71 cent). "
        "Tại nốt E3, f_1 (Bin 42) đạt biên độ ~4.5 trong khi họa âm bậc 2 (329.52 Hz) đạt ~28.0 và họa âm bậc 3 (494.99 Hz) đạt ~32.0; "
        "hệ thống đạt tần số trung bình 164.787 Hz, MAE chỉ 0.054 Hz (0.57 cent), độ lệch chuẩn std = 0.065 Hz.", indent=0.394)

    # 5.5 Đo đạc đặc tính các họa âm và hiện tượng Inharmonicity thực tế (BẢNG 5.2 GỐC)
    vh.add_heading_2(doc, "5.5. Đo đạc đặc tính các họa âm và hiện tượng dạt tần số (Inharmonicity) trên đàn piano thật")
    vh.add_p(doc, 
        "Một đóng góp thực nghiệm quan trọng của đề tài là việc đo đạc định lượng trực tiếp hiện tượng bất điều hòa (Inharmonicity) "
        "của dây đàn thép piano trên phần cứng thật. Bảng 5.2 tổng hợp giá trị tần số ước lượng của từng bậc họa âm (f_1, f_2/2, f_3/3) "
        "và độ dạt tần số tương ứng:", indent=0.394)

    # BẢNG 5.2 INHARMONICITY KHÔI PHỤC TỪ BẢN GỐC (Bảng 45)
    vh.add_caption(doc, "Bảng 5.2: Đo đạc đặc tính các họa âm và hiện tượng dạt tần số (Inharmonicity) trên đàn piano thật", is_table=True)
    tbl_52 = doc.add_table(rows=1, cols=7)
    tbl_52.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_52.autofit = False
    vh.set_table_borders(tbl_52)

    t52_w = [Inches(0.7), Inches(1.0), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.15), Inches(1.15)]
    t52_hdrs = ["Nốt", "Mục tiêu", "Họa âm m=1 (f₁)", "Họa âm m=2 (f₂/2)", "Họa âm m=3 (f₃/3)", "Độ dạt dev2\n[(f₂/2) − f₁]", "Độ dạt dev3\n[(f₃/3) − f₁]"]
    for idx, text in enumerate(t52_hdrs):
        c = tbl_52.rows[0].cells[idx]
        c.width = t52_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True

    # Exact numbers strictly preserved from original Table 5.2 (Table 45 in LeTanDung_24150654.docx)
    t52_data = [
        ("A4", "440.00 Hz", "440.285 Hz", "440.249 Hz", "440.633 Hz", "−0.036 Hz", "+0.348 Hz"),
        ("C4", "261.63 Hz", "261.675 Hz", "261.734 Hz", "261.839 Hz", "+0.059 Hz", "+0.164 Hz"),
        ("C5", "523.25 Hz", "523.445 Hz", "523.929 Hz", "524.869 Hz", "+0.484 Hz", "+1.424 Hz"),
        ("D3", "146.83 Hz", "146.621 Hz", "146.790 Hz", "146.973 Hz", "+0.157 Hz", "+0.334 Hz"),
        ("E3", "164.81 Hz", "164.700 Hz", "164.760 Hz", "164.995 Hz", "+0.060 Hz", "+0.295 Hz"),
    ]
    for r_data in t52_data:
        row = tbl_52.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t52_w[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_52)

    vh.add_p(doc, 
        "Nhận xét kỹ thuật then chốt từ Bảng 5.2: (1) Độ dạt họa âm tăng rất mạnh ở các nốt cao (C5 ghi nhận dev3 dạt lên tới +1.424 Hz "
        "do dây treble ngắn và có độ cứng uốn lớn); (2) Dữ liệu thực tế chứng minh rằng: Nếu áp dụng công thức trung bình cộng có trọng số đa họa âm (MHQI) "
        "một cách mù quáng, ước lượng f_0 sẽ bị các họa âm bậc 2 và 3 kéo lệch lên cao một cách nhân tạo (ví dụ C5 bị kéo lệch lên 523.641 Hz). "
        "Do đó, kiến trúc DSP của dự án đã quyết định sử dụng chính sách: Ưu tiên f_1 làm ước lượng số một (F1_PRIMARY) khi f_1 có SNR tốt, "
        "và chỉ sử dụng f_2/2 làm dự phòng (F2_FALLBACK) khi f_1 bị chìm sâu dưới ngưỡng nhiễu trong dải trầm [6].", indent=0.394)

    # 5.6 Phân tích thực nghiệm nốt trầm E2 (82.41 Hz) và dải Bass
    vh.add_heading_2(doc, "5.6. Phân tích thực nghiệm nốt trầm E2 (82.41 Hz) và dải Bass")
    vh.add_p(doc, 
        "Nhằm tuân thủ tuyệt đối tính trung thực khoa học, báo cáo không che giấu những khó khăn kỹ thuật tại dải nốt trầm, "
        "đặc biệt là nốt E2 (tần số danh định 82.41 Hz). Kết quả phân tích phổ chi tiết tại nốt E2 ghi nhận các số liệu thực tế sau:", indent=0.394)

    # BẢNG 5.4 KHÔI PHỤC NGUYÊN VĂN BẢN GỐC (Bảng 46)
    vh.add_caption(doc, "Bảng 5.4: Phân tích đặc tính phổ tại dải nốt trầm E2 (82.41 Hz) ghi nhận trên phần cứng", is_table=True)
    tbl_54 = doc.add_table(rows=1, cols=4)
    tbl_54.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_54.autofit = False
    vh.set_table_borders(tbl_54)

    t54_w = [Inches(1.8), Inches(1.4), Inches(1.3), Inches(2.2)]
    t54_hdrs = ["Thành phần phổ tại nốt E2", "Vị trí bin và Tần số", "Biên độ đo được (mag)", "Đánh giá âm học thực tế"]
    for idx, text in enumerate(t54_hdrs):
        c = tbl_54.rows[0].cells[idx]
        c.width = t54_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        r.bold = True

    # Exact numbers strictly preserved from original Table 5.4 (Table 46 in LeTanDung_24150654.docx)
    t54_data = [
        ("Tần số cơ bản f₀ (m=1)", "82.03 Hz (Bin 21)", "1.5 – 7.3", "Rất yếu (suy hao âm học cơ học của thùng đàn & mic)"),
        ("Họa âm bậc 2 (m=2)", "164.06 Hz (Bin 42)", "15.9 – 28.4", "Mạnh gấp 4–8 lần so với fundamental"),
        ("Họa âm bậc 3 (m=3)", "246.09 Hz (Bin 63)", "22.0 – 46.4", "Đỉnh năng lượng mạnh nhất trên toàn dải phổ"),
        ("Họa âm bậc 4 (m=4)", "328.12 Hz (Bin 84)", "12.4 – 25.1", "Mạnh gấp 3 lần so với fundamental"),
    ]
    for r_data in t54_data:
        row = tbl_54.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t54_w[idx]
            vh.set_cell_margins(c, top=60, bottom=60, left=60, right=60)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_54)

    vh.add_p(doc, 
        "Trong bài kiểm tra Clean Regression Test nghiêm ngặt (thu thập 20 khung liên tục độc lập khi gõ phím E2 trên đàn piano thật), "
        "kết quả thống kê ghi nhận:", indent=0.394)

    vh.add_p(doc, "• Tỷ lệ nhận diện đúng nốt E2 chỉ đạt 15.0% (3/20 khung).", indent=0.394, space_after=3)
    vh.add_p(doc, "• Tần số trung bình trong các khung bắt được là 83.160 Hz (std = 0.137 Hz, MAE = 0.750 Hz).", indent=0.394, space_after=3)
    vh.add_p(doc, 
        "• Trong 85% số khung còn lại, hệ thống bị đánh lừa bởi năng lượng áp đảo của họa âm bậc 2 (164 Hz) và nhận nhầm thành nốt E3 (~164.81 Hz). "
        "Mặc dù firmware đã được bổ sung giải thuật Bass-Gate Modification (nới lỏng ngưỡng biên độ cho dải 55–110 Hz khi có đủ họa âm hỗ trợ), "
        "nhưng độ ổn định thực tế tại E2 vẫn chưa đủ để đưa ra kết luận rằng hệ thống hoạt động tin cậy trên toàn bộ dải trầm của đàn piano.", indent=0.394, space_after=6)

    vh.add_placeholder_box(doc, 
        "Đồ thị phổ FFT thực tế của phím A4 (440 Hz) và phím E2 (82.4 Hz) thu từ đàn piano acoustic",
        "Hình 5.3: So sánh phổ biên độ FFT thực nghiệm giữa nốt trung âm A4 và nốt cực trầm E2")

    vh.add_placeholder_box(doc, 
        "Đồ thị diễn biến độ lệch Cent theo thời gian (20 khung) của các nốt thử nghiệm",
        "Hình 5.4: Diễn biến độ lệch Cent qua 20 khung phân tích liên tiếp trên các nốt kiểm chứng")

    # 5.7 Đo đạc độ trễ xử lý (Processing Latency vs Update Cadence)
    vh.add_heading_2(doc, "5.7. Đo đạc độ trễ xử lý (Processing Latency vs Update Cadence)")
    vh.add_p(doc, 
        "Một khía cạnh kỹ thuật tối quan trọng cần làm rõ là sự phân biệt giữa Độ trễ xử lý tính toán của khối DSP (Processing Latency) "
        "và Chu kỳ cập nhật giao diện tổng thể (Web Update Cadence):", indent=0.394)

    # BẢNG 5.5 ĐỘ TRỄ KHÔI PHỤC TỪ BẢN GỐC (Bảng 47)
    vh.add_caption(doc, "Bảng 5.5: Kết quả đo đạc độ trễ xử lý (Processing Latency) của khối DSP", is_table=True)
    tbl_55 = doc.add_table(rows=1, cols=3)
    tbl_55.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_55.autofit = False
    vh.set_table_borders(tbl_55)

    t55_w = [Inches(2.4), Inches(1.4), Inches(2.9)]
    t55_hdrs = ["Đại lượng độ trễ đo đạc", "Giá trị thực nghiệm", "Bản chất kỹ thuật và Phân tích"]
    for idx, text in enumerate(t55_hdrs):
        c = tbl_55.rows[0].cells[idx]
        c.width = t55_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.bold = True

    # Exact numbers strictly preserved from original Table 5.5 (Table 47 in LeTanDung_24150654.docx)
    t55_data = [
        ("Thời gian thực thi DSP (Processing Latency)", "23.56 – 25.37 ms", "Thời gian Core 1 CPU chạy FFT, QI, Harmonic Scoring (Đo bằng esp_timer)"),
        ("Chu kỳ bước nhảy đệm (Hop Interval)", "128.0 ms", "Thời gian cần thiết để DMA I2S thu nhận đủ 2048 mẫu âm thanh mới"),
        ("Thời gian đáp ứng nốt tối thiểu (Fast Lock)", "256.0 ms", "2 khung gối đầu liên tiếp cần thiết để bộ lọc ổn định xác nhận trạng thái STABLE"),
        ("Chu kỳ gửi yêu cầu Web Polling", "125.0 ms", "Nhịp gửi hàm fetch() định kỳ từ mã JavaScript trên trình duyệt client"),
        ("Tải chiếm dụng CPU của tác vụ DSP", "Xấp xỉ 18.5%", "Đo đạc trên lõi 240 MHz (Dư thừa >80% năng lực CPU cho Wi-Fi và Web Server)"),
    ]
    for r_data in t55_data:
        row = tbl_55.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t55_w[idx]
            vh.set_cell_margins(c, top=60, bottom=60, left=60, right=60)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx in [0, 2] else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_55)

    vh.add_p(doc, 
        "Kết luận: Độ trễ tính toán DSP thuần túy chỉ dao động trong khoảng 23.56 đến 25.37 ms, hoàn toàn đáp ứng xuất sắc tiêu chuẩn thời gian thực "
        "(< 50 ms). Tổng thời gian từ khi người chơi gõ phím đến khi kim đo trên trình duyệt phản hồi dao động trong khoảng 150 – 280 ms, "
        "hoàn toàn thỏa mãn yêu cầu cập nhật < 500 ms của đề tài môn học [2].", indent=0.394)

    # 5.8 Kiểm thử tự động Frontend trên Chrome Headless CDP Automation
    vh.add_heading_2(doc, "5.8. Kiểm thử tự động Frontend trên Chrome Headless CDP Automation")
    vh.add_p(doc, 
        "Để kiểm tra tính toàn vẹn của mã nguồn giao diện Web Frontend, hệ thống đã chạy quy trình kiểm thử tự động không đầu "
        "(Headless Browser Automation) thông qua giao thức Chrome DevTools Protocol (CDP). Kết quả xác nhận:", indent=0.394)

    vh.add_p(doc, "• Biên dịch firmware (Build): PASS.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Nạp chip vi điều khiển (Flash): PASS.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Kiểm tra lỗi JavaScript Console: Đạt 0 lỗi ngoại lệ (0 Errors / 0 Warnings).", indent=0.394, space_after=3)
    vh.add_p(doc, "• Chuyển cảnh giao diện (Scene Navigation): PASS.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Xác thực hiển thị chính xác các trạng thái từ API Endpoint:", indent=0.394, space_after=2)
    vh.add_p(doc, "   - Trạng thái A4: Nhận diện 440.10 Hz, độ lệch +0.39 cent, hiển thị banner 'ĐÚNG CAO ĐỘ' (IN TUNE), kim đo ở vị trí 50.39%.", indent=0.7, space_after=2)
    vh.add_p(doc, "   - Trạng thái C4: Nhận diện 259.50 Hz, độ lệch -14.15 cent, hiển thị banner 'THẤP' (TOO LOW), kim đo lệch về 35.87%.", indent=0.7, space_after=2)
    vh.add_p(doc, "   - Trạng thái E2: Nhận diện 83.20 Hz, độ lệch +16.52 cent, hiển thị banner 'CAO' (TOO HIGH), kim đo lệch về 66.47%.", indent=0.7, space_after=2)
    vh.add_p(doc, "   - Trạng thái Không có tín hiệu: Hiển thị banner 'KHÔNG CÓ TÍN HIỆU' (NO SIGNAL), kim đo trở về trạng thái nghỉ.", indent=0.7, space_after=6)

    # 5.9 Kiểm thử tính thích ứng giao diện (Responsive Layout Matrix)
    vh.add_heading_2(doc, "5.9. Kiểm thử tính thích ứng giao diện (Responsive Layout Matrix)")
    vh.add_p(doc, 
        "Khả năng thích ứng giao diện (Responsive) của trang web Celestial Tuner được kiểm định tự động trên 8 cấu hình độ phân giải màn hình "
        "tiêu chuẩn thông qua Chrome CDP. Kết quả kiểm tra được trình bày trong Bảng 5.7 (chưa xác minh trên thiết bị di động vật lý thật):", indent=0.394)

    # BẢNG 5.7 MỚI (BẢNG 48 GỐC)
    vh.add_caption(doc, "Bảng 5.7: Ma trận kiểm thử tính tương thích giao diện co giãn Responsive trên 8 Viewport (Chrome CDP)", is_table=True)
    tbl_resp = doc.add_table(rows=1, cols=6)
    tbl_resp.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_resp.autofit = False
    vh.set_table_borders(tbl_resp)

    t_resp_w = [Inches(1.8), Inches(1.1), Inches(1.0), Inches(1.0), Inches(1.0), Inches(0.8)]
    t_resp_hdrs = ["Thiết bị mô phỏng", "Độ phân giải (WxH)", "Chiều rộng Window", "Chiều rộng Doc", "Tràn ngang", "Kết quả"]
    for idx, text in enumerate(t_resp_hdrs):
        c = tbl_resp.rows[0].cells[idx]
        c.width = t_resp_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True

    # Exact 8 viewports from original Table 48
    resp_rows = [
        ("Desktop Full HD", "1920 × 1080", "1920 px", "1920 px", "KHÔNG", "PASSED"),
        ("Desktop WXGA", "1366 × 768", "1366 px", "1366 px", "KHÔNG", "PASSED"),
        ("Tablet Landscape", "1024 × 768", "1024 px", "1024 px", "KHÔNG", "PASSED"),
        ("Tablet Portrait", "768 × 1024", "768 px", "768 px", "KHÔNG", "PASSED"),
        ("Mobile Modern (Large)", "412 × 915", "412 px", "412 px", "KHÔNG", "PASSED"),
        ("Mobile iPhone 12/13/14", "390 × 844", "390 px", "390 px", "KHÔNG", "PASSED"),
        ("Mobile Compact", "360 × 800", "360 px", "360 px", "KHÔNG", "PASSED"),
        ("Mobile Landscape", "844 × 390", "844 px", "844 px", "KHÔNG", "PASSED"),
    ]
    for r_data in resp_rows:
        row = tbl_resp.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t_resp_w[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True
            if text == "PASSED":
                r.font.color.rgb = RGBColor(20, 120, 40)
                r.bold = True

    vh.make_table_responsive(tbl_resp)

    # =========================================================================
    # CHƯƠNG 6 — ĐÁNH GIÁ, THẢO LUẬN VÀ GIỚI HẠN KỸ THUẬT
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 6 — ĐÁNH GIÁ, THẢO LUẬN VÀ GIỚI HẠN KỸ THUẬT", is_chapter=True)

    # 6.1 Tổng kết các mục tiêu kỹ thuật đạt được
    vh.add_heading_2(doc, "6.1. Tổng kết các mục tiêu kỹ thuật đạt được")
    vh.add_p(doc, 
        "Đối chiếu với các yêu cầu đặt ra từ đề bài ban đầu, dự án đã đạt được những kết quả cụ thể sau:", indent=0.394)
    vh.add_p(doc, "1. Xây dựng thành công thiết bị phần cứng hoàn chỉnh, hoạt động độc lập với chi phí linh kiện thấp, sử dụng chip ESP32-S3 N16R8 và microphone MEMS INMP441 chất lượng cao.", indent=0.394, space_after=3)
    vh.add_p(doc, "2. Triển khai hoàn chỉnh pipeline DSP tối ưu bằng C/C++ thuần trong ESP-IDF, làm chủ toàn bộ các khâu từ thu nhận I2S DMA, khử DC, cửa sổ Hann, biến đổi FFT Radix-2 4 096 điểm, sàng lọc sàn nhiễu trung vị, chấm điểm giả thuyết họa âm và nội suy parabol bậc hai.", indent=0.394, space_after=3)
    vh.add_p(doc, "3. Đạt độ chính xác thực nghiệm cao trên 5 nốt kiểm chứng (MAE < 0.29 Hz, tương ứng dưới 1.10 cent, tỷ lệ nhận diện đúng 100.0%).", indent=0.394, space_after=3)
    vh.add_p(doc, "4. Tối ưu hóa độ trễ tính toán ấn tượng (chỉ 23.56 – 25.37 ms), tải CPU thấp (~18.5%), không gây gián đoạn tác vụ mạng Wi-Fi và Web Server.", indent=0.394, space_after=6)

    # 6.2 So sánh định tính với các phương pháp ước lượng cao độ truyền thống (BẢNG 6.1 ĐỊNH TÍNH)
    vh.add_heading_2(doc, "6.2. So sánh định tính với các phương pháp ước lượng cao độ truyền thống")
    vh.add_p(doc, 
        "Để làm rõ ưu thế kỹ thuật của giải pháp đề xuất (FFT + Nội suy Parabol + Chấm điểm đa họa âm), "
        "Bảng 6.1 tổng hợp so sánh định tính giữa phương pháp đề xuất và các giải thuật kinh điển:", indent=0.394)

    # BẢNG 6.1 ĐỊNH TÍNH (KHÔNG CÓ SỐ MS BỊA)
    vh.add_caption(doc, "Bảng 6.1: So sánh đặc tính kỹ thuật định tính giữa phương pháp đề xuất và các giải thuật ước lượng cao độ", is_table=True)
    tbl_61 = doc.add_table(rows=1, cols=5)
    tbl_61.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_61.autofit = False
    vh.set_table_borders(tbl_61)

    t61_w = [Inches(1.6), Inches(1.1), Inches(1.2), Inches(1.2), Inches(1.2)]
    t61_hdrs = ["Tiêu chí so sánh", "FFT + QI (Đề xuất)", "Tự tương quan (ACF)", "Thuật toán YIN", "HPS thuần túy"]
    for idx, text in enumerate(t61_hdrs):
        c = tbl_61.rows[0].cells[idx]
        c.width = t61_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True

    t61_rows = [
        ("Miền xử lý tín hiệu", "Tần số (Frequency domain)", "Thời gian (Time domain)", "Thời gian (Time domain)", "Tần số (Frequency domain)"),
        ("Độ phức tạp tính toán", "O(N log N)", "O(N²)", "O(N²)", "O(N log N)"),
        ("Độ mịn tần số", "Rất cao (nhờ nội suy parabol)", "Kém (lượng tử hóa chu kỳ mẫu)", "Khá cao (nội suy cực tiểu)", "Thấp (giới hạn bởi bin DFT)"),
        ("Khả năng khôi phục f₀ mất", "Tốt (nhờ mô hình đa họa âm)", "Khá tốt", "Rất tốt (bền vững)", "Trung bình (dễ nhân chập sai)"),
        ("Tính khả thi trên vi điều khiển", "Rất cao (chạy thời gian thực)", "Thấp (đòi hỏi tính toán nặng)", "Trung bình (cần tối ưu hóa)", "Cao (thuật toán đơn giản)"),
    ]
    for r_data in t61_rows:
        row = tbl_61.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t61_w[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True

    vh.make_table_responsive(tbl_61)

    # 6.3 Ma trận phân định ranh giới xác thực thực tế (BẢNG 6.2 GỐC)
    vh.add_heading_2(doc, "6.3. Ma trận phân định ranh giới xác thực thực tế (Verified vs. Not Verified)")
    vh.add_p(doc, 
        "Để đảm bảo tính liêm chính học thuật và độ tin cậy khoa học, ma trận phân định rõ ràng các ranh giới "
        "giữa phần đã được kiểm chứng thực nghiệm và phần chưa được xác minh:", indent=0.394)

    # BẢNG 6.2 KHÔI PHỤC TỪ BẢN GỐC (Bảng 50)
    vh.add_caption(doc, "Bảng 6.2: Ma trận phân định ranh giới xác thực thực tế (Verified vs. Not Verified)", is_table=True)
    tbl_62 = doc.add_table(rows=1, cols=3)
    tbl_62.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_62.autofit = False
    vh.set_table_borders(tbl_62)

    t62_w = [Inches(2.4), Inches(1.8), Inches(2.5)]
    t62_hdrs = ["Hạng mục kiểm thử và Khảo sát", "Trạng thái xác thực", "Căn cứ kỹ thuật và Ghi chú minh bạch"]
    for idx, text in enumerate(t62_hdrs):
        c = tbl_62.rows[0].cells[idx]
        c.width = t62_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        r.bold = True

    # Exact rows strictly preserved from original Table 50 in LeTanDung_24150654.docx
    t62_rows = [
        ("Nốt trung âm và cận trầm (A4, C4, C5, D3, E3)", "ĐÃ XÁC THỰC (VERIFIED)", "Đo đạc thực tế trên đàn piano cơ thật, đạt MAE 0.054 – 0.281 Hz"),
        ("Nốt trầm E2 (82.41 Hz)", "XÁC THỰC MỘT PHẦN (LIMITED)", "Tỷ lệ nhận diện đúng 15% trong test sạch, dễ nhầm sang E3 do họa âm mạnh"),
        ("Dải cực trầm (A0 – C2, 27.5 Hz đến 65.4 Hz)", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa đủ dữ liệu thực nghiệm để khẳng định độ chính xác"),
        ("Dải cực cao (C6 – C8, 1046 Hz đến 4186 Hz)", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa thu thập đủ mẫu kiểm thử trên đàn piano thật"),
        ("Độ chính xác < 0.5 Hz trên toàn bộ 88 phím", "KHÔNG ĐƯỢC TUYÊN BỐ", "Dữ liệu hiện tại không đủ để chứng minh toàn bộ bàn phím đạt tiêu chuẩn"),
        ("Tín hiệu hợp âm đa âm (Polyphonic / Chords)", "NGOÀI PHẠM VI (OUT OF SCOPE)", "Hệ thống chỉ thiết kế chuyên biệt cho nhận diện đơn âm"),
        ("Hiện tượng dậm pedal vang âm phức tạp", "CHƯA XÁC MINH (NOT VERIFIED)", "Chưa kiểm nghiệm sự giao thoa cộng hưởng đa dây khi mở damper"),
        ("Giao diện trên thiết bị di động vật lý thật", "CHƯA XÁC MINH (NOT VERIFIED)", "Mới chỉ xác thực trên trình duyệt Chrome giả lập qua giao thức CDP"),
    ]
    for r_data in t62_rows:
        row = tbl_62.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = t62_w[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=50, right=50)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx in [0, 2] else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True
            if "ĐÃ XÁC THỰC" in text:
                r.font.color.rgb = RGBColor(20, 120, 40)
                r.bold = True
            elif "XÁC THỰC MỘT PHẦN" in text:
                r.font.color.rgb = RGBColor(180, 100, 20)
                r.bold = True
            elif "CHƯA XÁC MINH" in text or "KHÔNG ĐƯỢC" in text or "NGOÀI PHẠM VI" in text:
                r.font.color.rgb = RGBColor(180, 20, 20)
                r.bold = True

    vh.make_table_responsive(tbl_62)

    # 6.4 Hiện tượng kéo giãn âm và đường cong Railsback
    vh.add_heading_2(doc, "6.4. Hiện tượng kéo giãn âm (Stretch Tuning) và đường cong Railsback")
    vh.add_p(doc, 
        "Trong âm học đàn piano cơ, hiện tượng bất điều hòa của dây thép khiến các họa âm bậc cao luôn bị dạt lên cao hơn "
        "bội số nguyên lý thuyết (như đã chứng minh trong Bảng 5.2). Để hòa âm giữa các quãng tám không xuất hiện tiếng phách (beat) khó chịu, "
        "nghệ nhân lên dây piano chuyên nghiệp bắt buộc phải kéo giãn âm: chỉnh các nốt cao cao hơn một chút và các nốt trầm thấp hơn một chút "
        "so với thang âm bình quân 12-TET lý thuyết. Đường cong này được gọi là đường cong Railsback. "
        "Do đó, việc thiết bị đạt độ chính xác theo tần số danh định 12-TET trong nghiên cứu này khẳng định độ tin cậy của thuật toán đo lường; "
        "tuy nhiên, để ứng dụng cho đàn biểu diễn hòa nhạc, thiết bị cần được phát triển thêm tính năng bù trừ theo đường cong Railsback.", indent=0.394)

    # =========================================================================
    # CHƯƠNG 7 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # =========================================================================
    vh.add_heading_1(doc, "CHƯƠNG 7 — KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", is_chapter=True)

    # 7.1 Kết luận
    vh.add_heading_2(doc, "7.1. Kết luận")
    vh.add_p(doc, 
        "Đề tài đã nghiên cứu, thiết kế và hiện thực thành công thiết bị lên dây đàn piano chromatic đơn âm thời gian thực "
        "hoạt động độc lập trên vi điều khiển ESP32-S3 kết hợp microphone MEMS kỹ thuật số INMP441. Các kết luận chính bao gồm:", indent=0.394)

    vh.add_p(doc, 
        "1. Hoàn thiện pipeline DSP tối ưu hoàn toàn bằng C/C++ trong ESP-IDF gồm: thu nhận I2S DMA 16 kHz, đệm trượt 50% (hop size 128 ms), "
        "cửa sổ Hann tuần hoàn, FFT Radix-2 4 096 điểm, lọc sàn nhiễu trung vị, chấm điểm giả thuyết họa âm và nội suy đỉnh parabol bậc hai.", indent=0.394, space_after=3)

    vh.add_p(doc, 
        "2. Đạt độ chính xác cao trên 5 nốt piano kiểm chứng thuộc dải trung âm và cận trầm (A4, C4, C5, D3, E3) với sai số MAE dưới 0.29 Hz "
        "(tương ứng dưới 1.10 cent, tỷ lệ nhận diện đúng 100.0%).", indent=0.394, space_after=3)

    vh.add_p(doc, 
        "3. Tối ưu hóa thời gian thực thi thuật toán DSP thuần chỉ mất 23.56 đến 25.37 ms với mức tải CPU xấp xỉ 18.5%, "
        "đảm bảo tổng độ trễ phản hồi từ khi gõ phím đến giao diện web nằm trong khoảng 150–280 ms.", indent=0.394, space_after=3)

    vh.add_p(doc, 
        "4. Xác định rõ ràng giới hạn vật lý tại nốt cực trầm E2 (82.41 Hz): do f_0 bị suy giảm năng lượng nghiêm trọng (biên độ chỉ 1.5–7.3 "
        "so với 46.4 của họa âm bậc 3), tỷ lệ nhận diện đúng chỉ đạt 15.0% và 85% khung bị nhầm sang E3.", indent=0.394, space_after=6)

    # 7.2 Hướng phát triển tiếp theo
    vh.add_heading_2(doc, "7.2. Hướng phát triển tiếp theo")
    vh.add_p(doc, "Các hướng nghiên cứu và phát triển tiếp theo nhằm hoàn thiện thiết bị bao gồm:", indent=0.394)
    vh.add_p(doc, "• Triển khai thuật toán ước lượng cao độ lai (Hybrid Pitch Detector): Kết hợp thuật toán YIN trong miền thời gian cho dải trầm dưới 110 Hz và FFT nội suy parabol cho dải trung và cao.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Bổ sung cảm biến đo rung tiếp xúc áp điện (piezo pickup) gắn trực tiếp lên soundboard để thu nhận tín hiệu dải cực trầm (A0–C2) mà không bị suy hao qua không khí.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Phát triển tính năng tự động bù trừ đường cong Railsback (Stretch Tuning) cho phép căn chỉnh theo đặc tính cơ học của từng cây đàn.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Nâng cấp giao thức truyền thông sang WebSocket để đẩy dữ liệu thời gian thực hai chiều thay cho cơ chế HTTP polling định kỳ hiện tại.", indent=0.394, space_after=3)
    vh.add_p(doc, "• Tiến hành kiểm chứng dài hạn (soak test) 24–48 giờ và đo đạc với nguồn âm thanh chuẩn tham chiếu độc lập.", indent=0.394, space_after=6)

    # =========================================================================
    # TÀI LIỆU THAM KHẢO
    # =========================================================================
    vh.add_heading_1(doc, "TÀI LIỆU THAM KHẢO", is_chapter=True)

    refs = [
        ("[1]", "J. W. Cooley and J. W. Tukey, \"An algorithm for the machine calculation of complex Fourier series,\" Mathematics of Computation, vol. 19, no. 90, pp. 297–301, 1965."),
        ("[2]", "Bộ môn Viễn thông - Xử lý tín hiệu, \"Tài liệu hướng dẫn thực hành Xử lý tín hiệu số,\" Trường Đại học Bách Khoa, ĐHQG-HCM, 2024."),
        ("[3]", "TDK InvenSense, \"INMP441: Omnidirectional Microphone with I2S Digital Output Data Sheet,\" Revision 1.1, 2014. [Trực tuyến]. Địa chỉ: https://invensense.tdk.com/products/digital/inmp441/"),
        ("[4]", "Espressif Systems, \"ESP32-S3 Series Datasheet,\" Version 1.7, 2024. [Trực tuyến]. Địa chỉ: https://www.espressif.com/en/products/socs/esp32-s3"),
        ("[5]", "The MIDI Association, \"Standard MIDI-File Format Spec. 1.1,\" Los Angeles, CA, 1996. [Trực tuyến]. Địa chỉ: https://www.midi.org/specifications"),
        ("[6]", "H. Fletcher, \"Normal vibration frequencies of a stiff piano string,\" The Journal of the Acoustical Society of America, vol. 36, no. 1, pp. 203–209, 1964. DOI: 10.1121/1.1918933."),
        ("[7]", "J. O. Smith, \"Spectral Audio Signal Processing,\" W3K Publishing, 2011. [Trực tuyến]. Địa chỉ: https://ccrma.stanford.edu/~jos/sasp/"),
        ("[8]", "A. V. Oppenheim and R. W. Schafer, \"Discrete-Time Signal Processing,\" 3rd ed., Upper Saddle River, NJ: Prentice Hall, 2009."),
        ("[9]", "E. Jacobsen and P. Kootsookos, \"The fast, biased, parabolic estimator,\" IEEE Signal Processing Magazine, vol. 24, no. 3, pp. 123–125, May 2007. [CẦN XÁC MINH THÔNG TIN THƯ MỤC]."),
        ("[10]", "M. Abe and J. O. Smith, \"Bias correction in parabolic interpolation of peak spectral magnitude,\" in Proc. IEEE ICASSP, vol. 2, pp. 213–216, 2004. [CẦN XÁC MINH THÔNG TIN THƯ MỤC]."),
    ]

    for tag, text in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        
        r_tag = p.add_run(f"{tag} ")
        r_tag.font.name = "Times New Roman"
        r_tag.font.size = Pt(11)
        r_tag.bold = True
        
        r_txt = p.add_run(text)
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(11)
        if "[CẦN XÁC MINH" in text:
            r_txt.font.color.rgb = RGBColor(180, 20, 20)

    # =========================================================================
    # PHỤ LỤC A: ĐẶC TẢ GÓI TIN DỮ LIỆU JSON
    # =========================================================================
    vh.add_heading_1(doc, "PHỤ LỤC A: ĐẶC TẢ GÓI TIN DỮ LIỆU JSON QUA GIAO THỨC HTTP/API", is_chapter=True)
    vh.add_p(doc, 
        "Dữ liệu kết quả phân tích cao độ thời gian thực được máy chủ Web nhúng ESP32-S3 cung cấp tại endpoint /api/data "
        "dưới dạng chuỗi JSON định dạng chuẩn:", indent=0.394)

    json_example = (
        "{\n"
        '  "note": "A4",\n'
        '  "freq": 440.281,\n'
        '  "target": 440.000,\n'
        '  "cents": 1.10,\n'
        '  "in_tune": true,\n'
        '  "octave": 4,\n'
        '  "confidence": 0.94,\n'
        '  "valid": true,\n'
        '  "latency_ms": 24.15\n'
        "}"
    )
    vh.add_code_block(doc, json_example)

    # =========================================================================
    # PHỤ LỤC B: BẢNG THIẾT BỊ KIỂM TRA VÀ ĐẶC TẢ MÔI TRƯỜNG THỬ NGHIỆM
    # =========================================================================
    vh.add_heading_1(doc, "PHỤ LỤC B: BẢNG THIẾT BỊ KIỂM TRA VÀ ĐẶC TẢ MÔI TRƯỜNG THỬ NGHIỆM", is_chapter=True)
    vh.add_p(doc, 
        "Bảng tổng hợp thiết bị và điều kiện môi trường đo đạc phục vụ quá trình kiểm thử thực nghiệm:", indent=0.394)

    vh.add_caption(doc, "Bảng B.1: Danh mục thiết bị thử nghiệm và thông số môi trường âm học", is_table=True)
    tbl_b = doc.add_table(rows=1, cols=3)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_b.autofit = False
    vh.set_table_borders(tbl_b)

    tb_w = [Inches(2.0), Inches(2.3), Inches(2.0)]
    tb_hdrs = ["Hạng mục thiết bị / Môi trường", "Thông số và Cấu hình thực tế", "Ghi chú xác thực"]
    for idx, text in enumerate(tb_hdrs):
        c = tbl_b.rows[0].cells[idx]
        c.width = tb_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.0)
        r.bold = True

    tb_rows = [
        ("Cây đàn piano thử nghiệm", "[CẦN BỔ SUNG: hãng và model đàn piano]", "Đàn acoustic cơ thật"),
        ("Vi điều khiển xử lý DSP", "ESP32-S3-WROOM-1 (N16R8, 240 MHz)", "Đã xác thực phần cứng"),
        ("Microphone thu âm", "INMP441 MEMS Omnidirectional I2S", "Đã xác thực phần cứng"),
        ("Môi trường âm học phòng đo", "[CẦN BỔ SUNG: đặc điểm phòng, nhiệt độ, dBA]", "Cần đo mức ồn nền"),
        ("Trình duyệt kiểm thử tự động", "Google Chrome (Headless CDP Automation)", "8 viewport độ phân giải"),
    ]
    for r_data in tb_rows:
        row = tbl_b.add_row()
        for idx, text in enumerate(r_data):
            c = row.cells[idx]
            c.width = tb_w[idx]
            vh.set_cell_margins(c, top=50, bottom=50, left=50, right=50)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx in [0, 1] else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            if idx == 0:
                r.bold = True
            if "[CẦN BỔ SUNG" in text:
                r.font.color.rgb = RGBColor(180, 20, 20)

    vh.make_table_responsive(tbl_b)

    # =========================================================================
    # PHỤ LỤC C: BẢNG TẦN SỐ CHUẨN 88 PHÍM ĐÀN PIANO (12-TET)
    # =========================================================================
    vh.add_heading_1(doc, "PHỤ LỤC C: BẢNG TẦN SỐ CHUẨN 88 PHÍM ĐÀN PIANO (HỆ 12-TET)", is_chapter=True)
    vh.add_p(doc, 
        "Bảng tần số chuẩn của toàn bộ 88 phím đàn piano (từ A0 đến C8) được tính toán chính xác theo hệ âm bình quân 12-TET "
        "với nốt chuẩn A4 = 440.000\u00A0Hz theo công thức f = 440.0 × 2^{(n_MIDI − 69)/12}:", indent=0.394)

    vh.add_caption(doc, "Bảng C.1: Tần số danh định của 88 phím đàn piano theo hệ âm 12-TET (A0 đến C8)", is_table=True)

    # Generate 88 keys into a clean 6-column table (2 sets of Note/MIDI/Freq)
    tbl_88 = doc.add_table(rows=1, cols=6)
    tbl_88.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_88.autofit = False
    vh.set_table_borders(tbl_88)

    t88_w = [Inches(0.9), Inches(0.8), Inches(1.3), Inches(0.9), Inches(0.8), Inches(1.3)]
    t88_hdrs = ["Nốt nhạc", "MIDI", "Tần số (Hz)", "Nốt nhạc", "MIDI", "Tần số (Hz)"]
    for idx, text in enumerate(t88_hdrs):
        c = tbl_88.rows[0].cells[idx]
        c.width = t88_w[idx]
        vh.set_cell_background(c, "EAECEF")
        vh.set_cell_margins(c, top=60, bottom=60, left=40, right=40)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True

    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    keys_data = []
    for midi in range(21, 109): # 21 (A0) to 108 (C8) = 88 keys
        n_idx = midi % 12
        octave = (midi // 12) - 1
        note_name = f"{NOTE_NAMES[n_idx]}{octave}"
        freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))
        keys_data.append((note_name, str(midi), f"{freq:.3f}"))

    half = 44 # 44 rows
    for r_idx in range(half):
        row = tbl_88.add_row()
        k1 = keys_data[r_idx]
        k2 = keys_data[r_idx + half]
        row_vals = [k1[0], k1[1], k1[2], k2[0], k2[1], k2[2]]
        for c_idx, val in enumerate(row_vals):
            c = row.cells[c_idx]
            c.width = t88_w[c_idx]
            vh.set_cell_margins(c, top=30, bottom=30, left=40, right=40)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 1, 3, 4] else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            if c_idx in [0, 3]:
                r.bold = True

    vh.make_table_responsive(tbl_88)

print("v2_ch5_ch7 module ready.")
