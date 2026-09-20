# Day 8 — RAG Pipeline: Trợ Lý Dịch Vụ & Quy Chế Đào Tạo VinUni

> **Học viên (Solo):** NGUYỄN VĂN SƠN (MSSV: 2A202602744)  
> **Lớp:** K4-L3A  
> **Chủ đề:** Hệ thống RAG hỏi đáp Dịch vụ, Quy chế Đào tạo tín chỉ, Chính sách Học bổng và Nội quy Ký túc xá Sinh viên VinUni (VinUni Student Handbook & Academic Services).  
> **Branch nộp bài:** `nhom-dalab`  
> **Trạng thái kiểm thử:** ✅ **20/20 tests passed** (`pytest -q` trong 0.21s)

---

## 1. Tổng quan Dự án & Kiến trúc Pipeline

Chatbot RAG hỗ trợ sinh viên tra cứu và giải đáp các chính sách đào tạo, điều kiện duy trì học bổng, nội quy ký túc xá và thủ tục học vụ với độ tin cậy cao, trích dẫn minh bạch và phòng chống ảo giác:

```
[User Query]
     │
     ├──► Dense Semantic Search (Google Gemini Embedding 3072-dim) ──┐
     │                                                               ├──► Reciprocal Rank Fusion (RRF k=60)
     └──► Lexical Search (BM25Okapi với Positive IDF Floor) ─────────┘               │
                                                                                    ▼
                                                                        Cosine Threshold Check (0.30)
                                                                             │             │
                                                        [Above Threshold] ───┘             └───► [Below Threshold]
                                                                  │                                    │
                                                      Lost-in-the-Middle Reorder               PageIndex Fallback
                                                                  │                                    │
                                                                  └──────────────┬─────────────────────┘
                                                                                 ▼
                                                                     LLM Generation (Gemini 3.1 Flash-Lite)
                                                                     Prompt grounded với [Document X] Citation
                                                                                 │
                                                                                 ▼
                                                                     Streamlit Web UI + Citation Highlighting
```

- **Embedding Model:** Google Gemini Embedding (`gemini-embedding-001`, 3072 chiều)
- **Generator Model:** Google Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`)
- **Retrieval Engine:** Hybrid Search kết hợp ChromaDB VectorStore & BM25Okapi với RRF ($k=60$)
- **Fallback Strategy:** Fallback sang PageIndex khi Cosine score < 0.30; Safe Refusal khi thiếu bằng chứng
- **Bonus Capabilities:** Lost-in-the-middle reordering, Multi-turn Conversation Memory, Visual Citation Badges

---

## 2. Cấu trúc Thư mục & Báo cáo Nộp bài

```text
K4-L3A-RAG-Pipeline/
├── TEAMMATES.md                     # Thông tin học viên (Solo), phân công module và cam kết
├── README.md                        # Hướng dẫn chi tiết, kiến trúc và kết quả
├── app.py                           # Giao diện Chatbot Streamlit hoàn chỉnh
├── .env.example                     # File cấu hình môi trường mẫu
│
├── data/
│   ├── landing/                     # Dữ liệu thu thập ban đầu
│   │   ├── legal/                   # 3 PDF quy chế (>2.7KB/file)
│   │   └── news/                    # 5 JSON tin tức (đầy đủ url, title, date_crawled, content)
│   └── standardized/                # Dữ liệu đã chuẩn hóa Markdown (>1000 ký tự/file)
│       ├── legal/                   # 3 Markdown quy chế
│       └── news/                    # 5 Markdown tin tức
│
├── src/                             # Mã nguồn 10 nhiệm vụ pipeline tuân thủ contracts
│   ├── task1_collect_legal_docs.py  # Thu thập 3 tài liệu quy chế PDF
│   ├── task2_crawl_news.py          # Thu thập 5 bài viết JSON
│   ├── task3_convert_markdown.py    # Chuẩn hóa văn bản sang Markdown
│   ├── task4_chunking_indexing.py   # Chunking (500/50) và Indexing vectorstore (Gemini)
│   ├── task5_semantic_search.py     # Truy vấn vector Cosine Similarity
│   ├── task6_lexical_search.py      # Truy vấn BM25Okapi với positive IDF floor
│   ├── task7_reranking.py           # Dung hợp thứ hạng RRF (k=60)
│   ├── task8_pageindex_vectorless.py# PageIndex vectorless search fallback
│   ├── task9_retrieval_pipeline.py  # Pipeline tích hợp, threshold fallback
│   └── task10_generation.py         # Generation có trích dẫn [Document X] & Safe Refusal
│
├── group_project/                   # Đánh giá dự án & Golden dataset
│   ├── evaluation/
│   │   ├── golden_dataset.json      # 16 cặp câu hỏi - câu trả lời - ngữ cảnh mẫu
│   │   └── RESULT.md                # Báo cáo A/B benchmark (Dense vs Hybrid RRF)
│   └── individual/                  # Báo cáo cá nhân
│       └── 2A202602744-Son.md       # Báo cáo cá nhân: Nguyễn Văn Sơn (Solo Full Pipeline)
│
├── reports/                         # Thư mục báo cáo đồng bộ
│   ├── RESULT.md                    # Báo cáo đánh giá RAG kết quả A/B (100% hoàn thiện)
│   └── 2A202602744-Son.md           # Báo cáo cá nhân: Nguyễn Văn Sơn
│
└── tests/                           # Kiểm thử tự động (20/20 passed)
    ├── test_contracts.py            # 15 tests kiểm tra schema và contract interface
    └── test_acceptance.py           # 5 tests kiểm tra dữ liệu, golden set, report
```

---

## 3. Quick Start & Hướng dẫn Chạy lại

### Bước 1: Thiết lập môi trường & cấu hình API Key

```bash
# Tạo và kích hoạt virtual environment
python -m venv .venv
source .venv/bin/activate        # Trên Windows: .venv\Scripts\activate

# Cài đặt dependencies (yêu cầu Python >= 3.10)
pip install -e ".[dev]"

# Tạo file .env từ mẫu và điền GEMINI_API_KEY
cp .env.example .env
```

Nội dung cơ bản trong `.env`:
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-001
GEMINI_API_KEY=your_gemini_api_key_here
SCORE_THRESHOLD=0.3
TOP_K=5
```

### Bước 2: Chạy kiểm thử tự động (20/20 tests)

```bash
pytest -q
```
*Kết quả:* `20 passed in 0.21s` (15 contract tests + 5 acceptance tests).

### Bước 3: Chạy giao diện Chatbot Streamlit

```bash
streamlit run app.py
```
Ứng dụng sẽ mở tại `http://localhost:8501`, cho phép:
- Tra cứu trực quan các câu hỏi quy chế đào tạo, học bổng, KTX.
- Bật/tắt chế độ Hybrid Search + RRF so với Dense-only.
- Xem chi tiết từng nguồn tài liệu trích dẫn, điểm Score và URL kiểm chứng.
- Kiểm tra cơ chế Safe Refusal trên câu hỏi ngoài phạm vi.

---

## 4. Tóm tắt Kết quả Đánh giá A/B (Benchmark 4 Metrics)

So sánh giữa **Config A (Dense-only)** và **Config B (Hybrid + RRF)** trên tập 16 Golden Q&A:

| Chỉ số (Metric) | Config A (Dense-only) | Config B (Hybrid + RRF) | Chênh lệch (Delta B−A) |
| :--- | :---: | :---: | :---: |
| **Faithfulness** (Độ trung thực) | 0.88 | **0.96** | **+0.08** |
| **Answer Relevance** (Độ liên quan) | 0.84 | **0.93** | **+0.09** |
| **Context Recall** (Độ bao phủ) | 0.81 | **0.94** | **+0.13** |
| **Context Precision** (Độ chính xác) | 0.79 | **0.91** | **+0.12** |
| **Điểm Trung Bình (Average)** | **0.830** | **0.935** | **+0.105 (+10.5%)** |

Chi tiết xem tại [`group_project/evaluation/RESULT.md`](group_project/evaluation/RESULT.md) hoặc [`reports/RESULT.md`](reports/RESULT.md).
