import os
import re
import pyperclip


def _change(seg):
    for i in range(0, int(len(seg) / 3)):
        seg[i * 3], seg[i * 3 + 1] = seg[i * 3 + 1], seg[i * 3]
    return seg


def process_text1(text):
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
    with open(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'martian.txt', 'r', encoding='utf-8') as f:
        str1 = f.readline().strip()
        hx = f.readline().strip()
        d = {}
        for i, o in zip(str1, hx):
            d[i] = o
        result = ''.join([d[i] if i in d else i for i in text])
        pyperclip.copy(result)
