.PHONY: dev cli-commenter auto-commenter auto-commenter-live lint lint-fix format check setup-cron remove-cron logs

# Development
dev:
	uv run main.py

# CLI Tools
cli-commenter:
	uv run -m app.scripts.cli_commenter

auto-commenter:
	uv run -m app.scripts.auto_commenter

auto-commenter-live:
	@echo "⚠️  WARNING: This will post REAL comments to Reddit!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || (echo "Aborted." && exit 1)
	uv run -m app.scripts.auto_commenter --live

# Code Quality
lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

check: lint format

# Automation
setup-cron:
	chmod +x scripts/daily_commenter.sh
	./scripts/daily_commenter.sh

remove-cron:
	crontab -l | grep -v "auto_commenter" | crontab - || true

logs:
	tail -f /tmp/temp.log