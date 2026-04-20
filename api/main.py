from fastapi import FastAPI
import redis.asyncio as redis
import uuid
import os

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Initialize Async Redis client 
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.post("/jobs")
async def create_job():
    job_id = str(uuid.uuid4())
    await r.lpush("job", job_id)
    await r.hset(f"job:{job_id}", "status", "queued")
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    status = await r.hget(f"job:{job_id}", "status")
    if not status:
        return {"error": "not found"}
    return {"job_id": job_id, "status": status.decode()}
