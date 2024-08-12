import fitz  # PyMuPDF
import re

def mask_confidential_words_in_pdf(input_pdf_path, output_pdf_path, confidential_words):
    # Open the input PDF
    document = fitz.open(input_pdf_path)

    # Iterate through each page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text_instances = page.search_for('')  # Search for empty string to get all text

        for word in confidential_words:
            word_mask = '*' * len(word)
            # Find all instances of the confidential word in the page
            found_instances = page.search_for(word)
            for inst in found_instances:
                # Redact the word with the mask
                page.add_redact_annot(inst, fill=(1, 1, 1))  # Add white rectangle over text
                page.apply_redactions()  # Apply the redaction to make the change

                # Insert the masked word in place of the original
                page.insert_text(inst[:2], word_mask, fontsize=12, color=(0, 0, 0))

    # Save the modified PDF to a new file
    document.save(output_pdf_path)

# Example usage
input_pdf = "input.pdf"
output_pdf = "output_masked.pdf"
confidential_words = ["9739657905", "banking", "BANKING", "softwareapplication.", "Ensuring", "CTAP"]

mask_confidential_words_in_pdf(input_pdf, output_pdf, confidential_words)
