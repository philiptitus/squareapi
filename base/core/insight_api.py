import textwrap
import google.generativeai as genai

def to_markdown(text):
    """
    Converts plain text to Markdown format.
    """
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def generate_markdown(api_key, trash_type):
    """
    Generates a markdown-formatted 'Did you know?' fact about the given trash type using Google Generative AI.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Using just one sentence give me a random did you know fact about {trash_type} Waste"
    
    response = model.generate_content([prompt], stream=True)
    response.resolve()

    markdown_text = to_markdown(response.text)
    return markdown_text
