# Avoor (Planbot+) Backend Documentation

Welcome to the Avoor backend documentation. This guide is designed to help you understand the project structure, the technologies used, and how everything fits together - even if you're relatively new to Python web development.

## Table of Contents

1. [What is Avoor?](#what-is-avoor)
2. [Technologies Overview](#technologies-overview)
3. [Project Structure](#project-structure)
4. [Core Concepts](#core-concepts)
   - [Flask: The Web Framework](#flask-the-web-framework)
   - [SQLAlchemy: The Database ORM](#sqlalchemy-the-database-orm)
   - [JWT Authentication](#jwt-authentication)
   - [WebSockets with Socket.IO](#websockets-with-socketio)
5. [Application Architecture](#application-architecture)
6. [Key Components](#key-components)
   - [Models (Database Tables)](#models-database-tables)
   - [Routes (API Endpoints)](#routes-api-endpoints)
   - [Authentication System](#authentication-system)
   - [File Storage](#file-storage)
   - [AI Integration](#ai-integration)
   - [Long Running Tasks](#long-running-tasks)
7. [How a Request Flows Through the App](#how-a-request-flows-through-the-app)
8. [Getting Started](#getting-started)
9. [Further Reading](#further-reading)

---

## What is Avoor?

Avoor (also known as Planbot+) is a **task management and time planning application**. Think of it as a to-do list app with extra features:

- **User accounts** with email verification
- **Task management** - create, update, complete, and delete tasks
- **Plancoins** - a gamification system that rewards users for completing tasks
- **Streaks** - track consecutive days of task completion
- **AI-powered scheduling** - uses Google's Gemini AI to help plan your day
- **Profile pictures** - upload and store user avatars

The backend is a REST API that mobile apps or web frontends can connect to. It also has a simple administration page intended to be used by support.

---

## Technologies Overview

Here's a quick summary of the main technologies and what they do:

| Technology | Purpose |
|------------|---------|
| **Python 3** | The programming language everything is written in |
| **Flask** | Web framework for handling HTTP requests and responses |
| **SQLAlchemy** | ORM (Object-Relational Mapper) for database operations |
| **PostgreSQL** | The database where all data is stored |
| **Flask-JWT-Extended** | Handles user authentication with tokens |
| **Socket.IO** | Real-time communication via WebSockets |
| **Google Gemini** | AI model for intelligent schedule planning |
| **Uvicorn** | ASGI server that runs the application |

---

## Project Structure

Here's how the codebase is organized:

```
backend/
├── server/                     # Main application code
│   ├── __init__.py             # App initialization (start here!)
│   ├── __main__.py             # Entry point when running the server
│   ├── models.py               # Database models (User, Task, etc.)
│   ├── common.py               # Shared utility functions
│   ├── decorators.py           # Authentication decorators
│   ├── env_vars.py             # Environment variable configuration
│   ├── compressor.py           # Image processing for profile pics
│   ├── token_generator.py      # Email confirmation token generation
│   ├── discovery.py            # WebSocket event handlers (real-time communication)
│   ├── sysprompt.py            # AI system prompts
│   │
│   ├── routes/                 # API endpoints organized by feature
│   │   ├── auth.py             # Login, register, email confirmation
│   │   ├── api.py              # Tasks, plancoins, user profile
│   │   ├── main.py             # Web UI routes
│   │   ├── admin.py            # Admin dashboard
│   │   └── app_only.py         # Mobile app redirects
│   │
│   ├── langchain/              # AI planning integration
│   │   ├── __init__.py         # LangGraph state machine setup
│   │   ├── tools.py            # AI tools for schedule planning
│   │   └── types.py            # Data type definitions
│   │
│   ├── templates/              # HTML templates for administration (Jinja2)
│   └── static/                 # Static files (CSS, JS, images)
│
├── ai_engine/                   # AI engine abstraction
│   ├── __init__.py             # Base AIEngine class
│   ├── gemini.py               # Google Gemini implementation
│   └── exceptions.py           # Custom exceptions
│
├── abstract_storage/            # File storage abstraction
│   ├── __init__.py             # Base AbstractStorage class
│   ├── folder.py               # Local file storage
│   └── google.py               # Google Cloud Storage
│
├── migrations/                  # Database migrations (Alembic)
│   └── versions/               # Individual migration files
│
├── docs/                        # Documentation
│   ├── overview.md             # This file - project overview
│   ├── api.md                  # API reference
│   ├── setup.md                # Deployment guide
│   ├── abstract-storage.md     # File storage abstraction
│   ├── ai-engine.md            # AI engine (deprecated)
│   └── long-running-tasks.md   # Background tasks
│
├── requirements.txt            # Python dependencies
├── setup.py                    # Setup script
├── app.yaml                    # Google App Engine config
└── cloudbuild.yaml             # Google Cloud Build config
```

---

## Core Concepts

### Flask: The Web Framework

[Flask](https://flask.palletsprojects.com/) is a lightweight Python web framework. It handles:

- Receiving HTTP requests (GET, POST, PUT, DELETE)
- Routing requests to the right function
- Sending HTTP responses back

**Basic Flask Example:**

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})
```

In this example:
- `@app.route('/hello')` tells Flask: "When someone visits `/hello`, run this function"
- `jsonify()` converts a Python dictionary to JSON format for the response

**In Avoor**, Flask is created in `server/__init__.py` with the `create_flask_app()` function.

**Learn more:** [Flask Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart/)

---

### SQLAlchemy: The Database ORM

[SQLAlchemy](https://www.sqlalchemy.org/) is an ORM (Object-Relational Mapper). It lets you work with database tables as Python classes instead of writing raw SQL.

**Without an ORM (raw SQL):**
```sql
SELECT * FROM users WHERE email = 'john@example.com';
```

**With SQLAlchemy:**
```python
user = User.query.filter_by(email='john@example.com').first()
```

**Defining a Model (Table):**

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
```

This creates a `users` table with columns: `id`, `email`, and `name`.

**Common Operations:**

```python
# Create a new user
new_user = User(email='jane@example.com', name='Jane')
db.session.add(new_user)
db.session.commit()

# Find a user by ID
user = User.query.get(1)

# Find all users
all_users = User.query.all()

# Update a user
user.name = 'Jane Doe'
db.session.commit()

# Delete a user
db.session.delete(user)
db.session.commit()
```

**In Avoor**, models are defined in `server/models.py`.

**Learn more:** [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)

---

### JWT Authentication

JWT (JSON Web Token) is a way to authenticate users without sessions. Here's how it works:

1. User logs in with email and password
2. Server validates credentials and creates a **token** (a long encoded string)
3. Client stores this token and sends it with every request
4. Server validates the token to identify the user

**Why JWT?**
- Stateless: Server doesn't need to store session data
- Perfect for APIs used by mobile apps
- Tokens can include expiration times

**In Avoor**, we use two types of tokens:
- **Access Token**: Short-lived (used for API requests)
- **Refresh Token**: Long-lived (used to get new access tokens)

**Example Request with JWT:**

```http
GET /api/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**In Avoor**, JWT is configured in `server/__init__.py` and used via decorators in `server/decorators.py`.

**Learn more:** [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)

---

### WebSockets with Socket.IO

Regular HTTP is request-response: the client asks, the server answers. **WebSockets** allow two-way real-time communication - the server can push data to clients at any time.

[Socket.IO](https://socket.io/) is a library that makes WebSockets easier to use, with features like:
- Automatic reconnection
- Room-based broadcasting
- Event-based communication

**Example:**

```python
# Server-side
@socketio.on('message')
def handle_message(data):
    print(f'Received: {data}')
    socketio.emit('response', {'msg': 'Got it!'})

# Client sends 'message' event
# Server receives it and sends back 'response' event
```

**In Avoor**, Socket.IO is used for the AI planning feature, allowing real-time conversation with the AI. The handlers are in `server/discovery.py`.

**Learn more:** [Python Socket.IO Documentation](https://python-socketio.readthedocs.io/)

---

## Application Architecture

Here's how the different parts of Avoor work together:

```
┌─────────────────────────────────────────────────────────────┐
│                        Client                                │
│                  (Avoor mobile app)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Uvicorn Server                          │
│                    (ASGI Server)                            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│      Flask App          │     │       Socket.IO             │
│   (REST API Requests)   │     │  (Real-time Communication)  │
└─────────────────────────┘     └─────────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│        Routes           │     │    Discovery Handler        │
│  (auth, api, admin)     │     │    (WebSocket Events)       │
└─────────────────────────┘     └─────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Services                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Models    │  │   Storage   │  │     AI Engine       │  │
│  │ (Database)  │  │   (Files)   │  │     (Gemini)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
              │                │                │
              ▼                ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌───────────────────┐
│   PostgreSQL    │  │  File System /  │  │   Google Gemini   │
│    Database     │  │ Google Cloud    │  │       API         │
└─────────────────┘  └─────────────────┘  └───────────────────┘
```

---

## Key Components

### Models (Database Tables)

Located in `server/models.py`, here are the main database tables:

#### User

Stores user account information:

```python
class User(db.Model):
    id              # Unique identifier
    email           # User's email (unique)
    password        # Hashed password (never stored in plain text!)
    name            # Display name
    is_confirmed    # Has the email been verified?
    photo_url       # Profile picture URL
    plancoins       # Reward currency balance
    current_streak  # Current consecutive days active
    longest_streak  # Best streak ever achieved
```

#### Task

Stores user tasks:

```python
class Task(db.Model):
    id              # Unique identifier
    user_id         # Which user owns this task
    title           # Task name
    description     # Detailed description
    is_completed    # Is the task done?
    priority        # 1=low, 2=medium, 3=high
    created_at      # When it was created
    completed_at    # When it was completed
    due_date        # Deadline
```

#### PlancoinTransaction

Records all plancoin earnings/spending:

```python
class PlancoinTransaction(db.Model):
    id              # Unique identifier
    user_id         # Which user
    amount          # How many plancoins (+ or -)
    reason          # Why they were earned/spent
    created_at      # When the transaction happened
```

**Relationships:** A User has many Tasks and many PlancoinTransactions. If a User is deleted, all their Tasks and Transactions are automatically deleted too (cascade delete).

---

### Routes (API Endpoints)

Routes are organized into **blueprints** - Flask's way of grouping related endpoints:

#### Authentication (`server/routes/auth.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register` | POST | Create a new account |
| `/api/login` | POST | Sign in and get tokens |
| `/api/confirm` | POST | Verify email address |
| `/api/resend` | POST | Resend verification email |
| `/api/refreshToken` | POST | Get a new access token |

#### API (`server/routes/api.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/me` | GET | Get current user info |
| `/api/me` | DELETE | Delete account |
| `/api/setPicture` | POST | Upload profile picture |
| `/api/tasks` | GET | List all tasks |
| `/api/tasks` | POST | Create a task |
| `/api/tasks/<id>` | PUT | Update a task |
| `/api/tasks/<id>` | DELETE | Delete a task |
| `/api/plancoins/add` | POST | Add plancoins |
| `/api/plancoins/history` | GET | View transaction history |
| `/api/streak` | GET | Get streak information |

For detailed API documentation with request/response examples, see [api.md](api.md).

---

### Authentication System

The authentication system uses multiple layers of protection:

#### Decorators

Decorators in `server/decorators.py` protect routes:

```python
# This route requires any valid JWT token
@api_auth_required
def get_user():
    pass

# This route requires a confirmed email
@api_confirmation_required
def create_task():
    pass

# This route is only for unconfirmed users
@api_unconfirmed_required
def resend_confirmation():
    pass
```

#### Password Security

Passwords are hashed using PBKDF2 with SHA-512. This means:
- The actual password is never stored
- Even if the database is compromised, passwords can't be recovered

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When registering
hashed = generate_password_hash(password, method='pbkdf2:sha512')

# When logging in
if check_password_hash(user.password, provided_password):
    # Password is correct
```

#### Password Requirements

The API enforces strong passwords:
- At least 8 characters
- At least 1 digit
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 symbol

---

### File Storage

Avoor uses an **abstraction layer** for file storage, allowing it to work with different backends:

```
abstract_storage/
├── __init__.py    # AbstractStorage base class
├── folder.py      # FolderStorage - saves to local folder
└── google.py      # GoogleCloudStorage - saves to GCS bucket
```

**Why an abstraction?** This lets the same code work in different environments:
- Development: Store files in a local folder
- Production: Store files in Google Cloud Storage

**Usage:**

```python
from abstract_storage import AbstractStorage

storage = AbstractStorage.get_instance()

# Upload a file
storage.upload(file_data, 'profile/user_1/photo.jpg')

# Get the public URL
url = storage.get_url('profile/user_1/photo.jpg')

# Delete a file
storage.delete('profile/user_1/photo.jpg')
```

The storage backend is configured via the `AVR_FS` environment variable:
- `folder` - Local folder storage
- `google_bucket` - Google Cloud Storage

**Learn more:** [Abstract Storage documentation](abstract-storage.md)

---

### AI Integration

Avoor includes the base for an AI-powered schedule planning system using Google's Gemini model.

> Please note that the system needs to be reworked after tbe 

#### AI Engine (Deprecated)

The `ai_engine/` module provides a simple abstraction for AI interactions. It's configured via the `AVR_AI` environment variable:
- `mock` - Returns placeholder responses (for testing)
- `gemini` - Uses real Gemini API

> **Note:** For new AI features, use the LangChain integration instead.

**Learn more:** [AI Engine documentation](ai-engine.md)

#### LangChain Integration

The `server/langchain/` directory contains a sophisticated planning system:

**How it works:**
1. User describes their day and constraints
2. AI asks clarifying questions
3. AI builds a schedule using "tools"
4. User can export the schedule to a calendar file

**AI Tools** (`server/langchain/tools.py`):
- `add_to_plan()` - Add a time block
- `get_plan()` - View current plan
- `show_plan()` - Display plan to user
- `clear_plan()` - Start over
- `remove_from_plan()` - Remove a block
- `add_to_calendar()` - Export as .ics file

**LangGraph** manages the conversation flow as a state machine, ensuring the AI follows a logical process.

---

### Long Running Tasks

Long Running Tasks (LRT) is a system for executing asynchronous operations that take too long for a normal HTTP request/response cycle. The system creates a separate asyncio event loop in a background thread.

> **Note:** The LRT system was primarily used in the project this codebase originated from. Current Avoor has minimal LRT usage, but the infrastructure remains for future features like batch email sending or scheduled tasks.

**How it works:**
1. Main thread handles HTTP requests via Flask
2. Background thread runs an asyncio event loop
3. Long operations are submitted to the background loop
4. Requests return immediately without waiting

**Learn more:** [Long Running Tasks documentation](long-running-tasks.md)

---

## How a Request Flows Through the App

Let's trace what happens when a user creates a new task:

```
1. Client sends POST /api/tasks with JSON body and JWT token

2. Uvicorn receives the HTTP request

3. Flask routes it to the tasks endpoint in server/routes/api.py

4. The @api_confirmation_required decorator:
   a. Extracts the JWT token from Authorization header
   b. Validates the token
   c. Loads the user from the database
   d. Checks if email is confirmed
   e. If all checks pass, calls the actual function

5. The create_task() function:
   a. Parses the JSON body (title, description, priority)
   b. Validates required fields
   c. Creates a new Task object
   d. Adds it to the database session
   e. Commits the transaction

6. Flask returns JSON response with the new task

7. Uvicorn sends the HTTP response back to the client
```

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- (Optional) Google Cloud account for Gemini AI and cloud storage

### Quick Start

1. **Clone the repository and enter the directory**

2. **Create a virtual environment** (recommended):
   ```bash
   pip3 install virtualenv
   virtualenv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Set environment variables** (create a `.env` file or export them):
   ```bash
   # Required
   AVR_DB_SK=your-database-secret-key
   AVR_DB_URL=postgresql://user:password@localhost/avoor
   AVR_JW_SK=your-jwt-secret-key
   AVR_SI_SK=your-socketio-secret-key
   AVR_TK_SL=your-token-salt
   AVR_EM_AD=noreply@yourdomain.com

   # Optional
   AVR_PORT=8000
   AVR_FS=folder
   AVR_AI=mock
   ```

5. **Set up the database:**
   ```bash
   flask --app server:create_flask_app db upgrade
   ```

6. **Run the server:**
   ```bash
   python3 -m server
   ```

7. **Test it:**
   ```bash
   curl http://localhost:8000/api/me
   # Should return 401 Unauthorized (no token provided)
   ```

For detailed deployment instructions, see [setup.md](setup.md).

---

## Further Reading

### Official Documentation

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com/
- **Flask-JWT-Extended**: https://flask-jwt-extended.readthedocs.io/
- **Socket.IO (Python)**: https://python-socketio.readthedocs.io/
- **Google Gemini**: https://ai.google.dev/docs
- **LangChain**: https://python.langchain.com/docs/

### Project Documentation

- **API Reference**: See [api.md](api.md)
- **Deployment Guide**: See [setup.md](setup.md)
- **Abstract Storage**: See [abstract-storage.md](abstract-storage.md)
- **AI Engine**: See [ai-engine.md](ai-engine.md)
- **Long Running Tasks**: See [long-running-tasks.md](long-running-tasks.md)

### Tutorials

If you're new to these technologies, here are some tutorials:

- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [JWT Authentication Explained](https://jwt.io/introduction)

---

## Glossary

| Term | Definition |
|------|------------|
| **API** | Application Programming Interface - a way for programs to communicate |
| **ASGI** | Asynchronous Server Gateway Interface - Python standard for async web servers |
| **Blueprint** | Flask's way of organizing routes into modules |
| **CRUD** | Create, Read, Update, Delete - basic database operations |
| **Decorator** | A function that wraps another function to add behavior |
| **Endpoint** | A specific URL path that handles requests |
| **JWT** | JSON Web Token - a standard for secure authentication tokens |
| **Migration** | A script that modifies the database schema |
| **ORM** | Object-Relational Mapper - maps database tables to Python classes |
| **REST** | Representational State Transfer - an API design style |
| **WebSocket** | Protocol for real-time, two-way communication |

---

*This documentation was created to help newcomers understand the Avoor backend. If something is unclear or you'd like more detail on a specific topic, feel free to ask!*
