import os

# File monitoring settings
SCANNER_FILE_PATH = "scanner_data.txt"  # Path to the file where scanner writes data
FILE_FORMAT = "single_line"  # Options: "single_line", "csv"

# Box settings
BOX_CAPACITY = 12  # Number of items per box

# Sound settings
SOUND_SUCCESS = "sounds/success.wav"
SOUND_ERROR = "sounds/error.wav"
SOUND_BOX_FULL = "sounds/box_full.wav"

# Export settings
EXPORT_FILE = "export/boxes.xlsx"

# Create necessary directories
os.makedirs("sounds", exist_ok=True)
os.makedirs("export", exist_ok=True) 