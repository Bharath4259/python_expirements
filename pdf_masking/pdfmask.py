import fitz  # PyMuPDF
import re

def mask_confidential_words_with_black_rect(input_pdf_path, output_pdf_path, confidential_words):
    # Open the input PDF
    document = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        for word in confidential_words:
            # Find all instances of the confidential word in the page
            found_instances = page.search_for(word)
            for inst in found_instances:
                # Draw a black rectangle over the word
                page.draw_rect(inst, color=(0, 0, 0), fill=(0, 0, 0))

    # Save the modified PDF to a new file
    document.save(output_pdf_path)


# Example usage
input_pdf = "input.pdf"
output_pdf = "output_masked.pdf"
confidential_words = ["9739657905", "banking", "BANKING", "aws", "softwareapplication.", "Ensuring", "CTAP"]

mask_confidential_words_with_black_rect(input_pdf, output_pdf, confidential_words)
