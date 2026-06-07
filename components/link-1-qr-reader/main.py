import cv2
import subprocess
import mss
from pynput import keyboard


keep_waiting = True

def on_press(key):
    global keep_waiting
    try:
        if key.char == 'p':  # or whatever key you want
            keep_waiting = False
            return False  # stops listener
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()


while keep_waiting:
    pass


print("Taking screenshot!")
with mss.MSS() as sct:
    outfile = sct.shot()
print(outfile)
# Get the image that contains the QR code
path = cv2.imread(outfile)

assert path is not None
text = cv2.QRCodeDetector().detectAndDecode(path)[0]

print(text)
subprocess.Popen(['xdg-open', text.strip()])
