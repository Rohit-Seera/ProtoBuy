# ProtoBuy

> **A conversational AI commerce agent that can discover products, build a cart, enforce spending limits, and hand off purchases to Razorpay — with every important decision recorded.**

ProtoBuy is a working prototype of **agentic commerce with hard application guardrails**. A buyer can describe what they need in natural language, the agent can search a merchant catalog and recommend in-stock products, build a basket, and initiate a Razorpay checkout. The key rule is simple: **the model can propose actions, but the application decides what is allowed.**

Built for the **Razorpay AI Buildathon 2026 — Track 1: AI Growth & Agentic Commerce**.

## Why ProtoBuy?

Once an AI agent can spend money on a user's behalf, recommendation quality is only half the problem. The system also needs deterministic controls around **how much the agent can spend, when it must ask for confirmation, what counts as trusted input, and what happens when an action fails**.

ProtoBuy demonstrates those controls in a compact end-to-end system.

## What it does

### 🤖 Conversational product discovery
Buyers can describe a need in plain language, including common budget constraints such as `under ₹3000`. The system ranks catalog matches using deterministic product/category signals, with an optional Groq-powered intent parser.

### 🛒 Cart building
The agent can add and remove products, keep a session cart, and calculate the current basket total. Product recommendations include the catalog image, price, and available sizing information.

### 💳 Bounded autonomous checkout
Every checkout is evaluated against `AUTONOMY_LIMIT` (default: **₹2000**).

- **At or below the limit:** the application can proceed without an extra confirmation step.
- **Above the limit:** the application stops and requires an explicit buyer confirmation before payment is created.

The guardrail is enforced in application code, not left to the LLM.

### 📈 AI-growth bundle recommendations
For goal-oriented requests such as *"build me a weekend trek kit under ₹4000"*, the agent can assemble a complementary basket from in-stock catalog items while respecting the requested budget. These recommendations are logged as growth signals and never bypass checkout controls.

### 🛡️ Prompt-injection defense
The demo catalog intentionally contains a malicious instruction embedded in one product description. Catalog/product text is treated as **untrusted data**, never as system authority. Suspicious instruction-like text is detected and logged rather than followed.

### 📦 Out-of-stock recovery
When a requested product/variant is unavailable, the system surfaces the failure cleanly and can return available alternatives instead of silently failing or inventing inventory.

### 💰 Razorpay test checkout
ProtoBuy creates Razorpay test-mode orders and payment links only after the application's checkout rules are satisfied. Payment failures are returned as explicit application errors and logged.

### 🧾 Audit trail
Important actions are written to an audit log, including guardrail checks, cart updates, stockouts, injection detections, payment failures, and order creation events.

## Architecture

```text
                    ┌──────────────────────────────┐
                    │        Browser Demo          │
                    │      index.html / UI         │
                    └──────────────┬───────────────┘
                                   │ HTTP / JSON
                                   ▼
                    ┌──────────────────────────────┐
                    │        FastAPI API           │
                    │         backend/main.py      │
                    └──────────────┬───────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
             ▼                     ▼                     ▼
      ┌─────────────┐       ┌─────────────┐       ┌──────────────┐
      │   agent.py  │       │ guardrails  │       │   catalog    │
      │ intent +    │       │ spending +  │       │   16 demo    │
      │ tool logic  │       │ audit log   │       │  products    │
      └──────┬──────┘       └─────────────┘       └──────────────┘
             │
             ▼
      ┌─────────────────┐
      │ razorpay_client │
      │ orders + links  │
      └─────────────────┘

      Optional LLM layer: Groq intent parsing
```

## Core design principle

```text
LLM proposes  →  Application validates  →  Application executes
```

That separation is intentional. Product descriptions, search results, and other catalog text are data. Spending limits, confirmation requirements, inventory checks, and payment execution are application responsibilities.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/catalog` | Return the merchant catalog |
| `POST` | `/api/chat` | Handle a natural-language buyer turn |
| `GET` | `/api/cart` | View the current session cart |
| `POST` | `/api/cart/add` | Add an item to the cart |
| `POST` | `/api/cart/remove` | Remove a cart item |
| `POST` | `/api/cart/clear` | Clear the cart |
| `POST` | `/api/checkout` | Run the guarded checkout flow |
| `GET` | `/api/history` | Return conversation history |
| `GET` | `/api/audit-log` | Return the audit trail |
| `GET` | `/api/health` | Health check |

Example request:

```json
{
  "session_id": "demo1",
  "message": "I need trekking gear under ₹4000"
}
```

## Run locally

### 1. Install backend dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `backend/.env` from the example file:

```powershell
Copy-Item .env.example .env
```

Add your **Razorpay TEST MODE** credentials and `GROQ_API_KEY` locally.

> Never commit `.env` or API keys to GitHub.

### 3. Start the FastAPI backend

```powershell
uvicorn main:app --reload
```

### 4. Start the frontend

From the project root, serve the static files:

```powershell
python -m http.server 5500
```

Then open:

```text
http://127.0.0.1:5500/
```

The demo supports product discovery, cart actions, spending-limit confirmation, Razorpay test checkout, audit logs, and failure recovery.

## Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `GROQ_API_KEY` | Groq API access | `gsk_...` |
| `GROQ_MODEL` | Intent-parser model | `openai/gpt-oss-120b` |
| `RAZORPAY_KEY_ID` | Razorpay test key | `rzp_test_...` |
| `RAZORPAY_KEY_SECRET` | Razorpay test secret | local only |
| `AUTONOMY_LIMIT` | Maximum autonomous checkout amount | `2000` |

## Failure handling

ProtoBuy treats failure as part of the product rather than an exception to hide:

- **Out of stock:** return an explicit stockout response and surface available alternatives.
- **Invalid cart action:** return a structured API error instead of mutating state incorrectly.
- **Payment failure:** distinguish Razorpay/payment errors and record them in the audit trail.
- **Prompt injection:** detect suspicious catalog instructions and treat them as data only.
- **LLM/parser failure:** fall back to deterministic intent handling where possible.

## Known limitations

This is a focused buildathon prototype, not a production commerce stack.

- Catalog retrieval is deterministic lexical/ranking logic rather than embedding-based semantic search.
- Sessions and carts are stored in process memory and do not survive a server restart.
- The demo currently wires one merchant/catalog.
- Prompt-injection detection is intentionally lightweight and is not a universal defense against adversarial inputs.
- The autonomy policy is a single global limit rather than a full policy engine with per-user, per-category, or merchant-specific rules.
- Razorpay integration is configured for a demo/test flow rather than production payment operations.

## Project structure

```text
ProtoBuy/
├── api/
│   └── index.py
├── backend/
│   ├── agent.py
│   ├── catalog.json
│   ├── guardrails.py
│   ├── main.py
│   ├── razorpay_client.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   └── assets/
├── index.html
├── requirements.txt
├── vercel.json
└── README.md
```

## Buildathon focus

**Track:** AI Growth & Agentic Commerce

ProtoBuy explores a practical question for agentic commerce:

> **How do you let an AI agent act autonomously without letting the model become the authority over money, inventory, or safety policy?**

The prototype answers that with deterministic guardrails, explicit confirmation, failure-aware flows, and an auditable execution path.
