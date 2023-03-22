from io import BytesIO
import win32clipboard
from PIL import ImageGrab, Image, ImageDraw, ImageFilter
import random
def send_to_clipboard(im):
    output = BytesIO()
    im.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def main():
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        try:
            width, height = im.size
            dots_per_pixel = 4
            im = im.filter(ImageFilter.GaussianBlur(1))
            draw = ImageDraw.Draw(im)
            for x in range(int(width / dots_per_pixel)):
                for y in range(int(height / dots_per_pixel)):
                    draw.point((random.randint(0, width), random.randint(0, height)), fill="grey")
            send_to_clipboard(im)
        except Exception as exp:
            print(exp)
            input()
    else:
        print('not an image')
        input()


if __name__ == '__main__':
    main()
