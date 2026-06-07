from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore
import colorama
import time
import random
import sys
import os
import glob
import pyautogui as pag
from PIL import ImageGrab
import cv2
import numpy as np


if sys.platform == 'darwin':
    CMD = Keys.COMMAND
else:
    CMD = Keys.CONTROL


colorama.init(autoreset=True)


class Browser:
    def __init__(self):
        if sys.platform == 'darwin':
            profiles_dir = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
        else:
            profiles_dir = os.path.expanduser("~/.mozilla/firefox/")
        profiles = glob.glob(os.path.join(profiles_dir, "*.default-release"))
        if not profiles:
            profiles = glob.glob(os.path.join(profiles_dir, "*.default"))
        if not profiles:
            print(Fore.RED + "No Firefox profile found.")
            sys.exit(1)

        options = Options()
        options.add_argument("-profile")
        options.add_argument(profiles[0])

        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.url = "https://mail.google.com/mail/u/0/#inbox"

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.driver.quit()


class Sender:
    def __init__(self, browser, typing_delay=0):
        self.browser = browser
        self.typing_delay = typing_delay
    
    def _pgauss(self, *args, **kwargs):
        return max(0, random.gauss(*args, **kwargs))

    def _send_keys_delay(self, field, str):
        for c in str:
            field.send_keys(c)
            delay = self._pgauss(self.typing_delay, 0.07)
            time.sleep(delay)  # in seconds!

    def send(self, recv, msg):
        self.browser.driver.get(self.browser.url)

        # create email button
        compose_button = self.browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[gh='cm']")))
        compose_button.click()

        # input the receiver email
        recipient_input = self.browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='To recipients']")))
        self._send_keys_delay(recipient_input, recv)
        self._send_keys_delay(recipient_input, Keys.RETURN)
        self._send_keys_delay(recipient_input, Keys.TAB)

        # input the subject
        subject_input = self.browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='Subject']")))
        self._send_keys_delay(subject_input, "Subject!")

        # input the message
        body_input = self.browser.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Message Body']")))
        body_input.click()
        if msg is None:
            # message is None -> we're sending from clipboard

            ActionChains(self.browser.driver).key_down(CMD).send_keys("v").key_up(CMD).perform()
            body_input.click()  # just in case?
        else:
            # we're sending plain text
            self._send_keys_delay(body_input, msg)

        # press enter to send message instead of locating the message button
        time.sleep(4)
        ActionChains(self.browser.driver).key_down(CMD).send_keys(Keys.RETURN).key_up(CMD).perform()

        # proprietary sleep
        time.sleep(20)


class Receiver:
    def __init__(self, browser):
        self.browser = browser
    
    def _get_mails(self):
        try:
            return self.browser.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.zA"))
            )
        except Exception:
            return 0
    
    def receive(self, callback, image=False, immediate=False):
        self.browser.driver.get("https://mail.google.com/mail/u/0/#inbox")

        mails = self._get_mails()
        num_mails = len(mails)

        while True:
            time.sleep(5)

            mails = self._get_mails()
            if len(mails) > num_mails or immediate:
                print(Fore.GREEN + f"New mail!. New count: {len(mails)}")

                # a new mail has entered the chat!
                last_mail = mails[0]
                mail_link = last_mail.find_element(By.CSS_SELECTOR, 'div[role="link"]')
                mail_link.click()

                if image:
                    # receiving an image
                    attach = self.browser.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "CToWUd")))[0]
                    # right click + save the image
                    ActionChains(self.browser.driver).context_click(attach).perform()
                    time.sleep(2)
                    pag.press("v")
                    time.sleep(2)
                    pag.press("enter")
                    time.sleep(1)
                    pag.press("enter")
                    time.sleep(1)
                    pag.press("enter")

                    pil_img = ImageGrab.grabclipboard()
                    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    detector = cv2.QRCodeDetector()
                    text, points, _ = detector.detectAndDecode(cv2_img)
                    callback(text)
                else:
                    # receiving text, so find the correct "div"
                    divs = self.browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[dir='ltr']")))
                    for i, div in enumerate(divs):
                        print(div.text)
                        # find the one that actually has text
                        if stripped := div.text.strip():
                            callback(stripped)
                            break
                break
        
            print(Fore.BLUE + f"No new mails. Current count: {num_mails}")

        time.sleep(10000)
