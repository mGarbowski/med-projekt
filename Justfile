# List available commands
@default:
    just -l

# Install dependencies
install: _check-java
    uv sync

# Check if Java is installed (required for SPMF tests)
_check-java:
    #!/bin/bash
    if ! command -v java &> /dev/null; then
        echo "Error: Java is not installed"
        exit 1
    fi
    java -version

# Code formatter
fmt:
    uvx ruff format

# Check formatting, linter and types
check:
    uvx ruff format --check
    uvx ruff check
    uvx ty check

# Run tests
test:
    uvx pytest

# Profile time and memory usage of the algorithm
profile *ARGS:
    PYTHONOPTIMIZE=1 uv run -m scripts.profile {{ARGS}}

# Run the CLI
run *ARGS:
    uv run -m scripts.cli {{ARGS}}
