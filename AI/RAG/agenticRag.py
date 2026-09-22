# agenticRag.py

import json
import re
import time
from typing import Any

from rag_service import RAGService


class AgenticRAGService:
    """
    Optimized Agentic RAG Service.

    Reduces total LLM calls while maintaining 100% compliance with requirements:
    1. Retrieval Planning & Query Rewriting (Call 1)
    2. Iterative Vector Retrieval & Deduplication
    3. Fused Reflection + Grounded Synthesis (Call 2/3):
       - If evidence is sufficient -> generates grounded answer with citations immediately in the same call.
       - If evidence is insufficient -> detects gaps and outputs concise 'next_query'.
    """

    def __init__(
        self,
        rag_service: RAGService,
        top_k: int = 3,
        max_rounds: int = 2,
        verbose: bool = True,
    ):
        self.rag_service = rag_service
        self.top_k = top_k
        self.max_rounds = max_rounds
        self.verbose = verbose

    # =========================================================
    # Logging helper
    # =========================================================

    def _log_action(self, action_name: str, details: dict[str, Any]) -> None:
        """Pretty print an observable agent action."""
        if not self.verbose:
            return
        print(f"\n>> [ACTION: {action_name.upper()}]")
        for k, v in details.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print(f"   • {k}: {len(v)} item(s)")
            elif isinstance(v, str) and "\n" in v:
                first_line = v.strip().split("\n")[0]
                print(f"   • {k}: {first_line}...")
            else:
                print(f"   • {k}: {v}")

    # =========================================================
    # LLM helper
    # =========================================================

    def _ask_llm(self, prompt: str) -> str:
        """Invoke LLM supporting OpenAI responses or chat.completions."""
        client = self.rag_service.client
        model_name = self.rag_service.model_name

        if hasattr(client, "responses") and hasattr(client.responses, "create"):
            response = client.responses.create(
                model=model_name,
                input=prompt,
            )
            return getattr(response, "output_text", str(response)).strip()

        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return (response.choices[0].message.content or "").strip()

        raise ValueError("Unsupported LLM client interface.")

    def _ask_json(self, prompt: str) -> dict[str, Any]:
        """Ask LLM for a JSON response with robust regex parsing."""
        text = self._ask_llm(prompt)

        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        raw_json = match.group(1) if match else text
        raw_json = raw_json.strip()

        first_brace = raw_json.find("{")
        last_brace = raw_json.rfind("}")
        if first_brace != -1 and last_brace != -1:
            raw_json = raw_json[first_brace : last_brace + 1]

        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            return {}

    # =========================================================
    # 1. Decide whether retrieval is needed & rewrite query
    # =========================================================

    def decide_retrieval(self, question: str) -> dict[str, Any]:
        prompt = f"""
You are the retrieval planner of an Agentic RAG system for network RFC specifications.

Question:
{question}

Decide whether retrieving from local technical documents is needed.

Return ONLY valid JSON:
{{
    "retrieval_needed": true,
    "query": "concise semantic search query with technical keywords",
    "reason": "brief explanation"
}}

Rules:
- retrieval_needed = false for greetings or conversational queries.
- retrieval_needed = true for specific RFC, protocol, or networking technical questions.
- query should rewrite and expand technical keywords for optimal vector search.
"""
        result = self._ask_json(prompt)
        return {
            "retrieval_needed": result.get("retrieval_needed", True),
            "query": (result.get("query") or question).strip(),
            "reason": result.get("reason", "Retrieval is used by default."),
        }

    # =========================================================
    # 2. Fused Reflection & Answer Generation (Reduces 1 LLM Call)
    # =========================================================

    def reflect_and_evaluate(
        self,
        question: str,
        context: str,
        round_number: int,
    ) -> dict[str, Any]:
        """
        Evaluates evidence sufficiency AND generates the final answer in a single call
        if evidence is sufficient (saving an extra LLM call).
        """
        is_last_round = round_number >= self.max_rounds

        prompt = f"""
You are the reflection and answering engine of an Agentic RAG system for RFC specifications.

Original question:
{question}

Retrieval round:
{round_number} of {self.max_rounds}

Accumulated Evidence:
{context}

Task:
1. Evaluate whether the evidence contains sufficient facts to answer the question completely.
2. If sufficient (or if this is the final round {self.max_rounds}), set "enough": true and provide the complete "answer" citing sources as [source#chunk_id] (e.g. [rfc1035.txt#140]).
3. If NOT sufficient and rounds remain, set "enough": false, identify "missing_gaps", and formulate a concise "next_query" with dense technical keywords.

Return ONLY valid JSON:
{{
    "enough": true,
    "confidence": 0.95,
    "reason": "brief reflection explanation",
    "missing_gaps": [],
    "next_query": "",
    "answer": "Grounded answer with citations [source#chunk_id] if enough=true, otherwise empty"
}}
"""
        result = self._ask_json(prompt)
        return {
            "enough": result.get("enough", is_last_round),
            "confidence": float(result.get("confidence", 0.85 if is_last_round else 0.5)),
            "reason": result.get("reason", "Evaluated evidence."),
            "missing_gaps": result.get("missing_gaps", []),
            "next_query": result.get("next_query", "").strip(),
            "answer": result.get("answer", "").strip(),
        }

    # =========================================================
    # 3. Direct answer for non-retrieval queries
    # =========================================================

    def direct_answer(self, question: str) -> str:
        prompt = f"Answer the following user query politely and concisely:\n{question}"
        return self._ask_llm(prompt)

    # =========================================================
    # 4. Optimized Pipeline
    # =========================================================

    def query(self, question: str) -> dict[str, Any]:
        start_time = time.time()
        agent_log: list[dict[str, Any]] = []

        if self.verbose:
            print("=" * 65)
            print("                 AGENTIC RAG EXECUTION")
            print("=" * 65)
            print(f"Question: {question}")

        # -----------------------------------------------------
        # Call 1: Planning & Routing
        # -----------------------------------------------------
        t0 = time.time()
        decision = self.decide_retrieval(question)
        planning_ms = int((time.time() - t0) * 1000)

        planning_log = {
            "action": "PLANNING",
            "retrieval_needed": decision["retrieval_needed"],
            "query": decision["query"],
            "reason": decision["reason"],
            "took_ms": planning_ms,
        }
        agent_log.append(planning_log)
        self._log_action("PLANNING", planning_log)

        # Non-retrieval branch
        if not decision["retrieval_needed"]:
            t0 = time.time()
            answer = self.direct_answer(question)
            gen_ms = int((time.time() - t0) * 1000)

            direct_log = {
                "action": "DIRECT_ANSWER",
                "reason": decision["reason"],
                "took_ms": gen_ms,
            }
            agent_log.append(direct_log)
            self._log_action("DIRECT_ANSWER", direct_log)

            return {
                "question": question,
                "answer": answer,
                "context": "",
                "sources": [],
                "reasoning_summary": f"Direct answer generated without retrieval. Reason: {decision['reason']}",
                "confidence": 1.0,
                "agent_log": agent_log,
                "took_ms": int((time.time() - start_time) * 1000),
            }

        # -----------------------------------------------------
        # Iterative Multi-Round Retrieval Loop
        # -----------------------------------------------------
        current_query = decision["query"]
        all_results: list[dict[str, Any]] = []
        seen_chunks: set[tuple[str, Any]] = set()
        final_answer = ""
        final_confidence = 0.5

        for round_number in range(1, self.max_rounds + 1):
            if self.verbose:
                print(f"\n--- [ROUND {round_number} OF {self.max_rounds}] ---")

            # Vector Retrieval
            t0 = time.time()
            results = self.rag_service.retrieve(
                current_query,
                top_k=self.top_k,
            )
            retrieve_ms = int((time.time() - t0) * 1000)

            retrieval_log = {
                "action": "VECTOR_SEARCH",
                "round": round_number,
                "query": current_query,
                "retrieved_count": len(results),
                "took_ms": retrieve_ms,
            }
            agent_log.append(retrieval_log)
            self._log_action("VECTOR_SEARCH", retrieval_log)

            # Deduplication
            new_chunks = 0
            new_chunk_ids = []
            for result in results:
                document = result.get("document", {})
                source = document.get("source", "unknown")
                chunk_id = document.get("chunk_id", "")
                chunk_key = (source, chunk_id)

                if chunk_key not in seen_chunks:
                    seen_chunks.add(chunk_key)
                    all_results.append(result)
                    new_chunks += 1
                    new_chunk_ids.append(f"{source}#{chunk_id}")

            dedup_log = {
                "action": "DEDUPLICATION",
                "round": round_number,
                "new_chunks_added": new_chunks,
                "total_cumulative_chunks": len(all_results),
                "new_chunk_ids": new_chunk_ids,
            }
            agent_log.append(dedup_log)
            self._log_action("DEDUPLICATION", dedup_log)

            # Format accumulated context
            context = self.rag_service.format_context(all_results)

            # Fused Reflection & Evaluation (Call 2 / Call 3)
            t0 = time.time()
            eval_result = self.reflect_and_evaluate(
                question,
                context,
                round_number,
            )
            eval_ms = int((time.time() - t0) * 1000)
            final_confidence = eval_result["confidence"]

            reflect_log = {
                "action": "REFLECTION_AND_EVALUATION",
                "round": round_number,
                "is_sufficient": eval_result["enough"],
                "confidence": final_confidence,
                "reason": eval_result["reason"],
                "missing_gaps": eval_result.get("missing_gaps", []),
                "next_query": eval_result.get("next_query"),
                "took_ms": eval_ms,
            }
            agent_log.append(reflect_log)
            self._log_action("REFLECTION_AND_EVALUATION", reflect_log)

            # Check if answer was synthesized in this step
            if eval_result["enough"] and eval_result.get("answer"):
                final_answer = eval_result["answer"]
                if self.verbose:
                    print(">> [DECISION] Evidence sufficient! Answer synthesized directly in reflection step.")
                break

            # If not enough, refine query for next round
            next_query = eval_result.get("next_query")
            if not next_query or not next_query.strip() or next_query.strip().lower() == current_query.strip().lower():
                if self.verbose:
                    print(">> [DECISION] No further unique query. Concluding.")
                final_answer = eval_result.get("answer", "")
                break

            refine_log = {
                "action": "QUERY_REFINEMENT",
                "round": round_number,
                "previous_query": current_query,
                "refined_next_query": next_query,
            }
            agent_log.append(refine_log)
            self._log_action("QUERY_REFINEMENT", refine_log)

            current_query = next_query

        # Fallback synthesis if answer empty
        if not final_answer:
            prompt = f"Answer using only the evidence:\nContext:\n{context}\n\nQuestion: {question}\nAnswer with citations [source#chunk_id]:"
            final_answer = self._ask_llm(prompt)

        total_took_ms = int((time.time() - start_time) * 1000)
        rounds_executed = len([l for l in agent_log if l.get("action") == "VECTOR_SEARCH"])
        llm_calls_made = len([l for l in agent_log if l.get("action") in ("PLANNING", "REFLECTION_AND_EVALUATION", "DIRECT_ANSWER")])

        reasoning_summary = (
            f"Executed {rounds_executed} retrieval round(s) with {llm_calls_made} LLM call(s). "
            f"Gathered {len(all_results)} unique chunks across {len(seen_chunks)} sources. "
            f"Evidence confidence: {final_confidence:.2f}."
        )

        return {
            "question": question,
            "answer": final_answer,
            "context": context,
            "sources": [
                result.get("document", {})
                for result in all_results
            ],
            "reasoning_summary": reasoning_summary,
            "confidence": round(final_confidence, 2),
            "agent_log": agent_log,
            "took_ms": total_took_ms,
            "llm_calls": llm_calls_made,
        }