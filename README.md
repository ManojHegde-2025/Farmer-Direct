# FarmerDirect 🌾

**Direct Farm-to-Buyer Agricultural Marketplace for Udupi & Dakshina Kannada**

A full-stack digital marketplace connecting verified farmers directly with buyers in the Udupi and Dakshina Kannada districts of Karnataka, India.

## Overview

FarmerDirect enables farmers to list their produce, set asking prices, receive offers, and negotiate directly with buyers — reducing avoidable intermediaries and improving price transparency.

### Supported Commodities
- Arecanut (ಅಡಿಕೆ)
- Coconut (ತೆಂಗಿನಕಾಯಿ)
- Rice (ಅಕ್ಕಿ)
- Banana (ಬಾಳೆಹಣ್ಣು)
- Vegetables (ತರಕಾರಿ)
- Cashew (ಗೋಡಂಬಿ)
- Pepper (ಮೆಣಸು)
- Other agricultural produce

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy (async) |
| Database | PostgreSQL 16 |
| Auth | JWT + Argon2 password hashing |
| Migrations | Alembic |

## Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.11
- **Docker** (for PostgreSQL)
- **Git**

## Quick Start

### 1. Clone and navigate
```bash
cd "Dev Hack 2026"
```

### 2. Start PostgreSQL
```bash
docker compose up -d db
```

### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env if needed (defaults work with Docker setup)

# Run migrations
alembic upgrade head

# Seed demo data
python -m scripts.seed_data

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env

# Start development server
npm run dev
```

### 5. Access the Application
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Creating Test Accounts

### Create an Admin
```bash
cd backend
source venv/bin/activate
python -m scripts.create_admin
```

### Register a Farmer
1. Open http://localhost:5173/register
2. Select "Farmer" role
3. Complete registration
4. Complete farmer profile with farm details
5. Wait for admin approval

### Register a Buyer
1. Open http://localhost:5173/register
2. Select "Buyer" role
3. Complete registration
4. Complete buyer profile

## Demo Workflow

1. **Farmer registers** and creates a listing for 100 kg arecanut
2. **Admin approves** the farmer via admin dashboard
3. **Buyer registers** and creates a requirement for 80 kg arecanut
4. **System matches** the listing to the requirement
5. **Buyer submits offer** — farmer can accept or counter
6. **Accepted offer** → order created, 80 kg reserved
7. **Both parties track** payment and delivery
8. **Remaining 20 kg** stays available for other buyers

## Project Structure

```
├── frontend/          # React + Vite + TypeScript
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── pages/       # Route pages
│   │   ├── services/    # API client
│   │   ├── contexts/    # Auth context
│   │   ├── hooks/       # Custom hooks
│   │   ├── types/       # TypeScript types
│   │   ├── utils/       # Utilities
│   │   └── locales/     # i18n (EN/KN)
│   └── ...
├── backend/           # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Config, security
│   │   ├── db/         # Database session
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Business logic
│   │   └── middleware/  # Auth middleware
│   ├── tests/          # Pytest tests
│   ├── alembic/        # Migrations
│   └── scripts/        # Admin, seed scripts
├── docs/              # Documentation
├── docker-compose.yml # PostgreSQL service
└── README.md
```

## Running Tests

```bash
# Backend tests
cd backend
source venv/bin/activate
pytest -v

# Frontend build check
cd frontend
npm run build
```

## Environment Variables

See `backend/.env.example` and `frontend/.env.example` for required configuration.

**Never commit `.env` files with real credentials.**

## Disclaimer

- Reference prices shown are clearly labelled demo/historical data unless an external data source is integrated
- This platform does not guarantee specific earnings or savings
- Simulated payments are clearly distinguished from real transactions
- The platform does not provide transportation services

## License

Private project — not for redistribution.
