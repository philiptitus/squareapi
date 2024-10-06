import io
import textwrap
import requests
import google.generativeai as genai
from PIL import Image

def to_markdown(text):
    """
    Converts plain text to Markdown format.
    """
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def get_waste_type_from_image(image_file, api_key):
    # Configure Google API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Open image
    img = Image.open(image_file)

    # Generate content
    response = model.generate_content(
        [
            "Choose only from this list of options the option that describes the waste in the picture: WASTE_TYPES = [ ('Plastic', 'Plastic'), ('Glass', 'Glass'), ('Metal', 'Metal'), ('Paper', 'Paper'), ('Organic', 'Organic'), ('Electronic', 'Electronic'), ('Hazardous', 'Hazardous'), ].", 
            img
        ], 
        stream=True
    )
    response.resolve()

    # Extract waste type from response text
    waste_type = extract_waste_type(response.text)
    return waste_type

def extract_waste_type(text):
    """
    Extracts the waste type from the AI response text.
    """
    waste_types = ['Plastic', 'Glass', 'Metal', 'Paper', 'Organic', 'Electronic', 'Hazardous']
    for waste_type in waste_types:
        if waste_type in text:
            return waste_type
    return "General"  # Default type if no match is found
