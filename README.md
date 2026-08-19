# Support AI Ticket Management Agent

An AI-assisted IT support ticket management system designed to automate ticket classification, severity prediction, priority assignment, SLA management, intelligent routing, duplicate detection, and support workflow management.

This project was developed as part of the **Infosys Springboard Internship Program** with the goal of creating an enterprise-style AI-powered IT helpdesk platform where artificial intelligence assists support teams while keeping human agents in control.

---

# Project Overview

Traditional IT support systems often rely on manual ticket categorization, priority assignment, and routing. This can lead to:

- slower response times
- inconsistent ticket handling
- incorrect prioritization
- inefficient workload distribution

The Support AI Ticket Management Agent introduces an intelligent workflow where tickets are automatically analyzed and processed through an AI-assisted pipeline.

The system workflow:

```
User Creates Ticket
        |
        ↓
Duplicate Ticket Detection
        |
        ↓
AI Classification
        |
        ↓
Severity Prediction
        |
        ↓
Deterministic Priority Calculation
        |
        ↓
SLA Calculation
        |
        ↓
Queue Routing
        |
        ↓
Agent Resolution
```

---

# Core Roles

The platform follows a role-based architecture with a shared frontend system.

## User

Users can:

- Create support tickets
- View their submitted tickets
- Track ticket status
- View ticket details
- View ticket timelines
- View resolution information
- Receive AI classification previews
- Receive duplicate ticket suggestions

---

## Agent

Agents have additional support capabilities:

- View assigned ticket queues
- Access detailed ticket workspaces
- Review AI classification information
- View severity and priority reasoning
- Add public comments
- Add internal comments
- Update ticket status
- Correct AI classifications
- Resolve tickets

---

## Admin

Admins have extended administrative capabilities:

- Administrative access
- User management capabilities
- System-level controls where supported by backend functionality

The system uses backend authorization as the final security boundary.

---

# Major Features

## 1. Intelligent Ticket Classification

The system automatically classifies incoming tickets using machine learning models.

The classification pipeline:

```
Ticket Subject + Description
            |
            ↓
Text Processing
            |
            ↓
Embedding Generation
            |
            ↓
Machine Learning Classification
            |
            ↓
Category + Subcategory Prediction
```

Supported categories include:

- ACCESS
- APPLICATION
- EMAIL
- HARDWARE
- NETWORK
- SOFTWARE
- VPN

---

# 2. FAST Classification Preview

Users receive a real-time classification preview while creating tickets.

The preview:

- Runs asynchronously
- Uses the FAST classification pipeline
- Provides category/subcategory confidence information
- Does not block ticket submission
- Does not invoke expensive AI generation workflows

The preview helps users understand how their issue may be categorized before submission.

---

# 3. Duplicate Ticket Detection

The system identifies possible duplicate tickets before submission.

The duplicate detection workflow:

```
New Ticket
      |
      ↓
Compare Against User's Recent Active Tickets
      |
      ↓
Embedding Similarity
      +
Token Overlap Analysis
      |
      ↓
Duplicate Confidence Score
      |
      ↓
User Warning
```

Features:

- User-specific comparison
- Recent ticket comparison
- Embedding-based similarity
- Token overlap scoring
- Advisory warning system

Duplicate detection does not prevent users from submitting tickets.

---

# 4. AI-Based Severity Prediction

Severity is predicted separately from category classification.

The model considers structured impact information:

- affected scope
- work blocked status
- urgency indicators
- workaround availability
- ticket category

Severity levels:

```
LOW
MEDIUM
HIGH
CRITICAL
```

---

# 5. Deterministic Priority System

Priority is calculated using business rules instead of machine learning.

Priority levels:

```
P1 - Critical
P2 - High
P3 - Medium
P4 - Low
```

Example:

```
Critical Severity → P1

High Severity + Team Impact → P2
```

This ensures consistent and explainable ticket prioritization.

---

# 6. SLA Management

The system calculates SLA deadlines using business-calendar logic.

Supports:

- Business hours
- Weekend exclusion
- Holiday handling
- Priority-based response timelines

SLA calculations are based on business time rather than simple wall-clock time.

---

# 7. Intelligent Queue Routing

Tickets are automatically routed based on classification.

Example routing:

```
VPN
 ↓
Network Support

Hardware
 ↓
Hardware Support

Software
 ↓
Application Support
```

Agent queues are prioritized using SLA urgency rather than ticket creation time.

---

# 8. Agent Classification Override

Human agents can correct AI predictions.

Agents can update:

- Category
- Severity

The system stores classification corrections for future improvement and maintains classification history.

---

# 9. Ticket Lifecycle Management

The system supports complete ticket lifecycle handling:

```
Open
  |
  ↓
In Progress
  |
  ↓
Resolved
```

The workflow includes:

- status transitions
- validation of allowed transitions
- status history tracking
- public comments
- internal comments
- resolution summaries
- timeline generation

---

# 10. Role-Based Data Protection

The system protects sensitive internal information.

Users can view:

- Their tickets
- Public timeline events
- Resolution information

Agents/Admins can additionally access:

- Internal comments
- Classification metadata
- AI reasoning information
- Operational details

Backend authorization remains the primary security layer.

---

# Technology Stack

## Frontend

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Axios
- Lucide React

---

## Backend

- Python
- Django
- Django REST Framework
- SimpleJWT Authentication
- MongoDB
- PyMongo

---

## Machine Learning / AI

- FastEmbed
- Sentence Transformer embeddings
- LightGBM
- NLP preprocessing
- Machine learning classification pipelines

---

# System Architecture

```
                 React Frontend
                       |
                       |
                 REST API Layer
                       |
        --------------------------------
        |              |               |
 Authentication   Ticket System    AI Pipeline
        |              |               |
       JWT         MongoDB       ML Models
```

---

# Backend Architecture

```
server/

├── AIticket/
│
├── apps/
│   |
│   ├── authentication/
│   |
│   ├── tickets/
│   │
│   ├── agents/
│   |
│   └── history/
│
├── training/
│
└── manage.py
```

---

# Database

MongoDB database:

```
SupportAI
```

Collections:

```
users
tickets
counters
classification_overrides
status_history
ticket_comments
```

---

# Authentication

The system uses JWT-based authentication.

Implemented features:

- User registration
- Login
- Access tokens
- Refresh tokens
- Protected API access
- Role-based dashboard access

---

# Security Features

Implemented security measures:

- JWT authentication
- Backend authorization checks
- Role-based permissions
- User ticket ownership validation
- Protected internal Agent/Admin information
- Separation of User and internal support data

---

# Project Development Milestones

## Milestone 1 — Intelligent Ticket Management

Completed major capabilities:

- Ticket creation workflow
- AI classification
- Severity prediction
- Priority calculation
- SLA management
- Duplicate detection
- Agent workflow
- Ticket lifecycle management
- Role-based frontend

---

## Future Enhancements

Planned future improvements:

- Knowledge Base integration
- Retrieval Augmented Generation (RAG)
- AI resolution suggestions
- Advanced analytics dashboard
- Automated email ticket ingestion
- Feedback-based model improvement
- Advanced reporting
- Enterprise integrations

---

# Project Goals

The objective of this project is to demonstrate how artificial intelligence can improve IT support operations by:

- reducing manual ticket sorting
- improving response prioritization
- helping agents make faster decisions
- maintaining explainable AI-assisted workflows
- improving overall support efficiency

---

# Internship Project

Developed as part of:

**Infosys Springboard Internship Program**

Project:

**Support AI Ticket Management Agent**

---

# License

This project is developed for educational and internship purposes.
```
