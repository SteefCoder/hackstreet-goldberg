import pyautogui as pg
import os
import time
import qrcode
import json
import pathlib
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from components.mail.mail import Sender, Browser

def generate_qr(text):
    qr = qrcode.QRCode(border=0)
    qr.add_data(text)
    qr.make(fit=True)
    
    matrix = [[1 if cell else 0 for cell in  row] for row in qr.get_matrix()]
    
    with open("components/mcserver/world/scripts/shared/qr.json", "w") as f:
        json.dump(matrix, f)


#name = open("received.txt").read().strip()
name = sys.argv[1]
generate_qr("http://172.16.0.47?text=" + name)
# generate_qr("abc")
os.system('wmctrl -a "Minecraft* 1.21.11"')
pg.sleep(1)
pg.click(950, 600)
pg.sleep(1)
pg.click(447, 239)

pg.sleep(3)

pg.hotkey("f1")
pg.sleep(0.2)
pg.typewrite("t")
pg.sleep(0.2)
pg.hotkey("backspace")
pg.typewrite("/player bob spawn")
pg.hotkey("enter")

#pg.typewrite("t")
#pg.typewrite("/fill 20 -61 81 50 -61 121 minecraft:grass_block")
#pg.hotkey("enter")

pg.sleep(1)

pg.typewrite("t")
pg.sleep(0.5)
pg.hotkey("backspace")
pg.typewrite("/script in qrcode invoke create_qr")
pg.hotkey("enter")


p =pathlib.Path("components/mcserver/world/scripts/shared/baz.txt")
while not p.exists():
    time.sleep(0.3)

os.system("rm components/mcserver/world/scripts/shared/baz.txt")
time.sleep(0.2)
os.system("scrot -e 'xclip -selection clipboard -t image/png -i $f'")

time.sleep(0.1)

s = Sender(Browser())
s.send("lianbitterbal@gmail.com", None)
