"""
Settings & Configuration
========================
Semua konfigurasi dari environment variables (.env file)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- TELEGRAM ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# --- GEMINI AI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://api.openai.com/v1")

# --- PRICING ---
CONSULTATION_PRICE = 99000  # Rp
COMMISSION_NEW_CLIENT = 20000  # Rp (one-time, klien baru)
COMMISSION_REPEAT = 10000  # Rp (setiap repeat order, lifetime)
SESSION_DURATION_HOURS = 48  # 2 hari

# --- MIDTRANS (optional, for later) ---
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY", "")
MIDTRANS_CLIENT_KEY = os.getenv("MIDTRANS_CLIENT_KEY", "")
MIDTRANS_IS_PRODUCTION = os.getenv("MIDTRANS_IS_PRODUCTION", "False").lower() == "true"
