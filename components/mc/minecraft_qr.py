import qrcode
import json


def generate_qr(text):
    qr = qrcode.QRCode()
    qr.add_data(text)
    qr.make(fit=True)
    
    matrix = [[1 if cell else 0 for cell in  row] for row in qr.get_matrix()]
    
    with open("qr_code.json", "w") as f:
        json.dump(matrix, f)

generate_qr("hello world!")





