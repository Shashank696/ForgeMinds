#!/bin/bash
# ══════════════════════════════════════════════════
#  ForgeMinds — One-Click Production Deployment Script
# ══════════════════════════════════════════════════

set -e

echo "🚀 Starting ForgeMinds deployment..."

# 1. Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Error: Docker is not installed. Please install Docker first." >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ] && ! docker compose version >/dev/null 2>&1; then
  echo "❌ Error: Docker Compose is not installed." >&2
  exit 1
fi

# 2. Check for .env file, create if missing
if [ ! -f .env ]; then
  echo "📝 Creating .env file from .env.example..."
  cp .env.example .env
  
  # Generate a secure JWT secret
  JWT_SECRET=$(openssl rand -hex 24)
  sed -i "s/JWT_SECRET_KEY=change-this-to-a-random-secret-string/JWT_SECRET_KEY=$JWT_SECRET/g" .env
  echo "✅ Generated secure JWT secret key."
fi

# 3. Prompt for Gemini API Key if not set
if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
  echo "🔑 Please enter your Google Gemini API Key:"
  read -r GEMINI_KEY
  sed -i "s/GEMINI_API_KEY=your_gemini_api_key_here/GEMINI_API_KEY=$GEMINI_KEY/g" .env
  echo "✅ Configured Gemini API Key."
fi

# 4. Build and start containers
echo "📦 Building and starting Docker containers..."
docker compose down --remove-orphans || true
docker compose up -d --build

echo "⏳ Waiting for databases to initialize..."
sleep 15

# 5. Run database migrations
echo "🗄️ Running PostgreSQL database migrations..."
docker compose exec -T api psql -h postgres -U forgeminds -d forgeminds -f /app/backend/db/migrations/001_initial.sql

# 6. Seed initial database data
echo "🌱 Seeding initial sample data..."
docker compose exec -T api python /app/scripts/seed_db.py

echo "🎉 Deployment successful!"
echo "--------------------------------------------------"
echo "🖥️  Frontend is live at:  http://localhost:5173"
echo "⚙️  Backend API is live at: http://localhost:8000"
echo "📚 API Docs available at:  http://localhost:8000/docs"
echo "--------------------------------------------------"
