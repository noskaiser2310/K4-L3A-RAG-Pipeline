"""
Ứng dụng Chatbot RAG — Hỏi đáp Dịch vụ & Quy chế Đào tạo, Học bổng Sinh viên VinUni.
Nhóm Dalab (K4-L3A) · Trưởng nhóm kỹ thuật: Nguyễn Văn Sơn (2A202602744).
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import re
import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import reorder_for_llm, format_context, call_llm, SYSTEM_PROMPT
from src.task9_retrieval_pipeline import retrieve


load_dotenv()

st.set_page_config(
    page_title="VinUni Student Assistant - RAG Pipeline",
    page_icon="🎓",
    layout="wide",
)

def highlight_citations(text: str) -> str:
    """Tô màu trực quan các trích dẫn [Document X] dưới dạng badge."""
    pattern = r"\[Document\s+(\d+)\]"
    replacement = (
        r'<span style="display:inline-block; background-color:#eff6ff; color:#1d4ed8; '
        r'padding:2px 7px; border-radius:10px; font-weight:600; font-size:0.85em; '
        r'border:1px solid #93c5fd; margin:0 2px;">📄 Doc \1</span>'
    )
    return re.sub(pattern, replacement, text)


if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🎓 VinUni RAG Assistant")
    st.caption("**Nhóm Dalab (K4-L3A)** — Lead: **Nguyễn Văn Sơn** (MSSV: 2A202602744)")
    st.markdown("---")
    
    st.subheader("⚙️ Cấu hình Truy vấn (Retrieval)")
    top_k = st.slider("Số lượng tài liệu (Top K chunks):", min_value=3, max_value=10, value=5)
    score_threshold = st.slider("Ngưỡng tin cậy Cosine (Threshold fallback):", min_value=0.1, max_value=0.8, value=0.3, step=0.05)
    
    use_rrf = st.checkbox("Sử dụng Hybrid Search + RRF", value=True, help="Nếu tắt, hệ thống sẽ chỉ dùng Dense-only (Vector search)")
    enable_memory = st.checkbox("Bật Conversation Memory (Multi-turn)", value=True, help="Giữ ngữ cảnh câu hỏi trước để hỗ trợ follow-up question")
    
    st.markdown("---")
    st.markdown("**Corpus bao gồm:**")
    st.markdown("- 3 Văn bản quy chế: *Đào tạo tín chỉ, Học bổng, Nội quy KTX*")
    st.markdown("- 5 Thông báo/tin tức: *Đăng ký KTX, Đăng ký học phần, Xét học bổng, Hoãn thi & phúc khảo, Điểm rèn luyện*")
    
    st.markdown("---")
    st.markdown("**AI Models:**")
    st.markdown("- Generator: `gemini-3.1-flash-lite` ⚡")
    st.markdown("- Embedding: `gemini-embedding-001` (3072 dims)")
    
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Header
st.title("🎓 Trợ Lý Thông Tin Sinh Viên VinUni")
st.caption("Chatbot RAG thông minh hỗ trợ giải đáp Quy chế đào tạo, Chính sách học bổng, Ký túc xá và Thủ tục học vụ (Powered by Gemini 3.1 Flash-Lite & Hybrid RRF).")

# Example Questions for quick testing
col1, col2, col3, col4 = st.columns(4)
sample_query = None
if col1.button("📌 Duy trì học bổng"):
    sample_query = "Điều kiện để duy trì học bổng tài năng VinUni cần CGPA bao nhiêu và mấy giờ cộng đồng?"
if col2.button("📌 Rút học phần & Điểm W"):
    sample_query = "Quy định về thời gian rút học phần và ghi điểm W diễn ra như thế nào?"
if col3.button("📌 Phí ký túc xá"):
    sample_query = "Mức phí phòng ký túc xá tiêu chuẩn 2 người là bao nhiêu một tháng và tiền đặt cọc là bao nhiêu?"
if col4.button("⚠️ Test Safe Refusal"):
    sample_query = "Thời tiết hôm nay trên sao Hỏa thế nào?"

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(highlight_citations(msg["content"]), unsafe_allow_html=True)
            if msg.get("sources"):
                retrieval_src = msg.get("retrieval_source", "hybrid")
                st.caption(f"🔍 **Phương thức truy vấn:** `{retrieval_src.upper()}` | **Số nguồn trích dẫn:** {len(msg['sources'])}")
                with st.expander(f"📚 Chi tiết các nguồn tài liệu ({len(msg['sources'])} chunks)"):
                    for idx, src in enumerate(msg["sources"], 1):
                        meta = src.get("metadata", {})
                        st.markdown(f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`)")
                        st.markdown(f"- **Điểm liên quan (Score):** `{src.get('score', 0.0):.4f}` | **Phương pháp:** `{src.get('retrieval_method', '')}`")
                        if meta.get("url"):
                            st.markdown(f"- **URL kiểm chứng:** [{meta['url']}]({meta['url']})")
                        st.text(src.get("content", "")[:300] + ("..." if len(src.get("content", "")) > 300 else ""))
                        st.markdown("---")
        else:
            st.markdown(msg["content"])

# Chat Input or Sample Button Trigger
chat_input = st.chat_input("Nhập câu hỏi về quy chế, học bổng, đăng ký học phần, ký túc xá...")
query = sample_query or chat_input

if query:
    # 1. Lưu câu hỏi của người dùng
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Xử lý câu trả lời từ RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm thông tin và tổng hợp câu trả lời có trích dẫn..."):
            retrieval_query = query
            history_ctx = ""
            if enable_memory and len(st.session_state.messages) > 1:
                prev_user_msgs = [m["content"] for m in st.session_state.messages[:-1] if m["role"] == "user"]
                if prev_user_msgs:
                    last_user_msg = prev_user_msgs[-1]
                    # Nếu câu hỏi ngắn hoặc có từ ngữ nối tiếp, mở rộng ngữ cảnh truy vấn
                    if len(query.split()) < 7 or any(w in query.lower() for w in ["thế còn", "vậy", "khi nào", "bao lâu", "ở đâu", "ai", "được không"]):
                        retrieval_query = f"{last_user_msg} {query}"
                    history_ctx = f"Ngữ cảnh câu hỏi trước: {last_user_msg}\n"

            # Lấy chunks qua retrieval pipeline
            chunks = retrieve(retrieval_query, top_k=top_k, score_threshold=score_threshold, use_reranking=use_rrf)
            
            if not chunks:
                answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
                sources = []
                retrieval_source = "none"
            else:
                reordered = reorder_for_llm(chunks)
                context = format_context(reordered)
                user_message = f"{history_ctx}Context:\n{context}\n\nQuestion: {query}"
                answer = call_llm(SYSTEM_PROMPT, user_message)
                if not answer or not answer.strip():
                    answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."
                sources = chunks
                retrieval_source = chunks[0].get("retrieval_method", "hybrid")
                if retrieval_source not in {"hybrid", "pageindex", "none"}:
                    retrieval_source = "hybrid"

            st.markdown(highlight_citations(answer), unsafe_allow_html=True)
            
            if sources:
                st.caption(f"🔍 **Phương thức truy vấn:** `{retrieval_source.upper()}` | **Số nguồn trích dẫn:** {len(sources)}")
                with st.expander(f"📚 Chi tiết các nguồn tài liệu ({len(sources)} chunks)"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(f"**[{idx}] {meta.get('title', 'Tài liệu')}** (`{meta.get('source', '')}`)")
                        st.markdown(f"- **Điểm liên quan (Score):** `{src.get('score', 0.0):.4f}` | **Phương pháp:** `{src.get('retrieval_method', '')}`")
                        if meta.get("url"):
                            st.markdown(f"- **URL kiểm chứng:** [{meta['url']}]({meta['url']})")
                        st.text(src.get("content", "")[:300] + ("..." if len(src.get("content", "")) > 300 else ""))
                        st.markdown("---")

    # 3. Lưu vào lịch sử phiên làm việc
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
