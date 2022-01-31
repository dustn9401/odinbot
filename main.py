import random

import win32gui
import win32api
import win32con
import win32ui
from ctypes import windll
import cv2
import numpy as np
import os
from PIL import ImageGrab
from Utils import *
from InputManager import ahk
from ahk import keys
import asyncio
import datetime


sep = os.path.sep
log_level = 1

delta_time = 0.1
state_check_delta_time = 1
state_check_duration = 3

HPMinPoint = (90, 50)
HPRedMin = 150

# hunt setting
hunt_type = 0
prison_level = 5
start_in_town = True


# common

quit_popup_button_pos = (1241, 55)

# go hunt
OpenMapKey = 'm'
FindMapButtonPos = (37, 104)
FavoriteListButtonPos = (254, 160)
FavoriteListTopItemPos = (187, 210)
FastMoveButtonPos = (1190, 675)

FastMoveConfirmButtonPos = (705, 448)
AutoHuntKey = 'g'

# go jail
EliteDungeonTabButtonPos = (243, 104)
PrisonDungeonButtonPos = (1121, 383)
PrisonDungeonLevelButtonPositions = [(150, 115 + y * 60) for y in range(7)]

# dungeon common
GoDungeonButtonPos = (1132, 663)

GoHomeKey = 'h'
GoHomeOkButtonPos = (708, 449)

# shop
GoShopKey = '4'
HPPotionBuyButtonPos = (149, 167)
BuyMaxButtonPos = (742, 427)
BuyConfirmButtonPos = (711, 526)

CompareHistDiffThreshold = 0.6
CompareHistSameThreshold = 0.95

# skill
SkillAreaStartPoint = (940, 480)
SubSkillAreaStartPoint = (814, 369)


class Player:
    WindowTitle = 'ODIN  '
    Width = 1280
    Height = 720

    def __init__(self):
        # 창 찾고 바운드 저장
        self.hwnd = win32gui.FindWindow(None, Player.WindowTitle)
        self.x = -7
        self.y = 0
        win32gui.MoveWindow(self.hwnd, self.x, self.y, Player.Width, Player.Height, True)
        win32gui.SetForegroundWindow(self.hwnd)
        self.w = Player.Width
        self.h = Player.Height
        self.hwndDC = win32gui.GetWindowDC(self.hwnd)
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)
        self.captureDC = self.mfcDC.CreateCompatibleDC()
        self.captureBitMap = win32ui.CreateBitmap()
        self.captureBitMap.CreateCompatibleBitmap(self.mfcDC, self.w, self.h)
        self.captureDC.SelectObject(self.captureBitMap)
        self.ahk_win = ahk.find_window(title=Player.WindowTitle.encode('utf-8'))

        self.hp_low_frame_count = 0

    def __del__(self):
        self.captureDC.DeleteDC()
        self.mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)
        win32gui.DeleteObject(self.captureBitMap.GetHandle())
        cv2.destroyAllWindows()

    def grab_screen(self):
        self.captureDC.BitBlt((0, 0), (self.w, self.h), self.mfcDC, (0, 0), win32con.SRCCOPY)
        signed_ints_array = self.captureBitMap.GetBitmapBits(True)
        ret = np.frombuffer(signed_ints_array, dtype='uint8')
        ret.shape = (self.h, self.w, 4)
        return ret

    async def update(self):
        if start_in_town:
            await self.go_hunt()

        while True:
            screen = self.grab_screen()
            await self.check_hp(screen)
            await self.check_sub_skill(screen)

            await asyncio.sleep(0.1)

    async def check_sub_skill(self, screen):
        skill_area = screen[SubSkillAreaStartPoint[1]:, SubSkillAreaStartPoint[0]:]
        mask = 255 * np.ones(skill_area.shape[:2], np.uint8)
        mask[120:, 120:] = 0
        masked_skill_area = cv2.bitwise_and(skill_area, skill_area, mask=mask)
        circles = get_circles(masked_skill_area, log_level)
        if len(circles) > 0:
            (x, y), r = circles[0]
            await self.send_key_press_async(keys.KEYS.LEFT_SHIFT)

    async def check_hp(self, screen):
        b, g, r, a = screen[HPMinPoint[1], HPMinPoint[0]]
        if r < HPRedMin:
            self.hp_low_frame_count += 1
            Player.log(f'hp low detect!! red value={r} count={self.hp_low_frame_count}')
            if self.hp_low_frame_count > 10:
                Player.log(f'go home...', 1)
                await self.buy_potion()
        else:
            self.hp_low_frame_count = 0

    async def buy_potion(self):
        await self.go_home()

        self.send_key_press(GoShopKey)
        try:
            await asyncio.wait_for(self.wait_state_changed(self.grab_screen()), timeout=20)
        except asyncio.TimeoutError:
            Player.log('go shop timeout!', 1)

        await self.send_click_async(*HPPotionBuyButtonPos)
        await self.send_click_async(*BuyMaxButtonPos)
        await self.send_click_async(*BuyConfirmButtonPos)
        await self.send_click_async(*quit_popup_button_pos)

        await self.go_hunt()

    async def go_home(self):
        await self.send_key_press_async(GoHomeKey)
        await self.send_click_async(*GoHomeOkButtonPos, 8)

    async def go_hunt(self):
        if hunt_type == 0:
            await self.go_favorite()
        elif hunt_type == 1:
            await self.go_jail()
        else:
            raise ValueError(f'hunt_type={hunt_type}')

        await self.send_key_press_async(AutoHuntKey)

    async def go_favorite(self):
        await self.send_key_press_async(OpenMapKey, 1)
        await self.send_click_async(*FindMapButtonPos, rand_offset_x=3, rand_offset_y=1)
        await self.send_click_async(*FavoriteListButtonPos, rand_offset_x=3, rand_offset_y=1)
        await self.send_click_async(*FavoriteListTopItemPos, 1, rand_offset_y=1)
        await self.send_click_async(*FastMoveButtonPos, 1, rand_offset_y=1)
        await self.send_click_async(*FastMoveConfirmButtonPos, 8)

        await asyncio.sleep(random.uniform(35, 40))
        # try:
        #     await asyncio.wait_for(self.wait_move(), timeout=60)
        # except asyncio.TimeoutError:
        #     Player.log('wait_move timeout', 2)

    async def go_jail(self):
        await self.send_key_press_async('c', 1)
        await self.send_click_async(*EliteDungeonTabButtonPos)
        await self.send_click_async(*PrisonDungeonButtonPos, 1)
        await self.send_click_async(*PrisonDungeonLevelButtonPositions[prison_level - 1], rand_offset_y=1)
        await self.send_click_async(*GoDungeonButtonPos)
        await Player.random_sleep(10, 12)
        press_duration = random.randint(10, 15)
        self.ahk_win.send('w', press_duration=press_duration * 1000)
        await asyncio.sleep(press_duration)

    async def send_key_press_async(self, key_code, after_delay=0.5):
        self.send_key_press(key_code)
        await asyncio.sleep(after_delay + random.uniform(0, 0.1))

    def send_key_press(self, key_code):
        self.ahk_win.send(key_code)

    async def send_click_async(self, x, y, after_delay=0.5, rand_offset_x=10, rand_offset_y=10):
        self.send_click(x, y, rand_offset_x=10, rand_offset_y=10)
        await asyncio.sleep(after_delay + random.uniform(0, 0.1))

    def send_click(self, x, y, rand_offset_x=10, rand_offset_y=10):
        screen_position_x = self.x + x + random.uniform(-rand_offset_x, rand_offset_x)
        screen_position_y = self.y + y + random.uniform(-rand_offset_y, rand_offset_y)
        self.ahk_win.activate()
        ahk.mouse_position = (screen_position_x, screen_position_y)
        ahk.click()

    async def wait_state_changed(self, start_screen):
        start_hist = cv2.calcHist([start_screen], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(start_hist, start_hist, 0, 1, cv2.NORM_MINMAX)
        break_timer = 0

        while True:
            await asyncio.sleep(state_check_delta_time)
            cur_hist = cv2.calcHist([self.grab_screen()], [0, 1], None, [180, 256], [0, 180, 0, 256])
            diff = cv2.compareHist(start_hist, cur_hist, cv2.HISTCMP_CORREL)
            Player.log(f'diff={diff}, break_timer={break_timer}')
            if diff < CompareHistDiffThreshold:
                break_timer += state_check_delta_time
                if break_timer > state_check_duration:
                    break
            else:
                Player.log(f'diff={diff}, reset timer')
                break_timer = 0

    async def wait_move(self):
        bef_hist = cv2.calcHist([self.grab_screen()], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(bef_hist, bef_hist, 0, 1, cv2.NORM_MINMAX)
        break_timer = 0

        while True:
            await asyncio.sleep(state_check_delta_time)
            cur_hist = cv2.calcHist([self.grab_screen()], [0, 1], None, [180, 256], [0, 180, 0, 256])
            diff = cv2.compareHist(bef_hist, cur_hist, cv2.HISTCMP_CORREL)
            if diff > CompareHistSameThreshold:
                Player.log(f'diff={diff}, break_timer={break_timer}')
                break_timer += state_check_delta_time
                if break_timer > state_check_duration:
                    break
            else:
                Player.log(f'diff={diff}, reset timer')
                break_timer = 0

            bef_hist = cur_hist
            cv2.normalize(bef_hist, bef_hist, 0, 1, cv2.NORM_MINMAX)

    @staticmethod
    def log(message, level=0):
        if log_level <= level:
            print(datetime.datetime.now(), message)

    @staticmethod
    async def random_sleep(min_value, max_value):
        await asyncio.sleep(random.uniform(min_value, max_value))


if __name__ == '__main__':
    player = Player()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(player.update())

