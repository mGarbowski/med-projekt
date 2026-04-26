# List available commands
@default:
    just -l

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
    PYTHONOPTIMIZE=1 uv run -m lcm.profile {{ARGS}}


# Compare results with SPMF for selected test datasets
correctness:
    uv run -m lcm.correctness