#!/bin/bash

echo "Starting AutoSub Bot..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker."
    exit 1
fi

echo "Docker is running. Starting services..."
echo ""

# Start Docker Compose
docker-compose up -d

echo ""
echo "Services started! Check status with: docker-compose ps"
echo "View logs with: docker-compose logs -f"
echo ""

