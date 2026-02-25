# AGENTS.md - Blur Project

## Build/Install Commands

```bash
# Install package locally
uv tool install -e .
make install

# Run main command
blur

# Run main module directly
python -m blur
```

**Note**: No formal test, lint, or type checking commands exist in this project.

---

## Project Structure

```
blur/
├── blur/
│   ├── __init__.py       # Public API exports
│   ├── __main__.py       # Entry point wrapper
│   ├── main.py           # Main application logic
│   ├── clipboard.py      # Cross-platform clipboard operations
│   ├── image.py          # Image processing (blur, deform, grid overlay)
│   ├── text.py           # Text processing (character transformation)
│   └── video.py          # Video processing
├── pyproject.toml        # Project config (hatchling backend)
├── Makefile              # Install shortcut
└── README.md
```

---

## Code Style Guidelines

### Imports

**Follow this order** (PEP 8 compliance):
1. Standard library (`import os`, `import sys`)
2. Third-party (`import pyperclip`, `from PIL import Image`)
3. Local imports (`from blur.clipboard import send_image_to_clipboard`)

Group imports with a blank line between each group. Avoid mixing third-party and local imports on the same line.

**Example:**
```python
import os
import sys
import subprocess

from io import BytesIO
from PIL import Image
from loguru import logger

from blur.clipboard import send_image_to_clipboard
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `process_image`, `send_image_to_clipboard`)
- **Classes**: `PascalCase` (e.g., `WaveDeformer`)
- **Private functions**: `_snake_case` prefix (e.g., `_check_command`, `_blur`)
- **Variables**: `snake_case` (e.g., `temp_dir`, `filepath`, `output_path`)

### Type Hints

**Minimal but recommended**:
- Add return type hints for public functions
- Use `from typing import List, Optional, Tuple, Callable` as needed
- Don't go overboard - this is a simple utility project

**Example:**
```python
from typing import Optional

def send_image_to_clipboard(im: Image.Image) -> None:
    """Send an image to the clipboard in a cross-platform way."""
```

### Error Handling

**Pattern for functions with external operations:**
```python
try:
    # operation
except Exception as e:
    logger.exception("descriptive error message")
    input()  # Pause on error (project convention)
    raise  # Or handle appropriately
```

Use `logger.exception()` to capture full traceback. The `input()` call is intentional - it allows manual inspection when run interactively.

### Logging

Use `loguru` for all logging:
```python
from loguru import logger

logger.exception("error description")  # For exceptions
# logger.info/debug/warning for other levels
```

### Code Organization

- **Public functions**: Export in `blur/__init__.py` via `__all__`
- **Utility functions**: Prefix with underscore if internal-only
- **File separation**: Organize by responsibility (clipboard, image, text, video)
- **Blank lines**: 2 blank lines between top-level functions, 1 between methods in classes

### Cross-Platform Support

When adding clipboard or OS-specific features:
1. Check `sys.platform` first (`win32`, `linux`, `darwin`)
2. Use `subprocess.run()` with `check=True` for external commands
3. Provide clear error messages for unsupported platforms
4. See `blur/clipboard.py` as reference for platform handling

### Dependencies

Add new dependencies to `pyproject.toml` in the `dependencies` list. Current stack:
- `pillow` - Image processing
- `moviepy` - Video processing
- `loguru` - Logging
- `pyperclip` - Clipboard text
- `scikit-image` - Image filters
- `pywin32` - Windows clipboard (conditional)

---

## Key Patterns from Existing Code

### Image Processing
- Use `ImageEnhance.Contrast()` for image adjustments
- Use `ImageOps.deform()` with custom deformers for image transformations
- Use `ImageDraw.Draw()` for drawing shapes/lines on images

### Text Processing
- Use regex for character detection: `re.match(r'[\u4e00-\u9fff]+', char)` for Chinese characters
- Use pyperclip for clipboard text: `pyperclip.paste()`, `pyperclip.copy(text)`

### File Path Handling
```python
import os
filepath = "/path/to/file.ext"
filename, file_extension = os.path.splitext(filepath)
dirname = os.path.dirname(os.path.realpath(__file__))
```

---

## Development Workflow

1. Edit code directly in the `blur/` directory
2. Reinstall to test changes: `uv tool install -e .` (or `make install`)
3. Run `blur` command to test clipboard processing
4. Check console output for `logger.exception()` messages

**Note**: No automated testing exists. Manual clipboard-based testing is required.
