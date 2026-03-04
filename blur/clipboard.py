import sys
import tempfile
import shutil
from pathlib import Path
from io import BytesIO
from typing import Optional

from PIL import Image
from loguru import logger


# 常量
MIME_PNG = "image/png"
MIME_URI_LIST = "text/uri-list"
PLATFORM_WIN32 = "win32"
PLATFORM_LINUX = "linux"
PLATFORM_DARWIN = "darwin"

# 命令缓存
_command_cache: dict[str, Optional[bool]] = {}


def _check_command(cmd: str) -> bool:
    """
    检查系统命令是否可用（带缓存）

    Args:
        cmd: 命令名称

    Returns:
        命令是否可用
    """
    if cmd in _command_cache:
        return _command_cache[cmd] if _command_cache[cmd] is not None else False

    available = shutil.which(cmd) is not None
    _command_cache[cmd] = available
    return available


def _get_image_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    将 PIL Image 转换为字节流

    Args:
        image: PIL Image 对象
        format: 图像格式（PNG、BMP 等）

    Returns:
        图像字节流
    """
    with BytesIO() as output:
        image.save(output, format=format)
        return output.getvalue()


def _send_image_to_windows_clipboard(image: Image.Image) -> None:
    """发送图像到 Windows 剪贴板"""
    try:
        import win32clipboard

        # 转换为 BMP 格式（去掉 BMP 头部）
        with BytesIO() as output:
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # 跳过 BMP 文件头

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        finally:
            win32clipboard.CloseClipboard()

    except Exception:
        logger.exception("Windows clipboard error")
        raise


def _send_image_to_linux_clipboard(image: Image.Image) -> None:
    """发送图像到 Linux 剪贴板（Wayland 或 X11）"""
    data = _get_image_bytes(image, "PNG")

    if _check_command("wl-copy"):
        try:
            import subprocess

            subprocess.run(["wl-copy", "--type", MIME_PNG], input=data, check=True)
        except Exception:
            logger.exception("wl-copy error")
            raise
    elif _check_command("xclip"):
        try:
            import subprocess

            subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", MIME_PNG],
                input=data,
                check=True,
            )
        except Exception:
            logger.exception("xclip error")
            raise
    else:
        raise RuntimeError(
            "No clipboard tool found. Install wl-clipboard (Wayland) or xclip (X11)"
        )


def _send_image_to_macos_clipboard(image: Image.Image) -> None:
    """发送图像到 macOS 剪贴板"""
    import subprocess

    try:
        # 使用临时文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            image.save(tmp_path, format="PNG")
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to POSIX file "{tmp_path}"'],
                check=True,
            )
        finally:
            # 清理临时文件
            tmp_path.unlink(missing_ok=True)

    except Exception:
        logger.exception("macOS clipboard error")
        raise


def send_image_to_clipboard(image: Image.Image) -> None:
    """
    跨平台发送图像到剪贴板

    Args:
        image: PIL Image 对象

    Raises:
        RuntimeError: 不支持的平台或缺少必要工具
    """
    platform = sys.platform

    if platform == PLATFORM_WIN32:
        _send_image_to_windows_clipboard(image)
    elif platform == PLATFORM_LINUX:
        _send_image_to_linux_clipboard(image)
    elif platform == PLATFORM_DARWIN:
        _send_image_to_macos_clipboard(image)
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")


def send_video_to_clipboard(filepath: str | Path) -> None:
    """
    跨平台发送视频文件路径到剪贴板

    Args:
        filepath: 视频文件路径

    Raises:
        RuntimeError: 不支持的平台或缺少必要工具
    """
    import subprocess

    platform = sys.platform
    path_str = str(filepath)

    if platform == PLATFORM_WIN32:
        subprocess.run(
            ["powershell", "Set-Clipboard", f"-Path '{path_str}'"],
            shell=True,
            check=True,
        )
    elif platform == PLATFORM_LINUX:
        if _check_command("wl-copy"):
            try:
                subprocess.run(["wl-copy", "--type", MIME_URI_LIST, path_str], check=True)
            except Exception:
                logger.exception("wl-copy error for video")
                raise
        elif _check_command("xclip"):
            try:
                subprocess.run(
                    [
                        "xclip",
                        "-selection",
                        "clipboard",
                        "-t",
                        MIME_URI_LIST,
                        "-i",
                        path_str,
                    ],
                    check=True,
                )
            except Exception:
                logger.exception("xclip error for video")
                raise
        else:
            raise RuntimeError(
                "No clipboard tool found. Install wl-clipboard (Wayland) or xclip (X11)"
            )
    elif platform == PLATFORM_DARWIN:
        try:
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to POSIX file "{path_str}"'],
                check=True,
            )
        except Exception:
            logger.exception("macOS clipboard error for video")
            raise
    else:
        raise RuntimeError(f"Unsupported platform: {platform}")
