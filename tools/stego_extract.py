from langchain_core.tools import tool
import requests
from PIL import Image
import io


@tool
def extract_lsb_message(image_url: str) -> str:
    """
    Extracts a hidden message from an image using LSB (Least Significant Bit) steganography.
    Tries multiple extraction methods to find the hidden message.
    
    Args:
        image_url: The URL of the image to analyze
        
    Returns:
        The hidden message extracted from the LSB of the image pixels
    """
    try:
        print(f"\nDownloading image from: {image_url}")
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Open the image
        img = Image.open(io.BytesIO(response.content))
        img = img.convert('RGB')
        pixels = list(img.getdata())
        width, height = img.size
        
        print(f"Image size: {width}x{height}, Total pixels: {len(pixels)}")
        
        results = []
        
        # Method 1: Extract LSB from Red channel only (row by row)
        binary_r = ""
        for pixel in pixels:
            binary_r += str(pixel[0] & 1)
        msg1 = binary_to_text(binary_r)
        results.append(("Red channel only", msg1))
        
        # Method 2: Extract LSB from all RGB channels sequentially
        binary_rgb = ""
        for pixel in pixels:
            binary_rgb += str(pixel[0] & 1)
            binary_rgb += str(pixel[1] & 1)
            binary_rgb += str(pixel[2] & 1)
        msg2 = binary_to_text(binary_rgb)
        results.append(("RGB sequential", msg2))
        
        # Method 3: Extract all R bits, then G bits, then B bits
        binary_r_all = "".join(str(p[0] & 1) for p in pixels)
        binary_g_all = "".join(str(p[1] & 1) for p in pixels)
        binary_b_all = "".join(str(p[2] & 1) for p in pixels)
        msg3 = binary_to_text(binary_r_all)
        results.append(("All R bits", msg3))
        
        # Method 4: RGBA if image has alpha
        try:
            img_rgba = Image.open(io.BytesIO(response.content)).convert('RGBA')
            pixels_rgba = list(img_rgba.getdata())
            binary_rgba = ""
            for pixel in pixels_rgba:
                for channel in pixel:
                    binary_rgba += str(channel & 1)
            msg4 = binary_to_text(binary_rgba)
            results.append(("RGBA all channels", msg4))
        except:
            pass
        
        # Find the best result (longest meaningful text)
        best_msg = ""
        best_method = ""
        for method, msg in results:
            print(f"  {method}: {msg[:50]}...")
            # Look for printable text
            if len(msg) > len(best_msg) and msg.isprintable():
                best_msg = msg
                best_method = method
        
        if best_msg:
            print(f"\nBest extraction ({best_method}): {best_msg}")
            return best_msg
        
        # Return the first non-empty result
        for method, msg in results:
            if msg:
                return msg
        
        return "No hidden message found"
        
    except Exception as e:
        return f"Error extracting LSB message: {str(e)}"


def binary_to_text(binary_str: str) -> str:
    """Convert binary string to text, stopping at null terminator or non-printable."""
    message = ""
    for i in range(0, min(len(binary_str), 8000), 8):  # Limit to prevent huge strings
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if char_code == 0:  # Null terminator
                if len(message) > 0:
                    break
                continue
            if 32 <= char_code <= 126:  # Printable ASCII
                message += chr(char_code)
            elif len(message) > 3:  # We have some text, non-printable might mean end
                break
    return message.strip()
