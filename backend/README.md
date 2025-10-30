# BlockMe Backend

FastAPI backend service for document processing and tax-focused Q&A system.

## Tech Stack

- **Python 3.11+** with type hints
- **FastAPI** - Modern async web framework
- **Anthropic Claude** - Skill routing and document analysis
- **GLM-4** - Chinese document processing and Q&A
- **PyMuPDF** - PDF processing
- **python-docx** - Word document processing

## Setup

### 1. Create virtual environment
```bash
cd backend
uv venv .venv
source .venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies
```bash
uv sync
# Install dev dependencies
uv sync --extra dev
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Run development server
```bash
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
backend/
├── pyproject.toml      # Python dependencies
├── .venv/              # Virtual environment
├── .env                # Environment variables
├── tests/              # Test suite
└── app/                # FastAPI application
    ├── main.py
    ├── api/            # API routes
    ├── services/       # Business logic
    ├── models/         # Data models
    └── utils/          # Utilities
```

## Development

### Run tests
```bash
pytest tests/ -v
pytest --cov=app tests/
```

### Code quality
```bash
# Format code
black .
ruff check .

# Type checking
mypy app/
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
