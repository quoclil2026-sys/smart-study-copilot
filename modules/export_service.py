"""
Module: export_service.py
Chức năng: Chuyển đổi dữ liệu phiên học (Tóm tắt, Quiz, Điểm số, Lịch sử)
sang định dạng Markdown và Plain Text để người dùng tải về lưu trữ cá nhân.
"""

from datetime import datetime
from typing import List, Dict, Any

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
        "📝 *Tạo tự động bởi Smart Study Copilot (Tích hợp Google Gemini 2.5 Flash & Streamlit)*"
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
    # Loại bỏ cơ bản các ký hiệu markdown để có text thuần
    text = md.replace("# ", "").replace("## ", "").replace("### ", "").replace("#### ", "")
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return text
