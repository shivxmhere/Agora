import aiosqlite
import json
import uuid
import os
import random
from datetime import datetime, date, timedelta

DB_PATH = os.getenv("DATABASE_URL", "./agora.db")

# ─── Context manager for dependency injection ──────────────────────────────────
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

# ─── Schema ────────────────────────────────────────────────────────────────────
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT UNIQUE,
                tagline TEXT,
                description TEXT,
                long_description TEXT,
                category TEXT,
                tags TEXT DEFAULT '[]',
                creator_name TEXT,
                creator_score REAL DEFAULT 0,
                capabilities TEXT DEFAULT '[]',
                pricing_model TEXT DEFAULT 'free',
                price_per_run INTEGER DEFAULT 0,
                rating REAL DEFAULT 4.5,
                total_runs INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 99,
                avg_run_time REAL DEFAULT 45,
                status TEXT DEFAULT 'live',
                input_placeholder TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                session_id TEXT,
                input TEXT,
                output TEXT,
                status TEXT DEFAULT 'queued',
                started_at TEXT,
                completed_at TEXT,
                run_time REAL,
                tokens_used INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                session_id TEXT,
                stars INTEGER,
                review TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                agent_name TEXT,
                action TEXT,
                location TEXT,
                created_at TEXT
            )
        """)
        await db.commit()

# ─── Helpers ───────────────────────────────────────────────────────────────────
async def get_agent_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM agents") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def get_today_run_count():
    async with aiosqlite.connect(DB_PATH) as db:
        today = date.today().isoformat()
        async with db.execute(
            "SELECT COUNT(*) FROM agent_runs WHERE started_at LIKE ?", (f"{today}%",)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def get_run(run_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM agent_runs WHERE id=?", (run_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def create_run(run_id: str, agent_id: str, session_id: str, input_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO agent_runs (id, agent_id, session_id, input, status, started_at)
            VALUES (?, ?, ?, ?, 'queued', ?)
        """, (run_id, agent_id, session_id, input_text, datetime.utcnow().isoformat()))
        await db.execute(
            "UPDATE agents SET total_runs = total_runs + 1 WHERE id = ?", (agent_id,)
        )
        await db.commit()
    # Fire-and-forget activity log
    await log_activity(agent_id)

async def update_run(run_id: str, status: str, output: str = None, run_time: float = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if output is not None and run_time is not None:
            await db.execute("""
                UPDATE agent_runs
                SET status=?, output=?, run_time=?, completed_at=?
                WHERE id=?
            """, (status, output, run_time, datetime.utcnow().isoformat(), run_id))
        else:
            await db.execute(
                "UPDATE agent_runs SET status=? WHERE id=?", (status, run_id)
            )
        await db.commit()

async def log_activity(agent_id: str):
    locations = [
        "Delhi, IN", "Mumbai, IN", "Bangalore, IN", "Chennai, IN",
        "Hyderabad, IN", "Pune, IN", "Kolkata, IN", "Jaipur, IN",
        "London, UK", "Singapore, SG", "Dubai, UAE", "San Francisco, US",
    ]
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT name FROM agents WHERE id=?", (agent_id,)) as cur:
            row = await cur.fetchone()
            agent_name = row["name"] if row else agent_id
        await db.execute("""
            INSERT INTO activity_log (id, agent_id, agent_name, action, location, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), agent_id, agent_name,
            "just ran", random.choice(locations), datetime.utcnow().isoformat()
        ))
        await db.commit()

# ─── Seeding ───────────────────────────────────────────────────────────────────
async def seed_agents_if_empty():
    count = await get_agent_count()
    # Removed early return so new agents can be added via INSERT OR IGNORE

    agents = [
        {
            "id": "autoresearch", "slug": "autoresearch",
            "name": "AutoResearch Agent",
            "tagline": "5-agent pipeline — any topic to a full research report in 90 seconds",
            "description": "Autonomous multi-agent research system using LangGraph. Searches, reads, analyzes, fact-checks, and synthesizes a comprehensive report.",
            "long_description": "AutoResearch Agent is AGORA's flagship agent — a 5-node LangGraph pipeline that transforms any research query into a comprehensive, cited report. The pipeline runs: Searcher (6 web queries via Tavily) → Reader (concurrent URL scraping) → Analyst (FAISS RAG + LLM analysis) → Fact Checker (claim verification with confidence scores) → Reporter (structured markdown output). Powered by Groq LLaMA 3.3 70B at 300 tokens/second.",
            "category": "Research",
            "tags": ["research", "rag", "langgraph", "web-search", "free"],
            "creator_name": "shivxmhere", "creator_score": 9.4,
            "capabilities": ["Web search across 10+ sources", "FAISS vector indexing", "Fact verification with confidence scores", "Structured markdown reports with citations", "< 90 second full pipeline"],
            "rating": 4.9, "total_runs": 247, "success_rate": 97, "avg_run_time": 78,
            "status": "live",
            "input_placeholder": "Enter any research topic... e.g. 'latest trends in AI agent marketplaces 2026'"
        },
        {
            "id": "codereview", "slug": "codereview",
            "name": "CodeReview Agent",
            "tagline": "Instant code analysis — bugs, security, complexity, improvements",
            "description": "Analyzes code snippets for bugs, security vulnerabilities, complexity issues, and suggests improvements with a verdict score.",
            "long_description": "CodeReview Agent uses Groq LLaMA 3.3 70B to perform a comprehensive analysis of any code snippet. It identifies critical bugs, security vulnerabilities (OWASP top 10), algorithmic complexity issues, and provides actionable improvement suggestions. Returns a structured report with severity levels and an overall verdict score out of 10.",
            "category": "Developer Tools",
            "tags": ["code", "security", "bugs", "review", "free"],
            "creator_name": "shivxmhere", "creator_score": 9.4,
            "capabilities": ["Bug detection with line references", "Security vulnerability scanning", "Big-O complexity analysis", "Improvement suggestions with examples", "Verdict score out of 10"],
            "rating": 4.7, "total_runs": 183, "success_rate": 99, "avg_run_time": 22,
            "status": "live",
            "input_placeholder": "Paste your code here... any language supported"
        },
        {
            "id": "contentwriter", "slug": "contentwriter",
            "name": "ContentWriter Agent",
            "tagline": "Blog posts, LinkedIn content, emails — crafted in your voice",
            "description": "3-stage writing pipeline: outline → draft → polish. Creates blog posts, LinkedIn posts, email drafts, and more from a brief.",
            "long_description": "ContentWriter Agent is a 3-node LangGraph pipeline that produces publication-ready content. Stage 1 creates a detailed outline with hooks, Stage 2 drafts the full content with engaging prose, Stage 3 polishes for tone, flow, and impact. Supports blog posts, LinkedIn posts, email campaigns, product descriptions, and social media content.",
            "category": "Creative",
            "tags": ["writing", "content", "linkedin", "blog", "free"],
            "creator_name": "shivxmhere", "creator_score": 9.4,
            "capabilities": ["Blog post generation (500-2000 words)", "LinkedIn post with hooks", "Email campaign drafts", "3-stage outline→draft→polish pipeline", "Tone customization"],
            "rating": 4.8, "total_runs": 156, "success_rate": 98, "avg_run_time": 35,
            "status": "live",
            "input_placeholder": "Describe what you want to write... e.g. 'LinkedIn post about AI agents marketplace for developers'"
        },
        {
            "id": "marketspy", "slug": "marketspy",
            "name": "MarketSpy Agent",
            "tagline": "Competitive intelligence and market research from a company or market name",
            "description": "Deep competitive analysis — company overview, market positioning, SWOT, competitor landscape, and strategic opportunities.",
            "long_description": "MarketSpy Agent performs comprehensive competitive intelligence using Groq LLaMA 3.3 70B with web-augmented knowledge. Input any company name or market vertical to get: company overview, market size and growth, SWOT analysis, top 5 competitors with differentiation matrix, pricing landscape, and strategic opportunities.",
            "category": "Business",
            "tags": ["market-research", "competitive-analysis", "swot", "business"],
            "creator_name": "aditya_dev", "creator_score": 8.1,
            "capabilities": ["Company overview and positioning", "Market size and growth estimates", "SWOT analysis", "Competitor matrix (top 5)", "Strategic opportunity identification"],
            "rating": 4.6, "total_runs": 89, "success_rate": 96, "avg_run_time": 30,
            "status": "live",
            "input_placeholder": "Enter a company name or market... e.g. 'Notion' or 'AI agent marketplace'"
        },
        {
            "id": "dataanalyst", "slug": "dataanalyst",
            "name": "DataAnalyst Agent",
            "tagline": "Interpret data, find patterns, generate actionable insights in plain English",
            "description": "Analyzes data descriptions, CSV snippets, or dataset summaries to extract key patterns, anomalies, and business insights.",
            "long_description": "DataAnalyst Agent translates raw data into business intelligence. Paste a CSV snippet, describe your dataset, or share metrics — the agent identifies trends, outliers, correlations, and generates actionable recommendations. Outputs structured insights with methodology, findings, and suggested next steps.",
            "category": "Analytics",
            "tags": ["data", "analytics", "insights", "csv", "patterns"],
            "creator_name": "aditya_dev", "creator_score": 8.1,
            "capabilities": ["Trend and pattern identification", "Outlier and anomaly detection", "Correlation analysis", "Business insight generation", "Actionable recommendation report"],
            "rating": 4.5, "total_runs": 67, "success_rate": 95, "avg_run_time": 25,
            "status": "live",
            "input_placeholder": "Paste data or describe your dataset... e.g. 'Q1 sales: Jan 45k, Feb 52k, Mar 38k — why the drop?'"
        },
        {
            "id": "cybersec", "slug": "cybersec",
            "name": "CyberSec Agent",
            "tagline": "Security audit, penetration test generation, and CVE analysis",
            "description": "Scans inputs for vulnerabilities, matches live CVE threats, and outputs an OWASP-aligned security audit report.",
            "long_description": "CyberSec Agent is your automated penetration tester. It pulls real-time common vulnerabilities and exposures (CVEs) using Tavily Web Search and compares them against your code, architecture, or tech stack using Groq LLaMA 3.3. Offers a full security audit including attack vectors, mitigations, and an overall risk score.",
            "category": "Developer Tools",
            "tags": ["security", "cve", "owasp", "audit"],
            "creator_name": "aditya_dev", "creator_score": 9.1,
            "capabilities": ["CVE live fetching", "Penetration test reporting", "OWASP standard checks", "Threat intel synthesis"],
            "rating": 4.9, "total_runs": 112, "success_rate": 99, "avg_run_time": 28,
            "status": "live",
            "input_placeholder": "Enter architecture, tech stack, or vulnerability type (e.g. log4j)..."
        },
        {
            "id": "uxresearcher", "slug": "uxresearcher",
            "name": "UXResearcher Agent",
            "tagline": "User personas, feedback synthesis, and UX heuristics",
            "description": "Synthesizes user feedback, scopes out competitor design patterns, and builds extensive UX empathetic models.",
            "long_description": "Stop guessing what your users want. UXResearcher Agent pulls live market design patterns and analyzes user friction points. It builds hyper-realistic user personas, highlights contradictory pain points in markets, and outputs a feature prioritization matrix so your dev team knows exactly what to build next.",
            "category": "Creative",
            "tags": ["ux", "design", "personas", "research"],
            "creator_name": "prabhav_dsgn", "creator_score": 8.8,
            "capabilities": ["Persona generation", "Friction point analysis", "Heuristics evaluation", "Competitor UX scanning"],
            "rating": 4.7, "total_runs": 95, "success_rate": 98, "avg_run_time": 32,
            "status": "live",
            "input_placeholder": "Enter your app idea or user problem (e.g. a grocery app for elderly users)..."
        },
        {
            "id": "devops", "slug": "devops",
            "name": "DevOps Agent",
            "tagline": "Infrastructure as Code, CI/CD, and scaling architecture",
            "description": "Generates Dockerfiles, GitHub Actions pipelines, and Kubernetes deployment strategies based on modern best practices.",
            "long_description": "DevOps Agent acts as a Principal Cloud Engineer. It performs web lookups for the latest scaling patterns for your specific tech stack. Generates ready-to-copy Docker configurations, CI/CD yaml pipelines, and highlights scalability warnings and cost optimizations. Stop writing boilerplate DevOps code.",
            "category": "Developer Tools",
            "tags": ["devops", "docker", "ci-cd", "cloud"],
            "creator_name": "shivxmhere", "creator_score": 9.6,
            "capabilities": ["Dockerfile generation", "CI/CD generation", "K8s architecture design", "Cost/scaling warnings"],
            "rating": 4.8, "total_runs": 134, "success_rate": 97, "avg_run_time": 25,
            "status": "live",
            "input_placeholder": "Describe what you need deployed (e.g. NextJS frontend + FastAPI python backend + Postgres)..."
        },
        {
            "id": "legaltech", "slug": "legaltech",
            "name": "LegalTech Agent",
            "tagline": "Contract boilerplate, GDPR compliance, and legal frameworks",
            "description": "Drafts standard compliance templates and flags potential liabilities in user agreements.",
            "long_description": "LegalTech Agent leverages real-time search for legal precedents (GDPR, CCPA) to draft professional boilerplate clauses, privacy policies, and Terms of Service. Note: outputs contain strict AI disclaimers and do not substitute a real lawyer. Instantly verify compliance checklists and liabilities.",
            "category": "Business",
            "tags": ["legal", "compliance", "gdpr", "contracts"],
            "creator_name": "shresta", "creator_score": 8.9,
            "capabilities": ["Boilerplate drafting", "Compliance check (GDPR)", "Liability flagging", "Precedent scanning"],
            "rating": 4.4, "total_runs": 55, "success_rate": 94, "avg_run_time": 34,
            "status": "live",
            "input_placeholder": "What legal document do you need? (e.g. basic terms of service for SaaS app)..."
        },
        {
            "id": "copywriter", "slug": "copywriter",
            "name": "Copywriter Agent",
            "tagline": "High-converting SEO marketing copy and A/B test hooks",
            "description": "Creates persuasive direct-response copy, email newsletters, and viral social media captions using live SEO trends.",
            "long_description": "Copywriter Agent scans live marketing trends to craft copy that actually converts. Using proven frameworks like PAS (Problem, Agitate, Solve), it generates multiple A/B hook variations, email drafts, and SEO keyword strategies. It highlights contradicting SEO tactics so you can make informed marketing decisions.",
            "category": "Creative",
            "tags": ["marketing", "seo", "copywriting", "sales"],
            "creator_name": "shresta", "creator_score": 9.2,
            "capabilities": ["A/B hook variants", "PAS framework emails", "SEO keyword strategy", "Social media captioning"],
            "rating": 4.9, "total_runs": 210, "success_rate": 99, "avg_run_time": 29,
            "status": "live",
            "input_placeholder": "What are you selling? (e.g. an AI agent marketplace to developers)..."
        },
    ]

    async with aiosqlite.connect(DB_PATH) as db:
        for a in agents:
            await db.execute("""
                INSERT OR IGNORE INTO agents
                (id, name, slug, tagline, description, long_description, category, tags,
                 creator_name, creator_score, capabilities, pricing_model, price_per_run,
                 rating, total_runs, success_rate, avg_run_time, status, input_placeholder, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                a["id"], a["name"], a["slug"], a["tagline"], a["description"],
                a["long_description"], a["category"], json.dumps(a["tags"]),
                a["creator_name"], a["creator_score"], json.dumps(a["capabilities"]),
                "free", 0, a["rating"], a["total_runs"], a["success_rate"],
                a["avg_run_time"], a["status"], a["input_placeholder"],
                datetime.utcnow().isoformat()
            ))
        await db.commit()

async def seed_activity_if_empty():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM activity_log") as cur:
            row = await cur.fetchone()
            if row and row[0] > 0:
                return

    agent_pairs = [
        ("autoresearch", "AutoResearch Agent"),
        ("codereview", "CodeReview Agent"),
        ("contentwriter", "ContentWriter Agent"),
        ("marketspy", "MarketSpy Agent"),
        ("dataanalyst", "DataAnalyst Agent"),
        ("cybersec", "CyberSec Agent"),
        ("uxresearcher", "UXResearcher Agent"),
        ("devops", "DevOps Agent"),
        ("legaltech", "LegalTech Agent"),
        ("copywriter", "Copywriter Agent"),
    ]
    locations = [
        "Delhi, IN", "Mumbai, IN", "Bangalore, IN", "Chennai, IN",
        "Hyderabad, IN", "Pune, IN", "Kolkata, IN", "London, UK",
        "Singapore, SG", "Dubai, UAE",
    ]

    async with aiosqlite.connect(DB_PATH) as db:
        for i in range(20):
            aid, aname = random.choice(agent_pairs)
            ts = (datetime.utcnow() - timedelta(minutes=random.randint(1, 180))).isoformat()
            await db.execute("""
                INSERT INTO activity_log (id, agent_id, agent_name, action, location, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), aid, aname, "just ran", random.choice(locations), ts))
        await db.commit()
