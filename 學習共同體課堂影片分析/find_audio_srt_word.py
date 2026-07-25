import os

search_dir = "g:/我的雲端硬碟"
keywords = ["20260507", "503", "2qaBMMWbYDk", "qaTGAnbhpX4", "SCW-T9SxsrM"]

audio_exts = [".m4a", ".mp3", ".wav", ".mts", ".mp4"]
srt_exts = [".srt"]
word_exts = [".docx", ".doc", ".odt", ".gdoc"]

found_audio = []
found_srt = []
found_word = []

for root, dirs, files in os.walk(search_dir):
    for file in files:
        file_path = os.path.join(root, file)
        # Check if the filename contains any of the keywords
        if any(k in file for k in keywords):
            ext = os.path.splitext(file.lower())[1]
            if ext in audio_exts:
                found_audio.append(file_path)
            elif ext in srt_exts:
                found_srt.append(file_path)
            elif ext in word_exts:
                found_word.append(file_path)
        # Check if file path contains the keywords and matches extensions
        elif any(k in root for k in ["20260507503", "20260507"]):
            ext = os.path.splitext(file.lower())[1]
            if ext in audio_exts:
                found_audio.append(file_path)
            elif ext in srt_exts:
                found_srt.append(file_path)
            elif ext in word_exts:
                found_word.append(file_path)

# Write findings to a txt file
with open("found_media_files.txt", "w", encoding="utf-8") as f:
    f.write("=== Word Documents ===\n")
    for w in found_word:
        f.write(w + "\n")
    f.write("\n=== Audio/Video Files ===\n")
    for a in found_audio:
        f.write(a + "\n")
    f.write("\n=== SRT Subtitles ===\n")
    for s in found_srt:
        f.write(s + "\n")

print(f"Done. Found {len(found_word)} Word files, {len(found_audio)} Audio files, {len(found_srt)} SRT files.")
