"""Generate a publication-grade PDF document for Phase 4:
NL-to-SQL Backend Architectural Walkthrough & Jury Defense Guide.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
    ListFlowable,
    ListItem,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass calculation for 'Page X of Y' and adds running headers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        page_w, page_h = letter
        
        # We don't draw running header on page 1 (cover-style header on page 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(54, page_h - 36, "NL-to-SQL ARCHITECTURAL WALKTHROUGH & JURY DEFENSE GUIDE")
            self.setFont("Helvetica", 8)
            self.drawRightString(page_w - 54, page_h - 36, "PHASE 4: SYSTEM ARCHITECTURE")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(54, page_h - 42, page_w - 54, page_h - 42)

        # Running footer on every page
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(54, 45, page_w - 54, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 32, "Confidential — Hackathon Jury Reference Document")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - 54, 32, page_str)
        self.restoreState()


def create_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Slate
    c_accent = colors.HexColor("#2563EB")     # Royal Blue
    c_accent_dark = colors.HexColor("#1D4ED8")
    c_body = colors.HexColor("#1E293B")       # Dark Charcoal body text
    c_muted = colors.HexColor("#64748B")      # Slate muted
    c_code_bg = colors.HexColor("#F8FAFC")    # Cool light gray
    c_card_bg = colors.HexColor("#F1F5F9")    # Soft gray background
    c_card_border = colors.HexColor("#CBD5E1")
    c_q_color = colors.HexColor("#1E40AF")     # Dark Blue
    c_warning_bg = colors.HexColor("#FEF3C7") # Amber light
    c_warning_border = colors.HexColor("#F59E0B")

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=14,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.white,
        spaceAfter=0,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=c_accent_dark,
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=c_body,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_body,
        leftIndent=12,
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
    )

    judge_q_style = ParagraphStyle(
        "JudgeQ",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13.5,
        textColor=c_q_color,
        spaceAfter=3,
    )

    judge_a_style = ParagraphStyle(
        "JudgeA",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
    )

    story = []

    # Title Banner
    story.append(Paragraph("NL-to-SQL Backend Engine", title_style))
    story.append(Paragraph("Phase 4 Architecture Walkthrough & Technical Jury Defense Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=10))

    # Introduction / Executive Summary Box
    intro_html = (
        "<b>System Overview:</b> This document provides an in-depth, code-level architectural walkthrough "
        "of the <code>nl2sql-backend</code> service. It breaks down each core file in order of runtime execution, "
        "covering engineering rationale, function-level mechanics, limitations, and model jury Q&A. "
        "Special focus is given to <b>deterministic AST validation</b>, <b>prompt engineering mechanics</b>, "
        "and <b>crash-proof pipeline resilience</b>."
    )
    intro_table = Table(
        [[Paragraph(intro_html, body_style)]],
        colWidths=[504],
    )
    intro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_card_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(intro_table)
    story.append(Spacer(1, 14))

    # Helper function to create section header banner
    def create_section_header(number: str, filename: str, title: str):
        content = [
            Paragraph(f"<b>{number}. {filename}</b> — <font size=9>{title}</font>", h1_style)
        ]
        t = Table([[content[0]]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_primary),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # Helper to render Judge Q&A Card
    def create_judge_card(question: str, answer: str):
        content = [
            Paragraph(f"<b>Judge Question:</b> \"{question}\"", judge_q_style),
            Paragraph(f"<b>Model Answer:</b> \"{answer}\"", judge_a_style),
        ]
        t = Table([[content]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
            ('LINELEFT', (0, 0), (-1, -1), 3, c_accent),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    # Helper to render Code Box
    def create_code_box(code_text: str):
        # Escape XML entities for Paragraph
        escaped = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;")
        p = Paragraph(escaped, code_style)
        t = Table([[p]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_code_bg),
            ('BOX', (0, 0), (-1, -1), 0.75, c_card_border),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # =========================================================================
    # FILE 1: app/config.py
    # =========================================================================
    story.append(create_section_header("1", "app/config.py", "Configuration & Environment Bootstrap"))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("<b>What It Does:</b> Centralizes file-system path resolution and environment variable loading across the backend. It guarantees deterministic absolute paths for databases and data folders while enforcing a strict fail-fast validation check on the Gemini API key upon startup.", body_style))
    
    story.append(Paragraph("<b>Key Mechanics & Objects:</b>", h2_style))
    story.append(Paragraph("• <b>Absolute Path Anchoring:</b> Uses <code>Path(__file__).resolve().parent.parent</code> to pin <code>BASE_DIR</code>, <code>DATA_DIR</code>, and <code>META_DB_PATH</code>, ensuring scripts work regardless of current working directory.", bullet_style))
    story.append(Paragraph("• <b>Hierarchical .env Discovery:</b> Checks <code>nl2sql-backend/.env</code> first, then falls back to workspace root <code>.env</code> before executing <code>load_dotenv()</code>.", bullet_style))
    story.append(Paragraph("• <b>Fail-Fast Validation:</b> Reads <code>GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')</code>. If empty or absent, immediately halts execution with a <code>ValueError</code>.", bullet_style))
    story.append(Paragraph("• <b>Database URI Definitions:</b> Preconfigures connection strings for <code>DATABASE_URL</code> (SQLite meta-database) and file pointers to demo databases (<code>demo_hospital.db</code>, <code>demo_ecommerce.db</code>).", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Built on the <i>Fail-Fast Principle</i>. A system should refuse to boot if required secrets or directories are missing, rather than failing silently mid-demo when a user triggers their first query.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> Configuration is loaded statically into process memory once at startup. Changing environment variables requires a complete process restart; there is no live reload or dynamic vault integration.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "Why hardcode SQLite connection URLs and file paths in config.py instead of passing them dynamically per tenant?",
        "For this prototype, our priority was zero-friction evaluation with self-contained demo databases (hospital and ecommerce). In an enterprise multi-tenant release, config.py would only declare engine pool defaults, while tenant connection strings would be encrypted and dynamically resolved via tenant headers."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 2: app/models/meta_db.py
    # =========================================================================
    story.append(create_section_header("2", "app/models/meta_db.py", "System Persistence & Audit Schema"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> Defines the relational database schema and SQLAlchemy ORM models for tracking system metadata, completely decoupled from business data. It maintains logs of active sessions, conversation threads, generated SQL history, and execution audit trails inside <code>data/meta.db</code>.", body_style))

    story.append(Paragraph("<b>ORM Models & Functions:</b>", h2_style))
    story.append(Paragraph("• <b>SessionModel (<code>sessions</code>):</b> Tracks connection sessions (<code>id</code> UUID string PK, <code>db_type</code>, <code>connected_at</code> timestamp).", bullet_style))
    story.append(Paragraph("• <b>ConversationModel (<code>conversations</code>):</b> Establishes thread groupings (<code>id</code> int PK, <code>session_id</code> FK, <code>created_at</code>).", bullet_style))
    story.append(Paragraph("• <b>QueryHistoryModel (<code>query_history</code>):</b> Persists every query translation (<code>id</code>, <code>session_id</code> FK, <code>nl_query</code> Text, <code>generated_sql</code> Text, <code>confidence</code> Float, <code>query_type</code>, <code>created_at</code>).", bullet_style))
    story.append(Paragraph("• <b>AuditLogModel (<code>audit_log</code>):</b> Captures actual executed SQL, affected row counts, and timestamps for governance.", bullet_style))
    story.append(Paragraph("• <b>init_db():</b> Calls <code>Base.metadata.create_all(bind=engine)</code> to ensure tables exist prior to handling traffic.", bullet_style))
    story.append(Paragraph("• <b>get_db_session():</b> FastAPI dependency generator that yields a SQLAlchemy <code>SessionLocal()</code> instance and ensures deterministic closing in a <code>finally</code> block.", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Complete isolation between metadata and business data. Recording LLM translation history in an independent metadata store ensures we never pollute the user's business database while retaining full telemetry for fine-tuning.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> SQLite file-level locking. Under high concurrent write volumes from multiple simultaneous users, SQLite write contention can produce <code>database is locked</code> timeouts. Production should use PostgreSQL.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "Why did you set connect_args={'check_same_thread': False} in your SQLite engine configuration?",
        "FastAPI processes requests across an asynchronous thread pool. Python's default SQLite driver raises a ProgrammingError if a connection created in one thread is accessed in another. Setting check_same_thread=False, paired with scoped session dependency injection (get_db_session()), enables safe multithreaded operation."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 3: app/services/session_store.py
    # =========================================================================
    story.append(create_section_header("3", "app/services/session_store.py", "In-Memory Session & Schema Cache"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> Provides an ultra-fast in-memory cache for active database connection metadata. It keeps target database paths, table listings, and extracted column schemas readily available in RAM so query translation does not re-inspect the database on every prompt.", body_style))

    story.append(Paragraph("<b>Key Functions:</b>", h2_style))
    story.append(Paragraph("• <b>SESSION_STORE:</b> Global module dictionary (<code>Dict[str, Dict[str, Any]]</code>) storing session state.", bullet_style))
    story.append(Paragraph("• <b>get_session(session_id):</b> Receives session UUID string; returns session metadata dictionary (or <code>None</code>).", bullet_style))
    story.append(Paragraph("• <b>set_session(session_id, data):</b> Receives session UUID and dictionary containing schema, db path, tables; writes directly to memory.", bullet_style))
    story.append(Paragraph("• <b>remove_session(session_id):</b> Evicts session data safely using <code>SESSION_STORE.pop(session_id, None)</code>.", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Database schema introspection (querying PRAGMA table info across dozens of tables) takes 20-50ms over disk I/O. Caching the structured schema in RAM reduces prompt assembly time to sub-millisecond speeds.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> State is volatile and tied to a single process. Restarting the server wipes active sessions, and running multiple Uvicorn worker processes creates split-brain state where sessions are not shared.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "What happens to session_store if we spin up 4 Uvicorn worker processes or deploy behind a load balancer?",
        "In a multi-process or multi-pod setup, an in-memory dictionary cannot be shared across processes. To scale horizontally, we would replace the internal dictionary with a Redis-backed session store using the exact same function signatures (get_session, set_session), applying an automatic 1-hour TTL."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 4: app/routers/connect_db.py
    # =========================================================================
    story.append(create_section_header("4", "app/routers/connect_db.py", "Database Onboarding & Schema Discovery"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> Exposes the <code>POST /api/connect-db</code> endpoint. It verifies the target database exists, uses SQLAlchemy's schema inspection engine to discover all tables and column types, logs the session in <code>meta.db</code>, and primes the in-memory cache.", body_style))

    story.append(Paragraph("<b>Execution Flow (connect_database):</b>", h2_style))
    story.append(Paragraph("1. <b>Input Validation:</b> Validates request payload using Pydantic (<code>Literal['hospital', 'ecommerce']</code>).", bullet_style))
    story.append(Paragraph("2. <b>File Check:</b> Verifies physical SQLite file existence in <code>data/</code>; raises 404 if missing.", bullet_style))
    story.append(Paragraph("3. <b>Dynamic Inspection:</b> Binds <code>sqlalchemy.inspect()</code> to inspect tables and loops through columns to compile a clean dictionary mapping: <code>{table: [{'name': col, 'type': type}]}</code>.", bullet_style))
    story.append(Paragraph("4. <b>Session Registration:</b> Generates a UUID <code>session_id</code> and records a <code>SessionModel</code> row in <code>meta.db</code>.", bullet_style))
    story.append(Paragraph("5. <b>Cache Population:</b> Invokes <code>set_session()</code> to store tables, schema, and path in RAM.", bullet_style))
    story.append(Paragraph("6. <b>Response:</b> Returns <code>ConnectDBResponse</code> with <code>session_id</code>, <code>status='connected'</code>, and <code>tables</code>.", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Schema discovery is completely dynamic. The code contains no hardcoded table or column names; it discovers schema directly from the database engine.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> Currently restricted to local demo databases. It does not yet accept user-uploaded SQLite files or remote JDBC/SQLAlchemy connection strings (PostgreSQL/MySQL).", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "If a database has 500 tables and 10,000 columns, won't extracting and storing the whole schema blow up your prompt?",
        "Yes, full schema injection on massive databases exceeds LLM token limits and harms accuracy. Our planned Phase 5/6 improvement is Schema Pruning using Vector Search (RAG): we index table/column descriptions in FAISS and retrieve only the top 3-5 relevant table schemas per query."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 5: app/services/sql_generator.py (CORE)
    # =========================================================================
    story.append(create_section_header("5", "app/services/sql_generator.py", "Core LLM Translation & Prompt Engineering"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> The translation core of the architecture. It retrieves cached schema context, constructs a grounded code-generation prompt, calls Google's <code>gemini-3.6-flash</code> model, sanitizes the raw output, and parses the structured JSON payload containing SQL, explanation, and confidence.", body_style))

    story.append(Paragraph("<b>Internal Mechanics:</b>", h2_style))
    story.append(Paragraph("• <b>_clean_json_string(text):</b> Strips markdown code fences (<code>```json ... ```</code> or <code>``` ... ```</code>) and surrounding whitespace using regular expressions.", bullet_style))
    story.append(Paragraph("• <b>_format_schema_for_prompt(schema):</b> Converts structured schema dictionaries into human-readable text (e.g. <code>Table 'patients': id (INTEGER), name (TEXT)...</code>).", bullet_style))
    story.append(Paragraph("• <b>_validate_result(data):</b> Validates that output is a dictionary with non-empty <code>sql</code> and <code>explanation</code> strings, casting <code>confidence</code> to a float.", bullet_style))
    story.append(Paragraph("• <b>generate_sql(session_id, nl_question):</b> Compiles prompt, invokes <code>gemini-3.6-flash</code>, parses JSON, and contains an automated self-healing retry prompt if JSON parsing fails on attempt 1.", bullet_style))

    story.append(Paragraph("<b>The Exact Prompt Sent to Gemini 3.6 Flash:</b>", h2_style))
    exact_prompt_text = (
        "You are an expert SQLite SQL engineer.\n"
        "Given the following SQLite database schema:\n"
        "Table 'patients': id (INTEGER), name (VARCHAR), age (INTEGER), gender (VARCHAR), diagnosis (VARCHAR)\n"
        "Table 'doctors': id (INTEGER), name (VARCHAR), specialty (VARCHAR)\n\n"
        "User Question: \"{nl_question}\"\n\n"
        "Instructions:\n"
        "1. Generate a valid, executable SQLite query that accurately answers the user's question.\n"
        "   If the user asks to delete, insert, or update data, generate that query directly.\n"
        "2. Return ONLY a single valid JSON object. Do not include markdown code fences, backticks, or extra text.\n"
        "3. The JSON object must strictly have this exact structure:\n"
        "{\n"
        '  "sql": "SQL query here",\n'
        '  "explanation": "Brief explanation of why this query answers the question",\n'
        '  "confidence": 0.95\n'
        "}"
    )
    story.append(create_code_box(exact_prompt_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Why Structured / Code-Generation Prompting & JSON Mode?</b>", h2_style))
    story.append(Paragraph("• <b>Deterministic Code Generation:</b> Unlike open-ended conversational prompting, code generation treats the LLM as a compiler. We constrain the dialect (SQLite), ground the context (schema), and demand exact structure.", bullet_style))
    story.append(Paragraph("• <b>Why JSON over Freeform Text:</b> A backend pipeline cannot reliably parse conversational text ('Sure, here is your query: SELECT...'). Returning raw SQL alone discards the explanation and confidence metrics. Returning a structured JSON object cleanly packages the executable code (<code>sql</code>), user-facing reasoning (<code>explanation</code>), and risk assessment (<code>confidence</code>) in a machine-parseable contract.", bullet_style))

    # Phase 3 Bug Story Box
    story.append(Spacer(1, 4))
    bug_story_html = (
        "<b>The Phase 3 Bug Story (Great Presentation Narrative):</b><br/>"
        "In our initial prompt, Instruction 1 strictly commanded: <i>'Generate a valid, executable SQLite SELECT query.'</i><br/>"
        "When we tested Case B with a write query (<i>'Delete all patients older than 90'</i>), Gemini followed our prompt instruction rather than user intent and generated: <code>SELECT * FROM patients WHERE age &gt; 90</code> to 'view' the patients to be deleted! "
        "The model actively masked the user's write intent, bypassing the test suite.<br/>"
        "<b>The Fix:</b> We modified the instruction to generate write statements directly (<code>DELETE FROM ...</code>) when requested. "
        "This allowed our dedicated AST validator (<code>sql_validator.py</code>) to intercept the operation, block execution, and return a clean error without modifying the database. "
        "<b>Lesson for Judges:</b> Never rely on the LLM prompt as your security boundary. Prompts translate intent; deterministic code enforces security."
    )
    story_table = Table([[Paragraph(bug_story_html, body_style)]], colWidths=[504])
    story_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_warning_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_warning_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(story_table)
    story.append(Spacer(1, 6))

    story.append(create_judge_card(
        "Why didn't you use Gemini's native response_schema or response_mime_type='application/json'?",
        "We chose a decoupled prompt-and-sanitization architecture with automated retry fallbacks to keep our pipeline model-agnostic. This design enables us to switch LLM providers (e.g. Claude 3.5, GPT-4o) or run a self-hosted open-source model (DeepSeek-Coder via Ollama) without refactoring SDK-specific schema bindings."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 6: app/services/sql_validator.py
    # =========================================================================
    story.append(create_section_header("6", "app/services/sql_validator.py", "AST Security & Read-Only Enforcement"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> Serves as the deterministic security gateway. It parses the generated SQL string into an Abstract Syntax Tree (AST) using <code>sqlglot</code>, verifying syntax correctness and strictly enforcing read-only (<code>SELECT</code>) queries while blocking any mutation, insertion, or administrative commands.", body_style))

    story.append(Paragraph("<b>Validation Logic (validate_sql):</b>", h2_style))
    story.append(Paragraph("1. <b>Empty Check:</b> Rejects empty or whitespace-only inputs immediately as <code>syntax_error</code>.", bullet_style))
    story.append(Paragraph("2. <b>AST Parsing:</b> Executes <code>sqlglot.parse(sql_string, read='sqlite')</code>. Catches any <code>ParseError</code> and returns a clean syntax error dictionary.", bullet_style))
    story.append(Paragraph("3. <b>Token Clean-Up:</b> Strips trailing null statements (such as extra semicolons).", bullet_style))
    story.append(Paragraph("4. <b>Statement Type Verification:</b> Inspects each statement node: <code>if not isinstance(stmt, (exp.Select, exp.Query)): return {'valid': False, 'reason': 'write_not_supported', 'message': 'This version only supports read (SELECT) queries.'}</code>.", bullet_style))
    story.append(Paragraph("5. <b>Stacked Query Prevention:</b> Checks <code>if len(statements) != 1</code> to block multi-statement SQL injection attacks (e.g. <code>SELECT 1; DROP TABLE users;</code>).", bullet_style))
    story.append(Paragraph("6. <b>Success:</b> Returns <code>{'valid': True}</code>.", bullet_style))

    story.append(Paragraph("<b>Design Decision (Why sqlglot over Regex?):</b> Regex keyword matching is notoriously fragile. A benign query like <code>SELECT * FROM orders WHERE status = 'DROP_SHIP'</code> would trigger a false positive on 'DROP'. Conversely, attackers can bypass regex with comments (<code>/*comment*/DROP table</code>). <code>sqlglot</code> analyzes semantic syntax trees with mathematical certainty.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> Lacks semantic schema checking. <code>SELECT fake_col FROM patients</code> is syntactically a valid SELECT AST, so it passes validation and relies on the execution engine to catch the missing column.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "Does your validator catch write operations disguised inside CTEs (Common Table Expressions)?",
        "Yes. In sqlglot, statement classification inspects the root operational node. In a statement like 'WITH cte AS (SELECT 1) DELETE FROM patients...', the root node is an exp.Delete instance, which fails our exp.Select/exp.Query type check and is rejected."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 7: app/services/execution_engine.py
    # =========================================================================
    story.append(create_section_header("7", "app/services/execution_engine.py", "Safe Execution & Error Containment"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> Executes validated read-only queries against the session's target SQLite database and extracts tabular rows into JSON-serializable dictionaries. It guarantees crash resilience by catching database-level runtime exceptions and returning clean error dictionaries.", body_style))

    story.append(Paragraph("<b>Execution Mechanics (run_select):</b>", h2_style))
    story.append(Paragraph("1. <b>Session & File Lookup:</b> Validates active session and confirms target database file exists on disk.", bullet_style))
    story.append(Paragraph("2. <b>Row Factory Configuration:</b> Opens connection with <code>conn.row_factory = sqlite3.Row</code> to enable dictionary-like column access.", bullet_style))
    story.append(Paragraph("3. <b>Execution & Extraction:</b> Runs <code>cursor.execute(sql)</code>, calls <code>cursor.fetchall()</code>, and uses list comprehension <code>[dict(row) for row in rows]</code> to serialize data.", bullet_style))
    story.append(Paragraph("4. <b>Exception Containment:</b> Wraps execution in <code>try...except Exception as exc:</code>, returning <code>{'error': str(exc)}</code> rather than crashing.", bullet_style))
    story.append(Paragraph("5. <b>Connection Cleanup:</b> Employs a <code>finally:</code> block to ensure <code>conn.close()</code> is always executed, preventing lock leaks.", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Uses lightweight raw <code>sqlite3.Row</code> instead of SQLAlchemy ORM models. Because dynamically generated SQL produces varying output column sets for every query, raw row dictionary mapping provides maximum performance and flexibility.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> No query timeout or pagination guardrails. An accidental Cartesian join or full scan across a million-row table could cause high latency or memory spikes without an enforced <code>LIMIT</code>.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "What prevents a user query from running indefinitely or causing a Denial of Service on the database?",
        "In this phase, we prioritized crash-proofing against errors and syntax failures. For production, we would add two safeguards: an execution timeout using sqlite3.set_progress_handler to abort queries after 3 seconds, and an AST transformation in sqlglot that injects an automatic LIMIT 100 clause."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # FILE 8: app/routers/query.py
    # =========================================================================
    story.append(create_section_header("8", "app/routers/query.py", "Orchestration Pipeline & Contract Normalization"))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>What It Does:</b> The central orchestration router exposing <code>POST /api/query</code>. It coordinates session retrieval, Gemini SQL generation, AST validation, execution, and telemetry logging, returning a reliable, uniform JSON response contract for the frontend.", body_style))

    story.append(Paragraph("<b>Step-by-Step Pipeline Flow (handle_query):</b>", h2_style))
    story.append(Paragraph("1. <b>Session Verification:</b> Validates <code>payload.session_id</code> in <code>session_store</code> (returns 404 if missing).", bullet_style))
    story.append(Paragraph("2. <b>Generation Step:</b> Calls <code>generate_sql()</code> to retrieve <code>sql</code>, <code>explanation</code>, and <code>confidence</code>.", bullet_style))
    story.append(Paragraph("3. <b>Validation Gate:</b> Calls <code>validate_sql(sql)</code>. If invalid (write query or syntax error): logs attempt to <code>meta.db</code> with <code>confidence=0.0</code> and returns a 200 OK <code>QueryResponse</code> with the validator's friendly explanation and <code>result=[]</code>.", bullet_style))
    story.append(Paragraph("4. <b>Execution Step:</b> If valid, calls <code>run_select(sql)</code>. If database execution throws an error: logs failure to <code>meta.db</code> and returns a 200 OK <code>QueryResponse</code> with the error explanation and <code>result=[]</code>.", bullet_style))
    story.append(Paragraph("5. <b>Success Path:</b> Commits successful query to <code>meta.db</code> and returns populated rows in <code>result</code>.", bullet_style))

    story.append(Paragraph("<b>Design Decision:</b> Consistent client-side contract. The endpoint avoids returning 500 server crashes or 400 errors for query failures. It returns a standardized 200 OK with <code>confidence: 0.0</code> and user-friendly explanations, allowing the frontend chat UI to gracefully display feedback without breaking.", body_style))
    story.append(Paragraph("<b>Honest Limitation:</b> No automated feedback retry loop yet. If a query fails due to a database schema mismatch (e.g. non-existent column), the error is surfaced to the user immediately rather than being fed back to Gemini for self-correction.", body_style))
    story.append(Spacer(1, 4))
    story.append(create_judge_card(
        "Why return HTTP 200 with confidence: 0 instead of returning HTTP 400 or 422 on blocked queries?",
        "In conversational AI products, a query blocked by policy or requesting unavailable data is a conversational event, not a network transport failure. Returning HTTP 200 with confidence: 0, the attempted SQL, and a friendly message allows the chat interface to render the agent's explanation naturally without triggering generic client error banners."
    ))
    story.append(Spacer(1, 14))

    # =========================================================================
    # THE 30-SECOND ELEVATOR PITCH
    # =========================================================================
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=4, spaceAfter=8))
    pitch_html = (
        "<b>The 30-Second Jury Elevator Pitch (Memorize This!):</b><br/>"
        "<i>\"We built an end-to-end, crash-proof Natural Language to SQL engine. It connects to any SQLite database, "
        "introspects its schema dynamically, and uses Gemini 3.6 Flash to translate user questions into SQL.<br/>"
        "Unlike fragile demos that crash on bad inputs or risk destructive database writes, we implemented a decoupled "
        "security and execution pipeline: every query must pass through an Abstract Syntax Tree (AST) validator using <code>sqlglot</code> "
        "that strictly allows read-only <code>SELECT</code> queries. If a user asks to delete or modify data, the AST validator detects the write intent "
        "and blocks execution before it ever reaches the database.<br/>"
        "Finally, our execution engine wraps all database calls in a crash-proof containment layer, ensuring the server stays up and the user receives "
        "a clear, friendly explanation every single time.\"</i>"
    )
    pitch_table = Table([[Paragraph(pitch_html, body_style)]], colWidths=[504])
    pitch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1.2, c_accent_dark),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(pitch_table)

    # Build PDF with custom NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF successfully generated at: {output_path}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Phase4_Architecture_and_Jury_Defense_Guide.pdf"
    create_pdf(out)
