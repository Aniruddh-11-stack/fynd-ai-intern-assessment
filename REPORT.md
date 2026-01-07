# Fynd AI Intern Assessment - Final Report

## 1. Overall Approach
The solution leverages **Google Gemini Pro** for both NLP tasks (rating classification) and the web application's intelligent features.
- **Task 1** focuses on prompt engineering evaluation, comparing different strategies to extract structured data from unstructured text.
- **Task 2** implements a clean, service-oriented architecture using **FastAPI** for the backend and raw **HTML/Tailwind** for a lightweight, dependency-free frontend that meets the "production-style" requirement without heavy JS frameworks (though Next.js was considered, FastAPI proved faster for a single-language stack given the timeframe).

## 2. Design & Architecture Decisions
- **Backend Framework**: **FastAPI** was chosen for its high performance, native async support (crucial for LLM calls), and automatic OpenAPI documentation.
- **Database**: **SQLite** is used for simplicity and portability, but the SQL logic is standard and easily migratable to PostgreSQL.
- **Frontend**: **Server-Side Rendered (SSR) / Static Templates** served by FastAPI. This avoids CORS complexity and simplifies deployment. **Tailwind CSS** (via CDN) ensures a modern, responsive UI.
- **Prompt Engineering**:
    - *Zero-shot*: Baseline.
    - *Chain-of-Thought (CoT)*: Encourages reasoning before classification.
    - *Structured/Few-shot*: Provides examples to enforce JSON output format and improve consistency.

## 3. Evaluation (Task 1)
*Note: Run `python task1/analysis.py` to generate the latest `evaluation_results.csv`.*

### Methodology
We evaluated 3 prompt designs on a subset of the Yelp dataset.
- **Metric 1: Accuracy**: exact match between predicted and actual stars.
- **Metric 2: JSON Validity**: % of responses successfully parsed as JSON.
- **Metric 3: Reliability**: Qualitative assessment of explanation quality.

### Observed Results (General Findings)
- **Zero-shot**: Often accurate but prone to formatting errors (returning text instead of JSON).
- **CoT**: Higher accuracy on ambiguous reviews but higher latency due to longer token generation.
- **Few-shot Structured**: The winner. consistently returns valid JSON and maintains high accuracy by following provided patterns.

## 4. System Behaviour (Task 2)
### User Dashboard
- Users receive immediate feedback.
- The system handles latency by showing a loading state while Gemini processes the response.
- "Business Response" is auto-generated to handle volume.

### Admin Dashboard
- **Live Updates**: Auto-refresh every 10s.
- **Aggregated Insights**: AI Actions provide immediate operational value ("Clean tables", "Training required") rather than just raw text.

### Trade-offs & Limitations
- **Latency**: Real-time LLM calls add 1-3s latency. *Improvement: Use background queues (Celery/Redis) for non-blocking submission.*
- **Context Window**: Currently treats each review in isolation. *Improvement: Feed last N reviews to AI for trend context.*
- **Security**: Basic implementation. *Improvement: Add Auth0/OAuth for Admin routes.*

## 5. Deployment
Both dashboards are deployable to Render/Vercel.
- **User URL**: [Access /user endpoint on deployed URL]
- **Admin URL**: [Access /admin endpoint on deployed URL]
