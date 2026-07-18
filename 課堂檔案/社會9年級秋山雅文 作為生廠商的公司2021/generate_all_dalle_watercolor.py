import os
import sys
import time
import base64
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
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    home_env = Path(os.path.expanduser("~")) / ".env"
    if home_env.exists():
        with open(home_env, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None

def generate_with_dalle(slide_num, prompt, output_path):
    api_key = load_openai_key()
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment or ~/.env file.")
        return False
        
    print(f"Calling OpenAI DALL-E (gpt-image-2) for slide {slide_num}...")
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.images.generate(
            model="gpt-image-2",
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1
        )
        b64_data = response.data[0].b64_json
        if b64_data:
            image_data = base64.b64decode(b64_data)
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"[OK] Saved slide {slide_num} illustration to {output_path}")
            return True
        else:
            print(f"Error: No image b64_data returned for slide {slide_num}")
            return False
    except Exception as e:
        print(f"Error generating image for slide {slide_num}: {e}")
        return False

def main():
    # Character Settings
    teacher_desc = "a mature middle-aged Asian male teacher in his 40s with neat short black hair, wearing a professional grey suit and a light blue tie, with a warm and experienced smile"
    student_desc = "9th-grade junior high school students (around 14-15 years old), boys wearing dark blue school uniforms (gakuran) and girls wearing simple blue school uniforms with neat hairstyles"
    style_desc = "A beautiful warm Japanese watercolor picture book illustration, soft pencil outlines, gentle watercolor color wash, natural muted Morandi colors (soft sage green, warm cream wood, denim blue, light lavender), cute and simple anime character style with simple dot-and-line facial expressions (fully de-identified, no realistic portrait details). Clean classroom setting with warm ambient light. Completely exclude any masks and exclude any outer observing teachers."

    scenes = {
        1: f"a classroom opening scene, {teacher_desc} standing in front of a green blackboard welcoming students. The blackboard has '我們的生活與經濟 - 作為製造場域的企業的組織' written on it. {student_desc} are sitting at wooden desks looking forward.",
        2: f"context setting scene, {teacher_desc} pointing to a large paper poster showing company business simulation game rules on the classroom wall, {student_desc} listening attentively.",
        3: f"guideline setting scene, {teacher_desc} writing lesson study observation guidelines on a whiteboard, {student_desc} looking at him.",
        4: f"group decision work scene, a 4-person group of {student_desc} (two boys, two girls) sitting around a desk, writing on hiring and labor contracts, discussing eagerly.",
        5: f"micro-observation discussion scene, a group of {student_desc} (two boys, two girls) happily discussing and laughing together, pointing to a company balance sheet paper on their desk.",
        6: f"group reporting scene, a {student_desc} standing and writing company revenue metrics and numbers on a blackboard with chalk, the {teacher_desc} stands nearby watching.",
        7: f"micro-observation surprise scene, a group of {student_desc} looking at the blackboard with surprised and excited expressions, talking in whispers about their group's company performance.",
        8: f"group evaluation scene, {teacher_desc} pointing to comparison metrics of different student companies on the board, guiding a discussion on corporate profitability.",
        9: f"card sorting evaluation scene, a 4-person group of {student_desc} sorting cards labeled S, A, B, C on their desk, deciding their company's social rating.",
        10: f"micro-observation listening scene, a group of {student_desc} pointing to a business data table on a desk, discussing and listening intently to a classmate's explanation with empathetic posture.",
        11: f"sustainable reflection scene, {student_desc} writing down reflections and the word 'Sustainable' (永續經營) on their worksheets.",
        12: f"social rating evaluation scene, the blackboard covered with colorful S, A, B, C grade cards representing different student groups' social contributions.",
        13: f"student presentation scene, a {student_desc} representative standing at the front of the classroom, presenting group findings, while the class and {teacher_desc} listen.",
        14: f"student-subject relationship reflection scene, a close-up of a {student_desc} looking down and reading a business simulation worksheet intensely, focusing on learning.",
        15: f"student-peer relationship reflection scene, two {student_desc} talking face-to-face in a friendly group setting, sharing ideas and smiling.",
        16: f"student-prior knowledge relationship reflection scene, a {student_desc} writing reflection notes in a diary/worksheet with a pencil, thinking deeply.",
        17: f"teacher guidance scene, {teacher_desc} bending down next to a student desk, listening patiently and guiding a student's question.",
        18: f"total reflection scene, a wide view of the classroom with {student_desc} in groups of four, actively discussing and listening to each other.",
        19: f"class wrap-up scene, {teacher_desc} standing at the front summarizing the class, with {student_desc} looking forward and nodding attentively."
    }

    print("Starting generation of all 19 slides in Japanese Watercolor style...")
    total_slides = 19
    success_count = 0
    
    for i in range(1, total_slides + 1):
        prompt = f"{scenes[i]} {style_desc}"
        dest_path = f"output/繪圖/slide_{i}.png"
        
        # Call DALL-E (gpt-image-2)
        success = generate_with_dalle(i, prompt, dest_path)
        if success:
            success_count += 1
        else:
            print(f"[Warning] Failed to generate slide {i}")
            
        # Standard rate-limiting delay: wait 8 seconds between requests to avoid RPM limit
        if i < total_slides:
            print("Waiting 8 seconds to prevent rate limit...")
            time.sleep(8)
            
    print(f"All slides generation finished! Success rate: {success_count}/{total_slides}")
    if success_count == total_slides:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
