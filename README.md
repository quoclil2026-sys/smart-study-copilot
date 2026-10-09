# 🎓 Smart Study Copilot
> **Trợ lý tóm tắt tài liệu học tập và tự động tạo bài kiểm tra trắc nghiệm tích hợp Google Gemini API**  
> *Đồ án / Dự án môn học ứng dụng AI dành cho Sinh viên CNTT*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini API](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-4285F4.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Giới thiệu Đề tài & Mục tiêu
Trong bối cảnh học tập hiện đại, sinh viên đại học thường xuyên đối mặt với khối lượng slide bài giảng, giáo trình PDF/Word khổng lồ. Việc tự tóm lược bằng tay tốn rất nhiều thời gian và thiếu công cụ ôn luyện trắc nghiệm tương tác tức thì để tự kiểm tra kiến thức trước kỳ thi.

**Smart Study Copilot** là ứng dụng Web mini được thiết kế tối ưu, gọn nhẹ:
1. **Tiền xử lý văn bản:** Tiếp nhận văn bản nhập trực tiếp hoặc tải tệp `.txt`, `.docx`, tự động chuẩn hóa, loại bỏ ký tự thừa và tính toán số từ/thời gian đọc.
2. **Tóm tắt thông minh phân tầng:** Tận dụng Google Gemini API (mô hình `gemini-2.5-flash`) để bóc tách dàn ý chính cốt lõi kèm bảng tra cứu thuật ngữ chuyên ngành (Glossary).
3. **Sinh Quiz trắc nghiệm tương tác:** Tự động tạo bộ 3–5 câu hỏi trắc nghiệm 4 lựa chọn (A, B, C, D) từ tài liệu, cho phép làm bài trực tiếp, chấm điểm và xem lời giải chi tiết.
4. **Quản lý phiên & Xuất dữ liệu:** Lưu trạng thái học tập qua `st.session_state` và hỗ trợ xuất toàn bộ nội dung ra định dạng Markdown (`.md`) hoặc Text (`.txt`).
5. **Chế độ Ngoại tuyến An toàn (Offline Mock Data):** Phòng ngừa rủi ro mất mạng hoặc nghẽn quota khi thuyết trình bảo vệ trực tiếp trước hội đồng.

---

## 🏗️ 2. Kiến trúc Hệ thống (System Architecture)

```
+-----------------------------------------------------------------------+
|                    GIAO DIỆN NGƯỜI DÙNG (STREAMLIT)                   |
|  - Tab 1: Nạp & Tiền xử lý văn bản (.txt, .docx, Direct text)         |
|  - Tab 2: Tóm tắt thông minh theo cấu trúc phân tầng                  |
|  - Tab 3: Làm bài Quiz trắc nghiệm & Chấm điểm tức thì                |
|  - Tab 4: Tải xuống bản ghi chép học tập (.md, .txt)                  |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|                   TẦNG XỬ LÝ LOGIC (PYTHON MODULES)                  |
|  - text_processor.py : Regex clean, trích xuất file, thống kê số từ   |
|  - export_service.py : Định dạng Markdown & Plain Text tải về         |
|  - mock_data.py      : Dữ liệu mẫu ngoại tuyến dự phòng rủi ro        |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|                   TẦNG AI (GOOGLE GEMINI 2.5 FLASH)                   |
|  - gemini_service.py : Prompt Engineering tối ưu & Bắt ngoại lệ       |
|  - Thư viện: google-genai SDK (Độ trễ thấp, chi phí miễn phí)         |
+-----------------------------------------------------------------------+
```

---

## 🚀 3. Hướng dẫn Cài đặt & Chạy Ứng dụng

### Yêu cầu hệ thống:
- Python 3.10 trở lên.
- Đã cài đặt `git` (để quản lý phiên bản).

### Các bước thực hiện:

1. **Clone repository về máy:**
   ```bash
   git clone https://github.com/your-username/smart-study-copilot.git
   cd smart-study-copilot
   ```

2. **Tạo và kích hoạt môi trường ảo (Khuyến nghị):**
   ```bash
   # Trên Windows:
   python -m venv venv
   .\venv\Scripts\activate

   # Trên Linux/macOS:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Cài đặt các gói phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình API Key:**
   - Tạo file `.env` từ file mẫu:
     ```bash
     copy .env.example .env   # Trên Windows
     cp .env.example .env     # Trên Linux/macOS
     ```
   - Mở file `.env` và điền API key miễn phí lấy từ [Google AI Studio](https://aistudio.google.com/app/apikey):
     ```env
     GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
     GEMINI_MODEL=gemini-2.5-flash
     ```
   *(Lưu ý: Nếu không có API Key hoặc gặp lỗi mạng, bạn chỉ cần gạt nút **"Chế độ Demo Ngoại tuyến"** ở sidebar để sử dụng Mock Data chuẩn).*

5. **Khởi chạy ứng dụng Web Streamlit:**
   ```bash
   streamlit run app.py
   ```
   Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`.

---

## 👥 4. Chiến lược Phân nhánh Git & Quy trình Làm việc Nhóm

### Sơ đồ Nhánh (Git Branching Flow):
```
main (v0.1) ───────────●──────────────────● (v1.0) ───────────────● (v2.0) ───────────────● (v3.0 - Final)
                        \                /                 /               /
dev                      ●──────●───────●                 ●───────●───────●
                                 \     /                           \     /
feature branches                  ●───● (feat/ui)                   ●───● (feat/gemini-quiz)
```

### Phân chia công việc giữa 2 thành viên:
| Thành viên | Vai trò | Nhiệm vụ chính |
|---|---|---|
| **Thành viên 1** (Lead / Backend-AI) | AI Engineer & Backend | Thiết lập kết nối Gemini API, Prompt Engineering, Xử lý ngoại lệ, Chế độ Mock Data, Viết báo cáo kỹ thuật |
| **Thành viên 2** (Frontend / Product) | UI/UX & Data Processing | Thiết kế giao diện Streamlit (Tabs, Metrics, Radio Form), Xử lý trích xuất file (.docx/.txt), Xuất Markdown, Dựng kịch bản Video |

### Lịch sử Commit minh chứng (Commit Log Chuẩn Conventional Commits):

#### Tuần 1: Khởi tạo nền tảng & Sprint 1
- `chore: initial repository structure and dependencies (streamlit, google-genai)`
- `feat: build base streamlit UI layout with text input area`
- `test: verify gemini api response on sample prompt`

#### Tuần 2: Tích hợp AI, Quiz & Sprint 2
- `feat: integrate gemini api for text summarization module`
- `feat: implement interactive quiz generator with radio buttons and scoring`
- `fix: handle empty input exception and api rate limit error`
- `docs: draft technical project report structure and system architecture diagram`

#### Tuần 3: Tối ưu hóa, Xuất file & Sprint 3 (Final Release)
- `feat: add markdown export feature for summary and quiz notes`
- `refactor: clean up code modularity and add inline comments`
- `release: tag version v3.0-final-release`

---

## 🎬 5. Kịch bản Video Demo YouTube (Thời lượng: 5 phút 30 giây)

| Mốc thời gian | Phân cảnh | Nội dung thuyết minh & Hành động |
|---|---|---|
| **0:00 - 0:45** | Mở đầu & Đặt vấn đề | - Giới thiệu 2 thành viên nhóm.<br>- Trình bày vấn đề: Sinh viên mất quá nhiều thời gian đọc slide dài và thiếu công cụ trắc nghiệm tương tác nhanh để ôn thi.<br>- Giới thiệu giải pháp Smart Study Copilot. |
| **0:45 - 2:45** | Demo sản phẩm trực tiếp (Live Demo) | - Bấm nút **"Nạp bài mẫu"** (Tiến trình & Tiểu trình trong Hệ điều hành).<br>- Giới thiệu các chỉ số thống kê (Word count, Reading time).<br>- Sang Tab 2: Bấm **"Tạo Tóm Tắt với Gemini AI"** -> Trình chiếu dàn ý phân tầng và bảng thuật ngữ chuẩn xác.<br>- Sang Tab 3: Bấm **"Sinh Bộ Trắc Nghiệm"** -> Làm trực tiếp 4 câu (cố tình làm 1 câu sai để phô diễn cơ chế chấm điểm và hiển thị lời giải thích màu đỏ/xanh).<br>- Sang Tab 4: Bấm **"Tải về định dạng Markdown"** để xem file ghi chú xuất ra hoàn chỉnh. |
| **2:45 - 3:45** | Cấu trúc Kỹ thuật & Prompt Engineering | - Mở slide/sơ đồ khối: Trình bày luồng `Streamlit ↔ Backend Logic ↔ Gemini 2.5 Flash`.<br>- Phân tích Prompt Engineering: Ép kiểu dữ liệu trả về mảng JSON chặt chẽ, hạ nhiệt độ `temperature` xuống `0.3 - 0.4` để triệt tiêu Hallucination (ảo giác AI). |
| **3:45 - 4:45** | Minh chứng Làm việc nhóm trên GitHub | - Mở giao diện GitHub của nhóm: Cho xem **Network Graph** hiển thị nhánh `main`, `dev`, `feat/ui`, `feat/gemini-quiz`.<br>- Xem danh sách Commit phân bổ đồng đều qua 3 tuần của 2 thành viên.<br>- Cho xem các Pull Request được review và Merge cẩn thận. |
| **4:45 - 5:30** | Tổng kết & Bài học kinh nghiệm | - Đánh giá ưu điểm ứng dụng (nhẹ, nhanh, miễn phí).<br>- Thừa nhận giới hạn (chưa hỗ trợ OCR ảnh, lưu trữ cloud dài hạn) và định hướng v4.0.<br>- Lời cảm ơn thầy cô và hội đồng. |

---

## 🛡️ 6. Rủi ro Tiềm ẩn & Giải pháp Khắc phục

1. **Rủi ro lộ khóa bí mật (API Key) trên GitHub:**
   - *Giải pháp:* Đưa khóa vào file `.env`, dùng `python-dotenv` hoặc `st.secrets`. Thêm `.env` vào `.gitignore` ngay từ commit đầu tiên. Không bao giờ hard-code chuỗi khóa trong code.
2. **Rủi ro API không ổn định hoặc mất mạng trong lúc bảo vệ trực tiếp:**
   - *Giải pháp:* Bọc toàn bộ các hàm gọi API trong khối `try...except`. Tích hợp chế độ **Offline Mock Data** (dữ liệu mẫu chất lượng cao có sẵn) tự động kích hoạt khi có sự cố hoặc qua nút gạt tại Sidebar.
3. **Rủi ro sa đà vào giao diện khiến trễ hạn tính năng:**
   - *Giải pháp:* Sử dụng 100% component dựng sẵn của thư viện Streamlit (Tabs, Columns, Metric cards, Radio form), tập trung tối đa nguồn lực vào luồng dữ liệu logic cốt lõi.

---

## 📄 7. Giấy phép
Dự án được phân phối dưới giấy phép **MIT License**.
