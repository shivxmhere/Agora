import json
import uuid
import datetime

async def create_tables(db):
    await db.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT,
            slug TEXT UNIQUE,
            tagline TEXT,
            description TEXT,
            long_description TEXT,
            category TEXT,
            tags TEXT,
            creator_name TEXT,
            creator_score REAL DEFAULT 0,
            capabilities TEXT,
            pricing_model TEXT DEFAULT 'free',
            price_per_run INTEGER DEFAULT 0,
            rating REAL DEFAULT 0,
            total_runs INTEGER DEFAULT 0,
            success_rate REAL DEFAULT 100,
            avg_run_time REAL DEFAULT 30,
            status TEXT DEFAULT 'live',
            input_placeholder TEXT,
            created_at TEXT
        )
    ''')

    await db.execute('''
        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            session_id TEXT,
            input TEXT,
            output TEXT,
            status TEXT,
            started_at TEXT,
            completed_at TEXT,
            run_time REAL,
            tokens_used INTEGER
        )
    ''')

    await db.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            session_id TEXT,
            stars INTEGER,
            review TEXT,
            created_at TEXT
        )
    ''')

    await db.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            agent_name TEXT,
            action TEXT,
            location TEXT,
            created_at TEXT
        )
    ''')

async def seed_agents(db):
    try:
        cursor = await db.execute("SELECT COUNT(*) as count FROM agents")
        row = await cursor.fetchone()
        if row and row['count'] > 0:
            return  # Agents already seeded
    except Exception:
        pass

    now = datetime.datetime.utcnow().isoformat()
    seeds = [
        ("autoresearch", "AutoResearch Agent", "autoresearch", "5-agent pipeline that turns any topic into a 90-second research report",
         "Research any topic dynamically.", "A complex multi-agent system powered by LangGraph, Groq, and Tavily. Analyzes diverse sources, applies factual checks, and compiles robust markdown reports.", 
         "Research", json.dumps(["AI", "Research", "Fast"]), "shivxmhere", 9.4, json.dumps(["Search", "Fact Check", "Synthesis"]),
         "free", 0, 4.9, 247, 100, 30, "live", "Enter any research topic...", now),
         
        ("codereview", "CodeReview Agent", "codereview", "Instant code analysis: bugs, security, complexity, improvements",
         "Analyze code snippets.", "Provide comprehensive code reviews identifying anti-patterns, security flaws, and performance improvements.", 
         "Developer Tools", json.dumps(["Code", "Review", "Security"]), "shivxmhere", 9.4, json.dumps(["Static Analysis", "Code Quality"]),
         "free", 0, 4.7, 183, 100, 15, "live", "Paste your code here...", now),
         
        ("contentwriter", "ContentWriter Agent", "contentwriter", "Blog posts, LinkedIn content, emails — written in your voice",
         "Generate various content.", "A 3-node structure that generates, drafts, and polishes original content natively adapted for specific platforms.", 
         "Creative", json.dumps(["Writing", "Blogs", "LinkedIn"]), "shivxmhere", 9.4, json.dumps(["Drafting", "Polishing"]),
         "free", 0, 4.8, 156, 100, 20, "live", "Describe what you want to write about...", now),
         
        ("marketspy", "MarketSpy Agent", "marketspy", "Competitive intelligence and market research from a company name",
         "Market research fast.", "A one-shot intelligent agent designed to do competitive market analysis, summarize finding and supply data points rapidly.", 
         "Business", json.dumps(["Business", "Intelligence"]), "aditya_dev", 8.1, json.dumps(["Market Analysis", "Trends"]),
         "free", 0, 4.6, 89, 100, 10, "live", "Enter a company name or market to analyze...", now),

        ("dataanalyst", "DataAnalyst Agent", "dataanalyst", "Interpret data, find patterns, generate insights in plain English",
         "Analyze data naturally.", "Takes snippets or CSV data directly and produces quick insights about key metric variations and notable anomalies.", 
         "Analytics", json.dumps(["Data", "Analysis"]), "aditya_dev", 8.1, json.dumps(["Data Parsing", "Insights"]),
         "free", 0, 4.5, 67, 100, 12, "live", "Describe your data or paste CSV snippet...", now)
    ]

    for seed in seeds:
        await db.execute('''
            INSERT INTO agents (id, name, slug, tagline, description, long_description, category, tags, creator_name, creator_score, capabilities, pricing_model, price_per_run, rating, total_runs, success_rate, avg_run_time, status, input_placeholder, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed)
