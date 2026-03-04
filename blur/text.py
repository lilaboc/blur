import random
from pathlib import Path
import pyperclip


def _swap_adjacent_chars(chars):
    """交换列表中相邻的字符（步长为2）"""
    chars = chars.copy()  # 避免修改原列表
    for i in range(0, len(chars) - 1, 2):
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return chars


def scramble_chinese_text(text, probability=0.5):
    """
    对文本中的中文字符进行相邻字符交换

    Args:
        text: 输入文本
        probability: 交换概率，0-1之间，默认1.0（全部交换）

    Returns:
        处理后的文本
    """
    result_parts = []
    chinese_chars = []

    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            chinese_chars.append(char)
        else:
            if chinese_chars:
                if random.random() < probability:
                    result_parts.append(''.join(_swap_adjacent_chars(chinese_chars)))
                else:
                    result_parts.append(''.join(chinese_chars))
                chinese_chars = []
            result_parts.append(char)

    # 处理剩余的中文字符
    if chinese_chars:
        if random.random() < probability:
            result_parts.append(''.join(_swap_adjacent_chars(chinese_chars)))
        else:
            result_parts.append(''.join(chinese_chars))

    result = ''.join(result_parts)
    pyperclip.copy(result)
    return result


def translate_with_martian(text):
    """
    使用火星文映射表翻译文本

    Args:
        text: 输入文本

    Returns:
        翻译后的文本
    """
    martian_file = Path(__file__).parent / 'martian.txt'

    with open(martian_file, 'r', encoding='utf-8') as f:
        original = f.readline().strip()
        translated = f.readline().strip()
        mapping = {orig: trans for orig, trans in zip(original, translated)}

    result = ''.join(mapping.get(char, char) for char in text)
    pyperclip.copy(result)
    return result
