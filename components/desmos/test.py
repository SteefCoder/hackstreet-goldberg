from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time


MORSE_TO_BINARY = {
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',    'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..',   'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',   'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-', 'R': '.-.',  'S': '...',  'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----','1': '.----','2': '..---','3': '...--',
    '4': '....-','5': '.....','6': '-....','7': '--...',
    '8': '---..','9': '----.'
}

def string_to_morse(str):
    unit = 0.5
    current_x = 0
    ret = r"f(x) = {"

    for char in str:
        char = char.upper()
        if char not in MORSE_TO_BINARY:
            continue

        dots = MORSE_TO_BINARY[char]
        for dot in dots:
            if dot == ".":
                ret += f"abs(x - {current_x + unit}) < {unit}, "
                current_x += unit * 2
            elif dot == "-":
                ret += f"abs(x - {current_x + 3 * unit}) < {3 * unit}, "
                current_x += 3 * unit * 2
            # single space after single dot
            current_x += unit * 2
        
        # after char, 7 units
        current_x += 7 * unit * 2

    return ret.removesuffix(", ") + "}"


driver = webdriver.Firefox()

driver.get("https://www.desmos.com/calculator/")

ActionChains(driver).send_keys(string_to_morse("HELLO WORLD")).perform()

keyboard_button = driver.find_element(By.CSS_SELECTOR, "#graph-container > div > div > div > div.dcg-keypad.dcg-keypad-interaction-container > div.dcg-show-keypad-container > div > div")
keyboard_button.click()

audio_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-label='Toggle Audio Trace']"))
)
audio_button.click()

zoom_out = WebDriverWait(driver,10).until(

    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Zoom Out']"))
)
for _ in range(4):
    zoom_out.click()
    time.sleep(0.35)

speed_down = WebDriverWait(driver,10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "span[aria-label='Speed Down']"))
)
for _ in range(3):
    speed_down.click()

hear_graph = WebDriverWait(driver,10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[dcg-command="hear-graph"]'))
)
hear_graph.click()

time.sleep(10000000)