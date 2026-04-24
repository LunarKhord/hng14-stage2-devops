#!/bin/bash
set -e
echo "Starting integration test…"
docker compose -f docker-compose.yml up -d
echo "Waiting for services to become healthy…"
for i in {1..12}; do
  HEALTHY=$(docker compose ps --format json | jq 'select(.Health == "healthy")' | wc -l)
  if [ "$HEALTHY" -ge 4 ]; then
    echo "All services healthy"
    break
  fi
  sleep 5
done
echo "Submitting a job…"
JOB_ID=$(curl -s -X POST http://localhost:3000/submit -H "Content-Type: application/json" | jq -r '.job_id')
echo "Job ID: $JOB_ID"
echo "Polling for completion…"
timeout 300 bash -c "
  while true; do
    STATUS=\$(curl -s http://localhost:3000/status/$JOB_ID | jq -r '.status')
    echo \"Status: \$STATUS\"
    if [ \"\$STATUS\" = 'completed' ]; then
      exit 0
    fi
    sleep 2
  done
"
echo "Integration test passed!"
docker compose down -v