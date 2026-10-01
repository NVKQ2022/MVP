"""Document Generator: Converts structured knowledge_base.json into searchable text files."""

import json
from pathlib import Path
from typing import Any


def format_article_to_text(article: dict[str, Any]) -> str:
    """Format a single knowledge base article dictionary into structured semantic text."""
    article_id = article.get("article_id", "UNKNOWN-ID")
    title = article.get("title", "")
    product = article.get("product", "")
    module = article.get("module", "")
    error_codes = ", ".join(article.get("error_codes", []))

    symptoms = "\n".join(f"- {s}" for s in article.get("symptoms", []))
    causes = "\n".join(f"- {c}" for c in article.get("causes", []))
    solutions = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(article.get("solutions", [])))
    verifications = "\n".join(f"- {v}" for v in article.get("verification", []))

    return (
        f"Article ID: {article_id}\n"
        f"Title: {title}\n"
        f"Product: {product}\n"
        f"Module: {module}\n"
        f"Error Codes: {error_codes}\n\n"
        f"Symptoms:\n"
        f"{symptoms}\n\n"
        f"Root Causes:\n"
        f"{causes}\n\n"
        f"Recommended Solutions:\n"
        f"{solutions}\n\n"
        f"Resolution Verification:\n"
        f"{verifications}\n"
    )


def generate_kb_text_files(
    json_path: str | Path = "data/knowledge_base.json",
    output_dir: str | Path = "data/kb_documents",
) -> list[Path]:
    """
    Read knowledge_base.json and write individual formatted .txt documents.
    
    Returns the list of generated file paths.
    """
    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"Knowledge base JSON not found: {json_file}")

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    data = json.loads(json_file.read_text(encoding="utf-8"))
    generated_files: list[Path] = []

    for item in data:
        article_id = item.get("article_id", "article")
        content = format_article_to_text(item)
        target_file = out_path / f"{article_id}.txt"
        target_file.write_text(content, encoding="utf-8")
        generated_files.append(target_file)

    return generated_files


if __name__ == "__main__":
    files = generate_kb_text_files()
    print(f"Generated {len(files)} text files in data/kb_documents/")
