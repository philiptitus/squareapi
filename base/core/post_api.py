
from PIL import Image  # Ensure this import is at the top of the file

import textwrap
import requests
import google.generativeai as genai
from io import BytesIO
import base64
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from base.models import Post, PostImage  # Adjust the import based on your project's structure

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def image_to_base64(image):
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def generate_markdown_from_images(image_urls, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    base64_images = [image_to_base64(download_image(url)) for url in image_urls]

    prompt = (
        "This is a social media post. Based on the following images, "
        "determine if this post is related to the environment (an environment social media post). Respond with only one word: YES or NO.\n\n"
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
