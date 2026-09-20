# TEAMMATES — K4-L3A · NGUYỄN VĂN SƠN (SOLO)

## 1. Thông tin học viên
- **Họ và tên:** NGUYỄN VĂN SƠN
- **Mã học viên (MSSV):** 2A202602744
- **Lớp:** K4-L3A
- **Hình thức thực hiện:** **Solo (100% độc lập)**
- **Nhánh làm việc (Branch):** `nhom-dalab`
- **Chủ đề RAG:** Dịch vụ & Quy chế Đào tạo, Học bổng, Ký túc xá Sinh viên VinUni (VinUni Student Handbook & Academic Services)

## 2. Phân công vai trò & Trách nhiệm kỹ thuật

Học viên Nguyễn Văn Sơn trực tiếp nghiên cứu, xây dựng và kiểm thử toàn bộ các thành phần trong hệ thống:

| Module / Deliverable | Công việc trực tiếp thực hiện | File mã nguồn / Artifact | Trạng thái |
| :--- | :--- | :--- | :---: |
| **Data Acquisition** | Thu thập 3 văn bản quy chế PDF (>2.7KB) và 5 tin tức/thông báo JSON đầy đủ metadata | `src/task1_collect_legal_docs.py`<br>`src/task2_crawl_news.py`<br>`data/landing/*` | ✅ Done |
| **Data Standardization** | Chuẩn hóa toàn bộ PDF và JSON sang định dạng Markdown phân cấp (>1000 ký tự/file) | `src/task3_convert_markdown.py`<br>`data/standardized/*` | ✅ Done |
| **Chunking & Embedding** | Cắt đoạn 500/50 ký tự, tích hợp vector embedding 3072 chiều (`gemini-embedding-001`), lưu trữ ChromaDB VectorStore | `src/task4_chunking_indexing.py`<br>`chroma_db/` | ✅ Done |
| **Retrieval Engine** | Xây dựng Semantic Cosine Search, Lexical BM25Okapi với positive IDF floor, dung hợp Reciprocal Rank Fusion ($k=60$) | `src/task5_semantic_search.py`<br>`src/task6_lexical_search.py`<br>`src/task7_reranking.py` | ✅ Done |
| **Fallback Pipeline** | Xây dựng PageIndex fallback an toàn và cơ chế ngưỡng tin cậy Cosine 0.30 | `src/task8_pageindex_vectorless.py`<br>`src/task9_retrieval_pipeline.py` | ✅ Done |
| **Generation & Citation** | Xây dựng prompt grounded trích dẫn `[Document X]`, thuật toán reorder chống "Lost in the middle", LLM `gemini-3.1-flash-lite`, Safe Refusal | `src/task10_generation.py` | ✅ Done |
| **Streamlit Web UI** | Phát triển giao diện chatbot Streamlit hoàn chỉnh, câu hỏi mẫu nhanh, hiển thị nguồn tài liệu, bộ nhớ hội thoại multi-turn | `app.py` | ✅ Done |
| **Evaluation & Benchmark** | Xây dựng 16 cặp Golden Dataset, benchmark 4 metrics A/B (Dense-only vs Hybrid RRF), hoàn thiện báo cáo RESULT.md | `group_project/evaluation/*`<br>`reports/RESULT.md` | ✅ Done |

## 3. Đầu mối liên hệ & Nộp bài
- **Người nộp bài:** NGUYỄN VĂN SƠN
- **Mã học viên:** 2A202602744
- **File báo cáo cá nhân:** [`reports/2A202602744-Son.md`](reports/2A202602744-Son.md)
- **Branch nộp:** `nhom-dalab`
- **Kết quả kiểm thử:** ✅ 20/20 test cases Passed (`pytest -q`)
