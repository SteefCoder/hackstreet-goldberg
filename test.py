from PIL import ImageGrab, Image
import cv2
import numpy as np
from qreader import QReader



def detect():
    image_path = "pil_img.png"

    qreader = QReader()
    image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)

    decoded_texts = qreader.detect_and_decode(image=image)

    print("text: ", decoded_texts)


detect()
