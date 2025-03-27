import os
from PIL import Image

def crop_images(input_folder, output_folder, crop_box):
    """
    Crops all PNG images in the input folder and saves them in the output folder.
    
    Parameters:
        input_folder (str): Path to the directory containing PNG images.
        output_folder (str): Path to save the cropped images.
        crop_box (tuple): The cropping rectangle (left, upper, right, lower).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            cropped_image = image.crop(crop_box)
            output_path = os.path.join(output_folder, filename)
            cropped_image.save(output_path)
            print(f"Cropped and saved: {output_path}")

# Example usage
input_dir = "assets/images/fish"   # Change this to your input folder
output_dir = "output_images"  # Change this to your output folder
crop_box = (402, 268, 520, 337)  # Change this to your desired crop dimensions

crop_images(input_dir, output_dir, crop_box)
