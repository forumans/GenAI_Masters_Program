# RAGAS Evaluation Plan — HR Assistant

## Overview

This document describes the plan to add a RAGAS-based evaluation feature to the HR Assistant application. The goal is to measure the quality of the RAG (Retrieval-Augmented Generation) pipeline using four objective metrics.

---

## What is RAGAS?

RAGAS is a framework specifically designed to evaluate RAG pipelines. It uses an LLM as a judge to produce numeric scores (0–1) for four aspects of RAG quality:

| Metric | Question it answers | Needs ground truth? |
|--------|---------------------|---------------------|
| **Faithfulness** | Is the answer based on what was actually retrieved, or did the LLM hallucinate? | No |
| **Answer Relevancy** | Does the answer actually address what the user asked? | No |
| **Context Precision** | Are the retrieved chunks the *right* ones — or is there a lot of noise? | Yes |
| **Context Recall** | Did the retriever find *all* the relevant information needed to answer correctly? | Yes |

---

## Implementation Steps

### Step 1 — Install Dependencies

```bash
pip install ragas datasets
```

- `ragas` — the evaluation framework
- `datasets` — HuggingFace library that RAGAS uses to structure evaluation data

### Step 2 — Bootstrap the HR Assistant Services (Without a Running Server)

The HR Assistant normally runs as a FastAPI web server connected to PostgreSQL. For evaluation we call the RAG pipeline directly — no web server, no database queries.

**How it works:**

1. Load the `.env` file (OPENAI_API_KEY, ChromaDB path, etc.) into environment variables **before** importing any app code.
2. This satisfies Pydantic's settings validation without needing a real database connection.
3. Directly instantiate two internal services:
   - **`VectorStoreService`** — connects to the existing ChromaDB (HR policy chunks already stored on disk), handles retrieval.
   - **`AIService`** — wraps the OpenAI LLM + the retriever, generates responses.

**Key constraint:** `AIService.__init__` calls `self.vector_store.vector_store.as_retriever(...)` — so `VectorStoreService.load_pdf()` must be called **before** creating `AIService`, to ensure the vector store is populated.

```python
vs = VectorStoreService(persist_directory=chroma_dir, openai_api_key=...)
vs.load_pdf(pdf_path)        # loads existing chunks; skips re-ingestion if already stored

ai = AIService(openai_api_key=..., vector_store=vs)
```

### Step 3 — Build a Test Dataset (12 Q&A Pairs)

12 HR policy questions covering 5 topics, each with a ground truth answer grounded in the HR policies PDF.

| # | Topic | Question | Ground Truth |
|---|-------|----------|--------------|
| 1 | Leave | When can employees start using annual leave after being hired? | Employees accrue annual leave immediately upon hire but may not use it until after 90 days of employment. |
| 2 | Leave | How much vacation time do employees earn based on years of service? | 1.5 pro-rated days/month for less than 2 years; 1.75 for years 2–6; 2.0 for 7+ years. |
| 3 | Leave | What happens to unused vacation time when an employee is terminated? | Any earned but unused vacation will be paid at the time of termination. |
| 4 | Leave | How far in advance must employees request vacation approval? | Employees should request approval in writing at least two weeks in advance. |
| 5 | Expense | What expenses does the organization not reimburse while traveling? | Personal activities, entertainment, liquor, dry cleaning, and similar personal expenses. |
| 6 | Expense | How many business days to submit a travel expense report after a trip? | Within 7 business days of completion of travel. |
| 7 | Hours | What are the standard working hours? | 8:00 a.m. to 4:30 p.m., Monday–Friday, with an unpaid 30-minute meal period. |
| 8 | Hours | When does the organization's workweek begin and end? | Begins at 12:00 a.m. Saturday, ends at 11:59 p.m. Friday. |
| 9 | Benefits | Which employees are eligible for paid holidays? | Regular full-time and regular part-time employees. |
| 10 | Benefits | If a paid holiday falls during scheduled vacation, what happens? | Holiday pay is provided and the vacation day is preserved for later use. |
| 11 | Conduct | What forms of harassment does the organization prohibit? | Harassment based on race, color, religion, sex, national origin, age, disability, veteran status, pregnancy, marital status, medical condition, sexual orientation, or other protected status. |
| 12 | Conduct | What is the policy on outside employment? | Permitted as long as it does not interfere with job performance or the ability to meet responsibilities. |

> **Important constraint:** No question can contain keywords like `"on leave"` or `"on vacation"`. Those keywords trigger a direct database lookup in `AIService._handle_leave_query()`, which would crash when `db=None` in the evaluation context.

### Step 4 — Run the RAG Pipeline on Each Question

For each of the 12 questions, the script does two calls:

1. **Retrieval** — `VectorStoreService.query(question, n_results=5)`  
   Returns the top 5 matching text chunks from ChromaDB → these become the `contexts`.

2. **Generation** — `AIService.generate_response(question, employee_context=None, conversation_history=None, db=None)`  
   Returns a JSON string like `{"type": "text", "data": "The leave policy states..."}`.  
   A helper function extracts the plain text from the `data` field → this becomes the `answer`.

**JSON response extraction logic:**

```
type = "text"   → use data as-is (string)
type = "table"  → flatten columns + rows into readable text
type = "metric" → format as "label: value"
type = "tree"   → use string representation
```

After the loop we have, for each question: `question`, `contexts` (list of 5 strings), `answer` (plain text), `ground_truth`.

### Step 5 — Feed Everything into RAGAS

Pack all 12 samples into a HuggingFace `Dataset` object with four columns, then call `ragas.evaluate()`:

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

dataset = Dataset.from_dict({
    "question":     [...],   # 12 questions
    "answer":       [...],   # 12 extracted text answers
    "contexts":     [...],   # 12 lists of 5 retrieved chunks
    "ground_truth": [...]    # 12 expected answers
})

result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
```

RAGAS internally uses OpenAI as an LLM judge to score each metric across all samples.

### Step 6 — Print a Report and Save Results

The script prints an aggregate report with pass/fail thresholds:

```
=================================================================
RAGAS Evaluation Report - HR Assistant RAG Pipeline
=================================================================

AGGREGATE SCORES:
  faithfulness       : 0.87  [target >= 0.80]  PASS
  answer_relevancy   : 0.91  [target >= 0.80]  PASS
  context_precision  : 0.75  [target >= 0.70]  PASS
  context_recall     : 0.83  [target >= 0.75]  PASS
```

And saves the full per-question breakdown to `evaluation_projects/ragas_results_<timestamp>.json`.

---

## The Big Picture

```
HR Policies PDF
      ↓ (already ingested)
  ChromaDB (203 chunks on disk)
      ↓
  [For each of 12 questions]
  VectorStoreService.query()      → contexts (5 text chunks)
  AIService.generate_response()   → answer (plain text, extracted from JSON)
      ↓
  RAGAS Dataset { question, answer, contexts, ground_truth }
      ↓
  ragas.evaluate()   → 4 metric scores (LLM-as-judge)
      ↓
  Console report + ragas_results_<timestamp>.json
```

---

## Output File

| File | Purpose |
|------|---------|
| `evaluation_projects/test_03_ragas.py` | Standalone evaluation script |
| `evaluation_projects/ragas_results_<timestamp>.json` | Per-question scores + aggregate |

---

## How to Run

```bash
python evaluation_projects/test_03_ragas.py
```

No running server or database required. Requires `OPENAI_API_KEY` in `hr_assistant/hr_assistant_api/.env`.

---

## Relationship to Existing Evaluations

| File | Framework | What it tests |
|------|-----------|---------------|
| `evaluation_projects/test_01_hallucination.py` | DeepEval | Basic hallucination check |
| `evaluation_projects/test_02_deepeval.py` | DeepEval | Tool use, formatting, policy adherence, task completion |
| `evaluation_projects/test_03_ragas.py` *(new)* | RAGAS | RAG-specific: retrieval quality + generation faithfulness |
