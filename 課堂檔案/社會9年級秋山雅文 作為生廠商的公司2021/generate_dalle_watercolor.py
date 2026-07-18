import os
import sys
import urllib.request
from pathlib import Path

# Ensure openai is installed
try:
    import openai
except ImportError:
    print("Installing openai python package...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "openai"], capture_output=True)
    import openai

def load_openai_key():
    # Try to load from environment
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
        
    # Try to load from ~/.env
    home_env = Path(os.path.expanduser("~")) / ".env"
    if home_env.exists():
        with open(home_env, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]
                    
    # Try to load from workspace .env
    workspace_env = Path(".env")
    if workspace_env.exists():
        with open(workspace_env, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def generate_with_dalle(slide_num, prompt, output_path):
    api_key = load_openai_key()
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment or ~/.env file.")
        return False
        
    print(f"Calling OpenAI DALL-E 3 for slide {slide_num}...")
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.images.generate(
            model="gpt-image-2",
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1
        )
        import base64
        b64_data = response.data[0].b64_json
        if b64_data:
            print("Image generated! Decoding base64 data...")
            image_data = base64.b64decode(b64_data)
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"[OK] Saved slide {slide_num} illustration to {output_path}")
            return True
        else:
            print("Error: No image URL or b64_json returned from API.")
            return False
    except Exception as e:
        print(f"Error generating image for slide {slide_num}: {e}")
        return False

def main():
    prompts = {
        5: "A beautiful warm Japanese watercolor picture book illustration of three junior high school students happily discussing and laughing together, pointing to a sheet of paper on the desk, soft pencil outlines, gentle watercolor color wash, natural muted Morandi colors (soft sage green, warm cream wood, denim blue, light lavender), cute and simple anime character style with simple dot-and-line facial expressions (fully de-identified, no realistic portrait details). Clean classroom setting with warm ambient light. Completely exclude any masks and exclude any outer observing teachers.",
        10: "A beautiful warm Japanese watercolor picture book illustration of three junior high school students pointing to a data table on a desk, discussing and listening intently to a peer's explanation, soft pencil outlines, gentle watercolor color wash, natural muted Morandi colors (soft sage green, warm cream wood, denim blue, light lavender), cute and simple anime character style with simple dot-and-line facial expressions (fully de-identified, no realistic portrait details). Clean classroom setting with warm ambient light. Completely exclude any masks and exclude any outer observing teachers."
    }
    
    target_slides = [5, 10]
    success_count = 0
    
    for slide_num in target_slides:
        prompt = prompts[slide_num]
        dest = f"output/繪圖/slide_{slide_num}.png"
        success = generate_with_dalle(slide_num, prompt, dest)
        if success:
            success_count += 1
            
    print(f"Re-generation finished. Success: {success_count}/{len(target_slides)}")
    if success_count > 0:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
