from langchain_core.tools import tool
import requests
import base64
import os
from google import genai
from google.genai import types


@tool
def analyze_image(image_url: str, question: str = "What is the secret code or text written in this image?") -> str:
    """
    Analyzes an image using Google's Gemini Vision model to extract text or answer questions about the image.
    
    Args:
        image_url: The URL of the image to analyze
        question: The question to ask about the image (default: extract secret code/text)
        
    Returns:
        The analysis result as a string
    """
    try:
        # Download the image
        print(f"\nAnalyzing image: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        image_data = response.content
        
        # Determine the mime type
        content_type = response.headers.get('Content-Type', 'image/png')
        if 'jpeg' in content_type or 'jpg' in content_type:
            mime_type = 'image/jpeg'
        elif 'gif' in content_type:
            mime_type = 'image/gif'
        elif 'webp' in content_type:
            mime_type = 'image/webp'
        else:
            mime_type = 'image/png'
        
        # Use Google Genai client
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Create the image part
        image_part = types.Part.from_bytes(
            data=image_data,
            mime_type=mime_type
        )
        
        # Generate content with vision
        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                question,
                image_part
            ]
        )
        
        answer = result.text.strip()
        print(f"Image analysis result: {answer}")
        return answer
        
    except Exception as e:
        return f"Error analyzing image: {str(e)}"
