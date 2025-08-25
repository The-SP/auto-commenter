# Reddit Auto Commenter API

A FastAPI application that analyzes Reddit posts and generates contextual AI-powered comments with customizable tones.

## Getting Started

1. Clone the repository
2. Set up environment variables in `.env`:

   - Create a `.env` file and populate it with your actual API keys, using the .env.sample file as a template.

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
uv run -m app.cli_commenter
```

**Automated Commenter** (for scheduled/automatic posting):

```bash
cd backend
uv run -m app.auto_commenter        # dry run mode (default)
uv run -m app.auto_commenter --live # live posting mode
```
