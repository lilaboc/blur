import os.path
import random
import string
import tempfile
from io import BytesIO
from typing import List
from skimage.filters import gaussian
import math
import pyperclip
import win32clipboard
from PIL import ImageGrab, Image, ImageDraw, ImageEnhance, ImageOps
import re
from loguru import logger
import os
from moviepy.editor import *


# https://medium.com/geekculture/deforming-images-in-python-66e0d0dcb17f
class WaveDeformer:
    def transform(self, x, y):
        y = y + 10 * math.sin(x / 40)
        return x, y

    def transform_rectangle(self, x0, y0, x1, y1):
        return (*self.transform(x0, y0),
                *self.transform(x0, y1),
                *self.transform(x1, y1),
                *self.transform(x1, y0),
                )

    def getmesh(self, img):
        self.w, self.h = img.size
        gridspace = 20

        target_grid = []
        for x in range(0, self.w, gridspace):
            for y in range(0, self.h, gridspace):
                target_grid.append((x, y, x + gridspace, y + gridspace))

        source_grid = [self.transform_rectangle(*rect) for rect in target_grid]

        return [t for t in zip(target_grid, source_grid)]


def send_image_to_clipboard(im):
    output = BytesIO()
    im.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def process_image(im):
    try:
        width, height = im.size
        dots_per_pixel = 13
        # im = ImageOps.grayscale(im)
        # im = im.filter(ImageFilter.GaussianBlur(1))
        im = ImageEnhance.Contrast(im).enhance(0.5)
        im = ImageOps.deform(im, WaveDeformer())
        draw = ImageDraw.Draw(im)
        # for x in range(int(width / dots_per_pixel)):
        # for y in range(int(height / dots_per_pixel)):
        # draw.point((random.randint(0, width), random.randint(0, height)), fill="black")
        # draw.point((random.randint(0, width), random.randint(0, height)), fill="grey")
        # draw.point((random.randint(0, width), random.randint(0, height)), fill="red")
        # draw.point((random.randint(0, width), random.randint(0, height)), fill="white")
        for i in range(int(width / dots_per_pixel)):
            # draw.line((dots_per_pixel * i, 0, dots_per_pixel * i, height), fill='lightgray' if i % 2 == 0 else 'gray', width=2)
            draw.line((dots_per_pixel * i, 0, dots_per_pixel * i, height), fill='gray', width=2)
        for i in range(int(height / dots_per_pixel)):
            # draw.line((0, dots_per_pixel * i, width, dots_per_pixel * i), fill='lightgray' if i % 2 == 0 else 'gray', width=2)
            draw.line((0, dots_per_pixel * i, width, dots_per_pixel * i), fill='gray', width=2)
        send_image_to_clipboard(im)
    except Exception as exp:
        logger.exception('error')
        input()

def send_video_to_clipboard(path):
    cmd = f"powershell Set-Clipboard -Path '{path}'"
    print(cmd)
    os.system(cmd)


def _change(seg):
    for i in range(0, int(len(seg) / 3)):
        seg[i * 3], seg[i * 3 + 1] = seg[i * 3 + 1], seg[i * 3]
    return seg


def process_text1(text):
    # https://www.zhihu.com/question/20428571
    result = ""
    seg = []
    for i in text:
        if re.match(r'[\u4e00-\u9fff]+', i, re.I|re.M|re.S):
            seg.append(i)
        else:
            result += ''.join(_change(seg))
            seg = []
            result += i
    if len(seg) != 0:
        result += ''.join(_change(seg))
    pyperclip.copy(result)


def process_text(text):
    # https://github.com/pilipala233/MartianText/
    with open(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'martian.txt', 'r', encoding='utf-8') as f:
        str1 = f.readline().strip()
        hx = f.readline().strip()
        d = {}
        for i, o in zip(str1, hx):
            d[i] = o
        result = ''.join([d[i] if i in d else i for i in text])
        pyperclip.copy(result)


def process_video(filepath):
    # create a temporary directory and change working directory to
    # that directory
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    video = VideoFileClip(filepath)
    video_blurred = video.fl_image(_blur)
    txt_clip = VideoFileClip(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'warning.mp4')
    # txt_clip.resize(height=video_blurred.h, resample=Image.LANCZOS)
    # txt_clip.resize(height=video_blurred.h)
    video_out = concatenate_videoclips([txt_clip, video_blurred, txt_clip], method="compose")
    # video_out = CompositeVideoClip([video_blurred, txt_clip])
    # video_out = CompositeVideoClip([txt_clip, video_blurred])
    filename, file_extension = os.path.splitext(os.path.basename(filepath))
    output_path = os.path.join(temp_dir, filename + "_blurred" + file_extension)
    video_out.write_videofile(output_path, threads=2)
    send_video_to_clipboard(output_path)

# copy video file into clipboard using winclipboard32

def _blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian(image.astype(float), sigma=2)

def main():
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        process_image(im)
    elif isinstance(im, List) and isinstance(im[0], str) and os.path.exists(im[0]):
        filepath = im[0]
        filename, file_extension = os.path.splitext(filepath)
        try:
            if file_extension in ['.mp4', '.avi']:
                process_video(filepath)
            else:
                im = Image.open(filepath)
                process_image(im)
        except Exception as exp:
            logger.exception('error')
            input()
    else:
        random.choice([process_text, process_text1])(pyperclip.paste())
        # process_text(pyperclip.paste())


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



if __name__ == '__main__':
    # process_text1("没有镜头感画质不好看怎么办?(专业摄像师上门拍摄，1天至少出片60条")
    main()