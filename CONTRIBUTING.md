# Contributing to AI Image Chat

Thank you for your interest in contributing to AI Image Chat! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ai-image-chat.git
   cd ai-image-chat
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- ComfyUI installation (see [QUICKSTART.md](./QUICKSTART.md))
- Ollama installed and running
- NVIDIA GPU with CUDA support (for image generation)

### Install Development Dependencies

**Quick Setup (Recommended):**

```bash
# Run the automated setup script
bash scripts/setup-dev.sh
```

This script will:
1. Install all development dependencies
2. Set up pre-commit hooks
3. Run initial code formatting
4. Verify the setup

**Manual Setup:**

```bash
# Install all development dependencies (includes testing, linting, formatting tools)
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (establish baseline)
pre-commit run --all-files

# Or use make
make install-dev
```

This installs:
- **Production dependencies**: gradio, requests, pillow, etc.
- **Testing tools**: pytest, pytest-cov, pytest-mock
- **Code quality tools**: black, ruff, mypy, pre-commit
- **Development utilities**: ipython, ipdb, pipdeptree

### Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to match your system paths (optional)
nano .env
```

## Code Style

We use automated code formatting and linting to maintain consistent code quality across the project.

### Tools

- **[Black](https://black.readthedocs.io/)**: Uncompromising Python code formatter
- **[Ruff](https://docs.astral.sh/ruff/)**: Fast Python linter (replaces flake8, isort, pylint, etc.)
- **[pytest](https://pytest.org/)**: Testing framework

### Configuration

All tool configurations are in `pyproject.toml`:
- Line length: 100 characters
- Target: Python 3.10+
- Black and Ruff are configured to work together

### Running Formatters

#### Using Make (Recommended)

```bash
# Format code with Black
make format

# Lint and auto-fix with Ruff
make lint

# Lint without auto-fix (check only)
make lint-check

# Run all checks (format + lint + test)
make check
# or
make all
```

#### Manual Commands

```bash
# Format code with Black
black core/ utils/ comfyui_api.py config.py app.py

# Lint with Ruff (auto-fix)
ruff check . --fix

# Lint with Ruff (check only)
ruff check .
```

### Pre-commit Hooks

**Automated Code Quality Checks:**

Pre-commit hooks run automatically before each commit to ensure code quality. Once installed (via `bash scripts/setup-dev.sh`), they will:

1. **Format code** with Black
2. **Lint code** with Ruff (with auto-fix)
3. **Remove trailing whitespace**
4. **Ensure files end with newline**
5. **Validate YAML/JSON syntax**
6. **Check for large files** (>100MB)
7. **Detect private keys**
8. **Check for merge conflicts**

**The hooks run automatically on `git commit`** - no manual action required!

#### Running Pre-commit Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black --all-files
pre-commit run ruff --all-files
```

#### Skipping Hooks (When Necessary)

Sometimes you may need to skip pre-commit hooks (not recommended for regular use):

```bash
# Skip all hooks for a single commit
git commit --no-verify -m "WIP: Work in progress"

# Or use the SKIP environment variable for specific hooks
SKIP=black,ruff git commit -m "Skip formatting checks"
```

**⚠️ Warning:** Skipping hooks should be rare. Only skip if:
- You're making a work-in-progress commit
- You're fixing issues that the hooks themselves introduce
- You're committing third-party code that shouldn't be formatted

#### What Each Hook Does

| Hook | Purpose | Auto-fix |
|------|---------|----------|
| **black** | Formats Python code to PEP 8 standard | ✅ Yes |
| **ruff** | Lints Python code and fixes common issues | ✅ Yes |
| **trailing-whitespace** | Removes trailing spaces | ✅ Yes |
| **end-of-file-fixer** | Ensures files end with newline | ✅ Yes |
| **check-yaml** | Validates YAML syntax | ❌ No |
| **check-json** | Validates JSON syntax | ❌ No |
| **check-added-large-files** | Prevents commits of files >100MB | ❌ No |
| **detect-private-key** | Detects accidentally committed keys | ❌ No |
| **check-merge-conflict** | Detects merge conflict markers | ❌ No |
| **mixed-line-ending** | Fixes line endings to LF | ✅ Yes |

#### Updating Hooks

Pre-commit hooks are version-pinned in `.pre-commit-config.yaml`. To update to the latest versions:

```bash
pre-commit autoupdate
```

### Before Committing

**Hooks run automatically, but you can also run checks manually:**

```bash
make check
```

This will:
1. Format your code with Black
2. Lint and fix issues with Ruff
3. Run the test suite

**Typical workflow:**
1. Make your code changes
2. Run tests: `make test`
3. Commit: `git commit -m "Your message"`
   - Pre-commit hooks run automatically ✨
   - If hooks make changes, review and re-commit
4. Push: `git push`

### Editor Integration

#### VS Code

Install these extensions:
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

Add to `.vscode/settings.json`:
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  },
  "black-formatter.args": ["--line-length=100"],
  "ruff.lint.args": ["--line-length=100"]
}
```

#### PyCharm / IntelliJ IDEA

1. Install Black plugin
2. Go to **Settings → Tools → Black**
3. Set line length to 100
4. Enable "On code reformat" and "On save"

For Ruff:
1. Go to **Settings → Tools → External Tools**
2. Add Ruff with arguments: `check . --fix`

### Code Style Guidelines

1. **Use Black for formatting** - Don't fight with Black's style choices
2. **Follow PEP 8** - Ruff enforces most PEP 8 rules
3. **Use type hints** - Add type hints to function signatures where practical
4. **Write docstrings** - Use Google-style or NumPy-style docstrings
5. **Keep functions focused** - Single responsibility principle
6. **Limit line length** - 100 characters (configured in tools)

#### Example: Well-Formatted Code

```python
from typing import Optional, Tuple
from core import AIImageChatException


def estimate_vram_usage(
    width: int, height: int, steps: int, model_size_gb: float = 8.0
) -> Tuple[float, Optional[str]]:
    """
    Estimate VRAM usage for image generation.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        steps: Number of generation steps
        model_size_gb: Base model size in GB

    Returns:
        Tuple of (estimated_vram_gb, warning_message)

    Raises:
        AIImageChatException: If parameters are invalid
    """
    if width <= 0 or height <= 0:
        raise AIImageChatException("Width and height must be positive")

    resolution_factor = (width * height) / (1024 * 1024)
    estimated_vram = model_size_gb * resolution_factor

    warning = None
    if estimated_vram > 16:
        warning = f"Warning: Estimated {estimated_vram:.1f}GB exceeds typical GPU VRAM"

    return estimated_vram, warning
```

## Testing

We use pytest for all tests. Tests should be comprehensive and cover edge cases.

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make coverage

# Run specific test file
pytest test_workflow_manager.py

# Run specific test function
pytest test_workflow_manager.py::test_load_workflow

# Run tests matching a keyword
pytest -k "workflow"
```

### Writing Tests

1. **Place tests in the project root** with prefix `test_*.py`
2. **Use descriptive test names**: `test_workflow_manager_loads_valid_json()`
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Use fixtures** for common setup
5. **Mock external dependencies** (ComfyUI API, Ollama, etc.)

#### Example Test

```python
import pytest
from core import WorkflowManager, WorkflowLoadError


def test_workflow_manager_raises_error_on_invalid_json(tmp_path):
    """Test that WorkflowManager raises WorkflowLoadError for invalid JSON."""
    # Arrange
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{invalid json")

    manager = WorkflowManager(workflows_dir=tmp_path)

    # Act & Assert
    with pytest.raises(WorkflowLoadError, match="Failed to parse"):
        manager._load_workflow_from_file(invalid_json)
```

### Test Coverage

We aim for **>80% code coverage** for core modules. Check coverage with:

```bash
make coverage
# Opens htmlcov/index.html with detailed coverage report
```

## Submitting Changes

### Commit Messages

Use clear, descriptive commit messages:

```
Add custom exception hierarchy for better error handling

- Created core/exceptions.py with 8 exception classes
- Updated mode_manager.py to use custom exceptions
- Added comprehensive documentation to CLAUDE.md
```

Format:
- **First line**: Short summary (50 chars or less)
- **Body**: Detailed explanation of what and why (wrap at 72 chars)
- **Use imperative mood**: "Add feature" not "Added feature"

### Pull Request Process

1. **Ensure all checks pass**:
   ```bash
   make check
   ```

2. **Update documentation** if needed:
   - Update CLAUDE.md for internal changes
   - Update README.md for user-facing changes
   - Update QUICKSTART.md for setup changes

3. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub:
   - Fill out the PR template completely
   - Describe what the PR does
   - Reference any related issues
   - Include screenshots for UI changes
   - Mention if breaking changes are introduced

5. **Wait for CI checks** (see [Continuous Integration](#continuous-integration) below)

6. **Address review feedback**:
   - Make requested changes
   - Push updates to the same branch
   - Respond to comments

## Continuous Integration

### Automated Checks

**All pull requests automatically run CI checks** via GitHub Actions. The following workflows run on every PR:

#### Tests and Linting Workflow

Runs on: Push to main/dev, Pull Requests

**Jobs:**
1. **Lint with Ruff** - Ensures code follows linting rules
2. **Check Black Formatting** - Verifies code is properly formatted
3. **Run Tests with Coverage** - Executes unit tests for core/ and utils/

**Badge:** [![Tests](https://github.com/CreativeNewEra/ai-image-chat/workflows/Tests%20and%20Linting/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/test.yml)

#### Documentation Check Workflow

Runs on: Push to main, Pull Requests

**Jobs:**
1. **Validate Documentation Files** - Ensures required docs exist and have content
2. **Check for Broken Links** - Validates internal markdown links
3. **Check Documentation Structure** - Verifies docs have proper sections

**Badge:** [![Documentation](https://github.com/CreativeNewEra/ai-image-chat/workflows/Documentation%20Check/badge.svg)](https://github.com/CreativeNewEra/ai-image-chat/actions/workflows/docs.yml)

### Viewing CI Results

1. Navigate to your PR on GitHub
2. Scroll to the "Checks" section at the bottom
3. Click on any check to see detailed logs
4. Green checkmark ✅ = passed
5. Red X ❌ = failed (click for details)

### What to Do if CI Fails

**If Linting Fails:**
```bash
# Fix linting issues locally
make lint

# Or manually
ruff check . --fix

# Commit and push fixes
git add .
git commit -m "Fix linting issues"
git push
```

**If Formatting Fails:**
```bash
# Format code locally
make format

# Or manually
black core/ utils/ comfyui_api.py config.py

# Commit and push fixes
git add .
git commit -m "Apply Black formatting"
git push
```

**If Tests Fail:**
```bash
# Run tests locally to see failures
make test

# Fix the failing tests
# ... make your fixes ...

# Verify tests pass
make test

# Commit and push fixes
git add .
git commit -m "Fix failing tests"
git push
```

**If Documentation Check Fails:**
- Fix any broken links in markdown files
- Ensure all required documentation files exist
- Add missing content to documentation files

### CI Configuration

CI workflows are defined in `.github/workflows/`:
- `test.yml` - Tests and linting
- `docs.yml` - Documentation validation

These workflows use:
- Python 3.10
- Pip caching for faster builds
- Unit tests only (integration tests skipped in CI)

### Running CI Checks Locally

You can run the same checks locally before pushing:

```bash
# Run all checks (format + lint + test)
make check

# Run individual checks
make lint              # Same as CI lint check
make format            # Format code (CI checks formatting)
make test              # Same as CI test check
pre-commit run --all-files  # Run all pre-commit hooks
```

### CI vs Pre-commit Hooks

| Check | Pre-commit Hooks | CI (GitHub Actions) |
|-------|------------------|---------------------|
| **When** | Before local commit | On push/PR |
| **Ruff Lint** | ✅ Auto-fix | ✅ Check only |
| **Black Format** | ✅ Auto-fix | ✅ Check only |
| **Tests** | ❌ No | ✅ Yes |
| **Coverage** | ❌ No | ✅ Yes |
| **Docs Check** | ❌ No | ✅ Yes |

**Pre-commit hooks** catch issues early (before commit), while **CI** provides a final verification before merging.

## Project Structure

```
ai-image-chat/
├── core/                  # Core business logic (11 modules)
├── utils/                 # Utility functions
├── workflows/             # ComfyUI workflow templates
├── app.py                 # Main Gradio application
├── comfyui_api.py         # ComfyUI API bridge
├── config.py              # Configuration management
├── pyproject.toml         # Tool configuration
├── Makefile               # Development commands
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── tests/                 # Test files (test_*.py)
```

See [CLAUDE.md](./CLAUDE.md) for detailed architecture documentation.

## Best Practices for Phase 3+

### Architecture Patterns

When implementing Phase 3 features (multiple workflows, ControlNet, LoRA), follow these patterns:

```python
class FeatureManager:
    """Base class for feature managers"""
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", True)

    def initialize(self):
        """Setup feature"""
        pass

    def cleanup(self):
        """Cleanup resources"""
        pass
```

### Configuration Management

Use environment variables for system-specific settings:

```python
# config.py
import os

# Load from environment or use defaults
COMFYUI_PATH = os.getenv("COMFYUI_PATH", "/home/ant/AI/ComfyUI")
OLLAMA_API = os.getenv("OLLAMA_API", "http://localhost:11434/api")
```

### Input Validation

Always validate user inputs:

```python
def generate_image(prompt_text, steps, width, height):
    if not (512 <= width <= 2048):
        raise ValueError("Width must be between 512 and 2048")
    if not (1 <= steps <= 100):
        raise ValueError("Steps must be between 1 and 100")
```

### Extract Repeated Code

Create helper functions for common patterns:

```python
def ollama_request(endpoint: str, payload: dict, timeout: int = 30):
    try:
        response = requests.post(
            f"{OLLAMA_API}/{endpoint}",
            json=payload,
            timeout=timeout
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        return None
```

## Questions?

- Check [CLAUDE.md](./CLAUDE.md) for developer documentation
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- Check [docs/](./docs/) for additional guides
- Open an issue on GitHub for questions or bug reports

---

**Thank you for contributing to AI Image Chat! 🎨✨**
