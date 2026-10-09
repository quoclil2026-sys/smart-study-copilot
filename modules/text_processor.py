"""
Module: text_processor.py
Chức năng: Tiền xử lý, trích xuất và phân tích thống kê văn bản từ người dùng hoặc tệp tải lên (.txt, .docx).
"""

import re
from typing import Tuple, Dict, Any
import io

def clean_text(raw_text: str) -> str:
    """
    Làm sạch văn bản:
    - Chuẩn hóa khoảng trắng và dòng trống liên tiếp.
    - Loại bỏ các ký tự điều khiển lạ.
    - Giữ lại cấu trúc phân đoạn tự nhiên.
    """
    if not raw_text:
        return ""
    
    # Loại bỏ các ký tự null hoặc ký tự điều khiển không hiển thị (trừ tab và newline)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw_text)
    
    # Chuẩn hóa khoảng cách ngang (nhiều space/tab liên tiếp thành 1 space)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Chuẩn hóa xuống dòng (tối đa 2 dòng trống liên tiếp)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()


def extract_text_from_file(uploaded_file) -> Tuple[str, str]:
    """
    Trích xuất văn bản từ file tải lên (.txt hoặc .docx).
    Trả về: (nội dung văn bản, thông báo lỗi nếu có)
    """
    if uploaded_file is None:
        return "", "Không có tệp nào được tải lên."
    
    file_name = uploaded_file.name.lower()
    
    try:
        if file_name.endswith('.txt'):
            # Đọc file văn bản thuần với xử lý encoding linh hoạt (UTF-8, Latin-1)
            raw_bytes = uploaded_file.read()
            try:
                content = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                content = raw_bytes.decode('latin-1', errors='replace')
            return clean_text(content), ""
            
        elif file_name.endswith('.docx'):
            try:
                import docx
            except ImportError:
                return "", "Thư viện 'python-docx' chưa được cài đặt. Hãy chạy: pip install python-docx"
            
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text)
            
            # Đọc cả nội dung trong bảng nếu có
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_text:
                        full_text.append(" | ".join(row_text))
                        
            return clean_text("\n\n".join(full_text)), ""
            
        else:
            return "", f"Định dạng tệp không được hỗ trợ ({file_name}). Vui lòng tải file .txt hoặc .docx."
            
    except Exception as e:
        return "", f"Lỗi khi đọc tệp: {str(e)}"


def get_text_statistics(text: str) -> Dict[str, Any]:
    """
    Tính toán các chỉ số thống kê của văn bản:
    - Tổng số từ
    - Số ký tự (bao gồm & không bao gồm khoảng trắng)
    - Số đoạn văn
    - Thời gian đọc ước tính (trung bình 200 từ/phút)
    """
    cleaned = clean_text(text)
    if not cleaned:
        return {
            "word_count": 0,
            "char_count": 0,
            "char_count_no_spaces": 0,
            "paragraph_count": 0,
            "reading_time_minutes": 0.0
        }
    
    words = cleaned.split()
    word_count = len(words)
    char_count = len(cleaned)
    char_count_no_spaces = len(re.sub(r'\s', '', cleaned))
    paragraphs = [p for p in cleaned.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    reading_time = round(word_count / 200, 1) if word_count > 0 else 0.0
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "paragraph_count": paragraph_count,
        "reading_time_minutes": reading_time
    }
