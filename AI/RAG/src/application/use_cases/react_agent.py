"""Use case for ReAct (Reasoning + Acting) Agent for RAG."""

import json
import re
import time
from typing import Any

from src.application.tools.rfc_tools import RFCInfoTool, RFCSearchTool
from src.domain.entities.agent import AgentAction, AgentResponse, AgentStep
from src.domain.entities.document import Chunk
from src.domain.interfaces.embedding import EmbeddingModelInterface
from src.domain.interfaces.llm import LLMClientInterface
from src.domain.interfaces.vector_store import VectorStoreInterface


class ReActAgentUseCase:
    """ReAct (Reasoning + Acting) Agent for Technical RFC Question Answering.

    Executes a structured Thought -> Action -> Observation loop:
    1. Reason about the user question and the current state of knowledge.
    2. Select a tool action (search_rfc or list_available_docs) to retrieve technical evidence.
    3. Observe the tool output and reflect on whether more information is needed.
    4. Conclude with 'final_answer' citing retrieved chunks [source#chunk_id].
    """

    def __init__(
        self,
        llm_client: LLMClientInterface,
        embedding_model: EmbeddingModelInterface,
        vector_store: VectorStoreInterface,
        max_steps: int = 4,
        default_top_k: int = 5,
    ) -> None:
        self.llm_client = llm_client
        self.max_steps = max_steps
        self.default_top_k = default_top_k

        # Initialize domain tools
        self.search_tool = RFCSearchTool(
            embedding_model=embedding_model,
            vector_store=vector_store,
        )
        self.info_tool = RFCInfoTool()

    def _build_system_prompt(self) -> str:
        return f"""You are an expert Network Systems and RFC Protocol ReAct Agent.
Your job is to answer technical questions accurately by retrieving evidence from indexed RFC specifications.

You have access to the following tools:
1. `{self.search_tool.name}`: {self.search_tool.description}
2. `{self.info_tool.name}`: {self.info_tool.description}

You must operate in a strict JSON Thought -> Action loop.
At each step, respond with EXACTLY ONE JSON object of the form:
{{
    "thought": "<Reason about what you know and what information is still missing>",
    "action": "<search_rfc | list_available_docs | final_answer>",
    "action_input": {{ ... }}
}}

For action 'search_rfc', action_input MUST contain:
  - "query": "<search keywords/technical phrases>"
  - "top_k": <integer, default {self.default_top_k}>

For action 'list_available_docs', action_input is empty: {{}}

For action 'final_answer', action_input MUST contain:
  - "answer": "<Comprehensive, grounded technical answer with citations like [rfc1035.txt#42]>"
  - "confidence": <float between 0.0 and 1.0>

Rules:
- NEVER guess RFC specifications without citing chunks retrieved.
- If you have enough evidence, immediately emit 'final_answer'.
- Always return valid JSON and nothing else.
"""

    def _parse_action(self, llm_output: str, question: str) -> AgentAction:
        """Parse LLM output safely into an AgentAction."""
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
        clean = match.group(1) if match else llm_output
        clean = clean.strip()

        first_brace = clean.find("{")
        last_brace = clean.rfind("}")
        if first_brace != -1 and last_brace != -1:
            clean = clean[first_brace : last_brace + 1]

        try:
            data = json.loads(clean)
            return AgentAction(
                thought=str(data.get("thought", "Evaluating next step...")),
                action=str(data.get("action", "search_rfc")),
                action_input=dict(data.get("action_input", {})),
            )
        except Exception:
            # Fallback action
            return AgentAction(
                thought="Searching the database for relevant RFC documents.",
                action="search_rfc",
                action_input={"query": question, "top_k": self.default_top_k},
            )

    def execute(
        self,
        question: str,
        top_k: int | None = None,
        max_steps: int | None = None,
    ) -> AgentResponse:
        """Execute the ReAct agentic workflow on a user question."""
        start_time = time.time()
        k = top_k or self.default_top_k
        limit = max_steps or self.max_steps

        trajectory: list[AgentStep] = []
        cumulative_chunks: list[Chunk] = []
        seen_chunk_ids: set[str] = set()

        system_prompt = self._build_system_prompt()
        conversation_history = f"User Question: {question}\n\nBegin your reasoning loop."

        final_answer = ""
        confidence = 0.85

        for step_idx in range(1, limit + 1):
            prompt = (
                f"{system_prompt}\n\n"
                f"{conversation_history}\n\n"
                f"Current Step: {step_idx} of {limit}\n"
                "Provide your next Thought and Action in strictly valid JSON format."
            )

            llm_output = self.llm_client.complete(prompt)
            action = self._parse_action(llm_output, question)

            if action.action == "final_answer":
                final_answer = str(action.action_input.get("answer", ""))
                confidence = float(action.action_input.get("confidence", 0.95))
                trajectory.append(
                    AgentStep(
                        step_num=step_idx,
                        thought=action.thought,
                        action="final_answer",
                        action_input=action.action_input,
                        observation="Final answer formulated.",
                        chunks_retrieved=0,
                    )
                )
                break

            # Execute selected tool
            obs = ""
            new_chunks_count = 0
            if action.action == "search_rfc":
                query_str = str(action.action_input.get("query", question))
                step_k = int(action.action_input.get("top_k", k))
                retrieved = self.search_tool.execute(query_str, top_k=step_k)

                obs_lines = []
                for chunk in retrieved:
                    if chunk.identifier not in seen_chunk_ids:
                        seen_chunk_ids.add(chunk.identifier)
                        cumulative_chunks.append(chunk)
                        new_chunks_count += 1
                    obs_lines.append(f"[{chunk.identifier}]: {chunk.text[:220]}...")

                obs = f"Retrieved {len(retrieved)} chunks:\n" + "\n".join(obs_lines)

            elif action.action == "list_available_docs":
                obs = self.info_tool.execute()

            else:
                obs = f"Unknown tool '{action.action}'. Please use 'search_rfc', 'list_available_docs', or 'final_answer'."

            trajectory.append(
                AgentStep(
                    step_num=step_idx,
                    thought=action.thought,
                    action=action.action_input.get("action", action.action),
                    action_input=action.action_input,
                    observation=obs[:500],
                    chunks_retrieved=new_chunks_count,
                )
            )

            conversation_history += (
                f"\n\nThought {step_idx}: {action.thought}\n"
                f"Action {step_idx}: {action.action}({action.action_input})\n"
                f"Observation {step_idx}: {obs}"
            )

        # Fallback if no final answer was produced in the loop
        if not final_answer:
            evidence_text = "\n\n".join(f"[{c.identifier}]\n{c.text}" for c in cumulative_chunks)
            fallback_prompt = (
                f"Based on the following collected evidence:\n{evidence_text}\n\n"
                f"Answer the question: {question}\n"
                "Cite sources as [source#chunk_id]."
            )
            final_answer = self.llm_client.complete(fallback_prompt)
            confidence = 0.70

        took_ms = int((time.time() - start_time) * 1000)

        sources = [
            {
                "source": c.source,
                "chunk_id": c.chunk_id,
                "score": c.metadata.get("score", 0.0),
            }
            for c in cumulative_chunks
        ]

        summary = (
            f"Executed {len(trajectory)} reasoning steps. "
            f"Retrieved {len(cumulative_chunks)} unique chunks across {len(seen_chunk_ids)} unique references."
        )

        return AgentResponse(
            question=question,
            answer=final_answer,
            sources=sources,
            retrieved_evidence=[c.to_dict() for c in cumulative_chunks],
            trajectory=trajectory,
            reasoning_summary=summary,
            confidence=confidence,
            total_steps=len(trajectory),
            took_ms=took_ms,
            llm_calls=len(trajectory) + (1 if not final_answer else 0),
        )

    def query(self, question: str, **kwargs: Any) -> AgentResponse:
        """Alias for execute."""
        return self.execute(question, **kwargs)
