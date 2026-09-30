"""Agent tools for RFC retrieval and protocol information."""

from typing import Any

from src.domain.entities.document import Chunk
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.vector_store import VectorStoreInterface


class RFCSearchTool:
    """Tool that performs semantic vector search over RFC documents."""

    name: str = "search_rfc"
    description: str = (
        "Search RFC technical specifications in the vector database. "
        "Inputs: query (str) - search query with technical terms/RFC numbers; top_k (int, default=5)."
    )

    def __init__(
        self,
        embedding_model: EmbeddingModelInterface,
        vector_store: VectorStoreInterface,
    ) -> None:
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def execute(self, query: str, top_k: int = 5) -> list[Chunk]:
        """Run vector search and return structured chunks."""
        query_vector = self.embedding_model.embed_text(query)
        raw_results = self.vector_store.search(query_vector, top_k=top_k)

        chunks: list[Chunk] = []
        for r in raw_results:
            doc = r.get("document", {})
            chunks.append(
                Chunk(
                    source=doc.get("source", "unknown"),
                    chunk_id=doc.get("chunk_id", 0),
                    text=doc.get("text", ""),
                    metadata={
                        "score": float(r.get("score", 0.0)),
                        "distance": float(r.get("distance", 0.0)),
                    },
                )
            )
        return chunks


class RFCInfoTool:
    """Tool that lists the available RFC documents and topics in the database."""

    name: str = "list_available_docs"
    description: str = "Returns the list of RFC documents and network protocols indexed in the database."

    AVAILABLE_DOCS = {
        "rfc791.txt": "Internet Protocol (IPv4) - Addressing, Fragmentation, Header Format",
        "rfc793.txt": "Transmission Control Protocol (TCP) - 3-Way Handshake, Sequence Numbers, Flags",
        "rfc1035.txt": "Domain Name System (DNS) - Implementation, Resource Records, Query Formats",
        "rfc6749.txt": "OAuth 2.0 Authorization Framework - Grant Types, Access & Refresh Tokens",
        "rfc8259.txt": "JSON Data Interchange Format - Syntax, Data Types, Grammar",
        "rfc8446.txt": "Transport Layer Security (TLS 1.3) - 1-RTT Handshake, Cipher Suites, Keys",
        "rfc9000.txt": "QUIC Transport Protocol - UDP Multiplexing, Streams, Connection Migration",
        "rfc9110.txt": "HTTP Semantics - Methods, Status Codes, Headers, Message Framing",
    }

    def execute(self) -> str:
        lines = ["Indexed RFC Documents:"]
        for filename, desc in self.AVAILABLE_DOCS.items():
            lines.append(f"- {filename}: {desc}")
        return "\n".join(lines)
