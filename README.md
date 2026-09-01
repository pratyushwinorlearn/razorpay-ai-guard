# 💳 Razorpay AI Guard: Merchant MCP Server

> An autonomous AI-to-AI shopping agent and server-side policy engine built for Track 01 of the Razorpay AI Buildathon.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![React](https://img.shields.io/badge/React-Vite%2FTailwind-cyan)
![Razorpay](https://img.shields.io/badge/Razorpay-Test%20Mode-teal)

---

## Overview
Traditional e-commerce is built for human interfaces (GUIs). **Razorpay AI Guard** re-architects commerce for autonomous AI agents. Instead of a human browsing a web frontend, an AI Buyer Agent communicates with a Model Context Protocol (MCP) Server to discover product catalogs, evaluate terms, and execute secure purchases using native Razorpay test-mode APIs.

---

## Key Features & Judging Criteria Alignment

* **Safety & Control:** The Large Language Model is strictly confined to tool execution. All financial math, budget ceilings, and SKU permissions are enforced server-side via a deterministic Python policy engine. The system never trusts the LLM's calculations or intent.
  * *Auto-Approval:* Orders under ₹5,000 are processed immediately with a generated test payment link.
  * *Human Intervention:* Orders between ₹5,000 and ₹50,000 are routed to a `pending_approval` queue requiring explicit merchant sign-off from the dashboard.
  * *Hard Block:* Orders exceeding ₹50,000 are rejected outright.
* **Complete Audit Trail:** Every agent interaction, tool call, raw payload, and explicit AI reasoning string is persisted to a SQLite database and streamed in real-time to the Merchant Command Center dashboard.
* **Robust Failure Handling:** Network drops, malformed payloads, or Razorpay API errors are intercepted by structured `try/except` blocks, safely logging error states and routing failed transactions to secure fallback queues instead of crashing the server.

---

## Tech Stack

* **Agent Layer:** Groq API (`openai/gpt-oss-120b`), native Python `requests` for MCP tool-calling.
* **Backend Core:** FastAPI, SQLAlchemy, SQLite, Pydantic.
* **Payment Gateway:** Razorpay Test-Mode API (yielding live `rzp.io` test payment links).
* **Control Dashboard:** React, Vite, Tailwind CSS.

---

## Project Structure

razor-mcp/
├── agent/
│   └── buyer.py          # Autonomous Groq-driven buyer agent script
├── backend/
│   ├── database.py       # SQLAlchemy database session setup
│   ├── main.py           # FastAPI server and MCP endpoints
│   ├── models.py         # Product, Order, and AuditLog schemas
│   ├── policy.py         # Server-side security and budget policy engine
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/App.jsx       # Interactive merchant dashboard interface
│   └── index.html        # HTML entry point with Tailwind CDN
├── .env                  # Configuration keys and limits
├── start.py              # One-click multi-process launcher script
├── .gitignore
└── README.md

# Quickstart & Execution Guide

### 1. Environment Configuration
Create a `.env` file in the root directory with your API credentials and budget rules:

RAZORPAY_KEY_ID=rzp_test_your_actual_key
RAZORPAY_KEY_SECRET=your_actual_secret
RAZORPAY_MOCK_MODE=false

GROQ_API_KEY=gsk_your_actual_key
GROQ_MODEL=openai/gpt-oss-120b

AUTO_APPROVE_LIMIT_PAISE=500000
HARD_MAX_PAISE=5000000
ALLOWED_SKUS=*

DATABASE_URL=sqlite:///./razormcp.db
CORS_ORIGINS=http://localhost:5173

### 2. Install Dependencies
Open your terminal in the root project directory and install the required packages for both backend and frontend:

cd backend
pip install -r requirements.txt
cd ../frontend
npm install
cd ..

### 3. Launch the System (One-Click Launcher)
Boot both the FastAPI backend and the Vite React frontend simultaneously and automatically open the Command Center dashboard in your browser:

```python
python start.py
```

Dashboard URL: http://localhost:5173

Backend API: http://localhost:8080

### 4. Run the AI Buyer Agent
While your servers are running via start.py, open a new terminal window and execute the autonomous buyer agent script to test purchasing scenarios (auto-approval, human intervention queue, and hard budget blocks):

python agent/buyer.py

Watch the terminal output trace the AI's real-time reasoning while your web dashboard instantly updates with live transaction statuses, audit logs, clickable Razorpay test payment links, and interactive human-override buttons.
