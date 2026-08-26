#!/usr/bin/env bash
set -e

echo "==========================================="
echo " MemoryChat Deployment Script"
echo "==========================================="

if [ ! -f .env ]; then
  echo "Error: .env file not found."
  echo "Please copy .env.example to .env and configure it before deploying."
  exit 1
fi

echo "Pulling latest changes..."
git pull || echo "Not a git repository or pull failed, skipping..."

echo "Building and starting containers..."
docker-compose up -d --build

echo ""
echo "Waiting for backend to be healthy..."
sleep 5

if docker-compose ps | grep backend | grep -q "healthy"; then
  echo "Backend is healthy."
else
  echo "Backend health status is not yet 'healthy'. Check 'docker-compose logs backend' if it stays this way."
fi

echo "==========================================="
echo "Deployment successful!"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "==========================================="
