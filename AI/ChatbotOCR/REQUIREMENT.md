# REQUIREMENT.md

# Screenshot-Based Support Chatbot

## 1. Background

The support team receives and resolves customer issues every day. A typical support workflow is:

1. A customer encounters an error while using the system.
2. The customer takes a screenshot of the error or the affected screen.
3. The customer sends the screenshot to the support team through a chat window.
4. A support staff member inspects the screenshot and identifies what happened.
5. The support staff member searches the available knowledge base for relevant troubleshooting information.
6. The support staff member sends an appropriate solution back to the customer.

The goal of this assignment is to build a chatbot that assists the support team by automating the screenshot analysis, knowledge retrieval, and response-generation steps.

---

## 2. Objective

Build a chatbot that accepts a customer screenshot, extracts useful information from the screenshot without using an LLM for information extraction, retrieves related knowledge from a Milvus-based knowledge base, and generates a useful support response for display in the chat window.

The system should reduce the amount of manual investigation required from support staff while keeping the retrieved knowledge traceable and the final response grounded in the knowledge base.

---

## 3. Scope

### 3.1 In Scope

The implementation must cover the complete pipeline:

```text
Customer / Support User
        |
        v
   Chat Window
        |
        | Screenshot
        v
 Screenshot Processing
        |
        | Structured information
        v
 Knowledge Retrieval
        |
        | Relevant knowledge
        v
 Response Generation
        |
        v
    Chat Window
```

The system must provide:

- A chat interface for uploading/sending screenshots.
- Screenshot preprocessing and non-LLM information extraction.
- Search over a knowledge base using Milvus Lite or Milvus Standalone.
- Generation of a natural-language support response using the retrieved knowledge.
- A runnable codebase.
- A brief solution document with a maximum length of 5 pages.

### 3.2 Out of Scope

The following are not required unless necessary for the demonstration:

- Full integration with a production customer-service platform.
- User authentication and enterprise identity management.
- Automatic modification of the customer's system.
- Training a custom OCR, vision, or language model from scratch.
- Replacing the support team completely.
- Production-scale distributed Milvus deployment.

---

## 4. Functional Requirements

### FR-01 — Chat Window

The system shall provide a chat interface that allows the user to:

- Enter a message.
- Upload or attach a screenshot.
- Submit the screenshot for analysis.
- View the generated support response.
- Continue the conversation after the initial response.

### FR-02 — Screenshot Input

The system shall accept common screenshot image formats, at minimum:

- PNG
- JPEG/JPG

The system should validate the uploaded file before processing and return a clear error message for unsupported or unreadable images.

### FR-03 — Screenshot Preprocessing

The system shall preprocess the screenshot before information extraction when necessary.

Possible preprocessing operations include:

- Image resizing.
- Grayscale conversion.
- Noise reduction.
- Contrast enhancement.
- Cropping or region detection.
- Other deterministic computer-vision operations that improve OCR quality.

The preprocessing stage must not use an LLM for information extraction.

### FR-04 — Information Extraction from Screenshot

The system shall extract necessary information from the screenshot without using an LLM as the extraction mechanism.

The extracted information may include, when visible:

- Error message.
- Error code.
- Warning message.
- Page or screen title.
- Product/module name.
- Visible URL, endpoint, or route.
- Relevant field values.
- Timestamp or request identifier.
- Other text or structured information that is useful for troubleshooting.

The extraction implementation should use OCR and/or deterministic image-processing techniques. Suitable implementations may use an OCR engine and rule-based post-processing.

The extraction component should return structured data rather than only raw OCR text. For example:

```json
{
  "error_code": "ERR-401",
  "error_message": "Unauthorized access",
  "page": "User Management",
  "url": "/admin/users",
  "raw_text": "..."
}
```

Fields that cannot be confidently extracted should be left empty or marked as unknown rather than fabricated.

### FR-05 — Knowledge Base

The system shall use Milvus Lite or Milvus Standalone as the knowledge base for retrieval.

The knowledge base should contain support-oriented documents such as:

- Known errors.
- Troubleshooting procedures.
- Frequently asked questions.
- System/module documentation.
- Configuration guidance.
- Error-code descriptions.
- Resolution steps.

Each knowledge item should contain enough metadata to identify its source and context. Recommended fields include:

- `id`
- `title`
- `content`
- `category`
- `product`
- `error_code` (when applicable)
- `source`
- `embedding`

### FR-06 — Knowledge Ingestion

The project shall include a repeatable way to load knowledge documents into Milvus.

The ingestion pipeline should:

1. Read source documents.
2. Clean/normalize their text.
3. Split long documents into retrieval-friendly chunks when necessary.
4. Generate vector embeddings.
5. Store vectors and metadata in Milvus.

Knowledge ingestion should be separate from online query processing so that the chatbot does not need to rebuild the entire database for every request.

### FR-07 — Knowledge Retrieval

After screenshot information is extracted, the system shall construct a search query from the extracted information and retrieve related knowledge from Milvus.

The retrieval process should:

1. Build a normalized textual query from the extracted fields.
2. Generate an embedding for the query.
3. Search the Milvus collection for relevant items.
4. Return the top relevant results.
5. Preserve metadata and source information for each result.

The implementation should expose a configurable `top_k` value.

A retrieval result should contain, at minimum:

```json
{
  "id": "KB-001",
  "score": 0.87,
  "title": "Unauthorized access error",
  "content": "...",
  "source": "support_guide.md"
}
```

### FR-08 — Response Generation

The system shall generate a natural-language support response using the retrieved knowledge.

The generation stage may use an LLM. The LLM must receive the relevant retrieved knowledge as grounding context.

The generated response should:

- Explain the detected issue in understandable language.
- Provide relevant troubleshooting or resolution steps.
- Avoid inventing unsupported technical facts.
- Prefer the retrieved knowledge over unsupported assumptions.
- Indicate when the available knowledge is insufficient.
- Be appropriate for a support-team/customer-facing conversation.

The response generator should not be responsible for extracting text from the screenshot. Screenshot information extraction and response generation are separate stages.

### FR-09 — Response Display

The generated response shall be returned to the chat window.

The UI should clearly distinguish:

- Customer/user message.
- Uploaded screenshot.
- Chatbot response.

For demonstration and debugging, the application should optionally expose the extracted information and retrieved knowledge used to produce the answer.

### FR-10 — Error Handling

The system shall handle at least the following failure cases:

- Invalid image file.
- Unreadable image.
- OCR failure or empty extraction.
- No matching knowledge found.
- Milvus unavailable.
- Embedding-generation failure.
- LLM/API failure.
- Invalid or incomplete request.

The system should return actionable error messages instead of crashing silently.

---

## 5. Mandatory Technical Constraints

### TC-01 — No LLM for Screenshot Information Extraction

An LLM must not be used to extract the necessary information from the screenshot.

Acceptable approaches include:

- OCR.
- Computer vision.
- Image preprocessing.
- Regular expressions.
- Rule-based parsing.
- Pattern matching.
- Deterministic post-processing.

An LLM may be used later for response generation.

### TC-02 — Milvus for Knowledge Retrieval

Milvus Lite or Milvus Standalone shall be used as the vector knowledge base.

Milvus Lite can run locally through the Python SDK and is intended for small-scale local vector-search use cases. Milvus Standalone can be run as a Docker-based Milvus deployment. The retrieval layer should be designed so that switching between Lite and Standalone requires configuration changes rather than a redesign of the application. citeturn671435view0turn671435view1

References:

- Milvus Lite: https://milvus.io/docs/milvus_lite.md
- Milvus Standalone prerequisites: https://milvus.io/docs/prerequisite-docker.md

### TC-03 — No Alternative Primary Vector Database

Another vector database must not replace Milvus as the primary knowledge-retrieval database.

### TC-04 — Traceable Retrieval

The system should retain the source and metadata of retrieved knowledge so that the generated answer can be traced back to the supporting documents.

### TC-05 — Deterministic Extraction Boundary

The screenshot extraction module should expose a clear structured interface so that its output can be tested independently from the LLM and retrieval components.

---

## 6. Recommended System Architecture

A modular architecture is expected:

```text
+----------------------+
|      Chat UI         |
| image + message      |
+----------+-----------+
           |
           v
+----------------------+
|   API / Orchestrator |
+----------+-----------+
           |
           v
+----------------------+
| Screenshot Processor |
| - preprocessing      |
| - OCR                |
| - rule-based parser  |
+----------+-----------+
           |
           | structured extraction
           v
+----------------------+
| Query Builder        |
| + Embedding Model    |
+----------+-----------+
           |
           v
+----------------------+
|      Milvus          |
| Lite / Standalone    |
+----------+-----------+
           |
           | top-k knowledge
           v
+----------------------+
| Response Generator   |
|       LLM            |
+----------+-----------+
           |
           v
+----------------------+
|      Chat UI         |
+----------------------+
```

The following components should be independently testable:

- `ScreenshotPreprocessor`
- `InformationExtractor`
- `QueryBuilder`
- `EmbeddingService`
- `KnowledgeRetriever`
- `ResponseGenerator`
- `Chat/API Layer`

---

## 7. Knowledge Base Requirements

### 7.1 Document Preparation

The project shall provide sample knowledge documents sufficient to demonstrate retrieval.

Recommended example knowledge records:

```text
Error Code: ERR-401
Product: Admin Portal
Title: Unauthorized access
Problem: User receives an Unauthorized access error on the User Management page.
Resolution:
1. Verify the user's authentication status.
2. Verify that the user has the required role.
3. Refresh the session.
4. Check the authentication service logs if the issue persists.
Source: admin_portal_troubleshooting.md
```

The demo knowledge base should contain multiple issues so that retrieval quality can be meaningfully demonstrated.

### 7.2 Embeddings

An embedding model shall be used to convert knowledge chunks and search queries into vectors.

The chosen embedding model, vector dimension, and similarity metric shall be documented.

### 7.3 Retrieval Configuration

The implementation shall make at least the following configurable:

- Milvus URI/path.
- Collection name.
- Embedding model.
- Vector dimension.
- Similarity metric.
- `top_k`.
- Knowledge-data location.

---

## 8. Screenshot Extraction Requirements

The extraction pipeline should prioritize information that is useful for matching support knowledge.

A recommended extraction flow is:

```text
Screenshot
   |
   v
Image preprocessing
   |
   v
OCR
   |
   v
Raw text
   |
   +----> Error-code detection
   |
   +----> URL/route detection
   |
   +----> Product/module detection
   |
   +----> Error-message extraction
   |
   v
Structured issue representation
```

Example internal representation:

```json
{
  "product": "Admin Portal",
  "module": "User Management",
  "error_code": "ERR-401",
  "error_message": "Unauthorized access",
  "url": "/admin/users",
  "raw_text": "..."
}
```

The implementation must not invent missing information. Extraction confidence or validation flags may be included where useful.

---

## 9. Response Generation Requirements

The response generator should receive:

- Extracted screenshot information.
- Retrieved knowledge.
- Optional conversation context.

A recommended prompt contract is:

```text
SYSTEM:
You are a support assistant. Answer using the supplied knowledge.
Do not invent troubleshooting steps that are not supported by the context.
If the context is insufficient, clearly say that additional investigation is required.

EXTRACTED ISSUE:
{structured_issue}

RETRIEVED KNOWLEDGE:
{retrieved_documents}

USER MESSAGE:
{user_message}
```

The response should be concise enough for a chat interaction while still providing actionable troubleshooting steps.

---

## 10. API Requirements

A minimal API may expose an endpoint similar to:

```http
POST /chat
Content-Type: multipart/form-data
```

Request:

- `message`: optional customer/support message.
- `image`: screenshot file.
- `conversation_id`: optional identifier.

Response:

```json
{
  "answer": "The screenshot indicates an unauthorized access error. ...",
  "extracted_info": {
    "error_code": "ERR-401",
    "error_message": "Unauthorized access"
  },
  "sources": [
    {
      "id": "KB-001",
      "title": "Unauthorized access error",
      "source": "support_guide.md",
      "score": 0.87
    }
  ]
}
```

The exact API framework is implementation-dependent.

---

## 11. Non-Functional Requirements

### NFR-01 — Modularity

The code should be organized into clear modules with separation between UI, API/orchestration, screenshot extraction, retrieval, and response generation.

### NFR-02 — Reproducibility

The project shall provide setup instructions that allow another developer to run the chatbot locally.

At minimum, provide:

- Dependency installation instructions.
- Environment-variable configuration.
- Knowledge-base initialization instructions.
- Milvus setup instructions.
- Application startup instructions.

### NFR-03 — Configuration

Secrets such as LLM API keys must not be hard-coded in source code. Use environment variables or an equivalent configuration mechanism.

### NFR-04 — Observability

The application should log major pipeline stages, such as:

- Image received.
- Extraction completed.
- Number of retrieved documents.
- Response generation completed.
- Errors/failures.

Logs should not expose sensitive customer information unnecessarily.

### NFR-05 — Testability

Core modules should be testable independently. At minimum, the project should include tests for:

- Screenshot extraction.
- Query construction.
- Knowledge retrieval.
- API request handling.

### NFR-06 — Performance

The system should provide a responsive interactive experience for a local/demo environment. The solution document should report representative latency for:

- Screenshot preprocessing/OCR.
- Vector retrieval.
- Response generation.
- End-to-end request processing.

---

## 12. Acceptance Criteria

The assignment is considered complete when all of the following are satisfied:

### AC-01 — Screenshot Submission

A user can upload a screenshot through the chat window and submit it successfully.

### AC-02 — Non-LLM Extraction

The system extracts relevant information from the screenshot using OCR/computer-vision/rule-based processing without using an LLM for extraction.

### AC-03 — Structured Issue

The extracted information is converted into a structured representation that can be inspected or logged.

### AC-04 — Milvus Retrieval

The structured issue is used to search a Milvus Lite or Milvus Standalone knowledge base and retrieve relevant knowledge.

### AC-05 — Grounded Response

The chatbot generates a support response based on the retrieved knowledge.

### AC-06 — Response in Chat

The generated response is displayed in the chat interface.

### AC-07 — No-Knowledge Case

When no sufficiently relevant knowledge is retrieved, the chatbot does not fabricate a specific resolution and instead indicates that additional investigation is needed.

### AC-08 — Reproducible Demo

A reviewer can follow the README/setup instructions and run the system locally.

### AC-09 — Documentation

The repository contains a solution briefing document of no more than 5 pages describing the architecture, implementation, design decisions, and demonstration results.

---

## 13. Suggested Evaluation Scenarios

The implementation should be demonstrated using several screenshot cases:

| Scenario | Expected Behavior |
|---|---|
| Known error code | Correctly extract code and retrieve matching knowledge |
| Known error message without code | Retrieve relevant troubleshooting information from the extracted text |
| Screenshot containing unrelated text | Ignore or down-weight irrelevant information |
| Poor-quality screenshot | Apply preprocessing and return the best available extraction |
| No matching knowledge | Clearly report insufficient knowledge instead of inventing a solution |
| Milvus unavailable | Return a controlled service error |
| LLM failure | Return a controlled generation error |

---

## 14. Suggested Evaluation Metrics

The solution briefing should report measurable results where practical.

### Extraction

- OCR/text extraction accuracy on a small labeled screenshot set.
- Error-code extraction accuracy.
- Key-field extraction precision/recall where labels are available.

### Retrieval

- Recall@K.
- Precision@K, where a relevance judgment set is available.
- Retrieval latency.

### Response Generation

- Response latency.
- Groundedness/faithfulness based on manual evaluation.
- Helpfulness based on manual evaluation against expected solutions.

### End-to-End

- Successful request rate.
- End-to-end latency.
- Failure handling behavior.

The assignment does not require a specific metric target unless additional targets are provided by the evaluator.

---

## 15. Deliverables

### D-01 — Source Code

A complete runnable codebase containing:

- Chat interface.
- Screenshot processing.
- Non-LLM information extraction.
- Embedding and retrieval logic.
- Milvus integration.
- LLM-based response generation.
- Configuration and setup scripts.
- Sample knowledge data.
- Tests where applicable.

### D-02 — README

The repository shall contain instructions covering:

1. Prerequisites.
2. Installation.
3. Environment configuration.
4. Milvus Lite setup or Milvus Standalone setup.
5. Knowledge-base ingestion.
6. Application startup.
7. Example usage.

### D-03 — Solution Briefing Document

Provide a document with a maximum length of **5 pages** covering:

1. Problem understanding.
2. System architecture.
3. Screenshot extraction approach and why it does not use an LLM.
4. Knowledge-base design and Milvus setup.
5. Retrieval approach.
6. Response-generation approach.
7. Key implementation/design decisions.
8. Evaluation results and example conversations.
9. Limitations and possible future improvements.

---

## 16. Definition of Done

The project is ready for evaluation when:

- The application starts successfully from documented instructions.
- A screenshot can be uploaded from the chat UI.
- Required information can be extracted without an LLM.
- The extracted information can be used to retrieve relevant records from Milvus.
- Retrieved records can be passed to the response generator.
- A useful response is returned to the chat UI.
- No-match and component-failure cases are handled gracefully.
- The knowledge base can be rebuilt from sample source documents.
- The solution is documented in a briefing document of no more than 5 pages.

---

## 17. Reference Documentation

- Milvus Lite — Run Milvus Lite Locally: https://milvus.io/docs/milvus_lite.md
- Milvus Standalone — Docker prerequisites: https://milvus.io/docs/prerequisite-docker.md

The current Milvus documentation states that Milvus Lite uses the Python SDK locally, supports vector persistence and similarity search, and shares the client API with Milvus Standalone. It is intended for small-scale vector search; larger deployments should use Standalone or Distributed Milvus. citeturn671435view0

---

## 18. Implementation Notes

The requirements intentionally do not mandate a specific programming language, web framework, OCR engine, embedding model, or LLM provider, except where the mandatory constraints above apply. These choices should be justified in the solution briefing document.

A strong implementation should keep the following boundaries explicit:

```text
Screenshot
   -> OCR / CV / Rules
   -> Structured Issue
   -> Embedding
   -> Milvus Retrieval
   -> Retrieved Context
   -> LLM Response Generation
   -> Chat Response
```

The most important architectural constraint is that **information extraction from the screenshot and natural-language response generation are separate responsibilities**. The first must not depend on an LLM; the second may use an LLM and should be grounded by the Milvus retrieval results.
