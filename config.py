import os

class Config:
    # Flask cookie-session settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_key")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE","0") == "1"

    # Admin creds
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    # hash for password 'admin123'
    ADMIN_HASH = os.environ.get(
    "ADMIN_HASH",
    "scrypt:32768:8:1$tnNcdiJv02Hlu6v9Zc7d6f006721ec51e274f7294d7721b69bb74e459ce8b07f2bccf1534ff4ed60412bf79e715de1736f6042cab04cfce02c06af5fde2b206fd3c962d0b4a04"
    )

    # Data & logging
    DATA_DIR = "data"
    CSV_PATH = "data/metrics.csv"

    SAMPLE_INTERVAL_SEC = int(os.environ.get("SAMPLE_INTERVAL_SEC", 5))
    ALERT_COOLDOWN_SEC = int(os.environ.get("ALERT_COOLDOWN_SEC", 300))
    CSV_MAX_MB = int(os.environ.get("CSV_MAX_MB", 10))

    CPU_THRESH = float(os.environ.get("CPU_THRESH", 80))
    MEM_THRESH = float(os.environ.get("MEM_THRESH", 80))
    DISK_THRESH = float(os.environ.get("DISK_THRESH", 85))