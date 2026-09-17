def chunk_text(
    text: str,
    chunk_size: int = 300,
    overlap: int = 30,
    drop_empty: bool = True,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to split.
        chunk_size: Maximum size of each chunk.
        overlap: Number of characters shared between consecutive chunks.
        drop_empty: Whether to ignore empty/whitespace-only chunks.

    Returns:
        A list of text chunks.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    if drop_empty and not text.strip():
        return []

    step = chunk_size - overlap
    chunks = []

    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size]

        if not drop_empty or chunk.strip():
            chunks.append(chunk)

        if start + chunk_size >= len(text):
            break

    return chunks
