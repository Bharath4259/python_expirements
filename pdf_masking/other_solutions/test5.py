import fitz  # PyMuPDF
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import re

def mask_confidential_words_in_pdf(input_pdf_path, output_pdf_path, confidential_words):
    # Step 1: Extract text with pdfplumber and create a list of pages' texts
    with pdfplumber.open(input_pdf_path) as pdf:
        pages_text = [page.extract_text() for page in pdf.pages]

    # Step 2: Mask confidential words in extracted text
    masked_pages_text = []
    for text in pages_text:
        for word in confidential_words:
            word_mask = '*' * len(word)
            text = re.sub(r'\b{}\b'.format(re.escape(word)), word_mask, text)
        masked_pages_text.append(text)

    # Step 3: Create a new PDF with the masked text while preserving layout
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    # Open the input PDF with PyMuPDF to get the structure
    document = fitz.open(input_pdf_path)
    
    for page_num, text in enumerate(masked_pages_text):
        page = document[page_num]
        page_rect = page.rect  # Get the page size

        # Reinsert the masked text while preserving font, position, etc.
        c.drawString(0, page_rect.height - 20, text)  # Adjust the position accordingly
        
        # Move to the next page
        c.showPage()

    c.save()

    # Step 4: Overlay the new masked text PDF onto the original PDF
    packet.seek(0)
    new_pdf = fitz.open("pdf", packet.read())

    for page_num in range(len(document)):
        page = document[page_num]
        new_page = new_pdf[page_num]
        page.show_pdf_page(page.rect, new_page, 0)

    # Step 5: Save the final PDF
    document.save(output_pdf_path)

# Example usage
input_pdf = "simple_doc.pdf"
output_pdf = "output_masked.pdf"
confidential_words = ["confidential", "secret", "sensitive"]

mask_confidential_words_in_pdf(input_pdf, output_pdf, confidential_words)
