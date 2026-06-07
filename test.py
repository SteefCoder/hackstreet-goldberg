from components.mail.mail import Browser, Sender, Receiver
from colorama import Fore


def callback(received):
    print(Fore.GREEN + received + Fore.RESET)


with Browser() as gmail:
    # sender = Sender(gmail, typing_delay=0)
    # sender.send(recv="richardkevinson279@gmail.com", msg=None)
    # sender.send(recv="lianbitterbal@gmail.com", msg=None)
    receiver = Receiver(gmail)
    receiver.receive(callback, image=True, immediate=True)
