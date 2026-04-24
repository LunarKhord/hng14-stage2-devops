
# FIXES.md – Stage 2 DevOps Microservices

This document records all bugs, misconfigurations, and architectural flaws found in the provided starter code, along with the exact changes made to resolve them.

### Overall FIX: Add comments were required.

## API Service (`api/main.py`)

### 1. Synchronous Redis Client Blocks Event Loop
- **File:** `api/main.py`
- **Lines:** `2` (`import redis`), `7` (`r = redis.Redis(...)`), `12` (`r.lpush`), `18` (`r.hget`)
- **Problem:** The code uses the synchronous `redis` client. FastAPI executes synchronous endpoints in a thread pool. When Redis I/O is slow, threads become blocked, exhausting the pool and causing request queuing / increased latency under load.
- **Fix:** Switched to the asynchronous `redis.asyncio` client. Converted endpoint functions to `async def` and added `await` to all Redis calls.


### 1.A Wrong Status Code Returned
- **File:** `api/main.py`
- **Lines:** `25`
- **Problem:** When a job is not found in Redis, the API returns the error message but with an HTTP 200 status code instead of 404.
- **Fix:** Changed the return to `raise HTTPException(status_code=404, detail="not found")` so the client receives a proper 404 response along with the error detail.


### 2. Hardcoded Redis Connection Parameters
- **File:** `api/main.py`
- **Line:** `7` (`host="localhost", port=6379`)
- **Problem:** The Redis host and port are hardcoded to `localhost:6379`. In a containerized environment, Redis runs in a separate container. `localhost` refers to the API container itself, causing connection failures. Changing the host would require modifying source code.
- **Fix:** Replaced hardcoded values with environment variables (`REDIS_HOST`, `REDIS_PORT`), providing sensible defaults for local development.

### 3. Blocking I/O in Endpoint Handlers
- **File:** `api/main.py`
- **Lines:** `11-21` (endpoint definitions)
- **Problem:** Although not a syntax error, the endpoint functions are synchronous (`def`) but perform blocking I/O (Redis operations). This prevents FastAPI from handling other requests concurrently while waiting for Redis.
- **Fix:** Converted both endpoint handlers to `async def` and used `await` for all Redis commands. This allows FastAPI's event loop to process other requests during I/O waits.

### 4. Missing Health Endpoint
- **File:** `api/main.py`
- **Lines:** N/A (endpoint not present)
- **Problem:** The FastAPI application lacks a `/health` endpoint. Without this, Docker's `HEALTHCHECK` cannot verify that the service is alive and ready to serve requests. This breaks container health monitoring and prevents `depends_on` conditions from working correctly in Docker Compose.
- **Fix:** Added a simple `GET /health` endpoint that returns a `200 OK` response.


## Worker Service (`worker/worker.py`)

### 1. Synchronous Redis Client and Blocking Sleep
- **File:** `worker/worker.py`
- **Lines:** `1` (`import redis`), `6` (`r = redis.Redis`), `10` (`time.sleep`), `14` (`r.hset`), `16` (`r.brpop`)
- **Problem:** Uses synchronous `redis` client and `time.sleep()`. In an async context, `time.sleep()` blocks the event loop, preventing the worker from handling timeouts or graceful shutdown. Synchronous Redis calls also block the loop.
- **Fix:** Replaced `import redis` with `import redis.asyncio as redis`. Replaced `time.sleep(2)` with `await asyncio.sleep(2)`. Added `import asyncio`. Made `process_job` an `async` function and used `await` for Redis commands and imported asyncio, where the asyncio time leaves.



### 2. Hardcoded Redis Connection Parameters
- **File:** `worker/worker.py`
- **Line:** `6`
- **Problem:** Redis host/port hardcoded to `localhost:6379`, causing container connection failures.
- **Fix:** Use environment variables `REDIS_HOST` and `REDIS_PORT` with defaults.


### 3. Missing Type Hint 
- **File:** `worker/worker.py`
- **Lines:** `13` (function signature), 
- **Problem:** `process_job` lacked a type hint, reducing code clarity. 
- **Fix:** Added type hint `job_id: str` to `process_job`.


### Missing Graceful Shutdown (Signal Handling)
- **File:** `worker/worker.py`
- **Lines:** `4` (`import signal` not used)
- **Problem:** The worker does not handle `SIGKILL`(kill -9 <pid>), `SIGINT`(Ctrl+C), `SIGTERM` (the signal sent by Docker when stopping a container). When `docker stop` is issued, the worker is abruptly terminated after a 10‑second grace period, potentially losing the current job and leaving its status stale in Redis. Clients waiting for the job will time out or hang indefinitely,.

- **Fix:** Added a `SIGINT`,`SIGKILL`, `SIGTERM` handler that sets a `shutdown` flag. The main loop checks this flag and stops accepting new jobs. The current job is allowed to complete (or is marked as `"failed"` if interrupted mid‑processing). This ensures clean shutdown and state consistency.



## Frontend Service (`frontend/app.js`)

### 1. Hardcoded API Base URL
- **File:** `frontend/app.js`
- **Line:** `6` (`const API_URL = "http://localhost:8000";`)
- **Problem:** The backend API URL is hardcoded to `localhost:8000`. In a containerized environment, the API service is reachable at a different hostname (e.g., `api`). Changing the URL requires modifying source code, which is not portable.
- **Fix:** Use an environment variable (`API_URL`) with a sensible default for local development.



### 2. Missing Health Endpoint
- **File:** `frontend/app.js`
- **Lines:** N/A (endpoint not present)
- **Problem:** The FastAPI application lacks a `/health` endpoint. Without this, Docker's `HEALTHCHECK` cannot verify that the service is alive and ready to serve requests. This breaks container health monitoring and prevents `depends_on` conditions from working correctly in Docker Compose.
- **Fix:** Added a simple `GET /health` endpoint that returns a `200 OK` response.

## Frontend Service (`views/index.html`)
 - Found no issues wit it


