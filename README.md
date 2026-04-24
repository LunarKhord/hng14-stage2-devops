# HNG14 Stage 2 DevOps – Microservices CI/CD

A production‑ready microservices job‑processing system that has been containerized, hardened, and equipped with a full CI/CD pipeline using GitHub Actions.

## Live Preview

The application stack runs locally and the CI/CD pipeline is triggered on every push to the `main` branch.

## The Application

The system consists of four services:

| Service   | Description                                      | Port  |
|-----------|--------------------------------------------------|-------|
| Frontend  | Node.js / Express dashboard to submit & track jobs | 3000  |
| API       | Python / FastAPI – creates jobs & returns statuses | 8000  |
| Worker    | Python – picks up jobs from Redis & processes them | –     |
| Redis     | Message queue shared between API and Worker       | 6379 (internal only) |

##  Bring Up the Entire Stack Locally

### Prerequisites

- Docker & Docker Compose
- Git

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/LunarKhord/hng14-stage2-devops
   cd hng14-stage2-devops
   ```

2. **Set environment variables**

   Copy the example file and adjust if needed.

   ```bash
   cp .env.example .env
   ```

   Open `.env` and review the values (defaults work fine for local development).

3. **Start all services**

   ```bash
   docker compose up -d
   ```

4. **Check the logs and health status**

   ```bash
   docker compose ps
   docker compose logs -f
   ```

   Wait until all services show `(healthy)` – this can take up to 30 seconds.

5. **Verify the application**

   - Frontend: [http://localhost:3000](http://localhost:3000)  
     Click "Submit New Job" and watch it move to `completed`.
   - API health: `curl http://localhost:8000/health`  
     Should return `{"status":"healthy"}`.
   - Worker status: `docker compose logs worker`  
     You should see `Processing job … Done`.

6. **Stop the stack**

   ```bash
   docker compose down
   ```

## CI/CD Pipeline (GitHub Actions)

The pipeline is defined in `.github/workflows/ci-cd.yml` and runs on every push and pull request to the `main` branch.

### Stages (strict sequential order)

| Stage            | Description |
|------------------|-------------|
| **Lint**         | Python (`flake8`), JavaScript (`eslint`), Dockerfiles (`hadolint`) |
| **Test**         | 4 unit tests for the API using `pytest` with Redis mocked; coverage report uploaded as an artifact |
| **Build**        | Builds API, Worker, and Frontend images, tags them with the Git SHA and `latest`, pushes to a local registry |
| **Security Scan**| Scans all images with Trivy, fails on `CRITICAL` vulnerabilities, uploads SARIF results |
| **Integration Test** | Brings the full stack up inside the runner, submits a job, polls until completion, tears down cleanly |
| **Deploy** *(main only)* | Simulates a rolling update – starts new stack, waits for healthy, then stops old stack; aborts on health check failure |

A failure in any stage prevents subsequent stages from running.

## Bugs & Fixes

All issues found in the starter code (hardcoded connections, missing health endpoints, synchronous Redis usage, improper signal handling, etc.) have been fixed and documented in **FIXES.md**. Every entry includes the file, line number, problem description, and the exact change made.

## Environment Variables

The following variables are used in `docker-compose.yml`. They are defined in `.env` (not committed). See `.env.example` for a template.

| Variable           | Service(s)       | Default       | Description                           |
|--------------------|------------------|---------------|---------------------------------------|
| `REDIS_HOST`       | API, Worker      | `redis`       | Hostname of Redis container           |
| `REDIS_PORT`       | API, Worker      | `6379`        | Redis port                            |
| `API_URL`          | Frontend         | `http://api:8000` | Backend API URL                    |
| `FRONTEND_PORT`    | Frontend         | `3000`        | Port for the frontend (host)          |
| `WORK_DURATION`    | Worker           | `2`           | Simulated work duration (seconds)     |

## Health Checks

All services include Docker `HEALTHCHECK` instructions. The Compose file uses `depends_on` with `condition: service_healthy` so that services only start after their dependencies are truly ready.

## Security

- All custom images run as a non‑root user.
- Multi‑stage builds keep final images small and free of build tools.
- Trivy scans block deployment on `CRITICAL` findings.
- Redis is never exposed to the host machine.

## Additional Documentation

- **FIXES.md** – Complete list of bugs discovered and how they were resolved.
- **.env.example** – Environment variable template.

## Author

- **Name:** Muhammad Hasim
- **HNG Username:** Krazy Genus
- **GitHub:** [@LunarKhord](https://github.com/LunarKhord)
