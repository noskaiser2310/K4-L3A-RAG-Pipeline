# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3 / Pytest 8.3.3 / Custom Evaluation Harness |
| Evaluator model                    | Google Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`) |
| Generator model                    | Google Gemini 3.1 Flash-Lite (`gemini-3.1-flash-lite`) |
| Embedding model                    | Google Gemini Embedding (`gemini-embedding-001`, 3072-dim, Cosine Similarity) |
| Corpus version/commit              | Branch `nhom-dalab`, commit head |
| Golden dataset size                | 16 grounded Q&A pairs (Legal & News) |
| `top_k`                            | 5 chunks |
| Fallback threshold and calibration | Cosine threshold = 0.30 (calibrated on in-domain vs OOD queries) |

## Configurations

- **Config A — dense-only:** Sử dụng truy vấn vector ngữ nghĩa thuần túy qua VectorStore (Google Gemini Embedding `gemini-embedding-001`, vector 3072 chiều), trích xuất top 5 chunks có khoảng cách cosine nhỏ nhất (similarity cao nhất).
- **Config B — hybrid + RRF:** Kết hợp truy vấn ngữ nghĩa Dense Search (Gemini Embedding 3072-dim) và truy vấn từ khóa Sparse Lexical Search (BM25Okapi với positive IDF floor), dung hợp danh sách xếp hạng bằng thuật toán Reciprocal Rank Fusion (RRF, tham số $k = 60$), trích xuất top 5 chunks sau khi khử trùng lặp.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A (Dense-only) | Config B (Hybrid + RRF) | Delta B−A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                  0.88 |                    0.96 |     +0.08 |
| Answer relevance  |                  0.84 |                    0.93 |     +0.09 |
| Context recall    |                  0.81 |                    0.94 |     +0.13 |
| Context precision |                  0.79 |                    0.91 |     +0.12 |
| **Average**       |              **0.83** |               **0.935** | **+0.105**|

## A/B comparison

- **Cấu hình tốt hơn:** **Config B (Hybrid + RRF)** vượt trội hoàn toàn so với Config A trên toàn bộ 4 tiêu chí đánh giá, với điểm trung bình tổng thể tăng **+10.5%** (từ 0.83 lên 0.935).
- **Evidence:** 
  1. *Context Recall* tăng mạnh nhất (+0.13, từ 0.81 lên 0.94). BM25 giải quyết triệt để điểm yếu của Dense search khi gặp các từ khóa số liệu định lượng và thuật ngữ quy chế đặc thù như: `CGPA >= 3.2`, `100.000 VND`, `IELTS 6.5`, `2.000.000 VND dat coc`, `diem W (Withdraw)`.
  2. *Context Precision* tăng từ 0.79 lên 0.91 (+0.12). Việc dung hợp RRF với $k=60$ đưa các tài liệu thỏa mãn đồng thời cả sự tương đồng ngữ nghĩa và trùng khớp từ khóa chính xác lên vị trí Top 1 - Top 2 trong ngữ cảnh.
  3. *Faithfulness* đạt 0.96 nhờ ngữ cảnh đầu vào chính xác và cơ chế sắp xếp `reorder_for_llm` chống hiện tượng "Lost in the middle", giúp LLM trích dẫn chuẩn xác số hiệu `[Document X]`.
- **Trade-off về latency/cost:**
  - *Độ trễ (Latency):* Config B tăng thêm khoảng 8–15ms cho quá trình tokenize BM25 và tính điểm RRF. Đây là mức chi phí thời gian không đáng kể so với thời gian gọi API LLM (~600–900ms).
  - *Chi phí (Cost):* Hoàn toàn tương đương nhau (0% delta chi phí token) vì cả hai cấu hình đều chỉ đưa đúng `top_k = 5` chunks vào prompt context gửi tới mô hình tạo sinh.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Quy định về thời gian rút học phần và ghi điểm W diễn ra như thế nào? | Config A | 0.80 | 0.82 | 0.70 | 0.65 | retrieval | Dense-only thiên về ngữ nghĩa chung của "đăng ký học phần", kéo chunk tổng quan môn học lên trên chunk chi tiết về rút môn và điểm W. |
|   2 | Mức phí phòng ký túc xá tiêu chuẩn 2 người là bao nhiêu một tháng? | Config A | 0.85 | 0.78 | 0.75 | 0.70 | retrieval | Dense search nhầm lẫn giữa khoản tiền đặt cọc tài sản (2.000.000 VND) và phí lưu trú hàng tháng (3.500.000 VND). Config B giải quyết được nhờ BM25 match chính xác từ khóa "3.500.000". |
|   3 | Sinh viên bị ốm phải nộp đơn xin hoãn thi trong vòng bao lâu và nộp kèm minh chứng gì? | Config A | 0.82 | 0.80 | 0.72 | 0.68 | generation | LLM tổng hợp thiếu chi tiết "bệnh viện tuyến quận/huyện trở lên" do chunk bị đặt ở giữa ngữ cảnh trước khi áp dụng thuật toán reordering. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Bổ sung từ điển từ đồng nghĩa và từ viết tắt (Query Expansion / Synonym Mapping) | Các truy vấn chứa từ viết tắt như "KTX", "GPA", "IELTS", "Add/Drop" đôi khi bị giảm độ tương đồng nếu người dùng gõ không dấu hoặc viết tắt. | Tăng Context Recall thêm +3% đến +5% trên các câu hỏi thực tế của sinh viên. | Chạy benchmark trên tập câu hỏi mở rộng có chứa từ lóng/viết tắt sinh viên. |
|        2 | Nâng cấp chiến lược Chunking theo Markdown Headings (Semantic Section Chunking) | Hiện tại dùng RecursiveSplitter 500 ký tự có thể cắt ngang một điều khoản dài nếu điều khoản đó vượt quá ngưỡng. | Giữ trọn vẹn từng Điều luật quy chế trong một chunk, tăng Context Precision lên > 0.95. | So sánh độ dài ngữ cảnh và đánh giá sự liền mạch của các Điều luật trong chunks. |
|        3 | Tích hợp Cross-Encoder Reranker cho Top 10 ứng viên trước khi chọn Top 5 | RRF dựa trên thứ tự xếp hạng (rank) mà không xét tương quan ngữ nghĩa sâu giữa query và chunk ở tầng cross-attention. | Cải thiện độ liên quan của các câu hỏi suy luận phức tạp hoặc đa điều kiện. | Đo lường MRR (Mean Reciprocal Rank) và NDCG@5 với Cross-Encoder BGE-Reranker. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| **Lost-in-the-middle Document Reordering** (`reorder_for_llm`) | Thứ tự gốc từ RRF ranking | Faithfulness: +0.05 (0.91 → 0.96) | +0.2ms latency / 0$ cost | Đưa chunks quan trọng nhất về đầu và cuối context giúp mô hình LLM chú ý tốt hơn và không bỏ sót bằng chứng khi tạo trích dẫn. |
| **Conversation Memory cho Follow-up Question** | Zero memory (Single-turn query) | Relevance: +0.08 trên follow-up câu hỏi phụ thuộc ngữ cảnh trước | +5ms / +120 input tokens | Giữ ngữ cảnh câu hỏi trước đó trong session state giúp chatbot trả lời mượt mà các câu hỏi đại từ thay thế (ví dụ: "Thế còn tiền cọc?", "Bao lâu thì được hoàn trả?"). |
| **UI Citation & Source Highlighting** | Plain markdown output | Trải nghiệm người dùng (UX) & Fact-checking score: +10% | 0ms / 0$ | Tô màu trực quan badge `[Document X]`, kèm thanh chi tiết nguồn có Score, Type, URL đối chiếu trực tiếp. |
| **Query Expansion & Keyword Normalization** | Raw query input | Recall: +0.06 trên các câu hỏi viết tắt ("KTX", "GPA", "W") | +1ms latency / 0$ | Chuẩn hóa các thuật ngữ viết tắt tiếng Việt/Anh sang dạng đầy đủ trước khi đưa vào BM25 giúp tăng đáng kể tỷ lệ bắt trúng tài liệu. |
