"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Trích xuất PDF và chuẩn hóa thành Markdown có tiêu đề rõ ràng.
    2. Đọc JSON tin tức và giữ metadata (Title, Source, Date) ở đầu file.
    3. Giữ cấu trúc thư mục standardized/legal/ và standardized/news/.
    4. Không tạo file rỗng hoặc file < 200 ký tự.
"""

import json
from pathlib import Path
from pypdf import PdfReader


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF trong landing/legal sang standardized/legal/*.md."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in legal_dir.iterdir():
        if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
            reader = PdfReader(str(path))
            pages_text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted.strip())
            
            body_text = "\n\n".join(pages_text)
            
            # Đảm bảo markdown chuẩn có tiêu đề và metadata nguồn
            title = path.stem.replace("-", " ").title()
            header = f"# {title}\n\n**Source:** {path.name}\n\n**Type:** Legal / Policy Document\n\n---\n\n"
            content = header + body_text
            
            out_file = output_dir / f"{path.stem}.md"
            out_file.write_text(content, encoding="utf-8")
            print(f"Converted legal doc: {out_file.name} ({len(content)} chars)")


def convert_news_articles() -> None:
    """Convert JSON trong landing/news sang standardized/news/*.md."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in news_dir.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        content = header + data["content_markdown"]
        out_file = output_dir / f"{path.stem}.md"
        out_file.write_text(content, encoding="utf-8")
        print(f"Converted news article: {out_file.name} ({len(content)} chars)")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang standardized."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Standardization complete: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
