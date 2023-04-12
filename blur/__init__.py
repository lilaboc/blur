import os.path
import random
from io import BytesIO
from typing import List

import math
import pyperclip
import win32clipboard
from PIL import ImageGrab, Image, ImageDraw, ImageEnhance, ImageOps
import re


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


def send_to_clipboard(im):
    output = BytesIO()
    im.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def process(im):
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

        send_to_clipboard(im)
    except Exception as exp:
        print(exp)
        input()


def process_text1(text):
    # https://www.zhihu.com/question/20428571
    if len(text) <= 2:
        return text
    pattern = '([A-Za-z]+|的)'
    result = text[:2]
    for i in re.split(pattern, text[2:], re.I|re.M|re.S):
        if re.match(pattern, i):
            result += i
        else:
            it = iter(i)
            for x in it:
                try:
                    result += next(it) + x
                except StopIteration:
                    result += x
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


def main():
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        process(im)
    elif isinstance(im, List) and isinstance(im[0], str) and os.path.exists(im[0]):
        try:
            im = Image.open(im[0])
            process(im)
        except Exception as exp:
            print(exp)
            input()
    else:
        random.choice([process_text, process_text1])(pyperclip.paste())
        # process_text(pyperclip.paste())


if __name__ == '__main__':
    main()


