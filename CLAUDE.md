# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Installation
```bash
make               # Install blur command using uv tool install
```

### Development
```bash
uv tool install -e .    # Install the blur command locally
blur                     # Run the blur command (processes clipboard content)
python -m blur          # Alternative way to run
```

## Architecture

This is a clipboard-based content transformation tool. The command detects the type of content in the clipboard (image, video file, or text) and applies appropriate transformations.

### Entry Point

- **`blur/main.py`**: `main()` function is the entry point
  - Detects clipboard content type using `ImageGrab.grabclipboard()`
  - Routes to appropriate processor based on content type:
    - `PIL.Image` → `process_image()`
    - List of file paths with `.mp4`/`.avi` extension → `process_video()`
    - Text → randomly chooses between `process_text()` or `process_text1()`

### Core Modules

**`blur/clipboard.py`** - Cross-platform clipboard infrastructure
- `send_image_to_clipboard(image)` - Handles Windows (win32clipboard), Linux (wl-copy/xclip), macOS (osascript + temp file)
- `send_video_to_clipboard(path)` - Copies file paths as text/uri-list
- Uses `shutil.which()` for command availability checking with caching
- All functions accept both `str` and `Path` objects for paths

**`blur/image.py`** - Image transformations
- `WaveDeformer` class - Applies wave distortion using PIL's `ImageOps.deform()`
- `apply_distortion_grid()` - Main image processor: reduces contrast, applies wave distortion, draws grid lines
- `_blur(image, sigma)` - Gaussian blur using scikit-image (exported for video.py)
- Constants at module level control transformation parameters (amplitude, frequency, grid spacing, etc.)

**`blur/video.py`** - Video processing
- `process_video(filepath)` - Applies `_blur()` from image.py to each frame using moviepy's `fl_image()`
- Creates temporary directory for output, sends result path to clipboard

**`blur/text.py`** - Text transformations
- `scramble_chinese_text(text, probability)` - Swaps adjacent Chinese characters (Unicode range \u4e00-\u9fff)
- `translate_with_martian(text)` - Character substitution using mapping from `martian.txt` file
- Both functions copy result to clipboard and return the transformed text

### Dependencies

- **pillow** - Image processing
- **moviepy** - Video processing
- **scikit-image** - Gaussian blur (`gaussian()` from `skimage.filters`)
- **pywin32** - Windows clipboard (conditional on sys_platform == 'win32')
- **pyperclip** - Text clipboard operations
- **loguru** - Logging

### Platform-Specific Requirements

**Linux**: Requires `wl-clipboard` (Wayland) or `xclip` (X11) for clipboard operations

**macOS**: Uses AppleScript via `osascript` for file path clipboard operations

**Windows**: Uses PowerShell `Set-Clipboard` and win32clipboard API

### Code Style Notes

- Uses `pathlib.Path` for all file path operations (migrated from `os.path`)
- Type hints are used in clipboard.py and other refactored modules
- Constants are defined at module level to avoid magic numbers
- Context managers (`with` statements) are used for resource cleanup
- Backward compatibility aliases preserved (e.g., `process_image` → `apply_distortion_grid`)
