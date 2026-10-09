"""
Module: mock_data.py
Chức năng: Cung cấp dữ liệu mẫu ngoại tuyến (Offline Mock Data) cho kịch bản demo phòng thi/bảo vệ,
tránh rủi ro mất mạng hoặc nghẽn quota Gemini API.
"""

MOCK_SUMMARY = """# 📌 DÀN Ý TÓM TẮT BÀI HỌC: TIẾN TRÌNH & TIỂU TRÌNH (OS)

### 1. Tổng quan về Tiến trình (Process)
- **Định nghĩa**: Một chương trình đang được nạp vào RAM và thực thi bởi CPU.
- **Không gian bộ nhớ độc lập**: Mỗi tiến trình sở hữu không gian địa chỉ ảo riêng biệt (Code, Data, Stack, Heap), giúp cô lập lỗi và tăng tính ổn định cho toàn hệ điều hành.
- **Cấu trúc quản lý PCB**: Hệ điều hành điều phối tiến trình thông qua Khối điều khiển tiến trình (PID, trạng thái New/Ready/Running/Waiting/Terminated, con trỏ lệnh, thanh ghi CPU).

### 2. Tiểu trình (Thread) & Đa luồng (Multithreading)
- **Bản chất**: Là đơn vị xử lý nhỏ nhất của CPU, nằm bên trong tiến trình.
- **Cơ chế chia sẻ tài nguyên**: Các tiểu trình cùng một tiến trình dùng chung mã nguồn, dữ liệu toàn cục, heap và file mở, nhưng độc lập về Stack và thanh ghi.
- **Ưu thế vượt trội**: Chuyển đổi ngữ cảnh (Context Switch) giữa các thread nhẹ hơn nhiều so với giữa các tiến trình; tận dụng tối đa CPU đa nhân để chạy song song.

### 3. Đồng bộ hóa và Tranh chấp tài nguyên
- **Race Condition**: Xảy ra khi nhiều luồng truy cập/sửa đổi dữ liệu dùng chung cùng lúc mà không kiểm soát.
- **Giải pháp**: Ứng dụng Khóa độc quyền (Mutex), Đèn báo (Semaphore) và Vùng găng (Critical Section).

---

### 📖 THUẬT NGỮ CHUYÊN NGÀNH CỐT LÕI
1. **Context Switch (Chuyển đổi ngữ cảnh)**: Quá trình lưu trạng thái của CPU cho một tiến trình/luồng cũ và tải trạng thái của tiến trình/luồng mới để thực thi.
2. **PCB (Process Control Block)**: Bảng dữ liệu lưu toàn bộ thông tin nhận dạng và trạng thái thực thi của một tiến trình.
3. **Race Condition (Tình trạng tranh chấp)**: Tình huống lỗi khi kết quả tính toán phụ thuộc vào thứ tự thực thi không thể đoán trước của các tiến trình/luồng.
4. **Critical Section (Đoạn găng)**: Đoạn mã truy cập tài nguyên chia sẻ, đòi hỏi tại một thời điểm chỉ có tối đa một tiến trình/luồng được phép thực thi.
"""

MOCK_QUIZ = [
    {
        "id": 1,
        "question": "Thành phần nào sau đây ĐƯỢC CHIA SẺ giữa các tiểu trình (Thread) thuộc cùng một tiến trình?",
        "options": {
            "A": "Vùng nhớ Ngăn xếp (Stack)",
            "B": "Tập thanh ghi CPU (CPU Registers)",
            "C": "Vùng nhớ Heap và Không gian địa chỉ",
            "D": "Process ID (PID) riêng biệt cho từng luồng"
        },
        "correct_answer": "C",
        "explanation": "Các tiểu trình trong cùng một tiến trình chia sẻ chung không gian địa chỉ, vùng nhớ code, data, heap và tài nguyên hệ thống, nhưng mỗi tiểu trình có Stack và tập thanh ghi riêng."
    },
    {
        "id": 2,
        "question": "Tại sao việc chuyển đổi ngữ cảnh (Context Switch) giữa các Thread lại nhanh và nhẹ hơn giữa các Process?",
        "options": {
            "A": "Vì Thread không cần thực thi mã lệnh của CPU",
            "B": "Vì các Thread chia sẻ chung không gian địa chỉ, không cần tráo đổi bảng phân trang bộ nhớ ảo (Page Tables)",
            "C": "Vì Thread luôn có độ ưu tiên cao hơn mọi Process trong hàng đợi CPU",
            "D": "Vì Thread không lưu trữ thông tin con trỏ lệnh Program Counter"
        },
        "correct_answer": "B",
        "explanation": "Context switch giữa các thread không cần hoán đổi bảng trang bộ nhớ ảo hay xả bộ nhớ đệm TLB như khi chuyển đổi giữa các tiến trình độc lập, do đó chi phí tài nguyên thấp hơn đáng kể."
    },
    {
        "id": 3,
        "question": "Cấu trúc dữ liệu nào được Hệ điều hành sử dụng để lưu trữ toàn bộ thông tin trạng thái, thanh ghi và tài nguyên của một tiến trình?",
        "options": {
            "A": "Thread Control Block (TCB)",
            "B": "Process Control Block (PCB)",
            "C": "Virtual Memory Manager (VMM)",
            "D": "Input/Output Descriptor Table"
        },
        "correct_answer": "B",
        "explanation": "Process Control Block (PCB) là cấu trúc dữ liệu cốt lõi lưu PID, trạng thái tiến trình (Ready, Running,...), con trỏ lệnh và thông tin cấp phát tài nguyên."
    },
    {
        "id": 4,
        "question": "Tình trạng 'Race Condition' (tranh chấp dữ liệu) trong lập trình đa luồng xảy ra trong điều kiện nào?",
        "options": {
            "A": "Khi hai luồng chạy trên hai máy tính khác nhau qua mạng LAN",
            "B": "Khi CPU bị quá nhiệt và tự động giảm xung nhịp",
            "C": "Khi nhiều luồng cùng thao tác trên dữ liệu dùng chung mà không có cơ chế đồng bộ hóa phù hợp",
            "D": "Khi tiến trình bị hệ điều hành cưỡng chế kết thúc (Terminated)"
        },
        "correct_answer": "C",
        "explanation": "Race Condition xảy ra khi nhiều luồng cùng truy cập và thay đổi biến/vùng nhớ chia sẻ mà không có cơ chế đồng bộ (như Mutex/Semaphore), dẫn đến kết quả sai lệch."
    }
]
