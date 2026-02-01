from io import BytesIO
from typing import List
from PIL import ImageGrab, Image, ImageDraw, ImageEnhance, ImageOps
from skimage.filters import gaussian
import math
from loguru import logger
from blur.clipboard import send_image_to_clipboard


class WaveDeformer:
    def transform(self, x, y):
        y = y + 10 * math.sin(x / 40)
        return x, y

    def transform_rectangle(self, x0, y0, x1, y1):
        return (
            *self.transform(x0, y0),
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


def process_image(im):
    try:
        width, height = im.size
        dots_per_pixel = 13
        im = ImageEnhance.Contrast(im).enhance(0.5)
        im = ImageOps.deform(im, WaveDeformer())
        draw = ImageDraw.Draw(im)
        for i in range(int(width / dots_per_pixel)):
            draw.line(
                (dots_per_pixel * i, 0, dots_per_pixel * i, height),
                fill="gray",
                width=2,
            )
        for i in range(int(height / dots_per_pixel)):
            draw.line(
                (0, dots_per_pixel * i, width, dots_per_pixel * i), fill="gray", width=2
            )
        send_image_to_clipboard(im)
    except Exception as exp:
        logger.exception("error")
        input()


def _blur(image):
    """Returns a blurred (radius=2 pixels) version of the image"""
    return gaussian(image.astype(float), sigma=1)
