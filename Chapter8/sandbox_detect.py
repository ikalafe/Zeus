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

