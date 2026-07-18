import cv2
import numpy as np
from pathlib import Path

def test_filter_v2():
    image_path = "output/截圖/screenshot_1.png"
    output_path = "output/test_watercolor_v2.png"
    
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
    
    # 1. Bilateral filter to smooth color details (removes photographic skin texture)
    watercolor = img.copy()
    for _ in range(3):
        watercolor = cv2.bilateralFilter(watercolor, d=9, sigmaColor=80, sigmaSpace=80)
        
    # 2. Softer sketch outline (larger Gaussian blur kernel to get thicker, artistic lines rather than sharp photo lines)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv_gray = 255 - gray
    # Larger kernel (35, 35) makes the outline softer and cartoon/drawing-like
    blurred_inv = cv2.GaussianBlur(inv_gray, (35, 35), 0)
    sketch_gray = cv2.divide(gray, 255 - blurred_inv, scale=256.0)
    
    # Smooth the lines to mimic a wet brush outline
    sketch_gray = cv2.GaussianBlur(sketch_gray, (5, 5), 0)
    sketch_3ch = cv2.merge([sketch_gray, sketch_gray, sketch_gray])
    
    # 3. Combine outline with smoothed watercolor colors
    combined = cv2.multiply(watercolor, sketch_3ch, scale=1.0/255.0)
    
    # 4. Desaturate greens by 60% and boost warm values slightly
    hsv = cv2.cvtColor(combined, cv2.COLOR_BGR2HSV)
    h_ch, s_ch, v_ch = cv2.split(hsv)
    
    # Target green tones (Hue 35-85)
    green_mask = cv2.inRange(hsv, (35, 30, 0), (85, 255, 255))
    s_green_reduced = np.where(green_mask > 0, (s_ch.astype(float) * 0.40).astype(np.uint8), s_ch)
    
    # Mute overall saturation slightly for a pastel look
    s_pastel = (s_green_reduced.astype(float) * 0.85).astype(np.uint8)
    v_bright = np.clip(v_ch.astype(float) * 1.05, 0, 255).astype(np.uint8)
    
    hsv_pastel = cv2.merge([h_ch, s_pastel, v_bright])
    combined_pastel = cv2.cvtColor(hsv_pastel, cv2.COLOR_HSV2BGR)
    
    # 5. Blend with pale natural paper background
    paper_bg = np.zeros(img.shape, dtype=np.uint8)
    paper_bg[:] = [238, 244, 248]  # pale wood/cream paper
    
    final = cv2.addWeighted(combined_pastel, 0.78, paper_bg, 0.22, 0)
    
    # Save output
    is_success, im_buf_arr = cv2.imencode(".png", final)
    if is_success:
        try:
            with open(output_path, "wb") as f:
                f.write(im_buf_arr)
            print(f"Saved soft watercolor test to {output_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            
if __name__ == "__main__":
    test_filter_v2()
