# utils.py
import textwrap
import requests
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def image_to_base64(image):
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def to_markdown(text):
    """
    Converts plain text to Markdown format.
    """
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def generate_markdown_from_images(image_urls, api_key):
    # Configure Google API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Download images and convert to base64
    base64_images = [image_to_base64(download_image(url)) for url in image_urls]

    # Generate content
    prompt = (
        "This is a social media post. Based on the following images, "
        "determine if this post is related to the environment (an enviroment social media post). Respond with only one word: YES or NO.\n\n"
    )
    for idx, img_base64 in enumerate(base64_images):
        prompt += f"Image {idx + 1}: {img_base64}\n"

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip().upper()
    except Exception as e:
        print(f"AI Error: {str(e)}")
        response_text = "NO"
    
    return response_text
