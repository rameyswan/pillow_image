import os
from PIL import Image, ImageOps
import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

def convert_heic_to_jpg(heic_path, jpg_path):
    try:
        heif_file = pillow_heif.open(heic_path)
        image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", heif_file.mode, heif_file.stride)
        image.save(jpg_path, "JPEG")
        return jpg_path
    except Exception as e:
        print(f"Error converting {heic_path} to JPG: {e}")
        return None

def create_collage(folder_path, output_path, base_image_size=(300, 300), scale_factor=1.0, frame_width=10, border_size=5):
    supported_formats = {'.jpg', '.jpeg', '.png', '.heic'}
    image_paths = set()

    # Collect image paths and convert HEIC images
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in supported_formats:
                file_path = os.path.join(root, file)
                if file_ext == '.heic':
                    jpg_path = os.path.splitext(file_path)[0] + '.jpg'
                    converted_path = convert_heic_to_jpg(file_path, jpg_path)
                    if converted_path:
                        image_paths.add(converted_path)
                else:
                    image_paths.add(file_path)

    image_paths = sorted(image_paths)
    num_images = len(image_paths)

    if num_images == 0:
        print("No images found in the specified folder.")
        return

    # Determine layout
    if num_images <= 4:
        cols, rows = 2, 2
    elif num_images <= 6:
        cols, rows = 3, 2
    else:
        cols, rows = 3, 3

    scaled_size = (int(base_image_size[0] * scale_factor), int(base_image_size[1] * scale_factor))
    collage_width = cols * scaled_size[0] + (cols + 1) * frame_width
    collage_height = rows * scaled_size[1] + (rows + 1) * frame_width

    collage_image = Image.new('RGBA', (collage_width, collage_height), (255, 255, 255, 0))

    for idx, image_path in enumerate(image_paths):
        if idx >= cols * rows:
            break
        image = Image.open(image_path)
        image = image.resize(scaled_size, Image.LANCZOS)
        image = ImageOps.expand(image, border_size, (0, 0, 128, 255))
        image = image.convert("RGBA")

        col = idx % cols
        row = idx // cols
        x_offset = col * scaled_size[0] + (col + 1) * frame_width
        y_offset = row * scaled_size[1] + (row + 1) * frame_width

        collage_image.paste(image, (x_offset, y_offset), image)

    collage_image.save(output_path, "PNG")
    collage_image.show()
    path_folder = os.getcwd()

# Test the application
if __name__ == "__main__":
    create_collage(  os.getcwd(), 'output_collage.png', base_image_size=(300, 300), scale_factor=1.0, frame_width=10, border_size=5)