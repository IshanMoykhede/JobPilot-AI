# JobPilot AI — Job Search Agent Pipeline

> A detailed end-to-end technical breakdown of how the AI Job Search Agent works, from the moment a user types a query to the final ranked job cards on the frontend.

---

## Architecture Overview

The Job Search Agent is built as a **LangGraph StateGraph** — a directed acyclic graph (DAG) where each node is a discrete processing step. The graph is compiled with a **PostgresSaver Checkpointer**, which means that if any node crashes mid-execution, the entire pipeline can be resumed from the exact point of failure without re-running earlier nodes.

The pipeline consists of **6 sequential nodes**:

```
START
  │
  ▼
┌─────────────────────────┐
│  1. Query Optimizer      │  (LLM — Groq Llama 3.1 8B)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│  2. Job Retrieval        │  (SerpAPI — Google Jobs)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│  3. Knowledge Extraction │  (LLM — Groq Llama 3.1 8B)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│  4. Embedding & Storage  │  (FastEmbed + Qdrant)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│  5. Semantic Matching    │  (Qdrant Vector Search)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│  6. Scorer               │  (MVP — Random scores)
└─────────────────────────┘
  │
  ▼
 END
```

---

## Tech Stack

| Component | Technology |
|---|---|
| **Orchestrator** | LangGraph (StateGraph) |
| **Checkpointing** | PostgresSaver (via `psycopg` connection pool) |
| **LLM** | Groq Cloud — `llama-3.1-8b-instant` |
| **Web Scraping** | SerpAPI (Google Jobs engine) |
| **Embedding Model** | `BAAI/bge-small-en-v1.5` (384-dim, via FastEmbed) |
| **Vector Database** | Qdrant Cloud |
| **Relational Database** | PostgreSQL (via SQLAlchemy + Alembic) |
| **API Layer** | FastAPI (SSE streaming) |
| **Rate Limiting** | `tenacity` (retry on 429 RateLimitError, 60s backoff, 3 attempts) |

---

## The Pipeline State

Every node reads from and writes to a shared `JobSearchState` TypedDict. This is the single source of truth that flows through the entire graph.

```python
class JobSearchState(TypedDict):
    job_search_id: Optional[str]           # UUID of the search session (DB primary key)
    candidate_profile_id: Optional[str]    # UUID of the logged-in user's profile

    user_query: str                        # Raw query from the user (e.g. "AI jobs in Pune")

    optimized_query: Optional[OptimizedQuery]  # Structured output from Node 1
    raw_jobs: Optional[list[dict]]             # Raw SerpAPI results from Node 2
    structured_jobs: Optional[list[JobKnowledge]]  # LLM-extracted knowledge from Node 3
    candidate_knowledge: Optional[str]         # (Reserved for future use)
    matched_jobs: Optional[list[JobKnowledge]] # Semantically matched jobs from Node 5
    final_response: Optional[str]              # (Reserved for future use)
```

---

## Node-by-Node Breakdown

---

### Node 1: Query Optimizer

**File:** `nodes/query_optimizer_node.py`
**Purpose:** Convert the user's raw, natural language query into a clean, structured search query that SerpAPI can understand.

#### How it works:

1. **Input:** The raw `user_query` string (e.g., `"AI engineering job opening in pune"`).
2. **LLM Call:** The query is sent to `Groq Llama 3.1 8B` via LangChain's `with_structured_output()`. The LLM is forced to return a Pydantic model:
   ```python
   class OptimizedQuery(BaseModel):
       job_role: str    # e.g. "AI Engineer"
       location: str    # e.g. "Pune, Maharashtra, India"
   ```
   The prompt instructs the LLM to:
   - Standardize the job title (e.g., "ML engineer" → "Machine Learning Engineer").
   - Always format location as `City, State, Country` in Title Case.
   - If the user only provides a city, the LLM must infer the state and country.
3. **Database Update:** The optimized `job_role` and `location` are saved to the `job_searches` table so they appear in the search history sidebar.
4. **Output:** Writes `optimized_query` to state.

#### Rate Limiting:
Uses `tenacity` to retry on `groq.RateLimitError` — waits 60 seconds, retries up to 3 times.

---

### Node 2: Job Retrieval

**File:** `nodes/job_retrieval_node.py`
**Purpose:** Scrape real job listings from Google Jobs using SerpAPI.

#### How it works:

1. **Input:** Reads `optimized_query.job_role` and `optimized_query.location` from state.
2. **SerpAPI Call:** Makes HTTP requests to SerpAPI's `google_jobs` engine:
   ```python
   params = {
       "engine": "google_jobs",
       "q": job_role,           # e.g. "AI Engineer"
       "location": location,    # e.g. "Pune, Maharashtra, India"
       "hl": "en",
       "gl": "in",
       "api_key": SERPAPI_API_KEY,
   }
   ```
3. **Pagination:** Google Jobs returns ~10 results per page. The service automatically follows `next_page_token` pagination tokens to fetch up to **30 jobs total** (3 pages).
4. **Extraction:** For each raw job, extracts:
   - `title`, `company_name`, `location`, `description`
   - `detected_extensions` (badges like "Full Time", "3 days ago")
   - `apply_link` (first apply option URL, or the Google share link as fallback)
5. **Output:** Writes `raw_jobs` (a list of up to 30 dicts) to state.

---

### Node 3: Job Knowledge Generator

**File:** `nodes/job_knowledge_generator_node.py`
**Purpose:** Use an LLM to extract deep, structured knowledge from the raw job descriptions. This is the most complex node.

#### How it works:

**Step 1 — Deduplication Check:**
Before sending anything to the LLM, the node checks if we've already processed this exact job before.

- For each raw job, it computes a stable hash: `MD5(lowercase(title + "_" + company))`.
- It queries the `job_knowledge` PostgreSQL table for this hash.
- If a record with status `EXTRACTED` exists, the node skips the LLM and reconstructs the `JobKnowledge` Pydantic object directly from the cached `raw_knowledge` JSONB column.
- If no cache hit, the job is added to a `jobs_to_process` list.

**Step 2 — Token-Aware Batching:**
The jobs that need LLM processing are split into batches using a custom **greedy token batcher** (`utils/token_batcher.py`).

- The batcher calculates the available token budget:
  ```
  available = max_context_tokens (10,000)
             - system_prompt_tokens
             - reserved_output_tokens (2,000)
             - safety_margin (500)
  ```
- It iterates through jobs, accumulating their token counts. When adding the next job would exceed the budget, it closes the current batch and starts a new one.
- Token counting uses `tiktoken` with the `cl100k_base` encoding.

**Step 3 — LLM Extraction:**
Each batch is sent to `Groq Llama 3.1 8B` with structured output. The LLM is forced to return a `JobKnowledgeBatch` containing a list of `JobKnowledge` objects:

```python
class JobKnowledge(BaseModel):
    job_title: str
    company_name: str
    location: str | None
    work_mode: str | None              # Remote, Hybrid, Onsite
    employment_type: str | None        # Full Time, Internship, Contract
    employment_level: str | None       # Intern, Junior, Mid, Senior, Lead
    minimum_experience_years: int | None
    preferred_experience_years: int | None
    required_degrees: list[str]
    preferred_degrees: list[str]
    required_specializations: list[str]
    preferred_specializations: list[str]
    primary_domain: str | None         # e.g. "Machine Learning"
    secondary_domains: list[str]
    required_technologies: list[str]   # e.g. ["Python", "TensorFlow"]
    preferred_technologies: list[str]
    required_capabilities: list[str]   # e.g. ["System Design", "Mentoring"]
    preferred_capabilities: list[str]
    required_certifications: list[str]
    preferred_certifications: list[str]
    responsibilities: list[str]
    benefits: list[str]
    salary_information: str | None
    industry: str | None
```

**Step 4 — Persist to Database:**
After each batch completes, the structured results are saved to the `job_knowledge` PostgreSQL table. The `raw_knowledge` JSONB column stores the full Pydantic model dump PLUS the original raw description and extensions from SerpAPI, so nothing is ever lost.

**Output:** Writes `structured_jobs` to state.

---

### Node 4: Embedding & Storage

**File:** `nodes/embedding_node.py`
**Purpose:** Generate semantic embedding vectors for every structured job AND the candidate's profile, and store them in Qdrant.

#### How it works:

**Step 1 — Embed the Candidate:**
- Loads the candidate's `CandidateProfile` from PostgreSQL (the `profile_json` JSONB field).
- Converts the entire profile JSON into a formatted string.
- Generates a 384-dimensional embedding using `BAAI/bge-small-en-v1.5` (via FastEmbed, runs locally on CPU).
- Upserts the embedding into a Qdrant collection called `candidate_knowledge`, using the `candidate_profile_id` as the point ID.

**Step 2 — Embed the Jobs:**
- Each `JobKnowledge` object is converted into a rich semantic document using the `semantic_formatter`:
  ```
  Job Title: AI Engineer
  Company: Deloitte
  Location: Mumbai, Maharashtra
  Employment Type: Full Time
  Required Technologies: Python, TensorFlow, PyTorch
  Required Capabilities: System Design, Model Training
  ...
  ```
- All documents are batch-embedded using the same `BAAI/bge-small-en-v1.5` model.
- Each embedding is stored in a Qdrant collection called `job_embeddings_testing`, with a stable UUID derived from `MD5(title + company)` to prevent duplicates.

**Output:** No state changes (embeddings are stored externally in Qdrant).

---

### Node 5: Semantic Matching

**File:** `nodes/semantic_matching_node.py`
**Purpose:** Use the candidate's embedding to find the most semantically similar jobs via vector search.

#### How it works:

1. **Retrieve Candidate Embedding:** Fetches the candidate's 384-dim vector from the `candidate_knowledge` Qdrant collection.
2. **Vector Search:** Queries the `job_embeddings_testing` collection using cosine similarity:
   ```python
   results = client.query_points(
       collection_name="job_embeddings_testing",
       query=candidate_embedding,
       limit=50,  # Return top 50 matches
       with_payload=True,
   )
   ```
3. **Reconstruct Objects:** Each Qdrant result contains the full `JobKnowledge` payload. The node reconstructs the Pydantic objects and returns them ranked by cosine similarity score.
4. **Fallback:** If the candidate embedding is missing (e.g., profile not completed), the node falls back to returning the first 10 `structured_jobs` directly without vector search.

**Output:** Writes `matched_jobs` to state.

---

### Node 6: Scorer (MVP)

**File:** `nodes/scorer_node.py`
**Purpose:** Assign match scores to each matched job and persist the results to the database.

#### Current Implementation (MVP):
The scorer currently generates **random scores** as a placeholder:
```python
semantic_score = random.uniform(60.0, 95.0)
deterministic_score = random.uniform(50.0, 99.0)
final_score = (semantic_score + deterministic_score) / 2.0
```

It also assigns hardcoded skill badges:
- If `final_score > 80`: matching_skills = `["Python", "SQL"]`
- If `final_score < 70`: missing_skills = `["Docker"]`

#### Database Persistence:
For each matched job, a `JobMatchScore` record is created in the `job_match_scores` table:

| Column | Description |
|---|---|
| `job_search_id` | FK to the search session |
| `job_knowledge_id` | FK to the job knowledge record |
| `semantic_score` | Score from vector similarity |
| `deterministic_score` | Score from rule-based matching |
| `final_score` | Combined weighted score |
| `matching_skills` | JSONB array of skills the candidate has |
| `missing_skills` | JSONB array of skills the candidate lacks |
| `ai_explanation` | JSONB (null until user requests it) |

**Output:** No state changes (scores are persisted to PostgreSQL).

---

## Database Schema

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   job_searches   │       │ job_match_scores  │       │  job_knowledge   │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK, UUID)    │◄──────│ job_search_id(FK)│       │ id (PK, UUID)    │
│ candidate_id     │       │ job_knowledge_id ├──────►│ job_hash (unique)│
│ original_query   │       │ semantic_score   │       │ title            │
│ optimized_role   │       │ deterministic    │       │ company          │
│ optimized_loc    │       │ final_score      │       │ location         │
│ status           │       │ matching_skills  │       │ apply_url        │
│ created_at       │       │ missing_skills   │       │ raw_knowledge    │
│ updated_at       │       │ ai_explanation   │       │ processing_status│
└──────────────────┘       │ created_at       │       │ created_at       │
                           └──────────────────┘       └──────────────────┘
```

**Key Design Decisions:**
- `job_knowledge` is **deduplicated** across all searches via the `job_hash` column. If two users search for the same job, the LLM only processes it once.
- `job_match_scores` is a **many-to-many mapping** between `job_searches` and `job_knowledge`. Each search session generates its own unique set of scores for the same underlying jobs.
- `raw_knowledge` (JSONB) stores the full LLM output plus the original SerpAPI description, so we never lose raw data.

---

## Frontend Integration

### SSE Streaming
The frontend connects to `POST /api/job-search/run` which returns a `StreamingResponse` with `text/event-stream` content type. As each LangGraph node completes, the backend emits an SSE event:

```
data: {"node": "query_optimizer_node", "status": "completed"}

data: {"node": "job_retrieval_node", "status": "completed"}

data: {"node": "job_knowledge_generator_node", "status": "completed"}

...

data: {"node": "DONE", "thread_id": "abc-123-uuid"}
```

The frontend uses these events to animate a **Cinematic Pipeline** visualization in real-time.

### Results Fetching
Once the frontend receives the `DONE` event, it calls `GET /api/job-search/{thread_id}/results` which:
1. Queries `job_match_scores` joined with `job_knowledge`.
2. Orders by `final_score DESC`.
3. Returns a structured JSON response with all job data, scores, skills, and insights.

### Pagination
The frontend paginates the results at **5 jobs per page** with Previous/Next navigation and smooth scrolling.

### Resume/Retry
If the pipeline crashes (LLM timeout, rate limit exhaustion, etc.), the search status is set to `FAILED`. The user can click "Retry Failed Step" which calls `POST /api/job-search/resume/{thread_id}`. This endpoint leverages the PostgresSaver checkpointer to resume execution from the exact node that failed.

---

## Known Limitations (MVP)

| Area | Limitation | Future Plan |
|---|---|---|
| **Scorer** | Uses random scores instead of real AI scoring | Build a proper LLM-based scorer that compares candidate profile against job requirements |
| **Matching Skills** | Hardcoded `["Python", "SQL"]` | Extract actual skill overlap between candidate profile and job knowledge |
| **AI Explanation** | `ai_explanation` column is always null | Generate a natural language explanation of why the candidate is a good/bad fit |
| **Job Count** | SerpAPI limited to ~30 jobs per search | Consider adding Indeed, LinkedIn APIs |
| **Embedding Model** | `bge-small-en-v1.5` is a lightweight model | Upgrade to a larger model for better semantic accuracy |
