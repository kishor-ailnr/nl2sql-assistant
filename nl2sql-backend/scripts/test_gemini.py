"""Test script for Gemini API integration.
Sends a single basic prompt and prints the response.
Tries gemini-2.0-flash, and falls back to gemini-3.6-flash / gemini-flash-latest
if gemini-2.0-flash has been deprecated by the API.
"""

import os
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=FutureWarning)

# Ensure paths
BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent

# Load .env (local nl2sql-backend/.env or workspace root .env)
env_path = BASE_DIR / ".env"
if not env_path.exists() and (WORKSPACE_DIR / ".env").exists():
    env_path = WORKSPACE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key or not api_key.strip():
    print("ERROR: GEMINI_API_KEY is not set or is empty in .env!", file=sys.stderr)
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai is not installed. Please run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)


def main():
    masked_key = f"{api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}"
    print(f"Loaded GEMINI_API_KEY: {masked_key}")
    print("Configuring Gemini client...")
    genai.configure(api_key=api_key)

    prompt = input("Enter your question: ")
    models_to_try = ["gemini-2.0-flash", "gemini-3.6-flash", "gemini-flash-latest"]

    for model_name in models_to_try:
        print(f"\nAttempting model '{model_name}'...")
        try:
            model = genai.GenerativeModel(model_name)
            print(f"Sending prompt: '{prompt}'")
            response = model.generate_content(prompt)
            print("\n--- Gemini Response ---")
            print(response.text.strip())
            print("-----------------------")
            print(f"\n[SUCCESS] Successfully received response using '{model_name}'.")
            return
        except Exception as e:
            err_msg = str(e)
            if "404" in err_msg or "not found" in err_msg.lower():
                print(f"[NOTE] Model '{model_name}' is not available/deprecated: {e}")
                print("Falling back to next available model...")
                continue
            else:
                print(f"[ERROR] API request failed: {e}", file=sys.stderr)
                sys.exit(1)

    print("[ERROR] Could not obtain a response from any attempted models.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
