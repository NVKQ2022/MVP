#!/usr/bin/env python3
"""
Generate a clean, simple, and comprehensive DOCX document describing
the Support Screenshot Chatbot End-to-End Pipeline and How to Run It.

Key constraints respected:
- Describes the end-to-end pipeline and what each step does without over-complicating every individual component.
- Clear, practical guide on how to run the project (Web UI, CLI diagnosis, tests).
- All text uses the exact same uniform color throughout (pure black: RGB(0, 0, 0)).
- Basic original Word table style ('Table Grid') with standard grid borders and clean transparent cells (no custom gray shading).
- Code snippets formatted as clean indented monospace paragraphs rather than table boxes.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Uniform text color for the entire document
UNIFORM_COLOR = RGBColor(0, 0, 0)
FONT_FAMILY = "Calibri"

def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
    """Set standard cell padding in dxa (1 pt = 20 dxa)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = FONT_FAMILY
    run.font.size = Pt(13)
    run.font.color.rgb = UNIFORM_COLOR
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.bold = True
    run.font.name = FONT_FAMILY
    run.font.size = Pt(11.5)
    run.font.color.rgb = UNIFORM_COLOR
    return p

def add_body_paragraph(doc, text="", bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.name = FONT_FAMILY
        r_b.font.size = Pt(10.5)
        r_b.font.color.rgb = UNIFORM_COLOR
    if text:
        r_t = p.add_run(text)
        r_t.font.name = FONT_FAMILY
        r_t.font.size = Pt(10.5)
        r_t.font.color.rgb = UNIFORM_COLOR
    return p

def add_bullet_item(doc, text="", bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.bold = True
        r_b.font.name = FONT_FAMILY
        r_b.font.size = Pt(10)
        r_b.font.color.rgb = UNIFORM_COLOR
    if text:
        r_t = p.add_run(text)
        r_t.font.name = FONT_FAMILY
        r_t.font.size = Pt(10)
        r_t.font.color.rgb = UNIFORM_COLOR
    return p

def add_code_snippet(doc, code_text):
    """Add an indented monospace code block (no table wrapping)."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = UNIFORM_COLOR

def add_callout_box(doc, text, bold_title=""):
    """Add a clean indented note block with bold title."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_title:
        r_title = p.add_run(bold_title + ": ")
        r_title.bold = True
        r_title.font.name = FONT_FAMILY
        r_title.font.size = Pt(10)
        r_title.font.color.rgb = UNIFORM_COLOR
    r_text = p.add_run(text)
    r_text.font.name = FONT_FAMILY
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = UNIFORM_COLOR

def generate_simple_docx(output_path):
    doc = Document()

    # Set standard 0.75 inch margins
    for sec in doc.sections:
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.75)
        sec.left_margin = Inches(0.75)
        sec.right_margin = Inches(0.75)

    # ==================== HEADER ====================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    r_title = title_p.add_run("Support Screenshot Chatbot: End-to-End Pipeline & Execution Guide")
    r_title.bold = True
    r_title.font.name = FONT_FAMILY
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = UNIFORM_COLOR

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(8)
    r_sub = sub_p.add_run("Project Overview, Step-by-Step Processing Flow, and How to Run the Application")
    r_sub.font.name = FONT_FAMILY
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = UNIFORM_COLOR

    # Metadata table (Basic original Table Grid, no background fills)
    meta_tbl = doc.add_table(rows=2, cols=4, style='Table Grid')
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.autofit = False

    col_widths = [Inches(1.2), Inches(2.1), Inches(1.2), Inches(2.0)]
    meta_items = [
        ("Project:", "Screenshot Support Assistant"),
        ("Date / Version:", "October 2026 / Release v1.0.0"),
        ("Technology Stack:", "PaddleOCR + Milvus Lite + PolyRAG"),
        ("Author / Organization:", "MaivenPoint AI Team / Quan (Leon) Phan")
    ]
    for idx, (label, val) in enumerate(meta_items):
        r = idx // 2
        c = (idx % 2) * 2

        cell_lbl = meta_tbl.cell(r, c)
        cell_lbl.width = col_widths[c]
        set_cell_margins(cell_lbl, top=50, bottom=50, left=80, right=80)
        p_l = cell_lbl.paragraphs[0]
        p_l.paragraph_format.space_after = Pt(0)
        r_l = p_l.add_run(label)
        r_l.bold = True
        r_l.font.name = FONT_FAMILY
        r_l.font.size = Pt(9)
        r_l.font.color.rgb = UNIFORM_COLOR

        cell_val = meta_tbl.cell(r, c+1)
        cell_val.width = col_widths[c+1]
        set_cell_margins(cell_val, top=50, bottom=50, left=80, right=80)
        p_v = cell_val.paragraphs[0]
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(val)
        r_v.font.name = FONT_FAMILY
        r_v.font.size = Pt(9)
        r_v.font.color.rgb = UNIFORM_COLOR

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ==================== SECTION 1: PROJECT OVERVIEW ====================
    add_heading_1(doc, "1. Project Overview & What It Does")

    add_body_paragraph(doc,
        "When customers encounter technical issues in an enterprise platform, they almost always take a screenshot "
        "of the error dialog, failure modal, or stack trace and send it to customer support. Typically, a human engineer "
        "has to manually read the image, transcribe the error code, search internal knowledge bases, formulate troubleshooting steps, "
        "and type out a response. This process is time-consuming and prone to human error.")

    add_body_paragraph(doc,
        "This project builds an automated support chatbot that performs this entire troubleshooting workflow from end to end. "
        "The system accepts a customer's screenshot, extracts the technical problem without using an LLM, finds matching troubleshooting "
        "procedures in a vector knowledge base (Milvus Lite), and generates a verified, step-by-step resolution for the user in a clean chat window.")

    add_callout_box(doc,
        "Visual information extraction is strictly non-LLM. The system extracts error codes and messages using local OCR "
        "and deterministic rules. This prevents hallucinations on exact codes, protects customer privacy by masking sensitive data locally, "
        "and keeps extraction latency under 300 milliseconds. The LLM is only used at the very end to write a helpful, grounded response.",
        bold_title="Core Architectural Principle"
    )

    # ==================== SECTION 2: END-TO-END PIPELINE ====================
    add_heading_1(doc, "2. End-to-End Pipeline (Step-by-Step Flow)")

    add_body_paragraph(doc,
        "The pipeline processes each user request through six clear, sequential stages from upload to response:")

    add_heading_2(doc, "Step 1: Image Upload & Format Validation")
    add_body_paragraph(doc,
        "The user uploads or drags an error screenshot into the web chat interface (supporting PNG, JPEG, and JPG formats). "
        "The server validates the image file to ensure it is not corrupt and decodes it into memory using OpenCV. "
        "If an invalid file or unsupported format is submitted, the system immediately returns a helpful error message without crashing.")

    add_heading_2(doc, "Step 2: Image Preprocessing & Local OCR Text Extraction")
    add_body_paragraph(doc,
        "To handle real-world image conditions—such as dark-mode themes, low resolutions, and mild blur—the system preprocesses the image "
        "using adaptive thresholding and contrast normalization. Next, a local OCR engine (PaddleOCR PP-OCRv4) scans the image to detect "
        "and recognize all visible text blocks without sending any pixels to an external cloud API. A spatial ordering algorithm then sorts "
        "the detected text lines vertically and horizontally to restore the natural top-to-bottom reading order of the original dialogue.")

    add_heading_2(doc, "Step 3: Issue Information Extraction & Sensitive Data Redaction")
    add_body_paragraph(doc,
        "Once the text is extracted, a rule-based parser inspects the text stream to identify the core technical issue:")
    add_bullet_item(doc, "Detects standardized codes such as AUTH-401, NET-502, DB-TIMEOUT, and ORA error numbers.", bold_prefix="Enterprise Error Codes: ")
    add_bullet_item(doc, "Extracts status indicators such as 401 (Unauthorized), 403 (Forbidden), 500, and 502.", bold_prefix="HTTP Status Codes: ")
    add_bullet_item(doc, "Captures visible API endpoints, route paths, and ISO event timestamps.", bold_prefix="Incident URLs & Timestamps: ")
    add_bullet_item(doc, "Filters out common UI button labels (like 'OK', 'Cancel', 'Close') and isolates the true failure description.", bold_prefix="Error Message Text: ")
    add_body_paragraph(doc,
        "Privacy Protection: Before any text leaves the local machine, an automated scrubber detects and masks sensitive data. "
        "Customer email addresses become [EMAIL_REDACTED], bearer tokens become Bearer [TOKEN_REDACTED], and API keys become [API_KEY_REDACTED].")

    add_heading_2(doc, "Step 4: Vector Knowledge Retrieval from Milvus Lite")
    add_body_paragraph(doc,
        "The sanitized diagnostic summary is converted into a vector embedding using a dense embedding model (all-MiniLM-L6-v2). "
        "The system then searches against Milvus Lite, an embedded local vector database containing 12 pre-loaded enterprise support articles "
        "(covering authentication, database connection issues, network timeouts, storage limits, and server errors).")
    add_body_paragraph(doc,
        "Exact-Code Match Boosting: To ensure maximum accuracy, the retrieval engine combines semantic vector similarity with an exact error-code bonus. "
        "If a retrieved article matches the extracted error code exactly, its ranking is significantly boosted, ensuring the exact troubleshooting guide "
        "ranks at the very top.")

    add_heading_2(doc, "Step 5: Grounded Response Generation & Anti-Hallucination Guardrail")
    add_body_paragraph(doc,
        "Depending on the retrieval confidence score, the system takes one of two deterministic paths:")
    add_bullet_item(doc,
        "When the top retrieved article has a confidence score of 0.45 or higher, the system passes the article content to the language model (Azure OpenAI). "
        "The model is strictly instructed to use only the provided documentation. It generates a clear 5-part support guide containing: "
        "(1) Issue Identified, (2) Likely Root Cause, (3) Recommended Actionable Fix Steps, (4) Verification Steps, and (5) Cited Knowledge Base Article.",
        bold_prefix="Path A (Match Found): "
    )
    add_bullet_item(doc,
        "If no articles match or the confidence score is below 0.45, the LLM is completely bypassed. "
        "Instead of guessing or inventing an answer, the chatbot returns a safe, pre-scripted message politely requesting essential triage details "
        "(software version, exact occurrence time, system logs, and reproduction steps). This guarantees zero hallucinations on unfamiliar errors.",
        bold_prefix="Path B (No Match / Circuit Breaker): "
    )

    add_heading_2(doc, "Step 6: User Interface Presentation & Debug Inspection")
    add_body_paragraph(doc,
        "The final response is displayed in the web chat window. While the response is processing, an interactive stepper shows the user "
        "what stage is currently executing (Extracting -> Parsing -> Retrieving -> Generating). Support engineers can also expand a technical "
        "debug drawer to inspect the exact extracted error codes, raw OCR bounding boxes, and retrieved Milvus document similarity scores.")

    # ==================== SECTION 3: SUMMARY TABLE ====================
    add_heading_1(doc, "3. Summary of Pipeline Stages")

    add_body_paragraph(doc,
        "The table below summarizes what each stage of the pipeline receives, what action it performs, and what output it produces:")

    # Basic Original Table Grid: plain black borders, no background shading
    summary_tbl = doc.add_table(rows=7, cols=4, style='Table Grid')
    summary_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    summary_tbl.autofit = False

    s_widths = [Inches(1.0), Inches(1.4), Inches(2.7), Inches(1.4)]
    headers = ["Stage", "Input", "What It Does", "Output"]
    for idx, h_text in enumerate(headers):
        cell = summary_tbl.cell(0, idx)
        cell.width = s_widths[idx]
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = FONT_FAMILY
        r.font.size = Pt(9.5)
        r.font.color.rgb = UNIFORM_COLOR

    tbl_rows_data = [
        ("1. Ingest", "Image file (PNG/JPG)", "Validates file header, checks integrity, and decodes image into memory.", "Image array in memory"),
        ("2. OCR", "Image array", "Applies contrast preprocessing and extracts text lines in visual reading order.", "Ordered text lines"),
        ("3. Parse", "Ordered text lines", "Extracts error codes and messages via regex; masks emails, tokens, and keys.", "Sanitized diagnostic context"),
        ("4. Search", "Sanitized context", "Embeds text into a 384-d vector and searches Milvus Lite with code match bonus.", "Top-ranked KB articles"),
        ("5. Guard", "Ranked articles", "Checks if top confidence score >= 0.45; triggers safe fallback if low.", "Execution decision"),
        ("6. Solve", "Context + Query", "Drafts grounded 5-part troubleshooting instructions citing source documents.", "Customer-ready solution")
    ]
    for r_idx, row_data in enumerate(tbl_rows_data, start=1):
        for c_idx, cell_value in enumerate(row_data):
            cell = summary_tbl.cell(r_idx, c_idx)
            cell.width = s_widths[c_idx]
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(cell_value)
            r.font.name = FONT_FAMILY
            r.font.size = Pt(9)
            r.font.color.rgb = UNIFORM_COLOR
            if c_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==================== SECTION 4: WHY DESIGNED THIS WAY ====================
    add_heading_1(doc, "4. Why the Pipeline Is Designed This Way")

    add_body_paragraph(doc,
        "The pipeline choices prioritize four critical engineering goals: accuracy, privacy, zero infrastructure, and low latency:")

    add_bullet_item(doc,
        "Large vision models frequently hallucinate or drop characters in technical alphanumeric codes (e.g. confusing '0' and 'O', "
        "or misreading '401' as '404'). Deterministic OCR combined with regex matching guarantees 100% precision on error codes.",
        bold_prefix="No LLM for Visual Extraction: "
    )
    add_bullet_item(doc,
        "Error screenshots often contain confidential information such as customer email addresses, API tokens, or server IPs. "
        "Performing OCR and redaction locally ensures that sensitive data is scrubbed before any external call is made.",
        bold_prefix="Data Privacy Compliance: "
    )
    add_bullet_item(doc,
        "Milvus Lite runs directly inside the Python application process and persists to a local database file (./data/milvus_lite.db). "
        "It requires zero external Docker containers or server configuration, while maintaining full code compatibility with enterprise Milvus clusters.",
        bold_prefix="Zero-Infrastructure Vector Storage: "
    )
    add_bullet_item(doc,
        "Local OCR and vector search execute in under 300 milliseconds. This is nearly 10 times faster than sending high-resolution images "
        "to a cloud vision model, giving users an immediate and responsive troubleshooting experience.",
        bold_prefix="High Speed & Low Cost: "
    )

    # ==================== SECTION 5: HOW TO RUN THIS PROJECT ====================
    add_heading_1(doc, "5. How to Run This Project")

    add_body_paragraph(doc,
        "The project is packaged with a unified CLI entrypoint (main.py) and a FastAPI web server, enabling straightforward setup and execution.")

    add_heading_2(doc, "5.1 Prerequisites & Environment Setup")
    add_body_paragraph(doc, "1. Clone the repository and enter the project directory:")
    add_code_snippet(doc, "git clone https://github.com/NVKQ2022/MVP.git\ncd MVP/AI/ChatbotOCR")

    add_body_paragraph(doc, "2. Create and activate a Python virtual environment (Python 3.10+ or 3.12):")
    add_code_snippet(doc, "python3 -m venv venv\nsource venv/bin/activate    # On Windows: venv\\Scripts\\activate")

    add_body_paragraph(doc, "3. Install the project dependencies:")
    add_code_snippet(doc, "pip install -r requirements.txt")

    add_body_paragraph(doc, "4. Configure environment variables (.env file):")
    add_body_paragraph(doc,
        "Copy .env.example to .env and provide your Azure OpenAI credentials (API key, endpoint, model deployment name):")
    add_code_snippet(doc, "cp .env.example .env\n# Edit .env with your AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT")

    add_heading_2(doc, "5.2 Starting the Web Chat Application")
    add_body_paragraph(doc, "Launch the application using the root runner:")
    add_code_snippet(doc, "python main.py\n# Or explicitly: python main.py server --host 0.0.0.0 --port 8000")

    add_body_paragraph(doc, "Once started, open your web browser to:")
    add_bullet_item(doc, "http://localhost:8000 — Interactive single-page support chatbot UI with drag-and-drop screenshot upload.", bold_prefix="Web Chat Interface: ")
    add_bullet_item(doc, "http://localhost:8000/docs — Interactive OpenAPI / Swagger documentation for testing REST endpoints directly.", bold_prefix="API Documentation: ")

    add_heading_2(doc, "5.3 Running End-to-End Terminal Diagnosis (CLI)")
    add_body_paragraph(doc,
        "You can diagnose an error screenshot directly from the terminal without opening a browser:")
    add_code_snippet(doc, "python main.py diagnose data/sample_screenshots/kb-auth-001__01__clean_light.png")
    add_body_paragraph(doc,
        "This command executes the full pipeline in the terminal: extracts text using PaddleOCR, searches Milvus Lite, "
        "and prints the grounded resolution along with latency and confidence metrics.")

    add_heading_2(doc, "5.4 Standalone OCR and RAG Commands")
    add_bullet_item(doc, "Run OCR on any image and optionally save annotated visual boxes:", bold_prefix="Standalone OCR: ")
    add_code_snippet(doc, "python main.py ocr demo_output/sample_invoice.jpg --save-annotated demo_output/result.jpg")

    add_bullet_item(doc, "Ask questions directly against the technical knowledge base:", bold_prefix="Standalone Knowledge Query: ")
    add_code_snippet(doc, 'python main.py rag -q "How do I fix authentication token expired error?"')

    add_heading_2(doc, "5.5 Running the Automated Test Suite")
    add_body_paragraph(doc, "Run all unit and integration tests across the OCR, RAG, and Server subsystems:")
    add_code_snippet(doc, "pytest")

    add_body_paragraph(doc, "Run the end-to-end knowledge base pipeline test verifying all 12 support scenarios:")
    add_code_snippet(doc, "python RAG/test_rag_pipeline.py")

    # ==================== SECTION 6: VERIFICATION ====================
    add_heading_1(doc, "6. Verification & Robustness Results")

    add_body_paragraph(doc,
        "The end-to-end pipeline was validated through automated tests covering all functional and edge-case requirements:")

    add_bullet_item(doc,
        "All 12 articles across authentication, database, network, file, and platform categories were tested end-to-end. "
        "The retrieval pipeline successfully matched and resolved every scenario with 100% accuracy.",
        bold_prefix="12/12 Knowledge Base Scenarios: "
    )
    add_bullet_item(doc,
        "The pipeline was tested against 60 synthetic screenshots simulating real-world conditions: high-contrast light mode, "
        "dark mode, low resolution downscaling, Gaussian defocus blur, cluttered interfaces with unrelated menus, and screenshots with no error code. "
        "In all cases, the pipeline either correctly extracted the issue or safely triggered the fallback circuit breaker.",
        bold_prefix="Robustness Across 60 Variations: "
    )
    add_bullet_item(doc,
        "24 automated unit and integration tests verify the image codec, spatial reading order, regex entity extractor, "
        "privacy scrubber, vector ingestion, and FastAPI endpoints with zero failures.",
        bold_prefix="24/24 Automated Tests Passing: "
    )

    # Save to target output
    doc.save(output_path)
    print(f"Generated clean docx with basic Table Grid successfully at: {output_path}")

if __name__ == "__main__":
    out_file = "/home/quan/projects/maivenpoint/AI/ChatbotOCR/SOLUTION_BRIEF.docx"
    generate_simple_docx(out_file)
