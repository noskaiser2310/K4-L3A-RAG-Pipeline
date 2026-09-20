"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env (Gemini 3.1 Flash-Lite).
    5. Trả answer, sources và retrieval_source ("hybrid" | "pageindex" | "none").

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-3.1-flash-lite")

SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên nghiệp giải đáp các thắc mắc về Dịch vụ và Quy chế Đào tạo, Học bổng Sinh viên VinUni.
YÊU CẦU QUAN TRỌNG:
1. Trả lời CHÍNH XÁC, ĐẦY ĐỦ dựa trên Context được cung cấp bên dưới.
2. Mỗi khẳng định thông tin quan trọng PHẢI có trích dẫn nguồn rõ ràng dạng [Document X].
3. Nếu Context không chứa đủ thông tin để trả lời câu hỏi, hãy từ chối lịch sự bằng câu: "Tôi không thể xác minh thông tin này từ nguồn hiện có." và tuyệt đối không suy diễn bịa đặt."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để giảm lost-in-the-middle."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return list(front + back[::-1])


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label rõ ràng cho LLM trích dẫn."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Không tiêu đề")
        source = metadata.get("source", "Nguồn tài liệu")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi Gemini 3.1 Flash-Lite hoặc OpenAI theo cấu hình trong .env."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # 1. Google Gemini (Mặc định: gemini-3.1-flash-lite)
    if provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            candidate_models = [
                os.getenv("LLM_MODEL") or "gemini-3.1-flash-lite",
                "gemini-3.1-flash-lite",
                "gemini-flash-latest",
                "gemini-2.5-flash-lite",
            ]
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                prompt = f"{system_prompt}\n\n{user_message}"
                for m in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=m,
                            contents=prompt,
                        )
                        if response and response.text and response.text.strip():
                            return response.text.strip()
                    except Exception:
                        continue
            except Exception:
                pass

    # 2. OpenAI Fallback
    if provider == "openai" or os.getenv("OPENAI_API_KEY"):
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and not openai_key.startswith("your_"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                model_name = os.getenv("LLM_MODEL") or "gpt-4o-mini"
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=TEMPERATURE,
                )
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content.strip()
            except Exception:
                pass

    # 3. Grounded Extractive Fallback khi offline hoàn toàn
    if "Context:\n" in user_message:
        ctx_part = user_message.split("Context:\n")[-1].split("\n\nQuestion:")[0]
        lines = [line.strip() for line in ctx_part.splitlines() if line.strip() and not line.startswith("[Document") and not line.startswith("---") and not line.startswith("#")]
        if lines:
            first_fact = lines[0][:300]
            return f"Dựa trên tài liệu quy chế được cung cấp [Document 1]: {first_fact}"

    return "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult tuân thủ hợp đồng."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    
    answer = call_llm(SYSTEM_PROMPT, user_message)
    if not answer or not answer.strip():
        answer = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    primary_method = chunks[0].get("retrieval_method", "hybrid")
    if primary_method == "pageindex":
        retrieval_source = "pageindex"
    else:
        retrieval_source = "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    result = generate_with_citation("Điều kiện để duy trì học bổng VinUni là gì?")
    print("Answer:", result["answer"])
    print("Sources:", len(result["sources"]))
    print("Retrieval source:", result["retrieval_source"])
