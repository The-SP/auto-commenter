# Reddit Auto Commenter API

A FastAPI application that analyzes Reddit posts and generates contextual AI-powered comments with customizable tones.

## Getting Started

1. Clone the repository
2. Set up environment variables in `.env`:

   - Create a `.env` file and populate it with your actual API keys, using the `.env.sample` file as a template.

3. **Install dependencies:**
   - Using `uv`
     ```bash
     uv sync
     ```
   - Using `pip`
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -r pyproject.toml
     ```

## Run the Application

1. **Run locally:**
   ```bash
   uv run main.py
   ```
2. **Run with Docker:**
   ```bash
   docker-compose up
   ```

- The API will be accessible at `http://localhost:8000`.

## Command Line Tools

**Interactive CLI Commenter** (with human oversight):

```bash
cd backend
uv run -m app.scripts.cli_commenter
```

**Automated Commenter** (for scheduled/automatic posting):

```bash
cd backend
uv run -m app.scripts.auto_commenter        # dry run mode (default)
uv run -m app.scripts.auto_commenter --live # live posting mode
```

## Scheduled Automation

**Set up daily automated commenting:**

```bash
cd backend
chmod +x ./scripts/daily_commenter.sh
./scripts/daily_commenter.sh  # Sets up daily cron job at 7:00 AM
```

The script will automatically run `auto_commenter.py` daily, posting AI-generated comments to random subreddits. Monitor activity with:

```bash
tail -f /tmp/temp.log
```

**Stop the cron job:**

```bash
crontab -e  # Remove the auto_commenter line and save
# Or remove all cron jobs: crontab -r
```

---

## Project Structure

```
backend/
├── main.py                     # FastAPI application entry point
├── scripts/                    # Shell scripts for automation
│   ├── daily_commenter.sh
│   └── test_bot.sh
└── app/
    ├── api/                    # API routes and models
    ├── core/                   # Configuration and utilities
    ├── services/               # External service integrations
    └── scripts/                # Python CLI tools
        ├── auto_commenter.py
        └── cli_commenter.py
```
