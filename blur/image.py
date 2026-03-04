import math
from typing import List

from PIL import Image, ImageDraw, ImageEnhance, ImageOps
from loguru import logger
from skimage.filters import gaussian

from blur.clipboard import send_image_to_clipboard


# 常量定义
WAVE_AMPLITUDE = 10
WAVE_FREQUENCY = 40
GRID_SPACE = 20
DOTS_PER_PIXEL = 13
CONTRAST_ENHANCEMENT = 0.5
GRID_COLOR = "gray"
GRID_WIDTH = 2
BLUR_SIGMA = 1


class WaveDeformer:
    """波浪变形器，对图像应用波浪效果"""

    def __init__(self, amplitude=WAVE_AMPLITUDE, frequency=WAVE_FREQUENCY, grid_space=GRID_SPACE):
        """
        Args:
            amplitude: 波浪幅度
            frequency: 波浪频率
            grid_space: 网格间距
        """
        self.amplitude = amplitude
        self.frequency = frequency
        self.grid_space = grid_space

    def transform(self, x, y):
        """变换单个坐标点"""
        y = y + self.amplitude * math.sin(x / self.frequency)
        return x, y

    def transform_rectangle(self, x0, y0, x1, y1):
        """变换矩形区域的四个角"""
        return (
            *self.transform(x0, y0),
            *self.transform(x0, y1),
            *self.transform(x1, y1),
            *self.transform(x1, y0),
        )

    def getmesh(self, img):
        """生成图像网格用于变形"""
        self.w, self.h = img.size

        target_grid = []
        for x in range(0, self.w, self.grid_space):
            for y in range(0, self.h, self.grid_space):
                target_grid.append((x, y, x + self.grid_space, y + self.grid_space))

        source_grid = [self.transform_rectangle(*rect) for rect in target_grid]

        return [t for t in zip(target_grid, source_grid)]


def apply_distortion_grid(image):
    """
    对图像应用波浪变形和网格线效果

    Args:
        image: PIL Image 对象

    Returns:
        处理后的 PIL Image 对象
    """
    try:
        width, height = image.size

        # 降低对比度
        image = ImageEnhance.Contrast(image).enhance(CONTRAST_ENHANCEMENT)

        # 应用波浪变形
        image = ImageOps.deform(image, WaveDeformer())

        # 绘制网格线
        draw = ImageDraw.Draw(image)

        # 垂直线
        for i in range(width // DOTS_PER_PIXEL):
            x = DOTS_PER_PIXEL * i
            draw.line((x, 0, x, height), fill=GRID_COLOR, width=GRID_WIDTH)

        # 水平线
        for i in range(height // DOTS_PER_PIXEL):
            y = DOTS_PER_PIXEL * i
            draw.line((0, y, width, y), fill=GRID_COLOR, width=GRID_WIDTH)

        send_image_to_clipboard(image)
        return image

    except Exception as exp:
        logger.exception("Failed to apply distortion grid to image")
        input()


# 保留向后兼容的别名
process_image = apply_distortion_grid


def _blur(image, sigma=BLUR_SIGMA):
    """
    对图像应用高斯模糊

    Args:
        image: 输入图像数组
        sigma: 高斯核的标准差

    Returns:
        模糊后的图像数组
    """
    return gaussian(image.astype(float), sigma=sigma)
