"""For encoding and decoding the body of responses.

Currently it does nothing since it appears that python3 will handle
this for us.  See https://docs.python.org/3/howto/unicode.html

The real question is whether our json encoder/decoder will do this
correctly.
"""

# import base64


def encode(text):
    """Encode the body for saving in JSON"""
    return text # base64.b64encode(text) #.encode()) # I don't understand this


def decode(encoded_text):
    return encoded_text # base64.b64decode(encoded_text)
