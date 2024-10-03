""" This function is written respect to generating the value for X-App-Access-Sig 

    1. Parse the URI from the URL
    2. Prepare the body as an empty string if not provided (GET)
    3. Concatenate the timestamp, method, URI and body for the signature
    4. create the HMAC to signature
"""

import hashlib
import hmac
import time
from urllib.parse import urlparse
from django.conf import settings
import json

import base64
from PIL import Image
from io import BytesIO
import string
import random


def get_auth_headers(url, method, body=''):
    timestamp = str(int(time.time()))

    parsed_url = urlparse(url=url)
    uri = parsed_url.path
    if parsed_url.query:
        uri += '?' + parsed_url.query

    # if body:
    #     body_data = json.dumps(body)
    # else:
    #     body_data = ''

    data_to_sign = f"{timestamp}{method}{uri}{body}"


    signature = hmac.new(
        settings.SUMSUB_SECRET_KEY.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    return {
        "X-App-Token": settings.SUMSUB_API_TOKEN,
        "X-App-Access-Ts": timestamp,
        "X-App-Access-Sig": signature
    }



def decode_base64_image(base64_string):
    try:        
        # this is to add padding to the base64
        missing_padding = len(base64_string) % 4
        if missing_padding != 0:
            base64_string += '=' * (4 - missing_padding)

        image_bytes = base64.b64decode(base64_string)
        image_buffer = BytesIO(image_bytes)
        image = Image.open(image_buffer)
        
        image.verify()
        image_buffer.seek(0)
        
        return base64_string
    except (IOError, ValueError, TypeError) as e:
        return None
    

def auto_generate(amount):  
    data_type = string.ascii_letters + string.digits
    id_length = random.sample(data_type, amount)
    code = "".join(id_length)
    return code