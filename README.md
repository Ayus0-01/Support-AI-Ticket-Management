# Support AI Ticket Management System

A multi-role IT support application for ticket intake, classification, agent assignment, knowledge-base search, and AI-assisted resolution. Customers, support agents, Support Managers, and administrators use the same React application with role-specific access. Django REST APIs and a persistent worker coordinate ticket processing; ticket and application-user records are stored in MongoDB Atlas.

| Portal | What it supports |
| --- | --- |
| Customer | Register and verify email, submit tickets, follow ticket history, and view customer-safe resolutions. |
| Agent | Work assigned tickets, inspect classification and staff workflow details, and prepare or send resolutions. |
| Support Manager | Monitor workload and reports, manage assignments and escalations, and inspect classification, workflow evidence, and sources. |
| Admin | Manage users and agent specialties, and access operational dashboards and settings. |

The supported account roles are `User` (customer), `Agent`, `Support Manager`, and `Admin`. 

### Technology at a glance

| Area | Project implementation |
| --- | --- |
| Web app | React 18, TypeScript, Vite, Tailwind CSS, React Router, Axios |
| API | Python, Django 6, Django REST Framework, JWT authentication |
| Data and jobs | MongoDB Atlas through PyMongo; MongoDB-backed persistent ticket queue |
| Classification and retrieval | LightGBM, FastEmbed embeddings, keyword search, reciprocal rank fusion, and a Transformer reranker |
| Resolution generation | Qwen3:4B through Ollama; generated answers use retrieved knowledge and the existing validation flow |
| Integrations | Existing SMTP configuration for email and Jira REST API for escalations |

### Where to find things

- [Architecture and ticket lifecycle](#architecture)
- [Authentication and email verification](#authentication-and-email-verification)
- [AI classification, knowledge search, and resolution](#ai-ticket-intelligence)
- [Environment variables](#backend-environment)
- [Local setup](#local-development)
- [API overview](#api-overview)
- [Testing and deployment notes](#tests-and-verification)

This repository is an existing application. Ticket lifecycle and AI logic live in their existing modules and should be extended there rather than duplicated.

## Start here: the project in plain language

Customers submit support requests in the React website. Django saves each ticket right away and places an AI-processing job in MongoDB. A separate ticket worker picks up that job, classifies the ticket, finds a matching support agent, searches the knowledge base, and prepares a resolution for review or delivery. The website checks the saved workflow periodically, so staff can see progress without manually refreshing the page.

For local use, three processes need to be running: the Django API, the ticket worker, and the React website. AI resolution generation also needs an Ollama service reachable at the configured `OLLAMA_URL`. For deployment, the worker must run as a persistent service; starting the website or Django API alone does not process queued tickets.

Application timestamps are stored in UTC for consistent ordering. Business-hour SLA calculations and date/time display use India Standard Time (`Asia/Kolkata`, UTC+05:30). API date values represent UTC; clients treat legacy timestamp strings without an offset as UTC, then convert them to India time for display.

### A few terms used in this README

- **Worker:** a long-running process that picks up saved background jobs. It keeps slow AI work out of the customer's ticket-submission request.
- **M1:** the existing category, subcategory, severity, and priority classification pipeline.
- **M2:** the existing knowledge search and resolution-generation pipeline.
- **M3:** the existing multi-agent workflow that diagnoses the issue, retrieves knowledge, generates a resolution, validates it, and may escalate it.
- **Embedding:** a numeric representation of text used to find knowledge articles with similar meaning.
- **RRF:** reciprocal rank fusion, which combines the ranked results from vector search and keyword search.
- **Reranking:** a second relevance check that reorders the retrieved articles before they are used as AI context.
- **JWT:** the signed access token the frontend sends to authenticated API routes.

## Architecture

```text
React + TypeScript + Vite
        │ REST / JWT
        ▼
Django + Django REST Framework
  ├─ MongoDB Atlas (users, tickets, workflow, KB, history)
  ├─ M1: LightGBM category / subcategory / severity and priority
  ├─ M2: embedding + keyword retrieval → RRF → filtering → reranking → packing
  ├─ M3: diagnosis → retrieval → Qwen3:4B → validation → resolution or escalation
  ├─ SMTP notifications
  └─ Jira REST API for escalations
        ▲
        │ durable MongoDB job queue
Ticket worker: `python manage.py run_ticket_worker`
```

The ticket API persists the ticket and queues one MongoDB job. A separate long-running worker claims queued jobs with a lease, runs the existing classification and M3 workflow, and records job completion or retry state. Run the worker as a persistent process; it is not a request thread and is not started by Django automatically.

### Repository layout

The diagram shows the application directories and startup files needed to orient yourself in the codebase. It leaves out local virtual environments, generated files, datasets, and design/support material.

```text
Support_AI_Ticket_Management_Agent/
├── client/                         React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── components/             Shared UI and feature components
│   │   ├── context/                Authentication and app state
│   │   ├── pages/                  Customer, agent, Support Manager, and admin screens
│   │   ├── services/               Frontend API clients
│   │   └── utils/                  Shared frontend utilities
│   ├── package.json
│   └── vite.config.ts
├── server/                         Django REST backend and ticket worker
│   ├── AIticket/                   Django settings, URLs, WSGI/ASGI
│   ├── apps/
│   │   ├── authentication/         Accounts, JWT, email verification
│   │   ├── tickets/                Ticket lifecycle, classification, queue
│   │   ├── agents/                 Orchestration, assignment, Jira, email
│   │   ├── knowledge_base/         Articles, retrieval, and resolutions
│   │   ├── history/
│   │   ├── notifications/
│   │   ├── reports/
│   │   └── admin_panel/
│   ├── training/artifacts/         Runtime LightGBM models and label maps
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── start-local.cmd                 Starts local API, worker, and frontend
```

The ticket worker is started through Django's `manage.py`; it does not have a separate source directory. `server/training/artifacts/` contains model files needed by classification at runtime.

## Ticket lifecycle

1. An authenticated customer submits a ticket. Django stores it with `Open` status and returns the ticket without waiting on AI work.
2. The API adds a customer in-app notification and records a durable processing job in MongoDB.
3. M1 predicts category, subcategory, severity, priority, SLA, and queue, then persists the result. The worker sends the customer ticket confirmation email after this classification so it can include the assigned category, severity, and priority.
4. Automatic human assignment runs after classification. Tickets of any classifier category use active Agent accounts whose specialties include that category. The existing active-ticket workload and tie-breaking rules select among eligible specialists.
5. The existing M3 orchestration performs diagnosis, retrieval, resolution generation, and validation. If there is no matching human specialist, the workflow takes its existing escalation branch; it records the escalation in the workflow and internal ticket timeline rather than assigning an unrelated agent. The existing Jira and escalation-email integrations run from that branch.
6. A validated AI resolution is saved in the existing response store and surfaced to the requester. The assigned agent and customer receive in-app/email notifications when configured. Customers can confirm or reject a resolution; staff retain the existing review, edit, reject, and manual-resolution actions.

Ticket states retain the existing `Open`, `In Progress`, `Resolved`, and `Closed` meanings. Escalation is represented in workflow data, ticket escalation metadata, and internal timeline events.

### Human-agent coverage

Agent accounts are existing user documents with role `Agent`; the application does not create filler agents. Admins can select any of the ten classifier categories as specialties in the Users page, when creating Agents or editing existing Agents. Configure the intended staffing scenario on the actual seven Agent records: five with VPN and two with NETWORK as initial coverage. Changing an Agent specialty affects future tickets in the selected category. Categories without an active matching specialist use the current escalation path. A missing/overloaded specialist pool does not silently route the ticket to an unrelated agent. Existing manual Support Manager assignment remains available.

The code does not seed or assert the number of Agent records in MongoDB. Confirm the live account records and active workloads during environment setup.

## Authentication and email verification

Public registration creates an unverified customer account, sends a single-use verification link, and returns no JWT. The token is generated with a cryptographically secure random source; only its SHA-256 digest is stored, and it expires after 24 hours. Successful verification consumes the stored token. Invalid, expired, and already-used links return an error; already-verified addresses are handled idempotently. Login does not issue JWTs for unverified customer accounts. Existing JWT access and refresh behavior and staff roles remain in place. Admin-provisioned staff accounts are trusted and marked verified at creation.

Registration requires working SMTP and `FRONTEND_URL` so the verification link returns to the frontend. When SMTP sending fails, the just-created account is removed and registration returns a service-unavailable response, allowing a clean retry.

## AI ticket intelligence

### Classification and routing (M1)

The trained LightGBM category, subcategory, and severity models are loaded from `server/training/artifacts/`. The checked-in category map has ten labels: ACCESS, APPLICATION, EMAIL, HARDWARE, NETWORK, PRINTER, SECURITY, SOFTWARE, UNCLASSIFIED, and VPN. Severity rules and the existing deterministic impact/severity priority mapping calculate priority and SLA. The classification routing module maps category to a team queue; ticket assignment separately uses eligible Agent account specialties and workload.

Staff ticket details show the category model's confidence as a diagnostic score so agents can inspect classification behavior. That score does not gate M2/M3 resolution generation or customer delivery; the existing classification model still uses its own thresholds to choose classification routing and the `UNCLASSIFIED` label. M3's existing validation result determines whether an AI resolution is delivered or escalated.

### Knowledge base and resolution (M2)

Knowledge articles can be created, published, searched, and ingested from supported HTML/text, DOCX, and PDF sources. The existing pipeline builds ticket search queries, runs vector and keyword retrieval, combines candidate rankings with reciprocal rank fusion (RRF), filters by published status and applicable category/department, reranks candidates, and packs context for generation. FastEmbed provides dense embeddings. The Transformer reranker uses `BAAI/bge-reranker-v2-m3`.

The generator uses Qwen3:4B through Ollama. `OLLAMA_URL` and `OLLAMA_MODEL` configure both the existing M2 generator and M3 resolution agent. The backend keeps retrieval logs, citations, confidence, validation, and response-review data for internal workflow use.

### Multi-agent workflow (M3) and human review

The orchestrator coordinates diagnosis, knowledge retrieval, resolution, validation, and the existing escalation branch. Successful AI responses are persisted and await customer confirmation. Agents and Admins can inspect response details and citations, edit or accept/reject drafts, and send manual responses. Support Managers can inspect the generated resolution summary, troubleshooting steps, confidence, retrieved knowledge chunks, and source snippets in a read-only workflow view. They cannot run the workflow, generate or review response drafts, send resolutions, or mark tickets resolved. Customers receive only the resolution ID/status, final summary, and final steps from the customer response endpoint; internal sources, citations, scores, and workflow details remain excluded from that response.

The staff M3 workflow panel records and displays elapsed milliseconds for classification, diagnosis, knowledge retrieval, resolution generation, validation, and escalation analysis, plus total M3 elapsed time. These are wall-clock durations for this application's calls and workflow work; they are useful for locating slow stages, not a performance guarantee. The classification time is included when processing starts from the background ticket worker. Manually rerun M3 workflows have no new classification stage, so that entry is shown as pending. Older workflow records created before timings were added do not contain these values.

### Jira and SMTP

Jira escalation creates an issue using the existing configured project and stores the Jira key/status mapping on the ticket. The integration also supports issue lookup/update and status synchronization. SMTP uses Django's configured mail backend and the existing `apps.agents.email_service` for ticket-created, assignment, resolution, and escalation messages. Email delivery failures are logged and do not reverse ticket persistence.

## Backend environment

Create `server/.env` for local development or configure these values in the deployment environment. Do not commit secrets.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing key; use a unique secret in each deployed environment. |
| `DEBUG` | Django debug mode; set to `False` in production. Defaults to `False`. |
| `MONGO_URI` | MongoDB Atlas connection URI (including credentials and database options). |
| `ALLOWED_HOSTS` | Comma-separated Django hostnames, including the deployed API hostname. |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins allowed to call the API. |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins for Django admin/session CSRF where used. |
| `FRONTEND_URL` | Frontend origin used to build email verification links. |
| `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Django SMTP backend settings. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SUPPORT_TEAM_EMAIL` | SMTP sender credentials and support mailbox. |
| `OLLAMA_URL` | Ollama `/api/generate` endpoint reachable from the backend and worker. Defaults to localhost. |
| `OLLAMA_MODEL` | Model tag available on that Ollama server. Defaults to `qwen3:4b`. |
| `OLLAMA_TIMEOUT` | M3 Ollama request timeout in seconds. |
| `JIRA_URL`, `JIRA_EMAIL` (or `JIRA_USERNAME`), `JIRA_API_TOKEN` | Jira base URL and API credentials. |
| `JIRA_PROJECT_KEY`, `JIRA_ISSUE_TYPE` | Jira escalation project and issue type. |

`EMAIL_*` values are read through Django's existing mail configuration. Jira and Ollama credentials/endpoints are environment-driven. `DEBUG=False` alone is not a complete production hardening checklist; set real hosts/origins, protect secrets, and verify TLS and provider access.

## Local development

Prerequisites: Python compatible with Django 6, Node.js/npm, MongoDB Atlas or a compatible MongoDB URI, and (for AI resolutions) an Ollama host with the configured model pulled. The M1 model artifacts are included in this repository. The reranker and FastEmbed models may be downloaded on first use.

On Windows, `start-local.cmd` starts the backend, persistent ticket worker, and frontend in separate Command Prompt windows. It expects the backend virtual environment at `server\venv` and frontend dependencies installed under `client\node_modules`.

To start each process manually, open separate terminals:

```cmd
cd /d server
call venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py check
python manage.py runserver
```

```cmd
cd /d server
call venv\Scripts\activate.bat
python manage.py run_ticket_worker
```

```cmd
cd /d client
npm install
npm run dev
```

Set the frontend API base URL using the existing `client/src/api.ts` configuration before connecting it to a non-local backend. Keep `server/.env` and all credential files out of source control.

## API overview

All routes are rooted at `/api/` and use the existing JWT header flow where the view requires authentication.

- `/api/auth/register/`, `/api/auth/verify-email/`, `/api/auth/login/`, `/api/auth/me/`, `/api/auth/admin/users/`
- `/api/tickets/`, `/api/tickets/my/`, `/api/tickets/<ticket_id>/`, `/api/tickets/queue/`, `/api/tickets/<ticket_id>/timeline/`
- Ticket status, comments, classification override, assignment, workload, Support Manager overview, and AI performance routes are under `/api/tickets/`.
- Resolution generation/review/feedback routes are under `/api/tickets/`; staff-only response listing and customer-safe sent-response retrieval use the existing response endpoints.
- Knowledge articles, search, ingestion, ingestion status, and knowledge gaps are under `/api/knowledge/`.
- M3 workflow execution/status/activity logs are under `/api/agents/`.
- Email logs and notifications are under `/api/email/` and `/api/notifications/`.
- Jira issue create/read/update/status sync are under `/api/jira/`.

The canonical endpoint definitions are in `server/AIticket/urls.py` and each app's `urls.py`.

## Tests and verification

Run the Django test suite from `server/`:

```cmd
cd /d server
call venv\Scripts\activate.bat
python manage.py test
```

The repository also contains focused test modules for classification, severity, routing, assignment, ticket status, retrieval, knowledge-base persistence, resolution views, Jira, and email services. Live end-to-end tests require configured MongoDB Atlas, SMTP, Jira, and Ollama services; mocked tests do not establish that those external credentials or network paths work.

## Deployment

Vercel can host the Django HTTP application when the Vercel project root is set to `server/`; the existing `.vercelignore` excludes local environments, test fixtures, and training datasets. The repository has no separate Vercel JSON deployment manifest. Confirm Vercel's Django detection/build output for the selected project root and install the runtime requirements before promoting a deployment.

Ticket AI processing requires the separate persistent `run_ticket_worker` process to consume the MongoDB job queue. Deploy that worker as a long-running service with access to the same MongoDB, model artifacts, Ollama endpoint, SMTP, and Jira configuration. A serverless HTTP function alone does not keep this worker running. Do not replace the queue with request-lifetime threads.

Before production use, verify:

- `DEBUG=False`, a unique `SECRET_KEY`, exact `ALLOWED_HOSTS`, CORS and CSRF origins, and no secrets in source control;
- MongoDB Atlas network access, database user permissions, TLS, and connection URI;
- a reachable Ollama endpoint running the configured Qwen model from both the HTTP backend and worker;
- model availability, memory, cold-start time, and function bundle size for FastEmbed, PyTorch, Transformers, and LightGBM;
- SMTP delivery and verification links using the deployed frontend origin;
- Jira permissions, project key, issue type, and the escalation issue/update/status flows;
- worker process supervision, queue retry alerts, and recovery of expired leases;
- frontend API origin, ticket creation response time, and customer-safe resolution responses.

No production deployment or live integration is claimed by this repository update. The serverless runtime, large ML packages, external model endpoint, and separate worker need deployment-environment validation before release.

## Security notes

- Never commit `.env`, JWT signing keys, Mongo credentials, SMTP passwords, Jira tokens, or public AI endpoint credentials.
- Use HTTPS and narrow host/CORS/CSRF allowlists in production.
- Enforce role restrictions in API views as well as the frontend. Direct email and Jira HTTP endpoints require staff authorization; ticket notifications and escalation integrations used by the worker call their existing services internally.
- Registration verification proves mailbox access; it does not validate a provider against a hardcoded list.
- Keep customer-facing response serializers limited to final user-safe resolution fields. RAG citations, retrieval metadata, validation, routing, and internal comments are staff/workflow data.
- Restrict MongoDB access to the application and worker identities and configure appropriate backups/retention.
- Review request throttling, audit retention, and secret rotation in the actual deployment environment.
