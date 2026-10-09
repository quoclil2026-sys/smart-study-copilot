"""
Module: gemini_service.py
Chức năng: Tích hợp Google Gemini API (gemini-2.5-flash) thông qua thư viện `google-genai`.
Bao gồm:
- Thiết kế Prompt Engineering tối ưu.
- Bắt lỗi ngoại lệ mạng, hạn ngạch (Rate Limit), khóa API sai.
- Chế độ tự động chuyển đổi sang Mock Data khi gặp lỗi hoặc khi bật Demo Mode.
"""

import os
import json
import re
from typing import Dict, Any, List, Tuple
from .mock_data import MOCK_SUMMARY, MOCK_QUIZ

# Tên mô hình khuyến nghị tối ưu tốc độ & chi phí miễn phí
DEFAULT_MODEL = "gemini-2.5-flash"

def get_gemini_client(api_key: str):
    """Khởi tạo client Google GenAI từ API Key."""
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Không thể khởi tạo Gemini Client: {str(e)}")


def generate_summary(text: str, api_key: str = "", force_mock: bool = False, custom_model: str = DEFAULT_MODEL) -> Tuple[str, bool, str]:
    """
    Sinh tóm tắt tài liệu học tập theo cấu trúc phân tầng + thuật ngữ.
    Trả về: (nội dung tóm tắt, cờ is_mock, thông báo lỗi nếu có)
    """
    if force_mock:
        return MOCK_SUMMARY, True, "Đang sử dụng Dữ liệu ngoại tuyến (Offline Mock Data)."
    
    if not api_key:
        return MOCK_SUMMARY, True, "Chưa cung cấp API Key. Đã tự động kích hoạt chế độ Mock Data."
    
    system_instruction = (
        "Bạn là 'Smart Study Copilot' - một trợ lý gia sư học tập thông minh dành cho sinh viên đại học. "
        "Nhiệm vụ của bạn là đọc nội dung bài giảng/tài liệu được cung cấp và tạo ra một bản tóm tắt học tập tối ưu, "
        "dễ hiểu, chuẩn kiến thức và súc tích."
    )
    
    prompt = f"""
Hãy phân tích và tóm tắt tài liệu học tập sau đây theo cấu trúc phân tầng chuẩn mực:

CẤU TRÚC BẮT BUỘC:
1. 📌 **TIÊU ĐỀ BÀI HỌC VÀ TỔNG QUAN NGẮN GỌN** (2-3 câu giới thiệu bức tranh toàn cảnh)
2. 📑 **DÀN Ý KIẾN THỨC CỐT LÕI (PHÂN TẦNG)**:
   - Chia thành các đề mục lớn (1, 2, 3...)
   - Dưới mỗi đề mục là các gạch đầu dòng ngắn gọn, cô đọng, nêu bật cơ chế/nguyên lý
3. 📖 **BẢNG TRA CỨU THUẬT NGỮ CHUYÊN NGÀNH (GLOSSARY)**:
   - Liệt kê các thuật ngữ quan trọng xuất hiện trong bài kèm định nghĩa ngắn gọn, dễ nhớ (1-2 câu mỗi thuật ngữ).
4. 💡 **LỜI KHUYÊN ÔN TẬP NHANH (TAKEAWAY)**:
   - 1-2 điểm mấu chốt sinh viên cần nhớ để làm bài thi.

--- NỘI DUNG TÀI LIỆU BẮT ĐẦU ---
{text}
--- NỘI DUNG TÀI LIỆU KẾT THÚC ---
"""
    
    try:
        client = get_gemini_client(api_key)
        response = client.models.generate_content(
            model=custom_model or DEFAULT_MODEL,
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.3, # Nhiệt độ thấp để đảm bảo tính chính xác học thuật
            }
        )
        
        if response and response.text:
            return response.text, False, ""
        else:
            return MOCK_SUMMARY, True, "API không trả về nội dung. Đã chuyển sang Mock Data."
            
    except Exception as ex:
        err_msg = str(ex)
        # Rơi về Mock Data khi gặp lỗi mạng, rate limit, quota
        return MOCK_SUMMARY, True, f"Lỗi gọi Gemini API ({err_msg}). Đã tự động kích hoạt Mock Data an toàn."


def generate_quiz(text: str, num_questions: int = 4, api_key: str = "", force_mock: bool = False, custom_model: str = DEFAULT_MODEL) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    Tự động sinh bộ câu hỏi trắc nghiệm (3-5 câu) 4 phương án A, B, C, D kèm lời giải.
    Trả về: (danh sách câu hỏi dạng JSON/Dict, cờ is_mock, thông báo lỗi nếu có)
    """
    if force_mock:
        return MOCK_QUIZ, True, "Đang sử dụng Bộ câu hỏi ngoại tuyến (Offline Mock Data)."
        
    if not api_key:
        return MOCK_QUIZ, True, "Chưa cung cấp API Key. Đã tự động kích hoạt Mock Data."
        
    prompt = f"""
Dựa vào nội dung tài liệu sau đây, hãy soạn chính xác {num_questions} câu hỏi trắc nghiệm khách quan (Multiple Choice Questions) để kiểm tra mức độ hiểu bài của sinh viên.

YÊU CẦU ĐẶC BIỆT:
- Mỗi câu hỏi gồm đúng 4 lựa chọn: A, B, C, D.
- Các phương án nhiễu phải hợp lý, câu hỏi phân hóa từ nhận biết đến thông hiểu.
- BẮT BUỘC có đáp án đúng ("correct_answer" là một trong các chữ cái "A", "B", "C", "D") và lời giải thích ngắn gọn ("explanation") lý giải tại sao đúng.
- CHỈ TRẢ VỀ DUY NHẤT một mảng JSON thuần túy (không bọc trong markdown hoặc chỉ bọc trong ```json ... ```), theo đúng cấu trúc sau:

[
  {{
    "id": 1,
    "question": "Nội dung câu hỏi...",
    "options": {{
      "A": "Lựa chọn A...",
      "B": "Lựa chọn B...",
      "C": "Lựa chọn C...",
      "D": "Lựa chọn D..."
    }},
    "correct_answer": "A",
    "explanation": "Giải thích chi tiết vì sao A đúng..."
  }}
]

NỘI DUNG TÀI LIỆU CẦN TẠO QUIZ:
{text}
"""
    
    try:
        client = get_gemini_client(api_key)
        response = client.models.generate_content(
            model=custom_model or DEFAULT_MODEL,
            contents=prompt,
            config={
                "temperature": 0.4,
            }
        )
        
        raw_output = response.text if response else ""
        if not raw_output:
            return MOCK_QUIZ, True, "API không trả về nội dung. Đã chuyển sang Mock Data."
            
        # Làm sạch chuỗi JSON nếu Gemini bọc trong ```json ... ```
        cleaned_json = raw_output.strip()
        if cleaned_json.startswith("```"):
            cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json)
            cleaned_json = re.sub(r"\s*```$", "", cleaned_json)
        cleaned_json = cleaned_json.strip()
        
        # Parse JSON
        quiz_data = json.loads(cleaned_json)
        if isinstance(quiz_data, list) and len(quiz_data) > 0:
            return quiz_data, False, ""
        else:
            return MOCK_QUIZ, True, "Dữ liệu JSON từ API không đúng định dạng mảng. Chuyển sang Mock Data."
            
    except Exception as ex:
        err_msg = str(ex)
        return MOCK_QUIZ, True, f"Lỗi tạo Quiz qua API ({err_msg}). Đã tự động kích hoạt Mock Data an toàn."
