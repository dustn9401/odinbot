import math
import win32api
import win32gui
import cv2
import numpy as np

L, U, R, D = range(4)

def getWindowList():
    def callback(hwnd, hwnd_list: list):
        title = win32gui.GetWindowText(hwnd)
        if win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and title:
            hwnd_list.append((title, hwnd))
        return True
    output = []
    win32gui.EnumWindows(callback, output)
    return output

def ImageSearch(target, where, accuracy = 0.8):
    h, w, c = target.shape
    res = cv2.matchTemplate(where, target, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    #print(f'ImageSearch Accuracy: {max_val}')
    return None if max_val < accuracy else Rect(*max_loc, w, h)

def GetRuneAnswer():
    return ['Left', 'Up', 'Right', 'Down']

class MovePump:
    def __init__(self):
        self.done = False

class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.magnitude = math.sqrt(pow(self.x, 2) + pow(self.y, 2))

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __truediv__(self, other):
        if type(other) is int:
            return Vector2(self.x // other, self.y // other)
        elif type(other) is Vector2:
            return Vector2(self.x // other.x, self.y // other.y)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __floordiv__(self, other):
        if type(other) in [float, int]:
            return Vector2(self.x / other, self.y / other)
        elif type(other) is Vector2:
            return Vector2(self.x / other.x, self.y / other.y)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __mul__(self, other):
        if type(other) in [float, int]:
            return Vector2(self.x * other, self.y * other)
        elif type(other) is Vector2:
            return Vector2(self.x * other.x, self.y * other.y)
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __str__(self):
        return f'x: {self.x}, y: {self.y}'

    @staticmethod
    def Distance(a, b):
        return math.sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2))

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.min = Vector2(x, y)
        self.max = Vector2(x + w, y + h)
        self.extents = Vector2(w // 2, h // 2)
        self.center = self.min + self.extents

    def Contains(self, pt):
        return self.min.x <= pt.x and self.min.y <= pt.y and self.max.x >= pt.x and self.max.y >= pt.y

    def Intersects(self, rect):
        return not(rect.max.x < self.min.x or rect.max.y < self.min.y or self.max.x < rect.min.x or self.max.y < rect.min.y)

    def __str__(self):
        return f'x: {self.x}, y: {self.y}, w: {self.w}, h: {self.h}'

def get_shape(contour):
    shape = "unidentified"
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    if len(approx) == 3:
        shape = "triangle"
    elif len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        ar = w / float(h)
        shape = "square" if 0.95 <= ar <= 1.05 else "rectangle"
    elif len(approx) == 5:
        shape = "pentagon"
    elif cv2.isContourConvex(approx):
        shape = "circle"
    return shape


def get_rects(screen, is_debug=False):
    gray_screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(gray_screen, 127, 255, 0)
    cont, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for c in cont:
        if get_shape(c) == 'rectangle':
            rects.append(cv2.boundingRect(c))
    # rects = [cv2.boundingRect(c) for c in list(filter(lambda x: get_shape(x) == 'rectangle', cont))]

    if is_debug:
        for r in rects:
            cv2.rectangle(screen, (r[0], r[1]), (r[2] + r[0], r[3] + r[1]), (0, 255, 0), 1)
        cv2.imshow('screen', screen)
        cv2.imshow('gray, thresh', np.hstack((gray_screen, thresh)))
        cv2.waitKey(1)

    return rects

def get_circles(screen, is_debug=False):
    gray_screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(gray_screen, 220, 255, 0)
    cont, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for c in cont:
        if get_shape(c) == 'circle':
            (x, y), r = cv2.minEnclosingCircle(c)
            if 30 < r < 50:
                rects.append(((int(x), int(y)), int(r)))

    # if is_debug:
    #     for c in rects:
    #         cv2.circle(screen, *c, (0, 255, 0), 1)
    #     cv2.imshow('screen', screen)
    #     cv2.imshow('gray, thresh', np.hstack((gray_screen, thresh)))
    #     cv2.waitKey(1)

    return rects
