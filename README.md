# InvoiceFlow

AI-powered invoice operations tool. Upload an invoice PDF and InvoiceFlow
extracts data, classifies it, checks it for errors and hands you a structured record to review and approve instead of reading every
invoice by hand.

This is a learning/portfolio project built with fake data, but designed and built the way real product would be.

## What it does

```
Upload invoice (PDF)
       ↓
Text extracted from the PDF
       ↓
Sent to Gemini for structured extraction (supplier, dates, amounts, category)
       ↓
Validated (math checks, required fields, confidence threshold)
       ↓
Ready for approval  —or—  Flagged for review, with a reason
       ↓
Reviewed / corrected by a human
       ↓
Approved
```

## Project structure

```
invoiceflow
├── backend
│   ├── Dockerfile
│   ├── alembic
│   ├── app
│   │   ├── api
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── invoices.py
│   │   │   └── suppliers.py
│   │   ├── config.py
│   │   ├── core
│   │   │   ├── celery_client.py
│   │   │   └── security.py
│   │   └── main.py
│   ├── requirements.txt
│   └── uploads
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
│   ├── index.html
│   ├── src
│   │   ├── App.jsx
│   │   ├── api
│   │   │   └── client.js
│   │   ├── components
│   │   │   ├── Layout.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── StatusBadge.jsx
│   │   ├── index.css
│   │   ├── main.jsx
│   │   └── pages
│   │       ├── Dashboard.jsx
│   │       ├── InvoiceDetail.jsx
│   │       ├── InvoiceList.jsx
│   │       ├── Login.jsx
│   │       ├── Signup.jsx
│   │       └── Suppliers.jsx
├── shared
│   ├── db
│   │   └── session.py
│   └── models
│       ├── base.py
│       ├── category.py
│       ├── invoice.py
│       ├── supplier.py
│       └── user.py
└── worker
    ├── Dockerfile
    ├── celery_app.py
    ├── config.py
    ├── requirements.txt
    ├── services
    │   ├── ai_pipeline.py
    │   ├── pdf_extractor.py
    │   └── validator.py
    └── tasks.py
```

## Tech stack

| Layer           | Tech                                       |
| --------------- | ------------------------------------------ |
| Backend         | Python, FastAPI                            |
| Database        | PostgreSQL, SQLAlchemy, Alembic migrations |
| Background jobs | Celery + Redis                             |
| AI              | Gemini (JSON output)                       |
| PDF parsing     | pdfplumber                                 |
| Frontend        | React + Vite                               |
| Deployment      | Docker / docker-compose                    |

## Features

- Email/password auth (JWT)
- Upload a PDF invoice, processed automatically in the background
- AI extraction of supplier, dates, amounts, and category
- Automatic validation — flags invoices with math mismatches, missing
  fields, or low-confidence extraction, with a human-readable reason
- Dashboard with invoice counts by status
- Invoice list with status filtering
- Invoice detail/review screen — edit extracted fields, view the original
  PDF, approve
- Supplier spend stats
- Dockerized development environment
- Duplicate-filename handling, invoice deletion

## Running it locally

**Requirements:** Docker and Docker Compose.

1. Copy the environment template and fill in your own values:

   ```
   cp .env.example .env
   ```

   You'll need a [Gemini API key](https://aistudio.google.com/apikey), and
   should generate a random `SECRET_KEY` :

   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Start everything:

   ```
   docker compose up -d --build
   ```
3. Run the database migrations:

   ```
   docker compose exec backend alembic upgrade head
   ```
4. Open the app:

   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Useful commands

```
# Open a psql shell
docker compose exec db psql -U invoiceflow -d invoiceflow

# Generate a new migration after changing a model
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
```

## API overview

| Method | Path                      | Description                                |
| ------ | ------------------------- | ------------------------------------------ |
| POST   | `/auth/signup`          | Create an account, returns a JWT           |
| POST   | `/auth/login`           | Log in, returns a JWT                      |
| GET    | `/dashboard/summary`    | Invoice counts by status                   |
| POST   | `/invoice/upload`       | Upload a PDF, starts background processing |
| GET    | `/invoice/`             | List invoices (optional`?status=`)       |
| GET    | `/invoice/{id}`         | Invoice detail                             |
| GET    | `/invoice/{id}/file`    | Download/view the original PDF             |
| PATCH  | `/invoice/{id}`         | Correct extracted fields                   |
| POST   | `/invoice/{id}/approve` | Approve an invoice                         |
| DELETE | `/invoice/{id}`         | Delete an invoice                          |
| GET    | `/suppliers/`           | Supplier spend stats                       |

Full interactive docs at `/docs` once the backend is running.