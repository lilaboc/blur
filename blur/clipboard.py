import sys
import os
import subprocess
import tempfile
from io import BytesIO
from PIL import Image
from loguru import logger


def _check_command(cmd):
    """Check if a command is available in the system."""
    try:
        subprocess.run(["which", cmd], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def send_image_to_clipboard(im):
    """Send an image to the clipboard in a cross-platform way."""
    if sys.platform == "win32":
        try:
            import win32clipboard

            output = BytesIO()
            im.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.exception("Windows clipboard error")
            raise
    elif sys.platform == "linux":
        if _check_command("wl-copy"):
            try:
                output = BytesIO()
                im.save(output, format="PNG")
                data = output.getvalue()
                output.close()
                subprocess.run(
                    ["wl-copy", "--type", "image/png"], input=data, check=True
                )
            except Exception as e:
                logger.exception("wl-copy error")
                raise
        elif _check_command("xclip"):
            try:
                output = BytesIO()
                im.save(output, format="PNG")
                data = output.getvalue()
                output.close()
                subprocess.run(
                    ["xclip", "-selection", "clipboard", "-t", "image/png"],
                    input=data,
                    check=True,
                )
            except Exception as e:
                logger.exception("xclip error")
                raise
        else:
            raise RuntimeError(
                "No clipboard tool found. Install wl-clipboard (Wayland) or xclip (X11)"
            )
    elif sys.platform == "darwin":
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
            im.save(tmp_path, format="PNG")
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to POSIX file "{tmp_path}"'],
                check=True,
            )
            os.unlink(tmp_path)
        except Exception as e:
            logger.exception("macOS clipboard error")
            raise
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")


def send_video_to_clipboard(path):
    """Send a video file path to the clipboard in a cross-platform way."""
    if sys.platform == "win32":
        cmd = f"powershell Set-Clipboard -Path '{path}'"
        os.system(cmd)
    elif sys.platform == "linux":
        if _check_command("wl-copy"):
            try:
                subprocess.run(["wl-copy", "--type", "text/uri-list", path], check=True)
            except Exception as e:
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
                        "text/uri-list",
                        "-i",
                        path,
                    ],
                    check=True,
                )
            except Exception as e:
                logger.exception("xclip error for video")
                raise
        else:
            raise RuntimeError(
                "No clipboard tool found. Install wl-clipboard (Wayland) or xclip (X11)"
            )
    elif sys.platform == "darwin":
        try:
            subprocess.run(
                ["osascript", "-e", f'set the clipboard to POSIX file "{path}"'],
                check=True,
            )
        except Exception as e:
            logger.exception("macOS clipboard error")
            raise
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")
