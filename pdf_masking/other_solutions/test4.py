import PyPDF2
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import StreamObject, DecodedStreamObject
from PyPDF2 import filters

# You change the phrases/text you want redacted and the file paths:
phrases = ["9739657905", "banking", "BANKING", "aws", "softwareapplication.", "Ensuring", "CTAP"]
read_path = "input.pdf"
write_path = "output.pdf"


def replace_w_stars(text, phrase):
    return text.replace(phrase, "*" * len(phrase))


def redact(text, phrases=phrases):
    if isinstance(text, bytes):
        text = text.decode()
    for phrase in phrases:
        text = replace_w_stars(text, phrase)
    return text


class EncodedStreamObject(StreamObject):
    def __init__(self):
        self.decodedSelf = None

    def getData(self):
        if self.decodedSelf:
            # cached version of decoded object
            return self.decodedSelf.getData()
        else:
            # create decoded object
            decoded = DecodedStreamObject()

            decoded._data = filters.decodeStreamData(self)
            decoded._data = redact(decoded._data)

            for key, value in list(self.items()):
                if not key in ("/Length", "/Filter", "/DecodeParms"):
                    decoded[key] = value
            self.decodedSelf = decoded
            return decoded._data

# Overload with redaction version
PyPDF2.generic.EncodedStreamObject = EncodedStreamObject

# Read in the PDFs
f = open(read_path, "rb")
r = PdfFileReader(f)

# Force the redaction by merging with itself
page = r.getPage(0)
page.mergePage(r.getPage(0))

# Write out the result
f_out = open(write_path, "wb")
w = PdfFileWriter()
w.addPage(page)
w.write(f_out)
f_out.close()