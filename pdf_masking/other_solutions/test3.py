import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

def get_average_color(image, bbox):
    """
    Get the average color of the area within the bounding box in the image.
    
    Parameters:
        image (PIL.Image): The image to analyze.
        bbox (tuple): The bounding box (x0, y0, x1, y1).
        
    Returns:
        tuple: The average color as an (R, G, B) tuple.
    """
    cropped_image = image.crop(bbox)
    np_image = np.array(cropped_image)
    
    # Calculate the average color
    avg_color = np.mean(np_image, axis=(0, 1))
    
    return tuple(avg_color.astype(int))

def mask_confidential_words_with_dynamic_rect(input_pdf_path, output_pdf_path, confidential_words):
    # Open the input PDF
    document = fitz.open(input_pdf_path)

    # Render the PDF as an image
    images = convert_from_path(input_pdf_path)

    # Iterate through each page
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pil_image = images[page_num]
        for word in confidential_words:
            # Find all instances of the confidential word in the page
            found_instances = page.search_for(word)
            for inst in found_instances:
                # Convert bbox from PDF coordinate system to image coordinate system
                x0, y0, x1, y1 = inst
                x0, y0, x1, y1 = map(int, (x0, pil_image.height - y1, x1, pil_image.height - y0))

                # Get the average background color of the bounding box
                avg_color = get_average_color(pil_image, (x0, y0, x1, y1))

                # Draw a rectangle over the word with the detected average color
                page.draw_rect(inst, color=avg_color, fill=avg_color)

    # Save the modified PDF to a new file
    document.save(output_pdf_path)

# Example usage
input_pdf = "input.pdf"
output_pdf = "output_masked.pdf"
confidential_words = ["9739657905", "banking", "BANKING", "aws", "softwareapplication.", "Ensuring", "CTAP"]

mask_confidential_words_with_dynamic_rect(input_pdf, output_pdf, confidential_words)
