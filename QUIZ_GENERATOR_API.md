# 🤖 Quiz Generator API Documentation

This module provides REST API endpoints for generating interview questions using the Gemini AI API. It wraps the internal `gemini_pkg` package and exposes its functionality through HTTP endpoints.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [API Base URL](#api-base-url)
- [Endpoints](#endpoints)
  - [Info Endpoints](#info-endpoints)
  - [Job Management](#job-management)
  - [Synchronous Generation](#synchronous-generation)
  - [Asynchronous Generation](#asynchronous-generation)
- [Request/Response Schemas](#requestresponse-schemas)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Quiz Generator module allows you to:

- **Generate interview questions** for specific careers, sectors, or all content
- **Track generation jobs** with progress updates
- **Resume interrupted generations** via checkpoint system
- **Choose sync or async execution** based on your needs

### Generation Types

| Type         | Duration     | Use Case                                |
| ------------ | ------------ | --------------------------------------- |
| Career/Level | 5-15 minutes | Testing, single quiz generation         |
| Soft Skills  | 5-10 minutes | Behavioral questions                    |
| Sector       | 2-6 hours    | All careers in a sector (5 levels each) |
| Full         | 12-24+ hours | Complete content generation             |

---

## Prerequisites

### 1. Gemini API Key

You must have a valid Gemini API key configured in your environment:

```env
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Optional Model Configuration

Override default models if needed:

```env
GEMINI_MODEL_JUNIOR=models/gemini-2.5-flash   # For levels 1-2
GEMINI_MODEL_SENIOR=models/gemini-2.5-pro     # For levels 3-5
GEMINI_MODEL_CRITIC=models/gemini-2.5-pro     # For validation/repair
```

---

## API Base URL

All endpoints are prefixed with:

```
/api/v1/quiz-generator
```

Full URL example: `http://localhost:8000/api/v1/quiz-generator/sectors`

---

## Endpoints

### Info Endpoints

These read-only endpoints provide information about available options and system status.

---

#### `GET /sectors`

**Description:** Get list of available sectors and their careers/branches.

**Response:**

```json
{
  "sectors": ["technology", "finance", "health_social_care", "education", "construction"],
  "sector_details": {
    "technology": {
      "Software Development": ["FRONTEND_DEVELOPER", "BACKEND_DEVELOPER"],
      "Mobile Development": ["IOS_DEVELOPER", "ANDROID_DEVELOPER", "MOBILE_DEVELOPMENT_CROSS_PLATFORM"],
      "Data Science & AI": ["DATA_SCIENTIST", "DATA_ANALYST", "DATA_ENGINEER", "AI_ML_ENGINEER"],
      "Infrastructure & Cloud Operations": ["DEVOPS_ENGINEER", "CLOUD_ENGINEER", "DATABASE_ADMINISTRATOR_DBA", "NETWORK_ENGINEER", "SYSTEMS_ADMINISTRATOR"],
      "Cybersecurity": ["CYBERSECURITY_ANALYST"],
      "Quality Assurance": ["QA_AUTOMATION_ENGINEER_SET"],
      "Product & Design": ["UX_UI_DESIGNER", "TECHNICAL_PRODUCT_MANAGER", "TECHNICAL_PROJECT_MANAGER_SCRUM_MASTER"]
    },
    "finance": { ... },
    "health_social_care": { ... },
    "education": { ... },
    "construction": { ... }
  }
}
```

**Use Case:** Discover valid sector/career names before starting generation.

---

#### `GET /checkpoint`

**Description:** Get the current checkpoint status from previous generation runs.

**Response:**

```json
{
	"has_checkpoint": true,
	"completed_chunks": 45,
	"chunks": [
		"technology_FRONTEND_DEVELOPER_lvl1_chunk1",
		"technology_FRONTEND_DEVELOPER_lvl1_chunk2",
		"technology_FRONTEND_DEVELOPER_lvl1_chunk3",
		"..."
	]
}
```

**Use Case:** Check progress before resuming an interrupted generation.

---

#### `GET /api-status`

**Description:** Check if the Gemini API key is configured.

**Response:**

```json
{
	"api_key_configured": true,
	"message": "Ready for generation"
}
```

or

```json
{
	"api_key_configured": false,
	"message": "GEMINI_API_KEY not set"
}
```

**Use Case:** Verify environment configuration before attempting generation.

---

### Job Management

Track and manage generation jobs.

---

#### `GET /jobs`

**Description:** List all generation jobs with optional filtering.

**Query Parameters:**

| Parameter | Type   | Default | Description                                                                |
| --------- | ------ | ------- | -------------------------------------------------------------------------- |
| `status`  | string | null    | Filter by status: `pending`, `running`, `completed`, `failed`, `cancelled` |
| `limit`   | int    | 50      | Max results (1-100)                                                        |
| `offset`  | int    | 0       | Pagination offset                                                          |

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
			"result_summary": {
				"questions_generated": 20,
				"job_type": "career_level"
			},
			"error_message": null,
			"created_at": "2024-01-15T10:30:00Z",
			"started_at": "2024-01-15T10:30:01Z",
			"completed_at": "2024-01-15T10:45:00Z"
		}
	],
	"total": 1
}
```

---

#### `GET /jobs/{job_id}`

**Description:** Get a specific job by ID.

**Path Parameters:**

| Parameter | Type | Description                 |
| --------- | ---- | --------------------------- |
| `job_id`  | UUID | The job's unique identifier |

**Response:** Same as single job in `/jobs` list.

**Error Response (404):**

```json
{
	"detail": "Job not found"
}
```

---

#### `DELETE /jobs/{job_id}`

**Description:** Delete a job record from the database.

**Path Parameters:**

| Parameter | Type | Description                 |
| --------- | ---- | --------------------------- |
| `job_id`  | UUID | The job's unique identifier |

**Response:** `204 No Content`

**Note:** This only deletes the job tracking record. Generated content is NOT deleted.

---

### Synchronous Generation

These endpoints run immediately and block until complete. Use for testing or small generations.

---

#### `POST /generate/career-level`

**Description:** Generate questions for a specific career and difficulty level.

**⚠️ Duration:** 5-15 minutes (blocks until complete)

**Request Body:**

```json
{
	"sector": "technology",
	"career": "FRONTEND_DEVELOPER",
	"level": 1
}
```

| Field    | Type   | Required                   | Description                                       |
| -------- | ------ | -------------------------- | ------------------------------------------------- |
| `sector` | string | No (default: "technology") | Sector name                                       |
| `career` | string | Yes                        | Career/role name (use exact name from `/sectors`) |
| `level`  | int    | Yes                        | Difficulty level 1-5                              |

**Response (Success):**

```json
{
	"success": true,
	"message": "Generated 20 questions for technology/FRONTEND_DEVELOPER Level 1",
	"questions_generated": 20,
	"details": {
		"sector": "technology",
		"career": "FRONTEND_DEVELOPER",
		"level": 1
	},
	"error": null
}
```

**Response (Failure):**

```json
{
	"success": false,
	"message": "Generation failed",
	"questions_generated": 0,
	"details": null,
	"error": "GEMINI_API_KEY not configured"
}
```

---

#### `POST /generate/soft-skills`

**Description:** Generate soft skills/behavioral interview questions.

**⚠️ Duration:** 5-10 minutes

**Request Body:** None required

**Response:**

```json
{
	"success": true,
	"message": "Generated 20 soft skills questions",
	"questions_generated": 20,
	"details": {
		"type": "soft_skills"
	},
	"error": null
}
```

---

#### `POST /generate/sector`

**Description:** Generate questions for ALL careers in a sector (5 levels each).

**⚠️ Duration:** 2-6 HOURS (consider using async endpoint instead)

**Request Body:**

```json
{
	"sector": "technology"
}
```

| Field    | Type   | Required | Description |
| -------- | ------ | -------- | ----------- |
| `sector` | string | Yes      | Sector name |

**Valid Sectors:**

- `technology`
- `finance`
- `health_social_care`
- `education`
- `construction`

**Response:**

```json
{
	"success": true,
	"message": "Generated 1800 questions for sector 'technology'",
	"questions_generated": 1800,
	"details": {
		"sector": "technology",
		"careers_processed": 18,
		"levels_per_career": 5
	},
	"error": null
}
```

---

### Asynchronous Generation

These endpoints return immediately with a job ID. Use for long-running generations.

---

#### `POST /generate/career-level/async`

**Description:** Start career/level generation as a background job.

**Request Body:** Same as synchronous `/generate/career-level`

**Response (202 Accepted):**

```json
{
	"message": "Generation started for technology/FRONTEND_DEVELOPER Level 1",
	"job_id": "550e8400-e29b-41d4-a716-446655440000",
	"job_type": "career_level",
	"status": "pending"
}
```

**Workflow:**

1. Call this endpoint → get `job_id`
2. Poll `GET /jobs/{job_id}` to check progress
3. Job `status` changes: `pending` → `running` → `completed` (or `failed`)

---

#### `POST /generate/soft-skills/async`

**Description:** Start soft skills generation as a background job.

**Request Body:** None

**Response (202 Accepted):**

```json
{
	"message": "Soft skills generation started",
	"job_id": "550e8400-e29b-41d4-a716-446655440001",
	"job_type": "soft_skills",
	"status": "pending"
}
```

---

#### `POST /generate/sector/async`

**Description:** Start sector generation as a background job.

**Request Body:**

```json
{
	"sector": "technology"
}
```

**Response (202 Accepted):**

```json
{
	"message": "Sector generation started for 'technology'",
	"job_id": "550e8400-e29b-41d4-a716-446655440002",
	"job_type": "sector",
	"status": "pending"
}
```

---

#### `POST /generate/full/async`

**Description:** Start FULL generation (all sectors) as a background job.

**⚠️ This can take 12-24+ hours!**

**Request Body:**

```json
{
	"include_soft_skills": true
}
```

| Field                 | Type | Default | Description                         |
| --------------------- | ---- | ------- | ----------------------------------- |
| `include_soft_skills` | bool | true    | Also generate soft skills questions |

**Response (202 Accepted):**

```json
{
	"message": "Full generation started (all sectors)",
	"job_id": "550e8400-e29b-41d4-a716-446655440003",
	"job_type": "full",
	"status": "pending"
}
```

---

## Request/Response Schemas

### Job Status Values

| Status      | Description                      |
| ----------- | -------------------------------- |
| `pending`   | Job created, waiting to start    |
| `running`   | Currently generating questions   |
| `completed` | Successfully finished            |
| `failed`    | Error occurred during generation |
| `cancelled` | Job was cancelled                |

### Job Types

| Type           | Description                             |
| -------------- | --------------------------------------- |
| `career_level` | Single career at one difficulty level   |
| `soft_skills`  | Behavioral/soft skills questions        |
| `sector`       | All careers in a sector (5 levels each) |
| `full`         | All sectors + soft skills               |

### Difficulty Levels

| Level | Description  | Time Limit | Passing Score |
| ----- | ------------ | ---------- | ------------- |
| 1     | Entry/Junior | 30 min     | 70%           |
| 2     | Early Career | 40 min     | 70%           |
| 3     | Mid-Level    | 50 min     | 75%           |
| 4     | Senior       | 50 min     | 75%           |
| 5     | Expert/Lead  | 60 min     | 80%           |

---

## Usage Examples

### cURL Examples

#### Check API Status

```bash
curl http://localhost:8000/api/v1/quiz-generator/api-status
```

#### List Available Sectors

```bash
curl http://localhost:8000/api/v1/quiz-generator/sectors
```

#### Generate Single Career/Level (Sync)

```bash
curl -X POST http://localhost:8000/api/v1/quiz-generator/generate/career-level \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "technology",
    "career": "FRONTEND_DEVELOPER",
    "level": 1
  }'
```

#### Generate Soft Skills (Sync)

```bash
curl -X POST http://localhost:8000/api/v1/quiz-generator/generate/soft-skills
```

#### Start Async Sector Generation

```bash
# Start the job
curl -X POST http://localhost:8000/api/v1/quiz-generator/generate/sector/async \
  -H "Content-Type: application/json" \
  -d '{"sector": "technology"}'

# Response: {"job_id": "abc-123-...", "status": "pending"}

# Check progress (repeat until status is "completed" or "failed")
curl http://localhost:8000/api/v1/quiz-generator/jobs/abc-123-...
```

#### List All Jobs

```bash
# All jobs
curl http://localhost:8000/api/v1/quiz-generator/jobs

# Only completed jobs
curl "http://localhost:8000/api/v1/quiz-generator/jobs?status=completed"

# With pagination
curl "http://localhost:8000/api/v1/quiz-generator/jobs?limit=10&offset=0"
```

#### Delete a Job Record

```bash
curl -X DELETE http://localhost:8000/api/v1/quiz-generator/jobs/abc-123-...
```

---

### Python Examples

#### Using requests library

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1/quiz-generator"

# Check API status
response = requests.get(f"{BASE_URL}/api-status")
print(response.json())

# Start async generation
response = requests.post(
    f"{BASE_URL}/generate/career-level/async",
    json={
        "sector": "technology",
        "career": "DATA_SCIENTIST",
        "level": 2
    }
)
job_data = response.json()
job_id = job_data["job_id"]
print(f"Started job: {job_id}")

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    job = response.json()

    print(f"Status: {job['status']} - {job['progress_message']}")

    if job["status"] in ["completed", "failed"]:
        break

    time.sleep(30)  # Check every 30 seconds

# Check result
if job["status"] == "completed":
    print(f"Generated {job['result_summary']['questions_generated']} questions!")
else:
    print(f"Failed: {job['error_message']}")
```

---

### JavaScript/Fetch Examples

```javascript
const BASE_URL = 'http://localhost:8000/api/v1/quiz-generator';

// Check API status
async function checkApiStatus() {
	const response = await fetch(`${BASE_URL}/api-status`);
	const data = await response.json();
	console.log(data);
}

// Start async generation
async function startGeneration() {
	const response = await fetch(`${BASE_URL}/generate/career-level/async`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			sector: 'technology',
			career: 'BACKEND_DEVELOPER',
			level: 3
		})
	});

	const data = await response.json();
	console.log(`Started job: ${data.job_id}`);
	return data.job_id;
}

// Check job status
async function checkJobStatus(jobId) {
	const response = await fetch(`${BASE_URL}/jobs/${jobId}`);
	return await response.json();
}

// Poll until complete
async function waitForCompletion(jobId) {
	while (true) {
		const job = await checkJobStatus(jobId);
		console.log(`Status: ${job.status} - ${job.progress_message}`);

		if (job.status === 'completed' || job.status === 'failed') {
			return job;
		}

		await new Promise((resolve) => setTimeout(resolve, 30000)); // 30 sec
	}
}
```

---

## Best Practices

### 1. Always Check API Status First

Before starting any generation, verify the API key is configured:

```bash
curl http://localhost:8000/api/v1/quiz-generator/api-status
```

### 2. Use Async for Long Operations

| Operation           | Recommendation               |
| ------------------- | ---------------------------- |
| Single career/level | Sync is OK (5-15 min)        |
| Soft skills         | Sync is OK (5-10 min)        |
| Entire sector       | **Use async** (2-6 hours)    |
| Full generation     | **Use async** (12-24+ hours) |

### 3. Poll Async Jobs Responsibly

Don't poll too frequently. Recommended intervals:

| Job Type     | Poll Interval      |
| ------------ | ------------------ |
| career_level | Every 30 seconds   |
| soft_skills  | Every 30 seconds   |
| sector       | Every 2-5 minutes  |
| full         | Every 5-10 minutes |

### 4. Check Checkpoint Before Resuming

If a previous run was interrupted:

```bash
curl http://localhost:8000/api/v1/quiz-generator/checkpoint
```

The generator automatically resumes from the last checkpoint.

### 5. Use Valid Career Names

Career names must match exactly. Get the list first:

```bash
curl http://localhost:8000/api/v1/quiz-generator/sectors | jq '.sector_details.technology'
```

---

## Troubleshooting

### Error: "GEMINI_API_KEY not configured"

**Cause:** The `GEMINI_API_KEY` environment variable is not set.

**Solution:**

1. Add to your `.env` file: `GEMINI_API_KEY=your_key_here`
2. Restart the application/container

### Error: "Unknown sector"

**Cause:** Invalid sector name provided.

**Solution:** Use one of: `technology`, `finance`, `health_social_care`, `education`, `construction`

### Job Stuck in "running" Status

**Cause:** The background task may have failed silently.

**Solution:**

1. Check application logs for errors
2. Verify the Gemini API quota is not exhausted
3. Delete the stuck job and retry

### Generation Taking Too Long

**Cause:** The Gemini API has rate limits and may throttle requests.

**Solution:**

- The generator has built-in retry logic and backoff
- Wait for rate limits to reset
- Check checkpoint status to monitor progress

### Empty Results

**Cause:** All chunks may have failed validation.

**Solution:**

1. Check the `results/logs/generation.log` file for errors
2. Verify the API key has sufficient quota
3. Try a smaller generation (single career/level) first

---

## Output Location

Generated questions are saved to:

| Output Type            | Path                                                          |
| ---------------------- | ------------------------------------------------------------- |
| **Production quizzes** | `data/generated_sectors/{sector}.json`                        |
| By sector/career       | `geminiGenerator/results/by_sector/{sector}/{career}/final/`  |
| Combined output        | `geminiGenerator/results/combined/all_sectors_quiz_bank.json` |
| Soft skills            | `geminiGenerator/results/by_sector/soft_skills/final/`        |
| Logs                   | `geminiGenerator/results/logs/generation.log`                 |
| Checkpoint             | `geminiGenerator/results/logs/generation_checkpoint.json`     |

> **Note:** Production quiz files are saved directly to the main project's `data/generated_sectors/` directory. Intermediate files (logs, raw responses, checkpoints) are saved within the `geminiGenerator/` folder.

---

## Related Documentation

- [Adding Endpoints Guide](ADDING_ENDPOINTS.md) - How to add new API endpoints
- [gemini_pkg README](geminiGenerator/README.md) - Original generator documentation

---

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f backend`
2. Verify environment: `GET /api-status`
3. Check Swagger docs: `http://localhost:8000/docs`
