import os
import tempfile
from pathlib import Path
from moviepy import VideoFileClip
from loguru import logger
from blur.image import _blur
from blur.clipboard import send_video_to_clipboard


def process_video(filepath):
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    video = VideoFileClip(filepath)
    video_blurred = video.fl_image(_blur)
    video_out = video_blurred
    filepath_path = Path(filepath)
    output_path = Path(temp_dir) / f"{filepath_path.stem}_blurred{filepath_path.suffix}"
    video_out.write_videofile(str(output_path), threads=2)
    send_video_to_clipboard(str(output_path))
