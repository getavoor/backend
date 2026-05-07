# Planbot+ / Avoor backend

The REST API backend for Avoor.

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (Flask-JWT-Extended)
- **Real-time communication**: Socket.IO
- **AI**: Google Gemini with LangChain/LangGraph
- **Server**: Uvicorn (ASGI)
- **Deployment**: Google App Engine ready

## Documentation

| Document | Description |
|----------|-------------|
| [Overview](docs/overview.md) | Project overview and architecture guide (start here if you're new!) |
| [API reference](docs/api.md) | Complete API reference with request/response examples |
| [Setup guide](docs/setup.md) | Deployment and configuration guide |

## Project Structure

```
backend/
├── server/              # Main application
│   ├── routes/          # API endpoints
│   ├── langchain/       # AI planning integration
│   ├── templates/       # HTML templates
│   └── static/          # Static files
├── ai_engine/           # AI engine abstraction (deprecated)
├── abstract_storage/    # File storage abstraction
├── docs/                # Documentation
├── migrations/          # Database migrations
└── requirements.txt     # Dependencies
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AVR_DB_URL` | Yes | PostgreSQL connection string |
| `AVR_DB_SK` | Yes | Database secret key |
| `AVR_JW_SK` | Yes | JWT secret key |
| `AVR_SI_SK` | Yes | Socket.IO secret key |
| `AVR_TK_SL` | Yes | Token salt for email verification |
| `AVR_EM_AD` | Yes | Sender email address |
| `AVR_PORT` | No | Server port (default: 8000) |
| `AVR_FS` | No | Storage: `folder` or `google_bucket` |
| `AVR_AI` | No | AI engine: `mock` or `gemini` |
| `AVR_GAK` | No | Google API key (required if using Gemini) |

## License

This project is proprietary software.
