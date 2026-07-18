import cv2
import numpy as np
from pathlib import Path

def test_filter():
    image_path = "output/截圖/screenshot_1.png"
    output_path = "output/test_watercolor_1.png"
    
    if not Path(image_path).exists():
        print(f"Error: {image_path} not found")
        return
        
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
    
    # 1. Bilateral filter for watercolor color wash (smooth colors, remove face details, keep shapes)
    # Applying strong bilateral filter multiple times to completely blur out facial features (de-identification)
    watercolor = img.copy()
    for _ in range(4):
        watercolor = cv2.bilateralFilter(watercolor, d=15, sigmaColor=150, sigmaSpace=150)
        
    # 2. Pencil outline (Color Dodge)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray = 255 - gray
    blurred_inv = cv2.GaussianBlur(inv_gray, (21, 21), 0)
    sketch_gray = cv2.divide(gray, 255 - blurred_inv, scale=256.0)
    
    # Smooth sketch outline slightly to make it look like pencil/brush
    sketch_gray = cv2.GaussianBlur(sketch_gray, (3, 3), 0)
    sketch_3ch = cv2.merge([sketch_gray, sketch_gray, sketch_gray])
    
    # 3. Combine sketch outline with watercolor wash
    combined = cv2.multiply(watercolor, sketch_3ch, scale=1.0/255.0)
    
    # 4. Convert to HSV to desaturate the greens and make it look natural and pastel
    hsv = cv2.cvtColor(combined, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Create mask for green tones (Hue between 35 and 85)
    # We want to lower the saturation of greens to make them natural, not overly artificial
    green_mask = cv2.inRange(hsv, (35, 30, 0), (85, 255, 255))
    
    # Desaturate greens by 60%
    s_green_reduced = np.where(green_mask > 0, (s.astype(float) * 0.4).astype(np.uint8), s)
    
    # Desaturate all colors slightly to make it pastel (multiply by 0.8)
    s_pastel = (s_green_reduced.astype(float) * 0.85).astype(np.uint8)
    
    # Boost brightness slightly
    v_bright = np.clip(v.astype(float) * 1.05, 0, 255).astype(np.uint8)
    
    hsv_pastel = cv2.merge([h, s_pastel, v_bright])
    combined_pastel = cv2.cvtColor(hsv_pastel, cv2.COLOR_HSV2BGR)
    
    # 5. Blend with a pale natural paper background (subdued beige/cream BGR: 235, 240, 248)
    paper_bg = np.zeros(img.shape, dtype=np.uint8)
    paper_bg[:] = [238, 244, 248]  # BGR for pale wood/cream paper
    
    final = cv2.addWeighted(combined_pastel, 0.75, paper_bg, 0.25, 0)
    
    # Save output
    is_success, im_buf_arr = cv2.imencode(".png", final)
    if is_success:
        try:
            with open(output_path, "wb") as f:
                f.write(im_buf_arr)
            print(f"Saved de-identified watercolor test to {output_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            
if __name__ == "__main__":
    test_filter()
