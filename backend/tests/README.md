# BlockMe Tests

This directory contains all tests for the BlockMe knowledge system.

## Test Categories

### Environment Tests
- `test_dependencies.py` - Verifies all Python dependencies are correctly installed
- `test_api_connections.py` - Validates API connections to Claude and GLM

### Running Tests

**Run all tests:**
```bash
source .venv/bin/activate
pytest tests/
```

**Run with coverage:**
```bash
pytest --cov=backend tests/
```

**Run specific test file:**
```bash
pytest tests/test_dependencies.py
pytest tests/test_api_connections.py
```

**Run with verbose output:**
```bash
pytest -v tests/
```

## Test Requirements

According to `development-policies` skill:
- **Unit Tests** - All business logic must have unit tests
- **Integration Tests** - API endpoints must have integration tests
- **Coverage** - Minimum 80% code coverage for new code

## CI/CD Usage

These environment tests are designed to be run in CI/CD pipelines to verify:
1. All dependencies are correctly installed
2. API keys are properly configured
3. External services are accessible
