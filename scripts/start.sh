#!/bin/bash

# Men's Circle Management Platform - Full Stack Startup Script
# This script implements task 1.5: Test full stack starts with `docker-compose up`

set -e  # Exit on any error

echo "🚀 Men's Circle Management Platform - Starting Full Stack..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    echo "Please install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker daemon is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Ensure .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file - please review and update with your values"
    else
        echo "❌ Error: Neither .env nor .env.example exists"
        exit 1
    fi
fi

# Validate Docker Compose configuration
echo "🔍 Validating Docker Compose configuration..."
if ! docker compose config --quiet; then
    echo "❌ Error: Docker Compose configuration is invalid"
    exit 1
fi
echo "✅ Docker Compose configuration is valid"

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down -v --remove-orphans

# Build images if needed
echo "🔨 Building application images..."
docker compose build

# Start all services
echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to become ready
echo "⏳ Waiting for services to become ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker compose ps

# Test service health
echo "🏥 Testing service health..."

# Test PostgreSQL
echo "  - PostgreSQL: " 
if docker compose exec -T postgres pg_isready -U postgres &> /dev/null; then
    echo "✅ Ready"
else
    echo "❌ Not Ready"
fi

# Test Redis
echo "  - Redis: "
if docker compose exec -T redis redis-cli ping &> /dev/null; then
    echo "✅ Ready"
else
    echo "❌ Not Ready"
fi

# Test Backend Health Endpoint
echo "  - Backend API: "
max_attempts=12
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Ready (http://localhost:8000/health)"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Not Ready after ${max_attempts} attempts"
        echo "Backend logs:"
        docker compose logs backend | tail -20
        break
    fi
    
    echo -n "."
    sleep 5
    ((attempt++))
done

# Test Frontend
echo "  - Frontend: "
max_attempts=12
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Ready (http://localhost:3000)"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Not Ready after ${max_attempts} attempts"
        echo "Frontend logs:"
        docker compose logs frontend | tail -20
        break
    fi
    
    echo -n "."
    sleep 5
    ((attempt++))
done

echo ""
echo "🎉 Full Stack Startup Complete!"
echo ""
echo "🌐 Available Services:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Health:    http://localhost:8000/health"
echo ""
echo "🛠  Management Commands:"
echo "  - View logs:     docker compose logs [service]"
echo "  - Stop services: docker compose down"
echo "  - Restart:       docker compose restart [service]"
echo ""
echo "📋 To stop all services, run:"
echo "   docker compose down"
echo "" 