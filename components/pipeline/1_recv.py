import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from components.mail.mail import Browser, Receiver


def callback(message):
    print(message)


with Browser() as gmail:
    recv = Receiver(gmail)
    recv.receive(callback, image=True, immediate=True)
