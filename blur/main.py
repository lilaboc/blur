import random
from pathlib import Path
from typing import List
import pyperclip
from PIL import ImageGrab, Image
from loguru import logger
from moviepy import VideoFileClip, TextClip
from blur.image import process_image
from blur.text import process_text, process_text1
from blur.video import process_video


def main():
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        process_image(im)
    elif isinstance(im, List) and isinstance(im[0], str) and Path(im[0]).exists():
        filepath = Path(im[0])
        try:
            if filepath.suffix in ['.mp4', '.avi']:
                process_video(str(filepath))
            else:
                im = Image.open(str(filepath))
                process_image(im)
        except Exception as exp:
            logger.exception('error')
            input()
    else:
        random.choice([process_text, process_text1])(pyperclip.paste())


def test():
    from moviepy.config import change_settings
    change_settings({"IMAGEMAGICK_BINARY": r"C:\Users\stern\scoop\apps\imagemagick\current\magick.EXE"})
    txt_clip = (TextClip("看不懂这是什么", fontsize=70, color='white', font='华文宋体')
                .set_position('center')
                .set_duration(2))
    txt_clip.write_videofile("warning.mp4", fps=24)


def fonts():
    from moviepy.config import change_settings
    change_settings({"IMAGEMAGICK_BINARY": r"C:\Users\stern\scoop\apps\imagemagick\current\magick.EXE"})
    for i in TextClip.list('font'):
        print(i)
