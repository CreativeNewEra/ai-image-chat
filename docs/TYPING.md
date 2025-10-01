# Type Checking Guide

This guide explains how we use type hints and static type checking with mypy in the AI Image Chat project.

## Table of Contents

- [Why Type Hints?](#why-type-hints)
- [Running Mypy](#running-mypy)
- [Type Hinting Patterns](#type-hinting-patterns)
- [Gradually Adding Types](#gradually-adding-types)
- [Common Issues](#common-issues)

## Why Type Hints?

Type hints provide several benefits:

1. **Early Error Detection**: Catch type errors before runtime
2. **Better IDE Support**: Improved autocomplete and inline documentation
3. **Self-Documenting Code**: Types clarify function signatures and intent
4. **Refactoring Safety**: Types help ensure changes don't break contracts
5. **Team Communication**: Makes code contracts explicit

**Example:**

```python
# Without type hints - unclear what this function expects/returns
def calculate_vram(width, height, steps):
    return (width * height / 1024 / 1024) * 8.0

# With type hints - clear and self-documenting
def calculate_vram(width: int, height: int, steps: int) -> float:
    """Calculate estimated VRAM usage in GB."""
    return (width * height / 1024 / 1024) * 8.0
```

## Running Mypy

### Command Line

```bash
# Check all files
mypy .

# Check specific file
mypy core/vram_estimator.py

# Check specific directory
mypy core/

# Use Makefile (recommended)
make type-check
```

### IDE Integration

**VS Code:**
1. Install Python extension
2. Install Pylance extension
3. Set `"python.analysis.typeCheckingMode": "basic"` in settings

**PyCharm:**
- Built-in type checking (enable in Preferences → Editor → Inspections → Python → Type Checker)

### CI Integration

Type checking runs automatically on:
- Every push to main/dev
- Every pull request
- Via GitHub Actions workflow

## Type Hinting Patterns

### Basic Types

```python
from typing import Optional, List, Dict, Tuple, Union

# Basic types
name: str = "AI Image Chat"
count: int = 42
ratio: float = 1.5
enabled: bool = True

# Collections
tags: list[str] = ["tag1", "tag2"]  # Python 3.10+
config: dict[str, int] = {"width": 1024}
coordinates: tuple[int, int] = (10, 20)

# Optional (can be None)
prompt: Optional[str] = None
# Or using Union
prompt: str | None = None  # Python 3.10+
```

### Function Signatures

```python
def estimate_vram(
    width: int,
    height: int,
    steps: int,
    base_vram: float = 8.0
) -> float:
    """
    Estimate VRAM usage for image generation.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        steps: Number of generation steps
        base_vram: Base VRAM requirement in GB

    Returns:
        Estimated VRAM usage in GB
    """
    resolution_factor = (width * height) / (1024 * 1024)
    return base_vram * resolution_factor
```

### Return Multiple Values

```python
def get_warnings(
    width: int,
    height: int,
    steps: int
) -> tuple[str, str]:
    """
    Generate VRAM warnings.

    Returns:
        Tuple of (warning_level, warning_message)
    """
    if width > 2048:
        return "error", "Width too large"
    return "none", "OK"
```

### Class Type Hints

```python
class SeedManager:
    """Manages generation seeds."""

    def __init__(self, history_size: int = 10) -> None:
        self.seeds: list[int] = []
        self.locked: bool = False
        self.current_seed: Optional[int] = None
        self.history_size: int = history_size

    def add_seed(self, seed: int) -> None:
        """Add seed to history."""
        self.seeds.append(seed)
        if len(self.seeds) > self.history_size:
            self.seeds.pop(0)

    def get_last_seed(self) -> Optional[int]:
        """Get the most recent seed."""
        return self.seeds[-1] if self.seeds else None
```

### Callable Types

```python
from typing import Callable

def execute_callback(
    callback: Callable[[int, str], bool],
    value: int,
    message: str
) -> bool:
    """Execute a callback function."""
    return callback(value, message)

# Example callback
def my_callback(value: int, message: str) -> bool:
    print(f"Value: {value}, Message: {message}")
    return True
```

### Type Aliases

```python
from typing import TypeAlias

# Define type aliases for clarity
ImageSize: TypeAlias = tuple[int, int]
Config: TypeAlias = dict[str, int | float | str]
Seeds: TypeAlias = list[int]

def resize_image(size: ImageSize) -> ImageSize:
    width, height = size
    return (width * 2, height * 2)
```

### Generic Types

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Queue(Generic[T]):
    """Generic queue implementation."""

    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> Optional[T]:
        return self.items.pop(0) if self.items else None

# Usage
int_queue: Queue[int] = Queue()
str_queue: Queue[str] = Queue()
```

## Gradually Adding Types

We use a **gradual typing** approach - adding types incrementally rather than all at once.

### Current Status

**Fully Typed Modules** (strict checking enabled):
- `core/vram_estimator.py`
- `core/seed_manager.py`
- `core/prompt_history.py`
- `utils/image_utils.py`

**Partially Typed Modules** (lenient checking):
- Most other core/ modules
- comfyui_api.py
- config.py

**Untyped Modules** (excluded from checking):
- Test files (test_*.py)
- Third-party code

### How to Add Types to a Module

**Step 1: Enable Stricter Checking**

Add to `mypy.ini`:
```ini
[mypy-core.your_module]
disallow_untyped_defs = True
disallow_incomplete_defs = True
```

**Step 2: Add Type Hints**

Start with function signatures:
```python
# Before
def calculate_something(x, y, z=10):
    return x + y * z

# After
def calculate_something(x: int, y: int, z: int = 10) -> int:
    return x + y * z
```

**Step 3: Run Mypy**

```bash
make type-check
# or
mypy core/your_module.py
```

**Step 4: Fix Errors**

Address each error reported by mypy. Common fixes:
- Add missing type hints
- Handle None cases with Optional
- Use proper collection types (list, dict, tuple)
- Add type: ignore comments for unavoidable issues

**Step 5: Commit**

Once mypy passes, commit the changes:
```bash
git add core/your_module.py mypy.ini
git commit -m "Add type hints to your_module"
```

### Type Ignore Comments

Sometimes you need to suppress mypy errors:

```python
# Ignore specific error on one line
result = third_party_function()  # type: ignore[attr-defined]

# Ignore all errors on one line (use sparingly)
data = legacy_code()  # type: ignore

# Ignore for entire file (last resort)
# mypy: ignore-errors
```

**When to use `type: ignore`:**
- Third-party libraries without type stubs
- Dynamic code that mypy can't understand
- Temporary workarounds (add TODO comment)

**When NOT to use:**
- As a shortcut instead of fixing types
- For code you wrote and control

## Common Issues

### Issue: "Incompatible return value type"

```python
def get_seed(self) -> int:
    return self.seed if self.seed else 0  # Error if seed is Optional[int]

# Fix: Handle None explicitly
def get_seed(self) -> int:
    return self.seed if self.seed is not None else 0
```

### Issue: "Missing type parameters"

```python
def get_items(self) -> list:  # Error: Generic type needs parameters
    return []

# Fix: Add type parameter
def get_items(self) -> list[str]:
    return []
```

### Issue: "Module has no attribute"

```python
from external_lib import SomeClass  # Error: No type stubs

# Fix: Add to mypy.ini
# [mypy-external_lib.*]
# ignore_missing_imports = True
```

### Issue: "Cannot determine type"

```python
def process(data):  # Error: Need type hint
    return data

# Fix: Add type hints
def process(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

### Issue: "Incompatible types in assignment"

```python
value: int = "string"  # Error: Incompatible types

# Fix: Use correct type
value: str = "string"
# Or use Union if it can be multiple types
value: int | str = "string"
```

## Best Practices

1. **Start with function signatures** - Most valuable type hints
2. **Use descriptive types** - `ImageSize` instead of `tuple[int, int]`
3. **Avoid `Any`** - Use specific types when possible
4. **Document complex types** - Add comments for clarity
5. **Run mypy frequently** - Catch errors early
6. **Enable strict checking gradually** - One module at a time
7. **Use IDE type checking** - Get instant feedback
8. **Review type errors in CI** - Don't merge broken types

## Resources

- [Python Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)

## Questions?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to ask questions or report issues.
