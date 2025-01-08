# Utilites functions used by app.py
import random
from html import escape # this is being used for bebugging
import qrcode
import io
import base64

class Util(object):
    def generate_random_code(length):

        # Define the character set, excluding the specified characters
        char_set = "2346789BCDEFGHJKMNPQRTVWXYZ"  # Avoided characters: I, L, 1, 0, O, A, S

        random_code = ''.join(random.choice(char_set) for _ in range(length))
        return random_code

    def generate_session_code():
        return 'S' + Util.generate_random_code(15)

    def generate_new_userID():
        return 'A' + Util.generate_random_code(6)

    def generate_new_locationID():
        return 'L' + Util.generate_random_code(8)
    
    def generate_new_glyphID():
        return 'G' + Util.generate_random_code(8)

    def generate_qr_code(data):
        """
        generate_qr_code creates a qr code image
        :param data: a string you want encoded
        :return: returns a base64 encoded PNG image to be used in a webpage.
        Example using usage: <img src="data:image/png;base64,{{ generate_qr_code(data) }}">
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return img_base64
    
    def sanitize(data):
        # I am having trouble finding documentation related to what type of input
        #  sanitation is needed for pymongo queries. I'll do a basic character
        #  filter here and hope it's good enough.
        banned_chars = r'{},$;"'
        return data.translate(str.maketrans( {char: None for char in banned_chars} ))