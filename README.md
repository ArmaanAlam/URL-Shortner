# First-Principles URL Shortener (Industrial Grade) 🚀

A production-grade, enterprise-structured URL Shortener project built directly following the principles outlined in **[Backend from First Principles](https://backend-from-first-principle.vercel.app/)**.

---

## 🏛️ Project Directory Structure

```text
Backend Engineering/
│
├── main.py                     # Application entry point / CLI runner
├── requirements.txt            # Project dependencies
├── test_app.py                 # Automated test suite (unit + integration)
│
├── frontend/                   # Decoupled Web Client (Minimal Light UI)
│   ├── index.html              # Clean single-page application interface
│   ├── style.css               # Minimalist light theme styling
│   ├── app.js                  # Pure JS REST API consumer & LocalStorage history
│   └── README.md               # Frontend overview & usage
│
├── app/                        # Main Backend Application Package (Pure Python)
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application Factory & Lifespan/Middlewares
│   │
│   ├── core/                   # Cross-cutting foundational modules
│   │   ├── config.py           # Environment-based configuration (Pydantic Settings)
│   │   ├── base62.py           # Base62 Bijective encoding algorithm
│   │   ├── cache.py            # Cache-Aside layer (In-memory thread-safe cache)
│   │   └── exceptions.py       # Domain-specific custom application exceptions
│   │
│   ├── db/                     # Data Access Layer
│   │   ├── session.py          # SQLite connection manager & WAL mode configuration
│   │   └── repositories.py     # Repository pattern (encapsulates SQL queries & isolation)
│   │
│   ├── schemas/                # Data Transfer Objects (DTOs)
│   │   └── url.py              # Pydantic request & response validation schemas
│   │
│   ├── services/               # Business Logic Layer
│   │   └── shortener_service.py# Business workflows (validation, deduplication, hot key resolution)
│   │
│   └── api/                    # Transport / Controller Layer
│       ├── deps.py             # Dependency Injection providers
│       └── endpoints/
│           └── url.py          # REST API route handlers
│
└── shortener.db                # Auto-generated SQLite database (with WAL journal)
```

---

## 💡 Industrial-Grade Design Patterns Applied

| Layer / Pattern | File Link | Purpose & Benefit |
|---|---|---|
| **Separation of Concerns** | Entire `app/` hierarchy | Separates Routing (Controller), Business Rules (Service), Data Access (Repository), and Cross-cutting utilities (Core). |
| **Bijective Base62 Algorithm** | [base62.py](file:///d:/Practice/Backend%20Engineering/app/core/base62.py) | Mathematical integer-to-alphanumeric mapping. Guarantees zero collisions, compact URL-safe keys, and $62^6 \approx \mathbf{56.8\text{ Billion}}$ possible URLs with only 6 characters. |
| **Cache-Aside Pattern** | [cache.py](file:///d:/Practice/Backend%20Engineering/app/core/cache.py) | High-speed in-memory store for viral URLs, offloading read pressure from the database. |
| **Repository Pattern** | [repositories.py](file:///d:/Practice/Backend%20Engineering/app/db/repositories.py) | Decouples SQL queries from business logic. Easy to swap SQLite for PostgreSQL or MySQL without altering business rules. |
| **Dependency Injection** | [deps.py](file:///d:/Practice/Backend%20Engineering/app/api/deps.py) | Injects singleton repositories and services cleanly into API route controllers. |
| **Async Click Audit** | [shortener_service.py](file:///d:/Practice/Backend%20Engineering/app/services/shortener_service.py) | Background threads handle timestamp, referrer, and user-agent logging to keep redirect latency $< 2\text{ms}$. |
| **HTTP 302 Found Semantics** | [main.py](file:///d:/Practice/Backend%20Engineering/app/main.py) | Prevents browsers from caching redirects locally, preserving accurate real-time click analytics. |

---

## ⚡ How to Run

### 1. Start the Server
```powershell
python main.py
```
Or with Uvicorn:
```powershell
uvicorn app.main:app --reload --port 8000
```
- Server URL: **`http://localhost:8000`**
- Interactive Swagger UI: **`http://localhost:8000/docs`**

### 2. Open the Minimal Light Web Client
Open [`frontend/index.html`](file:///d:/Practice/Backend%20Engineering/frontend/index.html) directly in any browser (or double-click it in Windows File Explorer). It communicates directly with your FastAPI backend over REST.

---

## 🧪 Run Tests

```powershell
python test_app.py
```
Validates Base62 bijective round-trip math, REST endpoints, idempotency, custom aliases, 302 redirects, and analytics auditing.
# URL-Shortner
