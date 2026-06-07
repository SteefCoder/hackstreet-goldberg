import pyautogui as pg
import os
import time
import qrcode
import json
import pathlib


def generate_qr(text):
    qr = qrcode.QRCode(border=0)
    qr.add_data(text)
    qr.make(fit=True)
    
    matrix = [[1 if cell else 0 for cell in  row] for row in qr.get_matrix()]
    
    with open("components/mcserver/world/scripts/shared/qr.json", "w") as f:
        json.dump(matrix, f)

generate_qr("http://172.16.0.47?text=" + "Hello, World")
# generate_qr("abc")
os.system('wmctrl -a "Minecraft* 1.21.11"')
time.sleep(0.3)
pg.mouseDown(447, 239)

time.sleep(3)

pg.typewrite("t")
time.sleep(0.2)
pg.typewrite("/player bob spawn")
pg.hotkey("enter")

#pg.typewrite("t")
#pg.typewrite("/fill 20 -61 81 50 -61 121 minecraft:grass_block")
#pg.hotkey("enter")

time.sleep(1)

pg.typewrite("t")
time.sleep(1)
pg.typewrite("/script in qrcode invoke create_qr")
pg.hotkey("enter")


pg.hotkey("f1")

p =pathlib.Path("components/mcserver/world/scripts/shared/baz.txt")
while not p.exists():
    time.sleep(0.3)

p.unlink()

im = pg.screenshot()
im.save('components/launch-minecraft/im.png')

pg.hotkey("alt", "tab")
