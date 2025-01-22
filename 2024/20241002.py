#file: screen_time_standalone_V-current.py
#initial version by Grok 2mini

import shutil
import os
from pathlib import Path
from datetime import datetime

# Define original database path
db_path = Path.home() / "Library/Application Support/Knowledge/knowledgeC.db"

# Get current date and time in the format YYYYMMDD_HHMM
current_time = datetime.now().strftime("%Y%m%d_%H%M")

# Define path for the copy with current timestamp
export_path = Path.home() / "Downloads" / f"knowledgeC_export_{current_time}.db"

# Copy the entire database file to a new location with the timestamp
try:
    shutil.copy2(db_path, export_path)
    # Get file size in bytes
    file_size_bytes = os.path.getsize(str(export_path))
    # Convert bytes to megabytes
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    print(f"Database copied to {export_path}")
    print(f"Database size: {file_size_mb:.2f} MB")
    print("You can now manually open this file with SQLiteStudio to explore all tables.")
except FileNotFoundError:
    print(f"Database not found at {db_path}. Please ensure the path is correct.")
except PermissionError:
    print(f"Permission denied. Check if you have the rights to access or copy {db_path}.")
except Exception as e:
    print(f"An error occurred: {e}")
