from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# One row per pour (choice, art, score). Kept as evidence of what
# customers chose; it holds no personal details.
SERVICE_LOG_PATH = BASE_DIR / "logs" / "service_log.csv"

# True while the GUI does not command the cobot: a staff member taps
# POUR FINISHED when the real pour is done. False runs the old 5 s
# simulated pour.
MANUAL_POUR_CONFIRM = True

# Seconds of no touches on the Home page before the attract screen shows.
ATTRACT_AFTER_SECONDS = 60
