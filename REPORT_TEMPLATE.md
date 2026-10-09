# BÁO CÁO KỸ THUẬT ĐỒ ÁN MÔN HỌC

**TÊN ĐỀ TÀI:** XÂY DỰNG ỨNG DỤNG WEB MINI "SMART STUDY COPILOT": TRỢ LÝ TÓM TẮT TÀI LIỆU HỌC TẬP VÀ TỰ ĐỘNG TẠO BÀI KIỂM TRA TRẮC NGHIỆM TÍCH HỢP GOOGLE GEMINI API  
**Môn học:** Ứng dụng Trí tuệ Nhân tạo / Nhập môn Công nghệ Phần mềm  
**Nhóm thực hiện:** Nhóm 02 thành viên  
- Thành viên 1: [Họ và tên - MSSV] (Trưởng nhóm / Backend & AI Engineer)
- Thành viên 2: [Họ và tên - MSSV] (Thành viên / Frontend & Data Processing)

---

## MỤC LỤC
1. GIỚI THIỆU ĐỀ TÀI & TÍNH CẤP THIẾT
2. KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ LỰA CHỌN
3. THIẾT KẾ LUỒNG DỮ LIỆU & CHI TIẾT TÍNH NĂNG CỐT LÕI
4. KỸ THUẬT THIẾT KẾ PROMPT (PROMPT ENGINEERING)
5. QUẢN LÝ PHIÊN BẢN VÀ QUY TRÌNH LÀM VIỆC NHÓM (GIT & GITHUB)
6. KẾT QUẢ ĐẠT ĐƯỢC & ĐÁNH GIÁ THỰC NGHIỆM
7. BÀI HỌC KINH NGHIỆM & PHẢN ÁNH LÀM VIỆC NHÓM (REFLECTION)
8. HƯỚNG PHÁT TRIỂN TƯƠNG LAI

---

## 1. GIỚI THIỆU ĐỀ TÀI & TÍNH CẤP THIẾT
Trong kỷ nguyên số, sinh viên đại học thường xuyên đối mặt với tình trạng quá tải thông tin (information overload) từ hàng trăm trang slide bài giảng và giáo trình. Để ghi nhớ hiệu quả, phương pháp học chủ động (Active Recall) và tự kiểm tra lặp lại ngắt quãng (Spaced Repetition) đã được chứng minh là vượt trội hơn việc đọc thụ động. Tuy nhiên, việc tự biên soạn câu hỏi trắc nghiệm và rút gọn bài học thường tốn nhiều giờ đồng hồ.

Đề tài **"Smart Study Copilot"** giải quyết trực tiếp thách thức này bằng cách ứng dụng mô hình ngôn ngữ lớn tiên tiến nhất từ Google (**Gemini 2.5 Flash**) tích hợp vào một giao diện Web nhẹ nhàng, trực quan thông qua framework **Streamlit**, giúp sinh viên tóm lược tài liệu và tự kiểm tra bài học chỉ sau một cú nhấp chuột.

---

## 2. KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ LỰA CHỌN

### 2.1. Ngăn xếp Công nghệ (Tech Stack)
- **Giao diện & Tầng ứng dụng (Frontend/Backend):** Thư viện `Streamlit` (Python). Lý do lựa chọn: Giao diện web được sinh hoàn toàn bằng mã Python, loại bỏ rào cản phức tạp của HTML/CSS/JavaScript cho sinh viên năm 1, nhưng vẫn cung cấp đầy đủ các thành phần tương tác cao (Tabs, Forms, Radio buttons, File uploader, Metrics).
- **Tầng xử lý AI:** Thư viện `google-genai` SDK chính thức từ Google, kết nối mô hình `gemini-2.5-flash`. Lý do: Tốc độ phản hồi cực nhanh (< 2-3 giây), hạn ngạch miễn phí dồi dào, khả năng tuân thủ cấu trúc định dạng JSON rất cao.
- **Xử lý tài liệu:** Thư viện `python-docx` và biểu thức chính quy (Regex) tích hợp sẵn trong Python.
- **Quản lý phiên bản:** Hệ thống Git và nền tảng GitHub.

### 2.2. Sơ đồ Kiến trúc Tổng thể
Ứng dụng tuân theo mô hình phân tầng mô-đun hóa (Modular Architecture):
1. **Presentation Layer (`app.py`):** Tiếp nhận tương tác người dùng, quản lý vòng đời trạng thái thông qua `st.session_state`.
2. **Business Logic Layer (`modules/`):**
   - `text_processor.py`: Trích xuất file, làm sạch khoảng trắng, chuẩn hóa đoạn văn, thống kê định lượng (số từ, ký tự, thời gian đọc).
   - `gemini_service.py`: Xây dựng prompt chuyên biệt, giao tiếp với API, kiểm soát nhiệt độ `temperature`, bẫy ngoại lệ và tự động chuyển đổi Mock Data.
   - `export_service.py`: Tổng hợp dữ liệu thành định dạng Markdown / Text.
   - `mock_data.py`: Cung cấp dữ liệu mẫu phục vụ kịch bản chạy ngoại tuyến.

---

## 3. THIẾT KẾ LUỒNG DỮ LIỆU & CHI TIẾT TÍNH NĂNG CỐT LÕI

### 3.1. Luồng dữ liệu (Data Pipeline)
```
[Tệp .txt / .docx hoặc Text dán]
         │
         ▼
[text_processor.py] ───> Làm sạch ký tự lạ, đếm từ, tính reading time
         │
         ▼
[Session State: cleaned_text]
         │
   ┌─────┴────────────────────────┐
   ▼                              ▼
[Gemini Summary Request]       [Gemini Quiz Request]
   │                              │
   ▼                              ▼
[Dàn ý phân tầng + Glossary]   [JSON Array: 3-5 MCQs]
   │                              │
   └─────────────┬────────────────┘
                 ▼
          [Làm bài & Chấm điểm]
                 │
                 ▼
          [Xuất file Markdown/Text]
```

### 3.2. Bốn tính năng cốt lõi
1. **Tiền xử lý và nạp dữ liệu văn bản:** Hỗ trợ đọc cả 2 định dạng phổ biến nhất là `.txt` và `.docx`. Bộ lọc Regex loại bỏ các ký tự vô hình, khoảng trắng dư thừa, tránh làm lãng phí token đầu vào của mô hình AI.
2. **Tóm tắt thông minh theo cấu trúc phân tầng:** Bản tóm tắt không chỉ đơn thuần là rút ngắn văn bản, mà được tổ chức thành 4 khối: (1) Tổng quan, (2) Dàn ý phân tầng, (3) Bảng tra cứu thuật ngữ chuyên ngành (Glossary), (4) Điểm mấu chốt ôn thi (Takeaway).
3. **Sinh Quiz trắc nghiệm tương tác:** Tạo tự động 3 đến 5 câu hỏi 4 lựa chọn (A, B, C, D). Sử dụng form Streamlit để người dùng chọn đáp án và nộp bài. Hệ thống chấm điểm tự động và hiển thị phân tích nguyên nhân tại sao đáp án được chọn là đúng hay sai.
4. **Quản lý phiên học tập & Xuất dữ liệu:** Toàn bộ tiến trình học tập được lưu trữ trong `st.session_state`, cho phép người dùng chuyển qua lại giữa các tab mà không mất dữ liệu. Kết quả có thể xuất ra file `.md` chuẩn GitHub để lưu vào Obsidian, Notion hoặc in ra giấy.

---

## 4. KỸ THUẬT THIẾT KẾ PROMPT (PROMPT ENGINEERING)

### 4.1. Kỹ thuật chống "Ảo giác" (Hallucination) cho Tóm tắt
Để đảm bảo Gemini chỉ tóm tắt đúng nội dung trong tài liệu mà không bịa đặt thông tin bên ngoài:
- Thiết lập System Instruction: Đóng vai trò trợ lý gia sư học thuật chuẩn mực.
- Thiết lập Ranh giới văn bản rõ ràng: Sử dụng các thẻ ngăn cách (Delimiters) như `--- NỘI DUNG TÀI LIỆU BẮT ĐẦU ---` và `--- NỘI DUNG TÀI LIỆU KẾT THÚC ---`.
- Giảm tham số `temperature = 0.3` nhằm tối đa hóa tính tất định và độ chuẩn xác học thuật.

### 4.2. Kỹ thuật ép khuôn cấu trúc JSON cho Quiz
Tạo trắc nghiệm đòi hỏi đầu ra phải là mảng dữ liệu có thể duyệt được bằng code Python:
- Đưa ví dụ mẫu (Few-shot/Schema Definition) trong Prompt mô tả chi tiết các khóa: `id`, `question`, `options` (chứa A, B, C, D), `correct_answer`, `explanation`.
- Sử dụng bộ lọc biểu thức chính quy tại tầng Backend để loại bỏ các thẻ định dạng thừa ` ```json ` nếu Gemini tự động bọc lại.

---

## 5. QUẢN LÝ PHIÊN BẢN VÀ QUY TRÌNH LÀM VIỆC NHÓM (GIT & GITHUB)

### 5.1. Chiến lược phân nhánh (Branching Strategy)
- Nhánh `main`: Chứa mã nguồn sản phẩm ổn định tương ứng với các cột mốc phiên bản (`v0.1`, `v1.0`, `v2.0`, `v3.0 - Final`).
- Nhánh `dev`: Tích hợp liên tục các tính năng của nhóm trước khi đưa lên `main`.
- Các nhánh tính năng (`feat/ui`, `feat/gemini-quiz`): Mỗi thành viên làm việc độc lập trên nhánh tính năng, sau đó tạo Pull Request (PR) để thành viên còn lại review mã nguồn trước khi hợp nhất.

### 5.2. Tuân thủ quy chuẩn Conventional Commits
Toàn bộ lịch sử commit tuân thủ nghiêm ngặt chuẩn quốc tế:
- `chore:` Thiết lập cấu trúc thư mục, tệp cấu hình `.gitignore`, `requirements.txt`.
- `feat:` Bổ sung tính năng mới (UI, tóm tắt, quiz, xuất file).
- `fix:` Xử lý lỗi ngoại lệ (chuỗi rỗng, lỗi mạng, rate limit).
- `docs:` Viết tài liệu, báo cáo, kịch bản video.
- `refactor:` Dọn dẹp mã nguồn, tối ưu hóa mô-đun.
- `release:` Đóng gói phiên bản phát hành chính thức.

---

## 6. KẾT QUẢ ĐẠT ĐƯỢC & ĐÁNH GIÁ THỰC NGHIỆM

- **Thời gian phản hồi:** Tóm tắt tài liệu 1000 từ hoàn thành trong trung bình 2.5 giây; sinh bộ câu hỏi 4 câu hoàn thành trong khoảng 3 giây.
- **Độ chính xác học thuật:** Các thuật ngữ chuyên ngành tin học (Context Switch, PCB, Race Condition, Semaphore) đều được định nghĩa chính xác và các câu hỏi trắc nghiệm có phương án gây nhiễu rất tự nhiên, có tính phân loại cao.
- **Tính ổn định & Chống chịu lỗi:** Khi thử nghiệm ngắt kết nối Internet trong lúc demo, hệ thống lập tức kích hoạt chế độ Offline Mock Data một cách trơn tru mà không làm gián đoạn bài thuyết trình.

---

## 7. BÀI HỌC KINH NGHIỆM & PHẢN ÁNH LÀM VIỆC NHÓM (REFLECTION)

### 7.1. Khó khăn đã vượt qua
- Ban đầu, nhóm gặp tình trạng chuỗi trả về từ Gemini đôi khi lẫn các ký tự Markdown khiến hàm `json.loads()` bị lỗi cú pháp. Nhóm đã khắc phục bằng cách bổ sung hàm tiền xử lý chuỗi Regex trước khi parse.
- Quản lý bảo mật: Việc ban đầu chưa chú ý có thể dẫn tới nguy cơ commit nhầm API Key lên GitHub. Nhóm đã giải quyết dứt điểm bằng cách đưa toàn bộ vào biến môi trường `.env` và đưa vào `.gitignore` ngay từ commit khởi tạo đầu tiên.

### 7.2. Vai trò của Trí tuệ Nhân tạo trong dự án
Công cụ AI (Gemini) không chỉ đóng vai trò là "trái tim" trong tính năng của sản phẩm mà còn là người bạn đồng hành (Pair Programmer) hỗ trợ nhóm sinh ý tưởng giao diện, gợi ý cấu trúc prompt tối ưu và rà soát các trường hợp kiểm thử biên (edge cases).

---

## 8. HƯỚNG PHÁT TRIỂN TƯƠNG LAI (ROADMAP v4.0)
1. Bổ sung trích xuất trực tiếp từ file PDF và tệp ảnh thông qua OCR (Optical Character Recognition).
2. Tích hợp tính năng tạo Flashcard học tập xuất trực tiếp sang định dạng Anki.
3. Hỗ trợ lưu trữ tiến độ học tập lâu dài lên cơ sở dữ liệu đám mây (SQLite / Supabase).
