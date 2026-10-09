"""
Smart Study Copilot - Trợ lý tóm tắt tài liệu học tập và tự động tạo bài kiểm tra trắc nghiệm
Tích hợp Google Gemini API & Streamlit
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Nạp biến môi trường từ .env nếu có
load_dotenv()

from modules.text_processor import clean_text, extract_text_from_file, get_text_statistics
from modules.gemini_service import generate_summary, generate_quiz
from modules.export_service import generate_markdown_export, generate_text_export
from modules.mock_data import MOCK_SUMMARY, MOCK_QUIZ

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Smart Study Copilot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Khởi tạo Session State để lưu trữ dữ liệu qua các lần tương tác
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""
if "cleaned_text" not in st.session_state:
    st.session_state.cleaned_text = ""
if "stats" not in st.session_state:
    st.session_state.stats = {}
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "summary_is_mock" not in st.session_state:
    st.session_state.summary_is_mock = False
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_is_mock" not in st.session_state:
    st.session_state.quiz_is_mock = False
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "score_info" not in st.session_state:
    st.session_state.score_info = {"correct": 0, "total": 0, "submitted": False}
if "history" not in st.session_state:
    st.session_state.history = []

# Đọc file mẫu sẵn có
def load_sample_lesson():
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_lesson.txt")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 3. Sidebar: Cấu hình kết nối & Công cụ điều khiển
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/graduation-cap.png", width=90)
    st.title("Smart Study Copilot")
    st.caption("🚀 Trợ lý học tập thông minh với Gemini 3.8 Flash")
    
    st.divider()
    st.subheader("⚙️ Cấu hình AI & API")
    
    # Ưu tiên lấy API key từ biến môi trường hoặc st.secrets nếu có
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    try:
        if not env_api_key and "GEMINI_API_KEY" in st.secrets:
            env_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    api_key_input = st.text_input(
        "Google Gemini API Key:",
        value=env_api_key,
        type="password",
        help="Nhập API Key từ Google AI Studio (https://aistudio.google.com/app/apikey). Khóa không bao giờ bị lưu trên GitHub."
    )
    
    selected_model = st.selectbox(
        "Mô hình Gemini:",
        ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Khuyến nghị gemini-3.8-flash hoặc 3.8-flash-lite: tốc độ cao, ổn định."
    )
    
    demo_mode = st.toggle(
        "🛡️ Chế độ Demo Ngoại tuyến (Mock Data)",
        value=False,
        help="Bật chế độ này khi trình bày demo mà không cần kết nối mạng hoặc khi hết hạn ngạch API."
    )
    
    st.divider()
    st.subheader("💡 Dữ liệu mẫu kiểm thử")
    if st.button("📥 Nạp bài mẫu: Tiến trình & Tiểu trình", use_container_width=True):
        sample_content = load_sample_lesson()
        if sample_content:
            st.session_state.raw_text = sample_content
            st.session_state.cleaned_text = clean_text(sample_content)
            st.session_state.stats = get_text_statistics(st.session_state.cleaned_text)
            st.success("Đã nạp bài học mẫu thành công!")
            st.rerun()

    st.divider()
    st.subheader("📌 Trạng thái phiên làm việc")
    if st.session_state.stats:
        st.write(f"📝 Số từ: **{st.session_state.stats.get('word_count', 0)}**")
        st.write(f"📑 Tóm tắt: {'✅ Sẵn sàng' if st.session_state.summary else '⏳ Chưa tạo'}")
        st.write(f"🎯 Quiz: {'✅ Đã tạo' if st.session_state.quiz_data else '⏳ Chưa tạo'}")
        if st.session_state.quiz_submitted:
            st.write(f"🏆 Điểm thi: **{st.session_state.score_info.get('correct', 0)}/{st.session_state.score_info.get('total', 0)}**")
            
    if st.button("🗑️ Đặt lại phiên học tập", type="secondary", use_container_width=True):
        st.session_state.raw_text = ""
        st.session_state.cleaned_text = ""
        st.session_state.stats = {}
        st.session_state.summary = ""
        st.session_state.quiz_data = []
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.score_info = {"correct": 0, "total": 0, "submitted": False}
        st.rerun()

# 4. Giao diện chính: 4 Tabs chức năng cốt lõi
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 1. Tiền xử lý & Nạp bài học",
    "📑 2. Tóm tắt thông minh",
    "🎯 3. Quiz trắc nghiệm tương tác",
    "💾 4. Quản lý phiên & Xuất dữ liệu"
])

# ----------------- TAB 1: NẠP VÀ TIỀN XỬ LÝ DỮ LIỆU -----------------
with tab1:
    st.header("1. Tiền xử lý và nạp dữ liệu văn bản")
    st.markdown("Chọn một trong hai phương thức: **Dán trực tiếp văn bản** hoặc **Tải lên tệp tài liệu (.txt, .docx)**.")
    
    col_input1, col_input2 = st.columns([1, 1])
    
    with col_input1:
        st.subheader("Cách 1: Tải tệp văn bản thô")
        uploaded_file = st.file_uploader(
            "Chọn tệp tài liệu học tập (.txt, .docx):",
            type=["txt", "docx"],
            help="Hệ thống tự động trích xuất và lọc bỏ ký tự thừa."
        )
        if uploaded_file is not None:
            extracted_text, err = extract_text_from_file(uploaded_file)
            if err:
                st.error(err)
            else:
                st.session_state.raw_text = extracted_text
                st.session_state.cleaned_text = clean_text(extracted_text)
                st.session_state.stats = get_text_statistics(st.session_state.cleaned_text)
                st.success(f"Đã trích xuất tệp '{uploaded_file.name}' thành công!")

    with col_input2:
        st.subheader("Cách 2: Dán nội dung trực tiếp")
        text_input = st.text_area(
            "Nhập hoặc dán nội dung bài học vào đây:",
            value=st.session_state.raw_text,
            height=200,
            placeholder="Dán bài học hoặc ghi chú bài giảng cần tóm tắt..."
        )
        if st.button("🔍 Xử lý & Phân tích văn bản", type="primary", use_container_width=True):
            if text_input.strip():
                st.session_state.raw_text = text_input
                st.session_state.cleaned_text = clean_text(text_input)
                st.session_state.stats = get_text_statistics(st.session_state.cleaned_text)
                st.success("Đã hoàn tất tiền xử lý và lọc ký tự thừa!")
            else:
                st.warning("Vui lòng nhập văn bản hoặc tải tệp lên trước khi xử lý.")

    # Hiển thị chỉ số thống kê
    if st.session_state.cleaned_text:
        st.divider()
        st.subheader("📊 Kết quả phân tích & Thống kê tài liệu")
        stats = st.session_state.stats
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Tổng số từ", f"{stats.get('word_count', 0):,} từ")
        m_col2.metric("Số ký tự", f"{stats.get('char_count', 0):,} ký tự")
        m_col3.metric("Số đoạn văn", f"{stats.get('paragraph_count', 0)} đoạn")
        m_col4.metric("Thời gian đọc ước tính", f"~{stats.get('reading_time_minutes', 0)} phút")
        
        with st.expander("👁️ Xem văn bản sau khi làm sạch"):
            st.text_area("Nội dung đã lọc:", value=st.session_state.cleaned_text, height=200, disabled=True)
            
        if stats.get("word_count", 0) < 30:
            st.warning("⚠️ Tài liệu hiện tại khá ngắn (< 30 từ). AI có thể tóm tắt và sinh câu hỏi chưa tối ưu.")
        else:
            st.info("👉 Tài liệu đã sẵn sàng! Chuyển sang **Tab 2 (Tóm tắt thông minh)** hoặc **Tab 3 (Quiz trắc nghiệm)** để tiếp tục.")

# ----------------- TAB 2: TÓM TẮT THÔNG MINH -----------------
with tab2:
    st.header("2. Tóm tắt thông minh theo cấu trúc phân tầng")
    st.markdown("Hệ thống tận dụng **Gemini API** để phân tích tài liệu thành dàn ý phân tầng kèm bảng tra cứu thuật ngữ chuyên ngành.")
    
    if not st.session_state.cleaned_text:
        st.warning("⚠️ Vui lòng nạp và làm sạch nội dung bài học ở **Tab 1** trước.")
    else:
        col_act, col_info = st.columns([1, 2])
        with col_act:
            btn_summarize = st.button("⚡ Tạo Tóm Tắt với Gemini AI", type="primary", use_container_width=True)
            
        with col_info:
            if demo_mode:
                st.info("🛡️ Đang bật Chế độ Demo Ngoại tuyến. Kết quả sẽ được tải từ Mock Data.")
            elif not api_key_input:
                st.info("ℹ️ Chưa có API Key. Bấm nút để trải nghiệm qua Mock Data hoặc nhập Key tại Sidebar.")
                
        if btn_summarize:
            with st.spinner("Đang kích hoạt Gemini 2.5 Flash để phân tích cấu trúc bài học..."):
                summary_res, is_mock, notice = generate_summary(
                    text=st.session_state.cleaned_text,
                    api_key=api_key_input,
                    force_mock=demo_mode,
                    custom_model=selected_model
                )
                st.session_state.summary = summary_res
                st.session_state.summary_is_mock = is_mock
                if notice:
                    st.info(notice)
                    
        if st.session_state.summary:
            st.divider()
            if st.session_state.summary_is_mock:
                st.caption("🏷️ Nguồn dữ liệu: **Offline Mock Data (Phục vụ Demo An Toàn)**")
            else:
                st.caption(f"🏷️ Nguồn dữ liệu: **Trực tiếp từ {selected_model}**")
                
            st.markdown(st.session_state.summary)

# ----------------- TAB 3: QUIZ TRẮC NGHIỆM TƯƠNG TÁC -----------------
with tab3:
    st.header("3. Tự động sinh Quiz trắc nghiệm tương tác")
    st.markdown("Hệ thống sinh bộ câu hỏi 4 lựa chọn (A, B, C, D), cho phép làm bài trực tiếp và nhận giải thích chi tiết.")
    
    if not st.session_state.cleaned_text:
        st.warning("⚠️ Vui lòng nạp nội dung bài học ở **Tab 1** trước.")
    else:
        has_summary = bool(st.session_state.summary)
        q_col1, q_col2, q_col3 = st.columns([1, 1, 1])
        with q_col1:
            num_q = st.slider("Số lượng câu hỏi:", min_value=3, max_value=5, value=4)
        with q_col2:
            quiz_source_options = ["Bản tóm tắt (Nhanh, nhẹ, ít quá tải)", "Văn bản gốc đầy đủ"] if has_summary else ["Văn bản gốc đầy đủ"]
            selected_source = st.selectbox(
                "Nguồn dữ liệu tạo Quiz:",
                quiz_source_options,
                index=0,
                help="Tạo từ bản tóm tắt giúp giảm 80% dung lượng gửi lên Google, tránh lỗi quá tải 503."
            )
        with q_col3:
            st.write("")
            btn_gen_quiz = st.button("🎲 Sinh Bộ Trắc Nghiệm Mới", type="primary", use_container_width=True)
            
        if btn_gen_quiz:
            # Chọn nguồn văn bản tối ưu: Tóm tắt (nếu chọn) hoặc Văn bản gốc
            input_content = st.session_state.summary if ("Bản tóm tắt" in selected_source and has_summary) else st.session_state.cleaned_text
            with st.spinner("AI đang biên soạn câu hỏi trắc nghiệm (vui lòng đợi 3-5 giây)..."):
                quiz_res, is_mock, notice = generate_quiz(
                    text=input_content,
                    num_questions=num_q,
                    api_key=api_key_input,
                    force_mock=demo_mode,
                    custom_model=selected_model
                )
                st.session_state.quiz_data = quiz_res
                st.session_state.quiz_is_mock = is_mock
                st.session_state.user_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.score_info = {"correct": 0, "total": 0, "submitted": False}
                if notice:
                    st.info(notice)
                    
        if st.session_state.quiz_data:
            st.divider()
            if st.session_state.quiz_is_mock:
                st.caption("🏷️ Bộ câu hỏi: **Offline Mock Data (Demo Mode)**")
            else:
                st.caption(f"🏷️ Bộ câu hỏi: **Sinh tự động bởi {selected_model}**")
                
            st.subheader(f"📝 Bài kiểm tra nhanh ({len(st.session_state.quiz_data)} câu hỏi)")
            
            # Form làm bài kiểm tra
            with st.form("quiz_form"):
                for idx, q in enumerate(st.session_state.quiz_data, 1):
                    q_id = q.get("id", idx)
                    st.markdown(f"**Câu {idx}: {q.get('question')}**")
                    
                    options = q.get("options", {})
                    # Định dạng hiển thị: "A. Nội dung..."
                    formatted_options = [f"{k}. {v}" for k, v in options.items()]
                    
                    # Tìm index phương án đã chọn trước đó (nếu có)
                    curr_choice = st.session_state.user_answers.get(q_id, None)
                    default_idx = None
                    if curr_choice:
                        for opt_i, opt_text in enumerate(formatted_options):
                            if opt_text.startswith(f"{curr_choice}."):
                                default_idx = opt_i
                                break
                                
                    selected = st.radio(
                        label=f"Chọn đáp án cho câu {idx}:",
                        options=formatted_options,
                        index=default_idx,
                        key=f"q_radio_{q_id}",
                        label_visibility="collapsed"
                    )
                    
                    # Lưu lại đáp án được chọn (lấy chữ cái A, B, C, D)
                    if selected:
                        st.session_state.user_answers[q_id] = selected[0]
                        
                    st.write("") # Dòng trống phân cách
                    
                submitted = st.form_submit_button("🏁 Nộp Bài & Chấm Điểm Ngay", type="primary", use_container_width=True)
                
            if submitted:
                # Tính điểm
                total = len(st.session_state.quiz_data)
                correct = 0
                for q in st.session_state.quiz_data:
                    q_id = q.get("id")
                    user_ans = st.session_state.user_answers.get(q_id)
                    correct_ans = q.get("correct_answer")
                    if user_ans and user_ans == correct_ans:
                        correct += 1
                        
                st.session_state.quiz_submitted = True
                st.session_state.score_info = {
                    "correct": correct,
                    "total": total,
                    "submitted": True
                }
                
            # Hiển thị kết quả và giải thích chi tiết khi đã nộp bài
            if st.session_state.quiz_submitted:
                st.divider()
                s_info = st.session_state.score_info
                pct = (s_info['correct'] / s_info['total'] * 100) if s_info['total'] > 0 else 0
                
                # Banner điểm số
                if pct == 100:
                    st.balloons()
                    st.success(f"🎉 **Xuất sắc!** Bạn đạt **{s_info['correct']}/{s_info['total']}** điểm ({pct:.0f}%). Bạn đã nắm trọn vẹn kiến thức!")
                elif pct >= 75:
                    st.info(f"👏 **Kết quả tốt!** Bạn đạt **{s_info['correct']}/{s_info['total']}** điểm ({pct:.0f}%). Hãy ôn lại một vài ý chưa chắc nhé.")
                else:
                    st.warning(f"💪 **Cố gắng hơn nhé!** Bạn đạt **{s_info['correct']}/{s_info['total']}** điểm ({pct:.0f}%). Hãy đọc lại tóm tắt ở Tab 2 nhé.")
                    
                st.subheader("🔍 Đánh giá và Lời giải chi tiết từng câu:")
                for idx, q in enumerate(st.session_state.quiz_data, 1):
                    q_id = q.get("id", idx)
                    user_ans = st.session_state.user_answers.get(q_id, "Chưa chọn")
                    corr_ans = q.get("correct_answer")
                    is_correct = (user_ans == corr_ans)
                    
                    with st.expander(
                        f"Câu {idx}: {'✅ Đúng' if is_correct else '❌ Sai'} (Bạn chọn: {user_ans} | Đáp án: {corr_ans})",
                        expanded=True
                    ):
                        st.write(f"**Nội dung câu hỏi:** {q.get('question')}")
                        for opt_k, opt_v in q.get('options', {}).items():
                            if opt_k == corr_ans:
                                st.markdown(f"- 🌟 **{opt_k}. {opt_v}** *(Đáp án chính xác)*")
                            elif opt_k == user_ans:
                                st.markdown(f"- ❌ **{opt_k}. {opt_v}** *(Bạn đã chọn phương án này)*")
                            else:
                                st.markdown(f"- {opt_k}. {opt_v}")
                                
                        st.info(f"💡 **Lời giải chi tiết:** {q.get('explanation')}")

# ----------------- TAB 4: QUẢN LÝ PHIÊN & XUẤT DỮ LIỆU -----------------
with tab4:
    st.header("4. Quản lý phiên học tập & Xuất dữ liệu")
    st.markdown("Lưu trữ tạm thời lịch sử bài học và điểm số trong phiên làm việc (`Session State`). Xuất tóm tắt và bộ trắc nghiệm ra file cá nhân.")
    
    col_exp1, col_exp2 = st.columns([1, 1])
    
    # Chuẩn bị nội dung xuất file
    md_content = generate_markdown_export(
        summary=st.session_state.summary,
        quiz_data=st.session_state.quiz_data,
        user_answers=st.session_state.user_answers,
        score_info=st.session_state.score_info,
        stats=st.session_state.stats
    )
    
    txt_content = generate_text_export(
        summary=st.session_state.summary,
        quiz_data=st.session_state.quiz_data,
        user_answers=st.session_state.user_answers,
        score_info=st.session_state.score_info,
        stats=st.session_state.stats
    )
    
    with col_exp1:
        st.subheader("📥 Tải bản ghi chép cá nhân")
        st.download_button(
            label="📄 Tải về định dạng Markdown (.md)",
            data=md_content,
            file_name="Smart_Study_Copilot_Notes.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.download_button(
            label="📝 Tải về định dạng Plain Text (.txt)",
            data=txt_content,
            file_name="Smart_Study_Copilot_Notes.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with col_exp2:
        st.subheader("📊 Tóm tắt phiên hiện tại")
        st.write(f"- **Văn bản nạp:** {'Có' if st.session_state.cleaned_text else 'Chưa có'}")
        st.write(f"- **Tóm tắt bài học:** {'Có' if st.session_state.summary else 'Chưa có'}")
        st.write(f"- **Bộ câu hỏi trắc nghiệm:** {len(st.session_state.quiz_data)} câu")
        st.write(f"- **Trạng thái làm bài:** {'Đã chấm điểm' if st.session_state.quiz_submitted else 'Chưa nộp bài'}")
        if st.session_state.quiz_submitted:
            s = st.session_state.score_info
            st.write(f"- **Điểm số:** {s['correct']}/{s['total']} ({s['correct']/s['total']*100:.1f}%)")

    st.divider()
    st.subheader("👁️ Bản xem trước trước khi xuất (Preview)")
    with st.expander("Bản xem trước tài liệu xuất ra:", expanded=False):
        st.code(md_content, language="markdown")
