#!/bin/bash

FILENAME="app/auto_commenter.py"

# Check if file exists
if [ ! -f "$FILENAME" ]; then
    echo "❌ Error: $FILENAME not found"
    exit 1
fi

# Make executable
chmod +x "$FILENAME"

# Add to crontab (runs every minute)
echo "* * * * * cd $(pwd) && .venv/bin/python -m app.auto_commenter >> /tmp/temp.log 2>&1" | crontab -

echo "✅ Done! $FILENAME will run every minute"
echo "Monitor: tail -f /tmp/temp.log"
