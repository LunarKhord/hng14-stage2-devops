import redis.asyncio as redis
import os
import signal
import asyncio

# Environment variables with sensible defaults
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis client with decode_responses=True to avoid manual .decode()
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

shutdown = False

def handle_shutdown(signum, frame):
    global shutdown
    print(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown = True

# Handle both SIGTERM (Docker stop) and SIGINT (Ctrl+C)
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


"""This function serves the purpose of taking in a string type job_id
and simulating the processing of a job by sleeping for 2 seconds. After the sleep, 
it updates the status of the job in Redis to "completed". 
The function also prints messages to indicate when it starts 
processing a job and when it has completed the job."""
async def process_job(job_id: str):
    print(f"Processing job {job_id}")
    await asyncio.sleep(2)  # simulate work
    await r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")



""" This function serves the purpose of taking in a string type
 job_id and simulating the termination of a job.
"""
async def terminate_job(job_id: str):
    print(f"Terminating job {job_id}")
    await r.hset(f"job:{job_id}", "status", "failed")
    print(f"Terminated: {job_id}")




async def main():
    print("Worker started.")
    while True:
            
        job = await r.brpop("job", timeout=5)

        if job:
            # job is a tuple: (list_name, job_id)
            _, job_id = job

            if not shutdown:
                await process_job(job_id)
            else:
                await terminate_job(job_id)
                break
        elif shutdown:
            # No job and we're shutting down – exit cleanly
            print("No active job. Exiting.")
            break

if __name__ == "__main__":
    asyncio.run(main())