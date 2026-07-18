import os
import sys
from pathlib import Path
try:
    import openai
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "openai"], capture_output=True)
    import openai

def main():
    # Load key
    key = None
    home_env = Path(os.path.expanduser("~")) / ".env"
    if home_env.exists():
        with open(home_env, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    key = line.strip().split("=", 1)[1]
                    
    if not key:
        print("No key found")
        return 1
        
    client = openai.OpenAI(api_key=key)
    try:
        models = client.models.list()
        print("Available models:")
        for m in models.data:
            if "dall" in m.id or "gpt" in m.id:
                print("  ", m.id)
    except Exception as e:
        print("Error listing models:", e)
    return 0

if __name__ == "__main__":
    sys.exit(main())
