import cv2
import numpy as np
import os
from pathlib import Path

def make_natural_watercolor(image_path, output_path):
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
    
    # 1. Bilateral filter for watercolor wash (paint look)
    # We do a strong smoothing to merge smaller color details into painterly strokes
    watercolor = img.copy()
    for _ in range(4):
        watercolor = cv2.bilateralFilter(watercolor, d=11, sigmaColor=70, sigmaSpace=70)
        
    # 2. Pencil Outline in dark brown/warm charcoal color (not black)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray = 255 - gray
    # Larger blur creates a wider, softer graphite line drawing look
    blurred_inv = cv2.GaussianBlur(inv_gray, (25, 25), 0)
    sketch_gray = cv2.divide(gray, 255 - blurred_inv, scale=256.0)
    sketch_gray = cv2.GaussianBlur(sketch_gray, (3, 3), 0)
    
    # Convert sketch to BGR but tint it warm charcoal/brown (BGR: 50, 60, 70)
    # White parts remain white, dark sketch lines get tinted
    sketch_tinted = np.zeros((h, w, 3), dtype=np.uint8)
    # Warm dark brown tone for line drawing
    line_color = np.array([45, 55, 65], dtype=np.float32) 
    
    sketch_norm = sketch_gray.astype(float) / 255.0
    for c in range(3):
        sketch_tinted[:, :, c] = (line_color[c] + (255.0 - line_color[c]) * sketch_norm).astype(np.uint8)
        
    # Multiply the watercolor wash with the tinted sketch outlines
    combined = cv2.multiply(watercolor, sketch_tinted, scale=1.0/255.0)
    
    # 3. Mute Greens by 60% and adjust palette to Morandi Pastel tones
    hsv = cv2.cvtColor(combined, cv2.COLOR_BGR2HSV)
    h_ch, s_ch, v_ch = cv2.split(hsv)
    
    # Green tones mask (Hue 35 to 85)
    green_mask = cv2.inRange(hsv, (35, 25, 0), (85, 255, 255))
    # Mute greens by 60% (retain only 40% of green saturation)
    s_ch = np.where(green_mask > 0, (s_ch.astype(float) * 0.40).astype(np.uint8), s_ch)
    
    # Overall saturation dampening for soft pastel tones
    s_ch = (s_ch.astype(float) * 0.85).astype(np.uint8)
    # Boost brightness slightly to look like a sun-drenched painting
    v_ch = np.clip(v_ch.astype(float) * 1.06, 0, 255).astype(np.uint8)
    
    hsv_pastel = cv2.merge([h_ch, s_ch, v_ch])
    combined_pastel = cv2.cvtColor(hsv_pastel, cv2.COLOR_HSV2BGR)
    
    # 4. Create warm hand-made paper background (BGR: 228, 236, 245 - soft beige/cream)
    paper_bg = np.zeros(img.shape, dtype=np.uint8)
    paper_bg[:] = [228, 236, 245]  
    
    # Add subtle paper pulp noise texture
    np.random.seed(100)
    paper_noise = np.random.normal(128, 6, (h, w)).astype(np.float32)
    paper_noise_blurred = cv2.GaussianBlur(paper_noise, (3, 3), 0)
    paper_noise_norm = paper_noise_blurred / 128.0
    
    # Apply noise to paper background
    for c in range(3):
        paper_bg[:, :, c] = np.clip(paper_bg[:, :, c].astype(float) * paper_noise_norm, 0, 255).astype(np.uint8)
        
    # Blend watercolor image (78%) with textured paper background (22%)
    final = cv2.addWeighted(combined_pastel, 0.78, paper_bg, 0.22, 0)
    
    # Save output BGR image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ext = os.path.splitext(output_path)[1]
    is_success, im_buf_arr = cv2.imencode(ext, final)
    if is_success:
        try:
            with open(output_path, "wb") as f:
                f.write(im_buf_arr)
            print(f"Successfully saved natural watercolor to {output_path}")
        except Exception as e:
            print(f"Error writing image: {e}")
    else:
        print("Error encoding image")

def main():
    src = "output/截圖/screenshot_4.png"  # Using Slide 4 (Group discussion) for testing
    dest = "output/test_natural_watercolor_4.png"
    make_natural_watercolor(src, dest)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
