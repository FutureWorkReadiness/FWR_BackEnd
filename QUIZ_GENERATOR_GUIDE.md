# Quiz Generator API - Complete Guide

> **Comprehensive documentation for the Quiz Generator module with step-by-step instructions, all scenarios, and job management explained.**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Understanding Jobs](#understanding-jobs)
5. [All Endpoints Reference](#all-endpoints-reference)
6. [Step-by-Step Scenarios](#step-by-step-scenarios)
7. [Job Lifecycle Deep Dive](#job-lifecycle-deep-dive)
8. [Output Files](#output-files)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Quiz Generator API provides endpoints to generate AI-powered quiz questions using Google's Gemini API. It wraps the `gemini_pkg` package and exposes its functionality through RESTful endpoints.

### What It Does

- **Generates quiz questions** for career assessments across multiple sectors
- **Supports multiple difficulty levels** (1-5) for each career
- **Tracks long-running jobs** with progress updates
- **Resumes interrupted generation** using checkpoints
- **Saves output to structured JSON files**

### Base URL

```
/api/v1/quiz-generator
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Router                            │
│  (router.py - defines all endpoints)                            │
├─────────────────────────────────────────────────────────────────┤
│                          ↓                                       │
├─────────────────────────────────────────────────────────────────┤
│                    Service Layer                                 │
│  (service.py - business logic, job management)                  │
├─────────────────────────────────────────────────────────────────┤
│                          ↓                                       │
├───────────────────────┬─────────────────────────────────────────┤
│   Database Models     │        gemini_pkg                        │
│   (models.py)         │   (AI generation logic)                  │
│   GenerationJob       │   GeminiQuizGeneratorV4                  │
├───────────────────────┴─────────────────────────────────────────┤
│                          ↓                                       │
├─────────────────────────────────────────────────────────────────┤
│                    PostgreSQL + File System                      │
│           (Job records + Generated JSON files)                   │
└─────────────────────────────────────────────────────────────────┘
```

### Files Structure

```
src/app/modules/quiz_generator/
├── __init__.py      # Module exports
├── models.py        # SQLAlchemy model: GenerationJob
├── schema.py        # Pydantic schemas for requests/responses
├── service.py       # Business logic and job management
└── router.py        # FastAPI endpoints
```

---

## Quick Start

### 1. Check API Status

Before generating anything, verify the Gemini API key is configured:

```bash
curl http://localhost:8000/api/v1/quiz-generator/api-status
```

**Expected Response:**

```json
{
	"api_key_configured": true,
	"message": "Ready for generation"
}
```

### 2. View Available Sectors

See what sectors and careers you can generate:

```bash
curl http://localhost:8000/api/v1/quiz-generator/sectors
```

**Response:**

```json
{
  "sectors": ["technology", "finance", "health_social_care", "education", "construction"],
  "sector_details": {
    "technology": {
      "Software Development": ["FRONTEND_DEVELOPER", "BACKEND_DEVELOPER", "FULLSTACK_DEVELOPER"],
      "Data": ["DATA_SCIENTIST", "DATA_ANALYST", "ML_ENGINEER"],
      ...
    },
    ...
  }
}
```

### 3. Generate Questions (Quick Test)

For a quick synchronous test:

```bash
curl -X POST http://localhost:8000/api/v1/quiz-generator/generate/career-level \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "technology",
    "career": "FRONTEND_DEVELOPER",
    "level": 1
  }'
```

---

## Understanding Jobs

### What is a Job?

A **Job** is a database record that tracks a quiz generation task. Jobs are essential for:

1. **Tracking Progress** - Know how far along a generation task is
2. **Async Operations** - Start a task and check on it later
3. **Error Recovery** - See what went wrong if a task fails
4. **History** - Keep a record of all generation attempts

### Job Types

| Type           | Description                             | Typical Duration |
| -------------- | --------------------------------------- | ---------------- |
| `career_level` | Single career at one level              | 5-15 minutes     |
| `soft_skills`  | Soft skills questions                   | 5-10 minutes     |
| `sector`       | All careers in a sector (5 levels each) | 1-4 hours        |
| `full`         | ALL sectors + soft skills               | Many hours       |

### Job Statuses

| Status      | Meaning                      | What to Do            |
| ----------- | ---------------------------- | --------------------- |
| `pending`   | Job created, not yet started | Wait for it to start  |
| `running`   | Currently generating         | Poll for progress     |
| `completed` | Successfully finished        | View results          |
| `failed`    | An error occurred            | Check `error_message` |
| `cancelled` | Job was cancelled            | N/A                   |

### Job Database Schema

```sql
CREATE TABLE generation_jobs (
    job_id          UUID PRIMARY KEY,
    job_type        VARCHAR(50) NOT NULL,      -- 'career_level', 'sector', etc.
    status          VARCHAR(20) NOT NULL,      -- 'pending', 'running', etc.
    parameters      JSON,                       -- Input params (sector, career, level)
    progress_percent INTEGER DEFAULT 0,        -- 0-100
    progress_message VARCHAR(500),              -- Human-readable status
    result_summary   JSON,                      -- Summary on completion
    error_message    TEXT,                      -- Error details on failure
    created_at      TIMESTAMP WITH TIME ZONE,
    started_at      TIMESTAMP WITH TIME ZONE,
    completed_at    TIMESTAMP WITH TIME ZONE
);
```

---

## All Endpoints Reference

### Info Endpoints (Read-Only)

#### GET `/sectors`

Returns available sectors and their careers.

```bash
curl http://localhost:8000/api/v1/quiz-generator/sectors
```

#### GET `/checkpoint`

Returns checkpoint status (what has been generated already).

```bash
curl http://localhost:8000/api/v1/quiz-generator/checkpoint
```

**Response:**

```json
{
  "has_checkpoint": true,
  "completed_chunks": 15,
  "chunks": ["technology__FRONTEND_DEVELOPER__1", "technology__FRONTEND_DEVELOPER__2", ...]
}
```

#### GET `/api-status`

Check if the Gemini API key is configured.

```bash
curl http://localhost:8000/api/v1/quiz-generator/api-status
```

---

### Job Management Endpoints

#### GET `/jobs`

List all generation jobs.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | string | null | Filter by status |
| `limit` | int | 50 | Max results (1-100) |
| `offset` | int | 0 | Pagination offset |

**Examples:**

```bash
# Get all jobs
curl "http://localhost:8000/api/v1/quiz-generator/jobs"

# Get only running jobs
curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=running"

# Get failed jobs with pagination
curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=failed&limit=10&offset=0"

# Get completed jobs
curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=completed"
```

**Response:**

```json
{
	"jobs": [
		{
			"job_id": "550e8400-e29b-41d4-a716-446655440000",
			"job_type": "career_level",
			"status": "completed",
			"parameters": {
				"sector": "technology",
				"career": "FRONTEND_DEVELOPER",
				"level": 1
			},
			"progress_percent": 100,
			"progress_message": "Generation complete!",
			"result_summary": { "questions_generated": 25 },
			"error_message": null,
			"created_at": "2025-12-19T10:00:00Z",
			"started_at": "2025-12-19T10:00:01Z",
			"completed_at": "2025-12-19T10:12:34Z"
		}
	],
	"total": 1
}
```

#### GET `/jobs/{job_id}`

Get a specific job by ID.

```bash
curl "http://localhost:8000/api/v1/quiz-generator/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**

```json
{
	"job_id": "550e8400-e29b-41d4-a716-446655440000",
	"job_type": "career_level",
	"status": "running",
	"parameters": {
		"sector": "technology",
		"career": "FRONTEND_DEVELOPER",
		"level": 1
	},
	"progress_percent": 45,
	"progress_message": "Generating technology/FRONTEND_DEVELOPER Level 1...",
	"result_summary": null,
	"error_message": null,
	"created_at": "2025-12-19T10:00:00Z",
	"started_at": "2025-12-19T10:00:01Z",
	"completed_at": null
}
```

#### DELETE `/jobs/{job_id}`

Delete a job record (not the generated files).

```bash
curl -X DELETE "http://localhost:8000/api/v1/quiz-generator/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Response:** `204 No Content` on success

---

### Synchronous Generation Endpoints

> ⚠️ **Warning:** These endpoints block until complete. Use for testing only.

#### POST `/generate/career-level`

Generate for a specific career and level (blocks until done).

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/career-level" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "technology",
    "career": "FRONTEND_DEVELOPER",
    "level": 1
  }'
```

**Request Body:**

```json
{
	"sector": "technology", // Optional, defaults to "technology"
	"career": "FRONTEND_DEVELOPER", // Required
	"level": 1 // Required, 1-5
}
```

**Response:**

```json
{
	"success": true,
	"message": "Generated 25 questions for technology/FRONTEND_DEVELOPER Level 1",
	"questions_generated": 25,
	"details": {
		"sector": "technology",
		"career": "FRONTEND_DEVELOPER",
		"level": 1
	}
}
```

#### POST `/generate/soft-skills`

Generate soft skills questions (blocks until done).

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/soft-skills"
```

**Response:**

```json
{
	"success": true,
	"message": "Generated 50 soft skills questions",
	"questions_generated": 50,
	"details": { "type": "soft_skills" }
}
```

#### POST `/generate/sector`

Generate for an entire sector (blocks, can take hours).

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/sector" \
  -H "Content-Type: application/json" \
  -d '{"sector": "finance"}'
```

---

### Asynchronous Generation Endpoints

> ✅ **Recommended:** These return immediately with a job ID.

#### POST `/generate/career-level/async`

Start async generation for a specific career/level.

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/career-level/async" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "technology",
    "career": "BACKEND_DEVELOPER",
    "level": 2
  }'
```

**Response (202 Accepted):**

```json
{
	"message": "Generation started for technology/BACKEND_DEVELOPER Level 2",
	"job_id": "550e8400-e29b-41d4-a716-446655440000",
	"job_type": "career_level",
	"status": "pending"
}
```

#### POST `/generate/soft-skills/async`

Start async soft skills generation.

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/soft-skills/async"
```

**Response (202 Accepted):**

```json
{
	"message": "Soft skills generation started",
	"job_id": "660e8400-e29b-41d4-a716-446655440001",
	"job_type": "soft_skills",
	"status": "pending"
}
```

#### POST `/generate/sector/async`

Start async generation for an entire sector.

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/sector/async" \
  -H "Content-Type: application/json" \
  -d '{"sector": "health_social_care"}'
```

**Response (202 Accepted):**

```json
{
	"message": "Sector generation started for 'health_social_care'",
	"job_id": "770e8400-e29b-41d4-a716-446655440002",
	"job_type": "sector",
	"status": "pending"
}
```

#### POST `/generate/full/async`

Start async generation for ALL sectors.

```bash
curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/full/async" \
  -H "Content-Type: application/json" \
  -d '{"include_soft_skills": true}'
```

**Response (202 Accepted):**

```json
{
	"message": "Full generation started (all sectors)",
	"job_id": "880e8400-e29b-41d4-a716-446655440003",
	"job_type": "full",
	"status": "pending"
}
```

---

## Step-by-Step Scenarios

### Scenario 1: Generate Questions for One Career Level (Quick Test)

**Goal:** Generate Level 1 questions for a Frontend Developer

**Steps:**

1. **Check API is ready:**

   ```bash
   curl http://localhost:8000/api/v1/quiz-generator/api-status
   ```

2. **Start async generation:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/career-level/async" \
     -H "Content-Type: application/json" \
     -d '{
       "sector": "technology",
       "career": "FRONTEND_DEVELOPER",
       "level": 1
     }'
   ```

3. **Save the job_id from response:**

   ```json
   { "job_id": "abc123...", "status": "pending" }
   ```

4. **Poll for progress (repeat every 30 seconds):**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs/abc123..."
   ```

5. **Check until status is `completed`:**

   ```json
   {
   	"status": "completed",
   	"progress_percent": 100,
   	"result_summary": { "questions_generated": 25 }
   }
   ```

6. **Find output file:**
   ```
   data/generated_sectors/technology.json
   ```

---

### Scenario 2: Generate an Entire Sector

**Goal:** Generate all careers and levels for the Finance sector

**Steps:**

1. **View what careers are in Finance:**

   ```bash
   curl http://localhost:8000/api/v1/quiz-generator/sectors | jq '.sector_details.finance'
   ```

2. **Start sector generation:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/sector/async" \
     -H "Content-Type: application/json" \
     -d '{"sector": "finance"}'
   ```

3. **Monitor progress:**

   ```bash
   # Get job ID from response, then poll
   watch -n 60 'curl -s "http://localhost:8000/api/v1/quiz-generator/jobs/YOUR_JOB_ID" | jq "{status, progress_percent, progress_message}"'
   ```

4. **Wait for completion (can take 1-4 hours)**

5. **Verify output:**
   ```bash
   cat data/generated_sectors/finance.json | jq 'keys'
   ```

---

### Scenario 3: Monitor Multiple Running Jobs

**Goal:** See all currently running generation jobs

**Steps:**

1. **List running jobs:**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=running"
   ```

2. **Get detailed status of each:**

   ```bash
   # For each job_id in the response
   curl "http://localhost:8000/api/v1/quiz-generator/jobs/{job_id}"
   ```

3. **View progress summary:**
   ```bash
   curl -s "http://localhost:8000/api/v1/quiz-generator/jobs?status=running" | \
     jq '.jobs[] | {job_id, job_type, progress_percent, progress_message}'
   ```

---

### Scenario 4: Resume After Server Restart

**Goal:** Continue generation after a restart/failure

**Steps:**

1. **Check checkpoint status:**

   ```bash
   curl http://localhost:8000/api/v1/quiz-generator/checkpoint
   ```

   Response shows what's already been generated:

   ```json
   {
     "has_checkpoint": true,
     "completed_chunks": 15,
     "chunks": ["technology__FRONTEND_DEVELOPER__1", ...]
   }
   ```

2. **Check for pending/running jobs that may have been interrupted:**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=running"
   ```

3. **The generator automatically skips completed chunks.** Just restart:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/sector/async" \
     -H "Content-Type: application/json" \
     -d '{"sector": "technology"}'
   ```

4. **The new job will resume from checkpoint**, not regenerate everything.

---

### Scenario 5: Investigate a Failed Job

**Goal:** Understand why a job failed

**Steps:**

1. **List failed jobs:**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=failed"
   ```

2. **Get full details:**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs/FAILED_JOB_ID" | jq
   ```

3. **Check error_message field:**

   ```json
   {
   	"status": "failed",
   	"error_message": "API rate limit exceeded. Please try again later.",
   	"parameters": {
   		"sector": "technology",
   		"career": "DATA_SCIENTIST",
   		"level": 3
   	}
   }
   ```

4. **Fix the issue and retry:**

   ```bash
   # Wait for rate limit to reset, then retry with same parameters
   curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/career-level/async" \
     -H "Content-Type: application/json" \
     -d '{"sector": "technology", "career": "DATA_SCIENTIST", "level": 3}'
   ```

5. **Clean up old failed job:**
   ```bash
   curl -X DELETE "http://localhost:8000/api/v1/quiz-generator/jobs/FAILED_JOB_ID"
   ```

---

### Scenario 6: Generate Everything (Full Generation)

**Goal:** Generate ALL quiz content for ALL sectors

**Steps:**

1. **⚠️ Warning:** This takes many hours. Plan accordingly.

2. **Start full generation:**

   ```bash
   curl -X POST "http://localhost:8000/api/v1/quiz-generator/generate/full/async" \
     -H "Content-Type: application/json" \
     -d '{"include_soft_skills": true}'
   ```

3. **Set up monitoring script:**

   ```bash
   #!/bin/bash
   JOB_ID="your-job-id-here"
   while true; do
     STATUS=$(curl -s "http://localhost:8000/api/v1/quiz-generator/jobs/$JOB_ID" | jq -r '.status')
     PROGRESS=$(curl -s "http://localhost:8000/api/v1/quiz-generator/jobs/$JOB_ID" | jq -r '.progress_percent')
     MESSAGE=$(curl -s "http://localhost:8000/api/v1/quiz-generator/jobs/$JOB_ID" | jq -r '.progress_message')

     echo "$(date): [$STATUS] $PROGRESS% - $MESSAGE"

     if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
       break
     fi

     sleep 300  # Check every 5 minutes
   done
   ```

4. **Verify all outputs:**
   ```bash
   ls -la data/generated_sectors/
   ```

---

### Scenario 7: Clean Up Old Jobs

**Goal:** Remove old job records from the database

**Steps:**

1. **List completed jobs:**

   ```bash
   curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=completed&limit=100"
   ```

2. **Delete specific jobs:**

   ```bash
   curl -X DELETE "http://localhost:8000/api/v1/quiz-generator/jobs/{job_id}"
   ```

3. **Script to delete all completed jobs:**
   ```bash
   for JOB_ID in $(curl -s "http://localhost:8000/api/v1/quiz-generator/jobs?status=completed" | jq -r '.jobs[].job_id'); do
     echo "Deleting $JOB_ID"
     curl -X DELETE "http://localhost:8000/api/v1/quiz-generator/jobs/$JOB_ID"
   done
   ```

---

## Job Lifecycle Deep Dive

### State Transitions

```
                    ┌─────────────┐
                    │   pending   │
                    └──────┬──────┘
                           │
                    (job starts)
                           │
                           ▼
                    ┌─────────────┐
                    │   running   │◀──────┐
                    └──────┬──────┘       │
                           │              │
              ┌────────────┼────────────┐ │
              │            │            │ │
              ▼            │            ▼ │
       ┌─────────────┐     │     ┌─────────────┐
       │  completed  │     │     │   failed    │
       └─────────────┘     │     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  cancelled  │
                    └─────────────┘
```

### Timeline of a Typical Job

```
Time  Event                           Status          Progress
────────────────────────────────────────────────────────────────
0s    POST /generate/sector/async     pending         0%
1s    Background task picks up job    running         0%
2s    Initializing generator...       running         5%
30s   Generating career 1/10...       running         10%
5min  Generating career 3/10...       running         30%
...   ...                             running         ...
2hr   Generation complete!            completed       100%
```

### What Each Field Means

| Field              | Type      | Description                                                    |
| ------------------ | --------- | -------------------------------------------------------------- |
| `job_id`           | UUID      | Unique identifier for this job                                 |
| `job_type`         | string    | What kind of generation (career_level, sector, etc.)           |
| `status`           | string    | Current state (pending, running, completed, failed, cancelled) |
| `parameters`       | JSON      | Input parameters (sector, career, level)                       |
| `progress_percent` | int       | 0-100, how far along                                           |
| `progress_message` | string    | Human-readable status like "Generating X..."                   |
| `result_summary`   | JSON      | On completion: what was generated                              |
| `error_message`    | text      | On failure: what went wrong                                    |
| `created_at`       | timestamp | When job was created                                           |
| `started_at`       | timestamp | When generation actually started                               |
| `completed_at`     | timestamp | When job finished (success or failure)                         |

---

## Output Files

### File Locations

| Content Type           | Path                                                          |
| ---------------------- | ------------------------------------------------------------- |
| **Production quizzes** | `data/generated_sectors/{sector}.json`                        |
| **Combined quiz bank** | `geminiGenerator/results/combined/all_sectors_quiz_bank.json` |
| **Checkpoints**        | `geminiGenerator/results/logs/generation_checkpoint.json`     |
| **Generation logs**    | `geminiGenerator/results/logs/`                               |
| **Raw API responses**  | `geminiGenerator/raw_responses_gemini_v2.5/`                  |
| **Cleaned chunks**     | `geminiGenerator/clean_quiz_chunks_gemini_v2.5/`              |

### Production Quiz File Structure

Each sector file (`data/generated_sectors/technology.json`):

```json
{
  "FRONTEND_DEVELOPER": {
    "level_1": {
      "quiz_pool": [
        {
          "id": "uuid-here",
          "question": "What is the purpose of CSS flexbox?",
          "options": [
            {"id": "a", "text": "Database management"},
            {"id": "b", "text": "Layout control"},
            {"id": "c", "text": "Server configuration"},
            {"id": "d", "text": "API design"}
          ],
          "correct_answer": "b",
          "explanation": "Flexbox is a CSS layout model...",
          "difficulty": 1,
          "category": "frontend",
          "tags": ["css", "layout", "flexbox"]
        }
      ]
    },
    "level_2": { ... },
    "level_3": { ... },
    "level_4": { ... },
    "level_5": { ... }
  },
  "BACKEND_DEVELOPER": { ... },
  ...
}
```

---

## Error Handling

### Common Errors and Solutions

| Error                                | Cause                | Solution                              |
| ------------------------------------ | -------------------- | ------------------------------------- |
| `503: GEMINI_API_KEY not configured` | Missing API key      | Set `GEMINI_API_KEY` in `.env`        |
| `400: Unknown sector: xyz`           | Invalid sector name  | Check `/sectors` for valid options    |
| `404: Job not found`                 | Invalid job ID       | Verify the job_id is correct          |
| API rate limit exceeded              | Too many requests    | Wait and retry, or use checkpoints    |
| Generation timeout                   | Very long generation | Use async endpoints, monitor progress |

### Error Response Format

```json
{
	"detail": "GEMINI_API_KEY not configured"
}
```

For failed jobs:

```json
{
	"job_id": "...",
	"status": "failed",
	"error_message": "Detailed error message here",
	"progress_percent": 45,
	"progress_message": "Failed during: Generating technology/DATA_SCIENTIST Level 3"
}
```

---

## Best Practices

### 1. Always Use Async for Production

```bash
# ❌ Don't do this in production (blocks for hours)
curl -X POST ".../generate/sector"

# ✅ Do this instead
curl -X POST ".../generate/sector/async"
```

### 2. Monitor Long-Running Jobs

```bash
# Set up a cron job or script to poll
*/5 * * * * curl -s "http://localhost:8000/api/v1/quiz-generator/jobs?status=running" >> /var/log/quiz-gen.log
```

### 3. Check API Status Before Starting

```bash
# Always verify first
if curl -s ".../api-status" | grep -q '"api_key_configured": true'; then
  curl -X POST ".../generate/sector/async" ...
else
  echo "API key not configured!"
fi
```

### 4. Use Checkpoints for Resumability

The generator automatically saves progress. If interrupted:

1. Check checkpoint status: `GET /checkpoint`
2. Restart the same job - it will skip completed chunks
3. No need to start from scratch

### 5. Clean Up Completed Jobs Periodically

```bash
# Delete jobs older than 7 days
for JOB_ID in $(curl -s ".../jobs?status=completed&limit=100" | jq -r '.jobs[].job_id'); do
  curl -X DELETE ".../jobs/$JOB_ID"
done
```

---

## Troubleshooting

### Job Stuck in "pending"

**Cause:** Background worker not processing

**Solution:**

1. Check server logs for errors
2. Verify database connection
3. Restart the application

### Job Stuck in "running" After Restart

**Cause:** Job was running when server stopped

**Solution:**

1. The job record is orphaned (no actual task running)
2. Delete the old job: `DELETE /jobs/{job_id}`
3. Start a new job - it will use checkpoints

### No Output Files Generated

**Cause:** Generation completed but files not found

**Check:**

1. Verify `data/generated_sectors/` directory exists
2. Check `geminiGenerator/results/` for intermediate files
3. Look for errors in job's `error_message`

### API Returns 503 Errors

**Cause:** Gemini API issues or rate limiting

**Solution:**

1. Check `GEMINI_API_KEY` is valid
2. Wait for rate limits to reset
3. Check Google Cloud console for API status

### Questions Quality Issues

**Cause:** Prompts or model configuration

**Solution:**

1. Check `geminiGenerator/gemini_pkg/prompts/` for prompt templates
2. Verify temperature and model settings in `config/settings.py`
3. Review raw responses in `geminiGenerator/raw_responses_gemini_v2.5/`

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUIZ GENERATOR API                           │
├─────────────────────────────────────────────────────────────────┤
│ BASE URL: /api/v1/quiz-generator                                │
├─────────────────────────────────────────────────────────────────┤
│ INFO:                                                           │
│   GET /sectors         - List available sectors                 │
│   GET /checkpoint      - View checkpoint status                 │
│   GET /api-status      - Check API key configuration            │
├─────────────────────────────────────────────────────────────────┤
│ JOBS:                                                           │
│   GET /jobs            - List all jobs (filter: ?status=...)    │
│   GET /jobs/{id}       - Get job details                        │
│   DELETE /jobs/{id}    - Delete a job                           │
├─────────────────────────────────────────────────────────────────┤
│ SYNC GENERATION (blocks until done):                            │
│   POST /generate/career-level                                   │
│   POST /generate/soft-skills                                    │
│   POST /generate/sector                                         │
├─────────────────────────────────────────────────────────────────┤
│ ASYNC GENERATION (returns immediately):                         │
│   POST /generate/career-level/async                             │
│   POST /generate/soft-skills/async                              │
│   POST /generate/sector/async                                   │
│   POST /generate/full/async                                     │
├─────────────────────────────────────────────────────────────────┤
│ JOB STATUSES: pending → running → completed/failed/cancelled    │
├─────────────────────────────────────────────────────────────────┤
│ OUTPUT: data/generated_sectors/{sector}.json                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [ADDING_ENDPOINTS.md](ADDING_ENDPOINTS.md) - How to add new endpoints
- [geminiGenerator/README.md](geminiGenerator/README.md) - Full gemini_pkg documentation
- [QUIZ_GENERATOR_API.md](QUIZ_GENERATOR_API.md) - Quick API reference

---

_Last updated: December 2025_
