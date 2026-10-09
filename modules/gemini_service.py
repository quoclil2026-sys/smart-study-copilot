"""
Module: gemini_service.py
Chức năng: Tích hợp Google Gemini API (gemini-3.8-flash) thông qua thư viện `google-genai`.
Bao gồm:
- Thiết kế Prompt Engineering tối ưu.
- Bắt lỗi ngoại lệ mạng, hạn ngạch (Rate Limit), máy chủ quá tải (503 UNAVAILABLE).
- Cơ chế tự động thử lại đa mô hình (Model Cascade: 3.8-flash -> 3.8-flash-lite -> 1.5-flash).
- Chế độ tự động chuyển đổi sang Mock Data an toàn khi gặp sự cố.
"""

import os
import json
import re
import time
from typing import Dict, Any, List, Tuple
from .mock_data import MOCK_SUMMARY, MOCK_QUIZ

# Mô hình mặc định và danh sách dự phòng khi máy chủ quá tải
DEFAULT_MODEL = "gemini-3.8-flash"
CANDIDATE_FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.8-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

def resolve_model_name(model_name: str) -> str:
    """Tự động chuyển đổi các mô hình cũ (như 2.5-flash đã hết hạn) sang phiên bản mới 3.8-flash."""
    if not model_name or "2.5-flash" in model_name:
        return "gemini-3.8-flash"
    return model_name


def format_friendly_error(err_str: str) -> str:
    """Chuyển đổi các mã lỗi kỹ thuật phức tạp thành thông báo tiếng Việt dễ hiểu cho sinh viên."""
    if "503" in err_str or "UNAVAILABLE" in err_str:
        return "Máy chủ Google Gemini đang tạm thời quá tải (Mã 503: High Demand) do lượng truy cập toàn cầu tăng cao. Hệ thống đã kích hoạt Mock Data an toàn để bài học không bị gián đoạn. Bạn có thể bấm thử lại sau 30-60 giây."
    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
        return "Tài khoản vượt hạn ngạch yêu cầu miễn phí tạm thời (Mã 429: Rate Limit). Đã chuyển sang Mock Data an toàn."
    if "404" in err_str or "NOT_FOUND" in err_str:
        return "Mô hình yêu cầu không khả dụng trên tài khoản Google của bạn (Mã 404: Not Found). Đã chuyển sang Mock Data."
    if "API_KEY_INVALID" in err_str or ("400" in err_str and "API key" in err_str):
        return "API Key không hợp lệ. Vui lòng kiểm tra lại khóa API tại Google AI Studio."
    return f"Lỗi gọi Gemini API ({err_str}). Đã tự động kích hoạt Mock Data an toàn."


def get_gemini_client(api_key: str):
    """Khởi tạo client Google GenAI từ API Key."""
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Không thể khởi tạo Gemini Client: {str(e)}")


def _call_gemini_with_fallback(
    api_key: str,
    prompt: str,
    system_instruction: str = None,
    temperature: float = 0.3,
    requested_model: str = DEFAULT_MODEL
) -> Tuple[str, str, str, str]:
    """
    Gọi Gemini API với cơ chế tự động chuyển mô hình dự phòng nếu gặp lỗi 503 (quá tải) hoặc 429/404.
    Trả về: (response_text, model_thực_tế_đã_dùng, thông_báo_chuyển_đổi, lỗi_nếu_thất_bại_toàn_bộ)
    """
    start_model = resolve_model_name(requested_model)
    models_to_try = [start_model]
    for m in CANDIDATE_FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    try:
        client = get_gemini_client(api_key)
    except Exception as e:
        return "", "", "", str(e)

    last_error = ""
    for idx, model_name in enumerate(models_to_try):
        try:
            config = {"temperature": temperature}
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            
            if response and response.text:
                notice = ""
                if idx > 0:
                    notice = f"⚡ Mô hình '{start_model}' bị quá tải, đã tự động chuyển sang '{model_name}' thành công!"
                return response.text, model_name, notice, ""
                
        except Exception as ex:
            last_error = str(ex)
            # Nếu gặp 503 quá tải hoặc 429/404, đợi 1.5s để Google phục hồi và thử mô hình dự phòng tiếp theo
            if any(err_code in last_error for err_code in ["503", "429", "404", "UNAVAILABLE"]):
                time.sleep(1.5)
                continue
            else:
                # Nếu lỗi sai API key hoặc cấu trúc thì không thử tiếp
                break

    return "", "", "", last_error


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
    
    text_res, used_model, notice, err = _call_gemini_with_fallback(
        api_key=api_key,
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=0.3,
        requested_model=custom_model
    )
    
    if text_res:
        return text_res, False, notice
    else:
        friendly_msg = format_friendly_error(err)
        return MOCK_SUMMARY, True, friendly_msg


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
    
    raw_res, used_model, notice, err = _call_gemini_with_fallback(
        api_key=api_key,
        prompt=prompt,
        system_instruction=None,
        temperature=0.4,
        requested_model=custom_model
    )
    
    if raw_res:
        # Làm sạch chuỗi JSON nếu Gemini bọc trong ```json ... ```
        cleaned_json = raw_res.strip()
        if cleaned_json.startswith("```"):
            cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json)
            cleaned_json = re.sub(r"\s*```$", "", cleaned_json)
        cleaned_json = cleaned_json.strip()
        
        try:
            quiz_data = json.loads(cleaned_json)
            if isinstance(quiz_data, list) and len(quiz_data) > 0:
                return quiz_data, False, notice
        except Exception:
            pass
            
    friendly_msg = format_friendly_error(err) if err else "Định dạng JSON từ AI bị lỗi cú pháp."
    return MOCK_QUIZ, True, friendly_msg
