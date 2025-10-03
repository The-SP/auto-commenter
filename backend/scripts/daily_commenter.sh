#!/bin/bash

FILENAME="app/scripts/auto_commenter.py"

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo "❌ Error: $FILENAME not found"
    exit 1
fi

# Make executable
chmod +x "$FILENAME"

# Add to crontab (runs daily at 7 AM)
echo "0 7 * * * cd $(pwd) && .venv/bin/python -m app.scripts.auto_commenter --live >> /tmp/temp.log 2>&1" | crontab -

echo "✅ Done! $FILENAME will run daily at 7:00 AM"
echo "Monitor: tail -f /tmp/temp.log"
