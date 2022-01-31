import win32gui
import win32api
import win32con
import win32ui
from ctypes import windll
import cv2
import numpy as np
import os
from PIL import ImageGrab
from InputManager import ahk
from ahk import keys
import asyncio


# def get_window_list():
#     def callback(hwnd, hwnd_list: list):
#         title = win32gui.GetWindowText(hwnd)
#         print(f'title={title}, hwnd={hwnd}')
#         if win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd) and title:
#             hwnd_list.append((title, hwnd))
#         return True
#     output = []
#     win32gui.EnumWindows(callback, output)
#     return output
#
#
# get_window_list()


test_cursor_pos = (250, 360)
hwnd = win32gui.FindWindow(None, 'ODIN  ')
# print(win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT))

# lParam = win32api.MAKELONG(*test_cursor_pos)
# win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
# win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)
# ahk_win = ahk.find_window(title='ODIN  '.encode('utf-8'))