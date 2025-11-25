#!/bin/bash

# Future of Work Readiness Platform - Demo Script
# Run this script to start everything using Docker Compose

echo "🚀 Starting Future of Work Readiness Platform with Docker Compose..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is available${NC}"

# Determine docker-compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo ""
echo -e "${BLUE}🐳 Starting Docker containers...${NC}"

# Stop any existing containers
echo "Stopping any existing containers..."
$COMPOSE_CMD down 2>/dev/null

# Build and start containers
echo "Building and starting containers..."
$COMPOSE_CMD up -d --build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start containers${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check if containers are running
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
$COMPOSE_CMD ps

echo ""
echo -e "${BLUE}🧪 Testing Services...${NC}"

# Test backend health
echo -n "Testing backend health check... "
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend health check failed${NC}"
    else
        sleep 2
    fi
done

# Test frontend
echo -n "Testing frontend... "
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is accessible${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
    else
        sleep 2
    fi
done

# Test API endpoints
echo ""
echo "Testing API endpoints..."
SECTORS_RESPONSE=$(curl -s http://localhost:8000/api/sectors 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sectors API working${NC}"
else
    echo -e "${RED}❌ Sectors API failed${NC}"
fi

QUIZZES_RESPONSE=$(curl -s http://localhost:8000/api/quizzes 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Quizzes API working${NC}"
else
    echo -e "${RED}❌ Quizzes API failed${NC}"
fi

echo ""
echo -e "${GREEN}🎉 DEMO READY!${NC}"
echo "================================================"
echo -e "${BLUE}📱 Frontend:${NC} http://localhost:3000/"
echo -e "${BLUE}🔧 Backend:${NC} http://localhost:8000/"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 Demo Flow for Presentation:${NC}"
echo "1. 🏠 Show landing page with navigation buttons"
echo "2. 🎯 Click 'Try Onboarding' - demonstrate sector selection"
echo "3. 📊 Complete onboarding and go to dashboard"
echo "4. 🔧 Show API documentation at /docs"
echo "5. 💾 Mention database integration and data persistence"
echo ""
echo -e "${BLUE}📋 Useful Commands:${NC}"
echo "  - View logs: $COMPOSE_CMD logs -f"
echo "  - Stop containers: $COMPOSE_CMD down"
echo "  - Restart: $COMPOSE_CMD restart"
echo ""
echo -e "${YELLOW}⚠️  Press Ctrl+C to view logs (containers will keep running)${NC}"
echo -e "${YELLOW}⚠️  Use '$COMPOSE_CMD down' to stop all containers${NC}"

# Show logs
echo ""
echo -e "${BLUE}📋 Container Logs (Press Ctrl+C to exit logs, containers will keep running):${NC}"
$COMPOSE_CMD logs -f
