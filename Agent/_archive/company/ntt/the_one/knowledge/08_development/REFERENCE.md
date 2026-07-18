# Development Reference — Tools & Frameworks Comparison

> Cross-cloud comparison of development tools for data pipelines.

## Python Tooling Comparison

| Tool | Category | Alternative | Why We Use It |
|------|----------|------------|---------------|
| **uv** | Package manager | pip, poetry, pdm | Fast, lockfile, workspace support |
| **ruff** | Linter + formatter | flake8 + black + isort | Single tool, fast, auto-fix |
| **mypy** | Type checker | pyright, pytype | Strict mode, pydantic plugin |
| **pytest** | Test framework | unittest, nose | Fixtures, parametrize, plugins |
| **pre-commit** | Git hooks | husky, lefthook | Language-agnostic, easy config |

## Architecture Pattern Comparison

| Pattern | Description | Our Usage |
|---------|-------------|-----------|
| **Hexagonal (Ports & Adapters)** | Core logic isolated from I/O | All collectors — domain/, adapters/, application/ |
| **Clean Architecture** | Dependency inversion layers | Similar concept, different naming |
| **MVC** | Model-View-Controller | Not used (no UI layer) |
| **Pipeline Pattern** | Linear chain of transforms | DoFn chain within Beam |
| **Composition Root** | Wire dependencies in one place | `main.py` in every collector |

## Testing Framework Comparison

| Framework | Type | Use Case |
|-----------|------|----------|
| **pytest** | Unit + integration | All Python tests |
| **TestPipeline** | Beam pipeline testing | DoFn tests with `assert_that` |
| **unittest.mock** | Mocking | API client mocks |
| **pytest-cov** | Coverage | `--cov=src` for coverage reports |
| **hypothesis** | Property-based | Not currently used |

## Detailed Reference

For comprehensive tool comparisons, see:
- `archive/knowledge_base/GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md` (Dataflow worker tuning)
