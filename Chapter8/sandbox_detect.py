from ctypes import byref, c_uint, c_ulong, sizeof, Structure, windll
import random
import sys
import time 
import win32api

class LASTIUTINFO(Structure):
    fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]

def get_last_input():
    structure_lastinputinfo = LASTIUTINFO()
    structure_lastinputinfo.cbSize = sizeof(LASTIUTINFO)

    windll.user32.GetLastInputInfo(byref(structure_lastinputinfo))
    run_time = windll.kernel32.GetTickCount()
    elapsed = run_time - structure_lastinputinfo.dwTime
    print(f"[*] It's been {elapsed} milliseconds since the last event.")
    return elapsed

class Detector:
    def __init__(self):
        self.double_click = 0
        self.keystrokes = 0
        self.mouse_clicks = 0

    def get_key_press(self):
        for i in range(0, 0xff):
            state = win32api.GetAsyncKeyState(i)
            if state & 0x0001:
                if i == 0x1:
                    self.mouse_clicks += 1
                    return time.time()
                elif i > 32 and i < 127:
                    self.keystrokes += 1
        return None
     