from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from .commons import *


class DesmosEncoder:
    def __init__(self, browser, msg):
        self.driver = browser.driver
        self.msg = msg
        self.frequences = []
    
    def encode(self):
        self.driver.get("https://www.desmos.com/calculator/")
        self.msg = self.msg
        self.msg = "@" + "".join(char + "|" for char in self.msg) + "!" * 5
        print(self.msg)
        frequencies = [char_to_freq[char.lower()] for char in self.msg]

        # write the piecewise function
        func_text = "f(x)={"
        duration = 10
        tot_duration = len(frequencies) * duration
        for i, freq in enumerate(frequencies):
            min_range = i * duration
            max_range = (i + 1) * duration
            func_text += f"{min_range}<=x<={max_range}: {freq}, "
        func_text = func_text.removesuffix(", ") + "}"

        ActionChains(self.driver).send_keys(func_text).send_keys(Keys.RETURN).perform()

        # write the animated time parameter p
        ActionChains(self.driver).send_keys("p=0").send_keys(Keys.RETURN).perform()
        time.sleep(1)
        ActionChains(self.driver).key_down(Keys.SHIFT).perform()
        for _ in range(6):
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        ActionChains(self.driver).key_up(Keys.SHIFT).perform()
        ActionChains(self.driver).send_keys("0", Keys.TAB, tot_duration, Keys.RETURN, Keys.RETURN).perform()

        # tone(f(p))
        ActionChains(self.driver).send_keys("tone(f(p))").perform()
        time.sleep(0.5)
        option_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "dcg-slider-menu-opener")))
        option_button.click()
        time.sleep(0.5)
        slower_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "dcg-action-slower")))
        time.sleep(0.5)
        for _ in range(7):
            slower_button.click()

        # play once button
        play_once = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Play once"')))
        play_once.click()    

        # mute button
        mute_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "dcg-global-mute-button"))
        )
        mute_button.click()

        # shift tab back to play the fucking sound
        ActionChains(self.driver).key_down(Keys.SHIFT).perform()
        for _ in range(3):
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        ActionChains(self.driver).key_up(Keys.SHIFT).perform()
        ActionChains(self.driver).send_keys(Keys.RETURN).perform()

        # zoom out
        zoom_out = WebDriverWait(self.driver,10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Zoom Out']"))
        )
        for _ in range(7):
            zoom_out.click()
            time.sleep(0.1)

        time.sleep(10000000)