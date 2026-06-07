import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from components.mail.mail import Browser, Receiver
from components.desmos.encoder import DesmosEncoder


def caesar(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def callback(message):
    decoded = caesar(message, -3)
    DesmosEncoder(firefox, decoded).encode()


with Browser() as firefox:
    recv = Receiver(firefox)
    recv.receive(callback, image=False, immediate=True)
