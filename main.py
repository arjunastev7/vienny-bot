"""
Vienny Metafisika Bot — Main Entry Point
==========================================
Jalankan: python main.py
"""

import logging
import sys

from config.settings import TELEGRAM_BOT_TOKEN
from src.bot.handlers import create_bot


def main():
    # ─── Logging ──────────────────────────────────────────────
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)

    # ─── Validasi token ───────────────────────────────────────
    if not TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN belum diisi!\n"
            "Buat file .env di folder proyek dan isi:\n"
            "  TELEGRAM_BOT_TOKEN=token_dari_botfather\n"
            "  GEMINI_API_KEY=api_key_dari_google\n"
            "  ADMIN_TELEGRAM_ID=telegram_id_kamu"
        )
        sys.exit(1)

    # ─── Start bot ────────────────────────────────────────────
    logger.info("Memulai Vienny Metafisika Bot...")
    app = create_bot(TELEGRAM_BOT_TOKEN)
    logger.info("Bot siap! Tekan Ctrl+C untuk menghentikan.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
