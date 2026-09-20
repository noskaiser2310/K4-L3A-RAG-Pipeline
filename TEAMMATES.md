# TEAMMATES — K4-L3A · Nhóm Dalab (VinUni Student Handbook RAG)

## 1. Thông tin chung
- **Tên nhóm:** Nhóm Dalab
- **Lớp:** K4-L3A
- **Nhánh làm việc (Branch):** `nhom-dalab`
- **Chủ đề RAG:** Dịch vụ & Quy chế Đào tạo, Học bổng, Ký túc xá Sinh viên VinUni (VinUni Student Handbook & Academic Services)
- **Đại diện kỹ thuật & Trưởng nhóm:** NGUYỄN VĂN SƠN (MSSV: 2A202602744)

## 2. Danh sách thành viên & Phân công vai trò

Dự án được triển khai toàn diện và kiểm thử độc lập, sẵn sàng đáp ứng cả hai hình thức đánh giá (Solo Execution hoặc Team Evaluation):

| STT | Họ và Tên | Mã Học Viên (MSSV) | Vai Trò Đảm Nhiệm | Trách Nhiệm Kỹ Thuật (Module & Deliverable) | File Báo Cáo Cá Nhân |
| :-: | :--- | :---: | :--- | :--- | :--- |
| **1** | **NGUYỄN VĂN SƠN** | **2A202602744** | **Full Pipeline Lead** | - Kiến trúc toàn hệ thống RAG, tích hợp end-to-end.<br>- Chuyển đổi mô hình Embedding `gemini-embedding-001` (3072 dims) và LLM `gemini-3.1-flash-lite`.<br>- Tối ưu fallback, caching, Streamlit UI và pass 100% test suite (20/20). | [`reports/2A202602744-Son.md`](reports/2A202602744-Son.md) |
| **2** | **TRẦN GIA BẢO** | **2A202602767** | **Retrieval & Evaluation Lead** | - Semantic Dense Search (`src/task5_semantic_search.py`).<br>- Lexical BM25Okapi với positive IDF floor (`src/task6_lexical_search.py`).<br>- Reciprocal Rank Fusion ($k=60$) (`src/task7_reranking.py`).<br>- Golden dataset 16 Q&A và benchmark 4 metrics A/B (`RESULT.md`). | [`reports/2A202602767-Bao.md`](reports/2A202602767-Bao.md) |
| **3** | **LÊ XUÂN BÁCH** | **2A202602515** | **Data & Preprocessing Lead** | - Thu thập 3 tài liệu quy chế PDF (>2.7KB) (`src/task1_collect_legal_docs.py`).<br>- Thu thập 5 tin tức JSON metadata (`src/task2_crawl_news.py`).<br>- Chuẩn hóa Markdown phân cấp (`src/task3_convert_markdown.py`).<br>- Chunking RecursiveSplitter 500/50 & Indexing VectorStore (`src/task4_chunking_indexing.py`). | [`reports/2A202602515-Bach.md`](reports/2A202602515-Bach.md) |
| **4** | **NGUYỄN MINH THÚY** | **2A202602960** | **Generation & UI Lead** | - PageIndex defensive fallback (`src/task8_pageindex_vectorless.py`).<br>- Retrieval pipeline threshold calibration (`src/task9_retrieval_pipeline.py`).<br>- Generation có citation & Safe Refusal (`src/task10_generation.py`).<br>- Giao diện Streamlit, Lost-in-the-middle reordering, citation badge (`app.py`). | [`reports/2A202602960-Thuy.md`](reports/2A202602960-Thuy.md) |

## 3. Đầu mối liên hệ & Nộp bài
- **Người nộp bài:** NGUYỄN VĂN SƠN
- **Mã học viên:** 2A202602744
- **Branch nộp:** `nhom-dalab`
- **Trạng thái kiểm thử:** 20/20 test cases Passed (`pytest -q`)
