import cv2
import numpy as np
import os
from pathlib import Path

def make_sketch(image_path, output_path):
    # Read image supporting unicode paths on Windows
    try:
        with open(image_path, "rb") as f:
            bytes_data = bytearray(f.read())
            numpyarray = np.asarray(bytes_data, dtype=np.uint8)
            img = cv2.imdecode(numpyarray, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return
        
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return
        
    h, w, _ = img.shape
    
    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Outline (Line Drawing) via Color Dodge
    inv_gray = 255 - gray
    blurred_inv = cv2.GaussianBlur(inv_gray, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blurred_inv, scale=256.0)
    
    # 2. Pencil Shading
    shaded = cv2.addWeighted(gray, 0.5, np.full(gray.shape, 255, dtype=np.uint8), 0.5, 0)
    
    # Add paper/pencil noise texture
    np.random.seed(42)
    noise = np.random.normal(128, 15, (h, w)).astype(np.float32)
    noise_blurred = cv2.GaussianBlur(noise, (3, 3), 0)
    noise_norm = noise_blurred / 128.0
    shaded_textured = np.clip(shaded.astype(float) * noise_norm, 0, 255).astype(np.uint8)
    
    # Combine outline and texture
    combined = cv2.multiply(sketch, shaded_textured, scale=1.0/255.0)
    
    # Enhance contrast
    min_val, max_val, _, _ = cv2.minMaxLoc(combined)
    combined_contrast = np.clip((combined.astype(float) - min_val) * (255.0 / (max_val - min_val)), 0, 255).astype(np.uint8)
    combined = cv2.addWeighted(combined_contrast, 0.8, combined, 0.2, 0)
    
    # Create pastel background (pale light blue/grey)
    pastel_bg = np.zeros((h, w, 3), dtype=np.uint8)
    pastel_bg[:] = [238, 228, 220]  # BGR for pale light blue-grey
    
    # Create delicate wisps of clouds in the background
    cloud_mask = np.zeros((h, w), dtype=np.uint8)
    np.random.seed(42)
    for _ in range(8):
        cx = np.random.randint(0, w)
        cy = np.random.randint(0, h)
        axes = (np.random.randint(w // 4, w // 2), np.random.randint(h // 8, h // 4))
        angle = np.random.randint(-15, 15)
        cv2.ellipse(cloud_mask, (cx, cy), axes, angle, 0, 360, 255, -1)
        
    # Heavily blur the cloud mask
    cloud_mask_blurred = cv2.GaussianBlur(cloud_mask, (151, 151), 0)
    cloud_mask_f = cloud_mask_blurred.astype(float) / 255.0
    
    # Blend pastel background with white clouds
    for c in range(3):
        pastel_bg[:, :, c] = (pastel_bg[:, :, c] * (1.0 - 0.4 * cloud_mask_f) + 255 * (0.4 * cloud_mask_f)).astype(np.uint8)
        
    # Convert combined gray sketch to 3 channels
    sketch_3ch = cv2.merge([combined, combined, combined])
    
    # Multiply the sketch with the pastel/cloud background
    final = (sketch_3ch.astype(float) * pastel_bg.astype(float) / 255.0).astype(np.uint8)
    
    # Save the output image supporting unicode paths on Windows
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ext = os.path.splitext(output_path)[1]
    is_success, im_buf_arr = cv2.imencode(ext, final)
    if is_success:
        try:
            with open(output_path, "wb") as f:
                f.write(im_buf_arr)
            print(f"Successfully saved sketch to {output_path}")
        except Exception as e:
            print(f"Error writing image: {e}")
    else:
        print("Error encoding image")

def main():
    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    screenshots_dir = Path("output/screenshots")
    
    failed_slides = [5, 10, 14, 15]
    for slide_num in failed_slides:
        src_path = screenshots_dir / f"screenshot_{slide_num}.png"
        dest_path = output_dir / f"slide_{slide_num}.png"
        if src_path.exists():
            print(f"Processing failed slide {slide_num}...")
            make_sketch(str(src_path), str(dest_path))
        else:
            print(f"Screenshot for slide {slide_num} does not exist at {src_path}")
            
    print("Failed slides processing finished!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
