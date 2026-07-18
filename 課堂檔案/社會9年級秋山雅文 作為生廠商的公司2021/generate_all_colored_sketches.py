import cv2
import numpy as np
import os
from pathlib import Path

def make_colored_sketch(image_path, output_path):
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
    
    # 1. Grayscale outline (Color Dodge Sketch)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray = 255 - gray
    blurred_inv = cv2.GaussianBlur(inv_gray, (21, 21), 0)
    sketch_gray = cv2.divide(gray, 255 - blurred_inv, scale=256.0)
    
    # 2. Pencil Shading and Noise Texture
    shaded = cv2.addWeighted(gray, 0.5, np.full(gray.shape, 255, dtype=np.uint8), 0.5, 0)
    np.random.seed(42)
    noise = np.random.normal(128, 15, (h, w)).astype(np.float32)
    noise_blurred = cv2.GaussianBlur(noise, (3, 3), 0)
    noise_norm = noise_blurred / 128.0
    shaded_textured = np.clip(shaded.astype(float) * noise_norm, 0, 255).astype(np.uint8)
    
    # Combine outline and texture into final grayscale sketch layer
    sketch_combined = cv2.multiply(sketch_gray, shaded_textured, scale=1.0/255.0)
    min_val, max_val, _, _ = cv2.minMaxLoc(sketch_combined)
    sketch_combined_contrast = np.clip((sketch_combined.astype(float) - min_val) * (255.0 / (max_val - min_val)), 0, 255).astype(np.uint8)
    sketch_final = cv2.addWeighted(sketch_combined_contrast, 0.85, sketch_combined, 0.15, 0)
    
    # 3. Multiply grayscale sketch with the original BGR image to get a Colored Pencil Sketch!
    sketch_3ch = cv2.merge([sketch_final, sketch_final, sketch_final])
    colored_sketch = cv2.multiply(img, sketch_3ch, scale=1.0/255.0)
    
    # 4. Blend with pastel paper background and cloud mask for artistic effect
    pastel_bg = np.zeros((h, w, 3), dtype=np.uint8)
    # Pale blue-grey paper color (BGR: 220, 228, 238)
    pastel_bg[:] = [238, 228, 220]  
    
    # Create delicate white clouds in background
    cloud_mask = np.zeros((h, w), dtype=np.uint8)
    np.random.seed(42)
    for _ in range(8):
        cx = np.random.randint(0, w)
        cy = np.random.randint(0, h)
        axes = (np.random.randint(w // 4, w // 2), np.random.randint(h // 8, h // 4))
        angle = np.random.randint(-15, 15)
        cv2.ellipse(cloud_mask, (cx, cy), axes, angle, 0, 360, 255, -1)
        
    cloud_mask_blurred = cv2.GaussianBlur(cloud_mask, (151, 151), 0)
    cloud_mask_f = cloud_mask_blurred.astype(float) / 255.0
    
    # Blend pastel BGR with clouds
    for c in range(3):
        pastel_bg[:, :, c] = (pastel_bg[:, :, c] * (1.0 - 0.4 * cloud_mask_f) + 255 * (0.4 * cloud_mask_f)).astype(np.uint8)
        
    # Final blend: 75% colored sketch + 25% pastel paper background
    final = cv2.addWeighted(colored_sketch, 0.75, pastel_bg, 0.25, 0)
    
    # Saturation boost to make colors pop
    hsv = cv2.cvtColor(final, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(float) * 1.25, 0, 255).astype(np.uint8)
    final = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    # Save output BGR image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ext = os.path.splitext(output_path)[1]
    is_success, im_buf_arr = cv2.imencode(ext, final)
    if is_success:
        try:
            with open(output_path, "wb") as f:
                f.write(im_buf_arr)
            print(f"Successfully saved colored sketch to {output_path}")
        except Exception as e:
            print(f"Error writing image: {e}")
    else:
        print("Error encoding image")

def main():
    output_dir = Path("output/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    screenshots_dir = Path("output/screenshots")
    
    # Process ALL 19 slides
    for i in range(1, 20):
        src_path = screenshots_dir / f"screenshot_{i}.png"
        dest_path = output_dir / f"slide_{i}.png"
        if src_path.exists():
            print(f"Processing slide {i} into Colored Sketch...")
            make_colored_sketch(str(src_path), str(dest_path))
        else:
            print(f"Error: Screenshot for slide {i} does not exist.")
            
    print("All 19 slides processed into Colored Sketches successfully!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
