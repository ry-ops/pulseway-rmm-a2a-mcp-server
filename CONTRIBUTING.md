# Contributing to Pulseway MCP Server

Thank you for your interest in contributing to the Pulseway MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and considerate in all interactions.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- Detailed description of the proposed feature
- Explanation of why this enhancement would be useful
- Possible implementation approaches

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes following the coding standards
4. Add or update tests as needed
5. Ensure all tests pass
6. Update documentation as needed
7. Commit your changes with clear, descriptive messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.10 or higher
- uv (recommended) or pip

### Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/pulseway-mcp-server.git
cd pulseway-mcp-server

# Install dependencies
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your test credentials
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pulseway_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py

# Run specific test
uv run pytest tests/test_client.py::TestPulsewayClient::test_list_systems
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Type checking
uv run mypy src/pulseway_mcp
```

## Coding Standards

### Style Guide

- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Python Version

- Maintain compatibility with Python 3.10+
- Use modern Python features when appropriate

### Documentation

- Add docstrings to all public functions, classes, and methods
- Use Google-style docstrings
- Update README.md if adding new features
- Include examples in docstrings when helpful

Example docstring:
```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use meaningful test names
- Follow the Arrange-Act-Assert pattern
- Mock external API calls

### Commits

- Write clear, concise commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issues in commit messages when applicable

Example commit message:
```
Add support for system metrics retrieval

- Implement get_system_metrics method
- Add MetricType enum
- Add tests for metrics functionality
- Update README with new tool documentation

Closes #123
```

## Project Structure

```
pulseway-mcp-server/
├── src/
│   └── pulseway_mcp/
│       ├── __init__.py      # Package initialization
│       ├── server.py        # MCP server implementation
│       ├── client.py        # Pulseway API client
│       └── models.py        # Data models
├── tests/
│   ├── __init__.py
│   ├── test_server.py       # Server tests
│   └── test_client.py       # Client tests
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── pyproject.toml           # Project configuration
├── README.md
└── CONTRIBUTING.md
```

## Adding New Features

### Adding a New Tool

1. Add the tool definition in `server.py`:
   ```python
   Tool(
       name="your_tool_name",
       description="Tool description",
       inputSchema={...},
   )
   ```

2. Implement the tool handler in the `call_tool` function

3. Add corresponding method to `PulsewayClient` if needed

4. Write tests for the new tool

5. Update README.md with tool documentation

### Adding a New Endpoint

1. Add the model in `models.py` if needed

2. Implement the client method in `client.py`

3. Add tests in `test_client.py`

4. Integrate with MCP tools if applicable

## Release Process

Releases are handled by maintainers:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag
4. Push to GitHub
5. GitHub Actions will build and publish

## Questions?

If you have questions, feel free to:

- Open an issue for discussion
- Reach out to maintainers

Thank you for contributing! 🎉
