# MangaDex Chapter Tracker

A lightweight Python script that monitors the [MangaDex](https://mangadex.org/) API for new manga chapter releases and sends real-time push notifications via Discord Webhooks.

---

## Features

- **Automated Polling**: Continuously checks the MangaDex API at a customizable interval.
- **Discord Push Notifications**: Sends formatted rich alerts with direct links when the target chapter drops.
- **Environment-based Configuration**: Keeps sensitive webhooks and parameters out of the code using `.env`.
- **Lightweight & Clean**: Minimal dependencies (`requests`, `python-dotenv`).

---

## Prerequisites

- **Python 3.8+**
- A **Discord Webhook URL** (optional, if you want notifications sent to a Discord channel)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shakedkun/check_chapter
   cd check_chapter
   ```

2. **Create and activate a virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Copy the sample environment file to create your local `.env`:

```bash
# Windows PowerShell
Copy-Item env_example .env

# macOS / Linux
cp env_example .env
```

Open `.env` and fill in your settings:

```env
# MangaDex Configuration
MANGA_ID=your-manga-id
MANGA_TITLE=your-manga-title
TARGET_CHAPTER=your-target-chapter
CHECK_INTERVAL_SECONDS=600

# Discord Notifications (Optional - leave blank to disable)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

### Configuration Options

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `MANGA_ID` | Yes | — | The MangaDex UUID for the manga series. |
| `MANGA_TITLE` | No | Series Title | Display name of the manga (used in logs and Discord alerts). |
| `TARGET_CHAPTER` | Yes | — | The chapter number you are waiting for (e.g. `33`). |
| `CHECK_INTERVAL_SECONDS` | No | `600` | How often to check for new chapters (in seconds; 600 = 10 mins). |
| `DISCORD_WEBHOOK_URL` | No | Empty | Discord Webhook URL for push notifications. |

### How to Find the MangaDex UUID
Navigate to the manga page on MangaDex in your browser. The URL format is:
```text
https://mangadex.org/title/<MANGA_ID>/<slug>
```
Example: In `https://mangadex.org/title/bb5f1b24-58a6-49e4-847b-a322c2addbd5/you-re-the-only-one-i-can-see`, the UUID is `bb5f1b24-58a6-49e4-847b-a322c2addbd5`.

### How to Get a Discord Webhook
1. Open Discord and go to your server's channel settings (gear icon).
2. Click **Integrations** > **Webhooks** > **New Webhook**.
3. Copy the webhook URL and paste it into `DISCORD_WEBHOOK_URL` in your `.env`.

---

## Usage

Run the tracking script:

```bash
python check_chapter.py
```

### Example Output

```text
Tracking Manga: You're the Only One I Can See
Waiting for Chapter: 33
Check Interval: 600 seconds
Discord notifications: Enabled
[23:19:26] Chapter 33 not yet uploaded. Retrying in 10 minutes...
```

When the chapter is found, an alert is sent to Discord and logged to the terminal:

```text
[23:29:30] New Chapter Alert!: Chapter 33 of *You're the Only One I Can See* is out on MangaDex!
Read here: https://mangadex.org/chapter/abcdef01-2345-6789-abcd-ef0123456789
```

---

## Run 24/7 in the Cloud (GitHub Actions)

This repository includes a pre-configured GitHub Actions workflow ([.github/workflows/check.yml](.github/workflows/check.yml)) that checks MangaDex automatically every 15 minutes for free.

### Setup Instructions:
1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Secrets and variables** > **Actions**.
3. Under **Repository secrets**, click **New repository secret**:
   - **Name:** `DISCORD_WEBHOOK_URL`
   - **Secret:** *(Paste your Discord Webhook URL)*
4. Under the **Actions** tab on GitHub, you can click **Check MangaDex Chapter** > **Run workflow** to test it immediately.
5. The workflow will run automatically every 15 minutes. Once the chapter is detected and the alert is posted, it automatically pauses the schedule so you don't get spammed.

---

## Project Structure

```text
check_chapter/
├── .github/workflows/
│   └── check.yml         # GitHub Actions scheduled 24/7 cron runner
├── .env                  # Local environment file with your settings (git-ignored)
├── .gitignore            # Git ignore file (prevents committing .env, venv, etc.)
├── check_chapter.py      # Main tracking and notification script
├── env_example           # Example template for environment variables
├── requirements.txt      # Python package dependencies
└── README.md             # Project documentation
```

---

## License

This project is licensed under the MIT License - feel free to modify and use it for your own tracking needs.
