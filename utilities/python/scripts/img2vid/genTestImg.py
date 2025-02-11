import os
from PIL import Image, ImageDraw, ImageFont

def generate_test_images(output_folder, count=30, width=1920, height=1080):
    """
    Generates numbered test images to verify video frame order.

    Args:
        output_folder (str): Directory to save images.
        count (int): Number of images to generate.
        width (int): Width of the images.
        height (int): Height of the images.

    Example:
        generate_test_images("test_images", count=100)
    """
    os.makedirs(output_folder, exist_ok=True)

    # Try to load a system font, otherwise use default
    try:
        font = ImageFont.truetype("arial.ttf", 200)
    except IOError:
        font = ImageFont.load_default()

    for i in range(1, count + 1):
        img = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        text = str(i)
        
        # Get text bounding box to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Draw text in the center
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)

        # Save the image
        img.save(os.path.join(output_folder, f"test_{i}.png"))

    print(f"Generated {count} test images in '{output_folder}'")

# Example usage
generate_test_images("test_images", count=30)
