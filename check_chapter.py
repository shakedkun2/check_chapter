import os
from pathlib import Path
import time
import requests
from dotenv import load_dotenv


import sys

# Determine base directory (handles running as script or as PyInstaller .exe)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

env_file = BASE_DIR / ".env"

# Load environment variables from .env file if available
try:
    load_dotenv(dotenv_path=env_file)
except ImportError:
    # Basic fallback parser if python-dotenv is not installed
    if env_file.is_file():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val

# MangaDex configuration
MANGA_ID = os.getenv("MANGA_ID", "bb5f1b24-58a6-49e4-847b-a322c2addbd5")
MANGA_TITLE = os.getenv("MANGA_TITLE", "You're the Only One I Can See")
TARGET_CHAPTER = os.getenv("TARGET_CHAPTER", "33")
try:
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "600"))
except ValueError:
    CHECK_INTERVAL_SECONDS = 600

# Discord Webhook URL for push notifications (configured in .env)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

# Set CHECK_ONCE=true to run a single check cycle (ideal for cron jobs like GitHub Actions)
CHECK_ONCE = os.getenv("CHECK_ONCE", "false").lower() in ("true", "1", "yes")


def notify(title: str, message: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {title}: {message}")
    
    if DISCORD_WEBHOOK_URL:
        try:
            payload = {"content": f"📢 **{title}**\n{message}"}
            requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        except requests.RequestException as err:
            print(f"Failed to post to Discord: {err}")


def get_latest_english_chapters(manga_id: str):
    url = f"https://api.mangadex.org/manga/{manga_id}/feed"
    params = {
        "translatedLanguage[]": ["en"],
        "order[chapter]": "desc",
        "limit": 5,
    }
    headers = {
        # MangaDex requires/recommends a custom User-Agent identifying your client
        "User-Agent": "MangaAlertScript/1.0 (ChapterTracker)"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    return response.json().get("data", [])


def monitor():
    print(f"Tracking Manga: {MANGA_TITLE}")
    print(f"Waiting for Chapter: {TARGET_CHAPTER}")
    print(f"Check Interval: {CHECK_INTERVAL_SECONDS} seconds")
    if DISCORD_WEBHOOK_URL:
        print("Discord notifications: Enabled")
    else:
        print("Discord notifications: Disabled (no DISCORD_WEBHOOK_URL configured)")

    retry_interval_desc = (
        f"{CHECK_INTERVAL_SECONDS // 60} minutes"
        if CHECK_INTERVAL_SECONDS >= 60 and CHECK_INTERVAL_SECONDS % 60 == 0
        else f"{CHECK_INTERVAL_SECONDS} seconds"
    )

    while True:
        try:
            chapters = get_latest_english_chapters(MANGA_ID)
            
            for ch in chapters:
                attributes = ch.get("attributes", {})
                chapter_num = attributes.get("chapter")
                chapter_id = ch.get("id")

                if chapter_num == TARGET_CHAPTER:
                    chapter_url = f"https://mangadex.org/chapter/{chapter_id}"
                    notify(
                        "New Chapter Alert!",
                        f"Chapter {TARGET_CHAPTER} of *{MANGA_TITLE}* is out on MangaDex!\nRead here: {chapter_url}",
                    )
                    # Notify GitHub Actions if running inside workflow
                    if os.getenv("GITHUB_OUTPUT"):
                        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                            f.write("chapter_found=true\n")
                    return  # Stop once found (remove this return to keep polling indefinitely)
            
            print(f"[{time.strftime('%H:%M:%S')}] Chapter {TARGET_CHAPTER} not yet uploaded. Retrying in {retry_interval_desc}...")

        except requests.RequestException as e:
            print(f"Network/API Error: {e}")

        if CHECK_ONCE:
            if os.getenv("GITHUB_OUTPUT"):
                with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
                    f.write("chapter_found=false\n")
            return

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    finally:
        if getattr(sys, "frozen", False):
            input("\nPress Enter to exit...")