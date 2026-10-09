"""
Module: export_service.py
Chức năng: Chuyển đổi dữ liệu phiên học (Tóm tắt, Quiz, Điểm số, Thống kê)
sang các định dạng:
1. Microsoft Word (.docx) - Chuẩn thiết kế chuyên nghiệp, màu sắc học thuật, bảng biểu đẹp mắt.
2. Adobe PDF (.pdf) - Chuẩn in ấn, hỗ trợ 100% tiếng Việt UTF-8 (Arial), phân chia khối rõ ràng.
3. Markdown (.md) - Chuẩn lưu trữ cho Obsidian/Notion.
4. Plain Text (.txt) - Văn bản thuần đơn giản.
"""

import io
import os
import re
from datetime import datetime
from typing import List, Dict, Any

# =========================================================================
# 1. XUẤT ĐỊNH DẠNG MICROSOFT WORD (.DOCX) SIÊU ĐẸP
# =========================================================================
def generate_docx_export(
    summary: str,
    quiz_data: List[Dict[str, Any]],
    user_answers: Dict[int, str],
    score_info: Dict[str, Any],
    stats: Dict[str, Any]
) -> bytes:
    """Tạo tệp Word (.docx) định dạng chuyên nghiệp với bảng, màu sắc và hộp ghi chú."""
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
        from docx.oxml import parse_xml, OxmlElement
        from docx.oxml.ns import nsdecls, qn
    except ImportError:
        return b""

    doc = docx.Document()

    # Thiết lập lề trang tiêu chuẩn (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    # Bảng màu chủ đạo (Executive Academic Palette)
    PRIMARY_COLOR = RGBColor(30, 58, 138)    # Deep Navy #1E3A8A
    SECONDARY_COLOR = RGBColor(37, 99, 235)  # Royal Blue #2563EB
    SUCCESS_COLOR = RGBColor(22, 101, 52)    # Dark Green #166534
    DANGER_COLOR = RGBColor(153, 27, 27)     # Dark Red #991B1B
    GRAY_TEXT = RGBColor(107, 114, 128)      # Gray #6B7280
    DARK_TEXT = RGBColor(31, 41, 55)         # Charcoal #1F2937

    def set_cell_background(cell, hex_color: str):
        """Đặt màu nền cho ô bảng."""
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    # 1. TIÊU ĐỀ BẢN GHI CHÉP
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    title_run = title_p.add_run("🎓 SMART STUDY COPILOT - BẢN GHI CHÉP HỌC TẬP")
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    title_run.font.color.rgb = PRIMARY_COLOR

    # Ngày tạo & metadata
    now_str = datetime.now().strftime("%d/%m/%Y lúc %H:%M:%S")
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(14)
    sub_run = sub_p.add_run(f"Được tạo tự động vào ngày {now_str} • Tích hợp Google Gemini AI")
    sub_run.font.size = Pt(9.5)
    sub_run.font.italic = True
    sub_run.font.color.rgb = GRAY_TEXT

    # 2. KHỐI 1: THỐNG KÊ TÀI LIỆU GỐC (Bảng chỉ số đẹp)
    h1 = doc.add_heading(level=1)
    h1.paragraph_format.space_before = Pt(10)
    h1.paragraph_format.space_after = Pt(6)
    h1_run = h1.add_run("📊 1. THỐNG KÊ TÀI LIỆU GỐC")
    h1_run.font.size = Pt(13)
    h1_run.font.bold = True
    h1_run.font.color.rgb = PRIMARY_COLOR

    table = doc.add_table(rows=2, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    col_names = ["Tổng số từ", "Số ký tự", "Số đoạn văn", "Thời gian đọc"]
    col_vals = [
        f"{stats.get('word_count', 0):,} từ",
        f"{stats.get('char_count', 0):,} ký tự",
        f"{stats.get('paragraph_count', 0)} đoạn",
        f"~{stats.get('reading_time_minutes', 0)} phút"
    ]

    for i in range(4):
        # Header cell
        c_hdr = table.cell(0, i)
        set_cell_background(c_hdr, "EFF6FF") # Light Blue
        p_hdr = c_hdr.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_hdr = p_hdr.add_run(col_names[i])
        r_hdr.font.size = Pt(9.5)
        r_hdr.font.bold = True
        r_hdr.font.color.rgb = PRIMARY_COLOR

        # Value cell
        c_val = table.cell(1, i)
        set_cell_background(c_val, "F8FAFC")
        p_val = c_val.paragraphs[0]
        p_val.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_val = p_val.add_run(col_vals[i])
        r_val.font.size = Pt(11)
        r_val.font.bold = True
        r_val.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 3. KHỐI 2: TÓM TẮT THÔNG MINH PHÂN TẦNG
    h2 = doc.add_heading(level=1)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2_run = h2.add_run("📑 2. TÓM TẮT & THUẬT NGỮ CHUYÊN NGÀNH")
    h2_run.font.size = Pt(13)
    h2_run.font.bold = True
    h2_run.font.color.rgb = PRIMARY_COLOR

    if summary:
        lines = summary.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            # Tiêu đề markdown #, ##, ###
            if line_str.startswith("### "):
                hp = doc.add_paragraph()
                hp.paragraph_format.space_before = Pt(8)
                hp.paragraph_format.space_after = Pt(2)
                hr = hp.add_run(line_str.replace("### ", ""))
                hr.font.bold = True
                hr.font.size = Pt(11.5)
                hr.font.color.rgb = SECONDARY_COLOR
            elif line_str.startswith("## ") or line_str.startswith("# "):
                hp = doc.add_paragraph()
                hp.paragraph_format.space_before = Pt(10)
                hp.paragraph_format.space_after = Pt(3)
                clean_h = re.sub(r"^#+\s*", "", line_str)
                hr = hp.add_run(clean_h)
                hr.font.bold = True
                hr.font.size = Pt(12)
                hr.font.color.rgb = PRIMARY_COLOR
            elif line_str.startswith("- ") or line_str.startswith("* "):
                # Gạch đầu dòng
                bp = doc.add_paragraph(style='List Bullet')
                bp.paragraph_format.space_after = Pt(2)
                content = line_str[2:].strip()
                # Phân tách thẻ bold **...**
                parts = re.split(r'(\*\*.*?\*\*)', content)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        r = bp.add_run(part[2:-2])
                        r.font.bold = True
                        r.font.color.rgb = DARK_TEXT
                    else:
                        r = bp.add_run(part)
                        r.font.color.rgb = DARK_TEXT
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(4)
                parts = re.split(r'(\*\*.*?\*\*)', line_str)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        r = p.add_run(part[2:-2])
                        r.font.bold = True
                    else:
                        r = p.add_run(part)
                    r.font.color.rgb = DARK_TEXT
    else:
        doc.add_paragraph("_Chưa có nội dung tóm tắt._")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 4. KHỐI 3: BỘ CÂU HỎI TRẮC NGHIỆM VÀ KẾT QUẢ
    h3 = doc.add_heading(level=1)
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(6)
    h3_run = h3.add_run("🎯 3. BÀI TẬP TRẮC NGHIỆM TƯƠNG TÁC")
    h3_run.font.size = Pt(13)
    h3_run.font.bold = True
    h3_run.font.color.rgb = PRIMARY_COLOR

    # Hộp điểm số (nếu đã nộp bài)
    if score_info and score_info.get("submitted", False):
        total = score_info.get("total", 0)
        correct = score_info.get("correct", 0)
        pct = (correct / total * 100) if total > 0 else 0

        score_tbl = doc.add_table(rows=1, cols=1)
        score_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        score_cell = score_tbl.cell(0, 0)
        set_cell_background(score_cell, "DCFCE7" if pct >= 75 else "FEF3C7") # Xanh lá hoặc Vàng nhạt
        
        sp = score_cell.paragraphs[0]
        sp.paragraph_format.space_before = Pt(4)
        sp.paragraph_format.space_after = Pt(4)
        sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr = sp.add_run(f"🏆 KẾT QUẢ ĐẠT ĐƯỢC: {correct}/{total} CÂU ĐÚNG ({pct:.1f}%)")
        sr.font.size = Pt(11)
        sr.font.bold = True
        sr.font.color.rgb = SUCCESS_COLOR if pct >= 75 else RGBColor(180, 83, 9)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    if quiz_data:
        for idx, q in enumerate(quiz_data, 1):
            q_id = q.get("id", idx)
            qp = doc.add_paragraph()
            qp.paragraph_format.space_before = Pt(8)
            qp.paragraph_format.space_after = Pt(2)
            qr = qp.add_run(f"Câu {idx}: {q.get('question', '')}")
            qr.font.bold = True
            qr.font.size = Pt(10.5)
            qr.font.color.rgb = PRIMARY_COLOR

            options = q.get("options", {})
            user_ans = user_answers.get(q_id, "")
            corr_ans = q.get("correct_answer", "")

            for opt_k, opt_v in options.items():
                op = doc.add_paragraph(style='List Bullet')
                op.paragraph_format.space_after = Pt(1)
                
                # Tag trạng thái
                if opt_k == corr_ans and opt_k == user_ans:
                    tag = op.add_run("[✅ Bạn chọn Đúng] ")
                    tag.font.bold = True
                    tag.font.color.rgb = SUCCESS_COLOR
                elif opt_k == user_ans and user_ans != corr_ans:
                    tag = op.add_run("[❌ Bạn chọn Sai] ")
                    tag.font.bold = True
                    tag.font.color.rgb = DANGER_COLOR
                elif opt_k == corr_ans:
                    tag = op.add_run("[🌟 Đáp án đúng] ")
                    tag.font.bold = True
                    tag.font.color.rgb = SUCCESS_COLOR

                opt_r = op.add_run(f"{opt_k}. {opt_v}")
                opt_r.font.size = Pt(10)
                if opt_k == corr_ans:
                    opt_r.font.bold = True

            # Hộp lời giải thích chi tiết
            exp_p = doc.add_paragraph()
            exp_p.paragraph_format.left_indent = Inches(0.25)
            exp_p.paragraph_format.space_before = Pt(2)
            exp_p.paragraph_format.space_after = Pt(6)
            exp_label = exp_p.add_run("💡 Lời giải thích: ")
            exp_label.font.bold = True
            exp_label.font.size = Pt(9.5)
            exp_label.font.color.rgb = SECONDARY_COLOR
            
            exp_r = exp_p.add_run(q.get('explanation', 'Không có giải thích.'))
            exp_r.font.italic = True
            exp_r.font.size = Pt(9.5)
            exp_r.font.color.rgb = DARK_TEXT

    doc_stream = io.BytesIO()
    doc.save(doc_stream)
    return doc_stream.getvalue()


# =========================================================================
# 2. XUẤT ĐỊNH DẠNG ADOBE PDF (.PDF) SIÊU ĐẸP & CHUẨN TIẾNG VIỆT
# =========================================================================
def generate_pdf_export(
    summary: str,
    quiz_data: List[Dict[str, Any]],
    user_answers: Dict[int, str],
    score_info: Dict[str, Any],
    stats: Dict[str, Any]
) -> bytes:
    """Tạo tệp PDF in ấn chất lượng cao, định dạng màu sắc đẹp, hỗ trợ 100% tiếng Việt UTF-8."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        return b""

    # Đăng ký phông chữ Arial hỗ trợ hoàn hảo tiếng Việt có dấu trên Windows
    font_name = "Helvetica"
    font_bold = "Helvetica-Bold"
    font_italic = "Helvetica-Oblique"

    windows_arial = "C:/Windows/Fonts/arial.ttf"
    windows_arialbd = "C:/Windows/Fonts/arialbd.ttf"
    windows_ariali = "C:/Windows/Fonts/ariali.ttf"

    if os.path.exists(windows_arial):
        try:
            pdfmetrics.registerFont(TTFont('VietArial', windows_arial))
            font_name = 'VietArial'
            if os.path.exists(windows_arialbd):
                pdfmetrics.registerFont(TTFont('VietArial-Bold', windows_arialbd))
                font_bold = 'VietArial-Bold'
            else:
                font_bold = font_name
                
            if os.path.exists(windows_ariali):
                pdfmetrics.registerFont(TTFont('VietArial-Italic', windows_ariali))
                font_italic = 'VietArial-Italic'
            else:
                font_italic = font_name
        except Exception:
            pass

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Bảng màu chuẩn
    c_primary = colors.HexColor("#1E3A8A")   # Deep Navy
    c_secondary = colors.HexColor("#2563EB") # Royal Blue
    c_text = colors.HexColor("#1F2937")      # Charcoal
    c_gray = colors.HexColor("#6B7280")
    c_success = colors.HexColor("#166534")
    c_danger = colors.HexColor("#991B1B")

    # Các Styles văn bản
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=font_italic,
        fontSize=8.5,
        leading=12,
        textColor=c_gray,
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'DocH1',
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4
    )
    h2_style = ParagraphStyle(
        'DocH2',
        fontName=font_bold,
        fontSize=10.5,
        leading=14,
        textColor=c_secondary,
        spaceBefore=6,
        spaceAfter=2
    )
    body_style = ParagraphStyle(
        'DocBody',
        fontName=font_name,
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        spaceAfter=3
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        fontName=font_name,
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        leftIndent=12,
        spaceAfter=2
    )
    exp_style = ParagraphStyle(
        'DocExp',
        fontName=font_italic,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        spaceAfter=6
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("🎓 SMART STUDY COPILOT - BẢN GHI CHÉP HỌC TẬP", title_style))
    now_str = datetime.now().strftime("%d/%m/%Y lúc %H:%M:%S")
    story.append(Paragraph(f"Tạo tự động: {now_str} • Tích hợp Google Gemini AI", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=0, spaceAfter=8))

    # 2. Bảng Thống kê
    story.append(Paragraph("📊 1. THỐNG KÊ TÀI LIỆU GỐC", h1_style))
    stat_data = [
        [
            Paragraph(f"<b>Tổng số từ</b><br/>{stats.get('word_count', 0):,} từ", body_style),
            Paragraph(f"<b>Số ký tự</b><br/>{stats.get('char_count', 0):,} ký tự", body_style),
            Paragraph(f"<b>Số đoạn</b><br/>{stats.get('paragraph_count', 0)} đoạn", body_style),
            Paragraph(f"<b>Thời gian đọc</b><br/>~{stats.get('reading_time_minutes', 0)} phút", body_style)
        ]
    ]
    stat_table = Table(stat_data, colWidths=[130, 130, 130, 130])
    stat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#DBEAFE")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 8))

    # 3. Bản Tóm tắt Phân tầng
    story.append(Paragraph("📑 2. TÓM TẮT & THUẬT NGỮ CHUYÊN NGÀNH", h1_style))
    if summary:
        for line in summary.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            
            # Format markdown bold **abc** thành thẻ <b>abc</b> của ReportLab
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line_str)
            
            if line_str.startswith("### "):
                story.append(Paragraph(formatted_line.replace("### ", ""), h2_style))
            elif line_str.startswith("## ") or line_str.startswith("# "):
                clean_h = re.sub(r"^#+\s*", "", formatted_line)
                story.append(Paragraph(clean_h, h1_style))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                story.append(Paragraph(f"• {formatted_line[2:]}", bullet_style))
            else:
                story.append(Paragraph(formatted_line, body_style))
    else:
        story.append(Paragraph("<i>Chưa có nội dung tóm tắt.</i>", body_style))

    story.append(Spacer(1, 8))

    # 4. Trắc nghiệm & Kết quả
    story.append(Paragraph("🎯 3. BÀI TẬP TRẮC NGHIỆM TƯƠNG TÁC", h1_style))

    if score_info and score_info.get("submitted", False):
        total = score_info.get("total", 0)
        correct = score_info.get("correct", 0)
        pct = (correct / total * 100) if total > 0 else 0
        bg_col = colors.HexColor("#DCFCE7") if pct >= 75 else colors.HexColor("#FEF3C7")
        txt_col = c_success if pct >= 75 else colors.HexColor("#B45309")
        
        score_para = Paragraph(f"<b>🏆 KẾT QUẢ ĐẠT ĐƯỢC: {correct}/{total} CÂU ĐÚNG ({pct:.1f}%)</b>", ParagraphStyle(
            'ScoreText', fontName=font_bold, fontSize=10, leading=14, textColor=txt_col, alignment=1
        ))
        score_box = Table([[score_para]], colWidths=[520])
        score_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_col),
            ('BOX', (0, 0), (-1, -1), 0.5, txt_col),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(score_box)
        story.append(Spacer(1, 6))

    if quiz_data:
        for idx, q in enumerate(quiz_data, 1):
            q_id = q.get("id", idx)
            q_elements = []
            
            q_text = f"<b>Câu {idx}: {q.get('question', '')}</b>"
            q_elements.append(Paragraph(q_text, ParagraphStyle('QP', fontName=font_bold, fontSize=9.5, leading=13, textColor=c_primary)))

            user_ans = user_answers.get(q_id, "")
            corr_ans = q.get("correct_answer", "")

            for opt_k, opt_v in q.get('options', {}).items():
                prefix = ""
                opt_color = c_text
                if opt_k == corr_ans and opt_k == user_ans:
                    prefix = "<font color='#166534'><b>[✅ Đúng]</b></font> "
                elif opt_k == user_ans and user_ans != corr_ans:
                    prefix = "<font color='#991B1B'><b>[❌ Bạn chọn]</b></font> "
                elif opt_k == corr_ans:
                    prefix = "<font color='#166534'><b>[🌟 Đáp án]</b></font> "

                bold_wrap = f"<b>{opt_k}. {opt_v}</b>" if opt_k == corr_ans else f"{opt_k}. {opt_v}"
                opt_line = f"&nbsp;&nbsp;{prefix}{bold_wrap}"
                q_elements.append(Paragraph(opt_line, bullet_style))

            exp_line = f"💡 <b>Giải thích:</b> {q.get('explanation', '')}"
            q_elements.append(Paragraph(exp_line, exp_style))
            q_elements.append(Spacer(1, 4))
            
            story.append(KeepTogether(q_elements))

    # Xây dựng file PDF
    doc.build(story)
    return buffer.getvalue()


# =========================================================================
# 3. XUẤT ĐỊNH DẠNG MARKDOWN & TEXT
# =========================================================================
def generate_markdown_export(
    summary: str,
    quiz_data: List[Dict[str, Any]],
    user_answers: Dict[int, str],
    score_info: Dict[str, Any],
    stats: Dict[str, Any]
) -> str:
    """Tạo chuỗi định dạng Markdown hoàn chỉnh để xuất file."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_lines = [
        f"# 📚 SMART STUDY COPILOT - BẢN GHI CHÉP HỌC TẬP",
        f"*Thời gian tạo: {now_str}*",
        "",
        "---",
        "## 📊 1. THỐNG KÊ TÀI LIỆU GỐC",
        f"- **Số lượng từ:** {stats.get('word_count', 0):,} từ",
        f"- **Số ký tự:** {stats.get('char_count', 0):,} ký tự",
        f"- **Số đoạn văn:** {stats.get('paragraph_count', 0)} đoạn",
        f"- **Thời gian đọc ước tính:** ~{stats.get('reading_time_minutes', 0)} phút",
        "",
        "---",
        "## 📑 2. TÓM TẮT & THUẬT NGỮ CHUYÊN NGÀNH",
        "",
        summary if summary else "_Chưa có nội dung tóm tắt._",
        "",
        "---",
        "## 🎯 3. BÀI TẬP TRẮC NGHIỆM TƯƠNG TÁC & KẾT QUẢ",
        ""
    ]
    
    if score_info and score_info.get("submitted", False):
        total = score_info.get("total", 0)
        correct = score_info.get("correct", 0)
        pct = (correct / total * 100) if total > 0 else 0
        md_lines.extend([
            f"### 🏆 Kết quả làm bài: {correct}/{total} ({pct:.1f}%)",
            ""
        ])
    
    if quiz_data:
        for idx, q in enumerate(quiz_data, 1):
            q_id = q.get("id", idx)
            md_lines.append(f"#### Câu {idx}: {q.get('question', '')}")
            
            options = q.get("options", {})
            user_ans = user_answers.get(q_id, "Chưa chọn")
            corr_ans = q.get("correct_answer", "")
            
            for opt_key, opt_val in options.items():
                prefix = "- "
                if opt_key == corr_ans and opt_key == user_ans:
                    prefix = "- ✅ **[Bạn chọn Đúng]** "
                elif opt_key == user_ans and user_ans != corr_ans:
                    prefix = "- ❌ **[Bạn chọn Sai]** "
                elif opt_key == corr_ans:
                    prefix = "- 🌟 **[Đáp án chính xác]** "
                
                md_lines.append(f"{prefix}**{opt_key}.** {opt_val}")
            
            md_lines.append("")
            md_lines.append(f"> **Giải thích:** {q.get('explanation', 'Không có giải thích.')}")
            md_lines.append("")
    else:
        md_lines.append("_Chưa có câu hỏi trắc nghiệm._\n")
        
    md_lines.extend([
        "---",
        "📝 *Tạo tự động bởi Smart Study Copilot (Tích hợp Google Gemini AI & Streamlit)*"
    ])
    
    return "\n".join(md_lines)


def generate_text_export(
    summary: str,
    quiz_data: List[Dict[str, Any]],
    user_answers: Dict[int, str],
    score_info: Dict[str, Any],
    stats: Dict[str, Any]
) -> str:
    """Tạo chuỗi plain text đơn giản."""
    md = generate_markdown_export(summary, quiz_data, user_answers, score_info, stats)
    text = md.replace("# ", "").replace("## ", "").replace("### ", "").replace("#### ", "")
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return text
