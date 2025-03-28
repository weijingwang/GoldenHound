from PIL import Image
import os

def add_black_borders(image_path, output_path, target_size=(1280, 720)):
    with Image.open(image_path) as img:
        original_size = img.size
        new_img = Image.new("RGB", target_size, (0, 0, 0))
        
        x_offset = (target_size[0] - original_size[0]) // 2
        y_offset = (target_size[1] - original_size[1]) // 2
        
        new_img.paste(img, (x_offset, y_offset))
        new_img.save(output_path)

def process_directory(directory):
    output_directory = os.path.join(directory, "processed")
    os.makedirs(output_directory, exist_ok=True)
    
    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory, filename)
            output_path = os.path.join(output_directory, filename)
            add_black_borders(image_path, output_path)
            print(f"Processed: {filename}")

if __name__ == "__main__":
    images_directory = "assets/images/titles"
    process_directory(images_directory)
