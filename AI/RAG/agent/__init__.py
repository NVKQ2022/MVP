"""
agent - Minimal, fully-functional ReAct Agentic RAG package.
"""

from agent.models import (
    AgentAction,
    AgentResponse,
    AgentStep,
    RetrievedChunk,
)
from agent.react_agent import ReActAgent
from agent.tools import RFCInfoTool, RFCSearchTool


def build_react_agent(
    client,
    embedding_service,
    vector_db,
    model_name: str,
    max_steps: int = 4,
    default_top_k: int = 5,
) -> ReActAgent:
    """Factory function to build a ReActAgent instance."""
    return ReActAgent(
        client=client,
        embedding_service=embedding_service,
        vector_db=vector_db,
        model_name=model_name,
        max_steps=max_steps,
        default_top_k=default_top_k,
    )


__all__ = [
    "ReActAgent",
    "build_react_agent",
    "RFCSearchTool",
    "RFCInfoTool",
    "AgentAction",
    "AgentStep",
    "AgentResponse",
    "RetrievedChunk",
]
