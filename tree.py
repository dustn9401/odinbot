import win32gui
import win32api
import win32con
import os
from ahk import AHK
import time

sep = os.path.sep
ahk = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')

while True:
    # print(ahk.mouse_position)
    # ahk.click(922, 604)
    # ahk.right_click(1130, 460)
    # time.sleep(0.3)

    ahk.right_click(1331,709)
    time.sleep(110)
    ahk.right_click(1133,368)
    time.sleep(35)
    