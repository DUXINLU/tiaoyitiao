# coding=UTF-8
from PIL import Image, ImageFilter
from pylab import *
import os


def get_range(drct):
    drct_queue = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    i = drct_queue.index(drct)

    pre = drct_queue[(i + 8 - 1) % 8]
    next = drct_queue[(i + 8 + 1) % 8]

    return (pre, next)


def get_next_pst(mtrx, x, y, path):
    min = 256
    next = (0, 0)
    pre_drct = (0, 0)

    if len(path) < 2:
        pre_drct = (1, 0)
    else:
        pre_drct = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])

    p, n = get_range(pre_drct)

    if mtrx[x + p[0]][y + p[1]] < min and (x + p[0], y + p[1]) not in path:
        min = mtrx[x + p[0]][y + p[1]]
        next = (x + p[0], y + p[1])

    if mtrx[x + pre_drct[0]][y + pre_drct[1]] < min and (x + pre_drct[0], y + pre_drct[1]) not in path:
        min = mtrx[x + pre_drct[0]][y + pre_drct[1]]
        next = (x + pre_drct[0], y + pre_drct[1])

    if mtrx[x + n[0]][y + n[1]] < min and (x + n[0], y + n[1]) not in path:
        min = mtrx[x + n[0]][y + n[1]]
        next = (x + n[0], y + n[1])

    path.append(next)
    return next


def is_head(img_mtrx, x, y):
    mtrx = img_mtrx
    # path = [(921, 333)]
    path = [(x, y)]
    drct = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    while len(drct) != 0:
        x, y = path[-1]
        next = get_next_pst(mtrx, x, y, path)
        if (next[0] - x, next[1] - y) in drct:
            drct.remove((next[0] - x, next[1] - y))

    x_min = 1080
    x_max = -1
    y_min = 1080
    y_max = -1

    for _ in path:
        if _[0] < x_min:
            x_min = _[0]
        if _[0] > x_max:
            x_max = _[0]
        if _[1] < y_min:
            y_min = _[1]
        if _[1] > y_max:
            y_max = _[1]

    x_range = x_max - x_min
    y_range = y_max - y_min

    if x_range in [58, 59, 60] and y_range in [58, 59, 60]:
        return ((x_min + x_max) / 2, (y_min + y_max) / 2)
    else:
        return (0, 0)


def is_equal_list(l1, l2):
    for _ in range(len(l1)):
        if l1[_] != l2[_]:
            return False

    return True


def get_head_pst(img_mtrx):
    mtrx = img_mtrx

    for row in range(760, 1090):
        for col in range(0, 1080):
            if is_equal_list(mtrx[row][col:col + 6], [0, 0, 0, 0, 0, 0]):
                head_pst = is_head(mtrx, row, col)
                if head_pst == (0, 0):
                    continue
                else:
                    return head_pst
    return False


def get_dstc(img_mtrx):
    mtrx = img_mtrx
    head_pst = get_head_pst(mtrx)
    col_start = 0
    col_end = 0
    square_pst = (0, 0)

    if head_pst[1] < 540:
        for row in range(650, 1070):
            for col in range(head_pst[1] + 43, 1080):
                if mtrx[row][col] < 200:
                    col_start = col
                    break

            for col in range(1079, head_pst[1] + 43, -1):
                if mtrx[row][col] < 200:
                    col_end = col
                    square_pst = (row, (col_start + col_end) / 2)
                    print square_pst[1] - head_pst[1]
                    return square_pst[1] - head_pst[1]

    else:
        for row in range(650, 1070):
            for col in range(0, head_pst[1] - 43):
                if mtrx[row][col] < 200:
                    col_start = col
                    break

            for col in range(head_pst[1] - 43, 0, -1):
                if mtrx[row][col] < 200:
                    col_end = col
                    square_pst = (row, (col_start + col_end) / 2)
                    print head_pst[1] - square_pst[1]
                    return head_pst[1] - square_pst[1]


def convert_img():
    img = Image.open('autojump.png').convert('L')
    img_mtrx = np.array(img.filter(ImageFilter.CONTOUR))
    return img_mtrx


def get_img_from_device():
    os.system('adb shell screencap -p /sdcard/autojump.png')
    os.system('adb pull /sdcard/autojump.png .')


def press_screen(dstc):
    press_time = dstc * 1.55
    press_time = int(press_time)
    cmd = 'adb shell input swipe 320 410 320 410 ' + str(press_time)
    os.system(cmd)


if __name__ == '__main__':
    get_img_from_device()
    dstc = get_dstc(convert_img())
    press_screen(dstc)
