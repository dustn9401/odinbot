import os
import time
import random
from ahk import AHK

sep = os.path.sep
L, U, R, D = range(4)
Dirs = {L: 'Left', U: 'Up', R: 'Right', D: 'Down'}
ahk = AHK(executable_path=f'C:{sep}Program Files{sep}AutoHotkey{sep}AutoHotkey.exe')

def down_jump():
    ahk.key_down('Down')
    ahk.key_press('Alt')
    ahk.key_release('Down')

def up_jump():
    key_press('PgDn')

def jump(dir = None):
    if dir is not None:
        ahk.key_down('Right' if dir else 'Left')
    ahk.key_press('Alt')
    if dir is not None:
        ahk.key_release('Right' if dir else 'Left')

def key_press(key, delay = random.uniform(0.15, 0.25)):
    ahk.key_down(key)
    time.sleep(delay)
    ahk.key_release(key)

def double_jump(is_right, delay = random.uniform(0.25, 0.35)):
    ahk.key_down('Right' if is_right else 'Left')
    jump()
    time.sleep(delay)
    jump()
    ahk.key_release('Right' if is_right else 'Left')

def dash(xDir):
    ahk.key_press(Dirs[xDir])
    ahk.key_press(Dirs[xDir])

def move_to(start, dest, callback):
    diff = dest - start

    if abs(diff.x) < 3 and abs(diff.y) < 3:
        print('arrived to dst')
        if callback is not None:
            callback()
        return

    if abs(diff.x) > 2:     #x축 우선 이동
        jump(diff.x > 0)
    if abs(diff.y) > 2:
        if abs(diff.y) > 10:
            up_jump() if diff.y < 0 else down_jump()
        else:
            jump() if diff.y < 0 else down_jump()