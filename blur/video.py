import os
import tempfile
from moviepy import VideoFileClip
from loguru import logger
from blur.image import _blur


def send_video_to_clipboard(path):
    cmd = f"powershell Set-Clipboard -Path '{path}'"
    print(cmd)
    os.system(cmd)


def process_video(filepath):
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    video = VideoFileClip(filepath)
    video_blurred = video.fl_image(_blur)
    video_out = video_blurred
    filename, file_extension = os.path.splitext(os.path.basename(filepath))
    output_path = os.path.join(temp_dir, filename + "_blurred" + file_extension)
    video_out.write_videofile(output_path, threads=2)
    send_video_to_clipboard(output_path)
