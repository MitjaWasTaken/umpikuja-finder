import hashlib
import hmac
import base64
import urllib.parse as urlparse

from secret import secret

def sign_url(url):

    url = urlparse.urlparse(url)
    url_to_sign = url.path + "?" + url.query

    decoded_key = base64.urlsafe_b64decode(secret)
    signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query
    return f"{original_url}&signature={encoded_signature.decode()}"