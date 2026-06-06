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


colorama.init(autoreset=True)


class Browser:
    def __init__(self):
        profiles_dir = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/")
        profiles = glob.glob(os.path.join(profiles_dir, "*.default-release"))
        if not profiles:
            profiles = glob.glob(os.path.join(profiles_dir, "*.default"))
        if not profiles:
            print("❌ No Firefox profile found.")
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
        self._send_keys_delay(body_input, msg)

        # press enter to send message instead of locating the message button
        ActionChains(self.browser.driver).key_down(Keys.CONTROL).send_keys(Keys.RETURN).key_up(Keys.CONTROL).perform()
        ActionChains(self.browser.driver).key_down(Keys.COMMAND).send_keys(Keys.RETURN).key_up(Keys.COMMAND).perform()

        # proprietary sleep
        time.sleep(5)


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
    
    def receive(self, callback):
        self.browser.driver.get("https://mail.google.com/mail/u/0/#inbox")

        mails = self._get_mails()
        num_mails = len(mails)

        while True:
            time.sleep(5)

            mails = self._get_mails()
            if len(mails) > num_mails:
                # a new mail has entered the chat!
                last_mail = mails[0]
                mail_link = last_mail.find_element(By.CSS_SELECTOR, 'div[role="link"]')
                mail_link.click()

                divs = self.browser.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[dir='ltr']")))
                for i, div in enumerate(divs):
                    # find the one that actually has text
                    if stripped := div.text.strip():
                        callback(stripped)
                        break
                break
        
            print(Fore.BLUE + f"No new mails. Current count: {num_mails}")

        time.sleep(6000)
