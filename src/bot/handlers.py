"""
Bot Handlers — Telegram Conversation Flow
==========================================
Alur percakapan bot:
  /start → tanya nama → tanya DOB → hitung formula → Gemini generate → kirim
  /konsultasi → cek subscription → terima masalah → Gemini jawab
  /raport → (agen only) tampilkan raport komisi
  /laporan → (admin only) tampilkan semua agen
"""

import re
import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

from src.formulas.manutiras import calculate as calc_manutiras
from src.ai.interpreter import generate_free_reading, generate_consultation_reply
from src.bot.states import FreeReadState, ConsultationState
from config.settings import ADMIN_TELEGRAM_ID
from src.bot.database import get_user_reading, save_user_reading

logger = logging.getLogger(__name__)

# ─── STORAGE ──────────────────────────────────────────────────────────────────
# Data dikelola via src/bot/database.py (Supabase)


# ─── HELPER ────────────────────────────────────────────────────────────────────

def validate_dob(text: str) -> bool:
    """Validasi format DD/MM/YYYY"""
    pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
    if not re.match(pattern, text.strip()):
        return False
    try:
        parts = text.strip().split('/')
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030):
            return False
        return True
    except (ValueError, IndexError):
        return False


def normalize_dob(text: str) -> str:
    """Normalize ke format DD/MM/YYYY (dengan leading zero)"""
    parts = text.strip().split('/')
    day = parts[0].zfill(2)
    month = parts[1].zfill(2)
    year = parts[2]
    return f"{day}/{month}/{year}"


# ─── /start — FREE BASIC READ ─────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler /start — sambut user dan minta nama."""

    # Cek apakah ada referral code di parameter
    if context.args:
        referral_code = context.args[0]
        context.user_data['referral'] = referral_code
        logger.info(f"User {update.effective_user.id} datang via referral: {referral_code}")

    await update.message.reply_text(
        "Halo, selamat datang 🌙\n\n"
        "Aku bisa membantu kamu membaca energi yang tersimpan "
        "dalam nama dan tanggal lahirmu.\n\n"
        "Hasilnya langsung, tanpa perlu menunggu.\n\n"
        "Boleh aku tahu nama lengkapmu?\n"
        "(Sesuai KTP ya, termasuk nama tengah kalau ada)",
        reply_markup=ReplyKeyboardRemove()
    )
    return FreeReadState.WAITING_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Terima nama, lalu minta tanggal lahir."""
    nama = update.message.text.strip()

    # Validasi: minimal 2 huruf, hanya alphabet dan spasi
    if len(nama) < 2 or not all(c.isalpha() or c.isspace() for c in nama):
        await update.message.reply_text(
            "Hmm, sepertinya ada yang kurang tepat. "
            "Boleh kirim nama lengkapmu dengan huruf saja ya? "
            "(tanpa angka atau simbol)"
        )
        return FreeReadState.WAITING_NAME

    context.user_data['nama'] = nama
    await update.message.reply_text(
        f"Terima kasih, {nama.split()[0]} 😊\n\n"
        "Sekarang boleh aku tahu tanggal lahirmu?\n"
        "Format: DD/MM/YYYY\n"
        "Contoh: 02/11/1988"
    )
    return FreeReadState.WAITING_DOB


async def receive_dob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Terima DOB, hitung formula, generate reading via Gemini."""
    dob_text = update.message.text.strip()

    if not validate_dob(dob_text):
        await update.message.reply_text(
            "Format tanggal belum tepat. "
            "Coba kirim ulang dengan format DD/MM/YYYY ya.\n"
            "Contoh: 15/03/1995"
        )
        return FreeReadState.WAITING_DOB

    dob = normalize_dob(dob_text)
    nama = context.user_data.get('nama', 'Sahabat')

    # Kirim pesan "sedang membaca..."
    thinking_msg = await update.message.reply_text(
        f"Sebentar ya, aku sedang membaca energi dari {nama.split()[0]}... ✨"
    )

    try:
        # 1. Hitung formula Manutiras (< 1 detik)
        result = calc_manutiras(nama, dob)
        data = result.to_dict()

        # Simpan ke Database Supabase
        user_id = update.effective_user.id
        referral = context.user_data.get('referral', None)
        save_user_reading(user_id, nama, dob, data, referral)

        # 2. Generate reading via Gemini
        reading_text = await generate_free_reading(data)

        # 3. Kirim hasil
        await thinking_msg.delete()
        await update.message.reply_text(reading_text)

        # 4. CTA untuk konsultasi
        await update.message.reply_text(
            "─────────────────\n\n"
            "Itu baru permukaannya 💫\n\n"
            "Kalau kamu mau ngobrol lebih dalam — "
            "soal karir, jodoh, keputusan besar, atau apapun "
            "yang sedang kamu hadapi — aku siap menemani.\n\n"
            "Ketik /konsultasi untuk memulai sesi pribadi."
        )

    except Exception as e:
        logger.error(f"Error processing reading: {e}", exc_info=True)
        await thinking_msg.delete()
        await update.message.reply_text(
            "Mohon maaf, ada kendala saat membaca energimu. "
            "Coba ulangi dari awal dengan ketik /start ya 🙏"
        )

    return ConversationHandler.END


# ─── /konsultasi — PAID CHAT ──────────────────────────────────────────────────

async def cmd_konsultasi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handler /konsultasi — cek apakah sudah bayar atau belum."""
    user_id = update.effective_user.id

    # Phase 1: SKIP payment check — langsung aktif (untuk testing)
    # Phase 2: tambahkan pengecekan Midtrans payment di sini

    # Cek Database Supabase
    user = get_user_reading(user_id)
    if not user or not user.get('reading'):
        await update.message.reply_text(
            "Sepertinya kamu belum pernah membaca energi namamu.\n"
            "Ketik /start dulu ya, supaya aku bisa mengenalmu lebih baik 😊"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Selamat datang di sesi konsultasi 🌙\n\n"
        "Di sini kamu bisa cerita apapun yang sedang kamu hadapi — "
        "soal karir, hubungan, keputusan besar, atau hal yang "
        "membuatmu gelisah.\n\n"
        "Cerita aja dulu. Aku mendengarkan.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConsultationState.CHATTING


async def receive_consultation_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Terima pesan konsultasi, jawab via Gemini."""
    user_id = update.effective_user.id
    masalah = update.message.text.strip()

    # Cek Database
    user = get_user_reading(user_id)
    if not user or not user.get('reading'):
        await update.message.reply_text(
            "Ketik /start dulu ya supaya aku bisa mengenalmu. 😊"
        )
        return ConversationHandler.END

    # Kirim "sedang berpikir..."
    thinking = await update.message.reply_text("Aku sedang merenungkan apa yang kamu sampaikan... 🌙")

    try:
        # Ambil chat history dari context
        history = context.user_data.get('chat_history', '')
        history += f"\nKlien: {masalah}\n"

        # Generate jawaban via Gemini
        reply = await generate_consultation_reply(
            data=user['reading'],
            masalah=masalah,
            chat_history=history
        )

        # Simpan history
        history += f"Konsultan: {reply}\n"
        context.user_data['chat_history'] = history

        await thinking.delete()
        await update.message.reply_text(reply)

        await update.message.reply_text(
            "Ada lagi yang mau kamu tanyakan? "
            "Aku masih di sini 💙\n\n"
            "Ketik /selesai kalau sudah cukup."
        )

    except Exception as e:
        logger.error(f"Error in consultation: {e}", exc_info=True)
        await thinking.delete()
        await update.message.reply_text(
            "Mohon maaf, ada kendala. Coba kirim ulang pesanmu ya 🙏"
        )

    return ConsultationState.CHATTING


async def cmd_selesai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Akhiri sesi konsultasi."""
    context.user_data.pop('chat_history', None)
    await update.message.reply_text(
        "Terima kasih sudah berbagi ceritamu hari ini 🌙\n\n"
        "Semoga apa yang kita obrolan bisa memberi sedikit ketenangan "
        "dan kejelasan untukmu.\n\n"
        "Kapanpun kamu butuh, aku ada di sini.\n"
        "Ketik /start untuk membaca energi nama baru,\n"
        "atau /konsultasi untuk ngobrol lagi.\n\n"
        "Jaga dirimu baik-baik ya 💙"
    )
    return ConversationHandler.END


# ─── /help ─────────────────────────────────────────────────────────────────────

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tampilkan bantuan."""
    await update.message.reply_text(
        "🌙 Vienny Metafisika\n\n"
        "Perintah yang tersedia:\n\n"
        "/start — Baca energi nama & tanggal lahirmu (gratis)\n"
        "/konsultasi — Sesi tanya jawab pribadi\n"
        "/selesai — Akhiri sesi konsultasi\n"
        "/help — Tampilkan bantuan ini"
    )


# ─── FALLBACK ──────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    await update.message.reply_text(
        "Oke, tidak apa-apa 😊\n"
        "Ketik /start kapanpun kamu siap.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ─── BUILD BOT ─────────────────────────────────────────────────────────────────

def create_bot(token: str) -> Application:
    """Buat instance bot dengan semua handler."""

    app = Application.builder().token(token).build()

    # ─── Conversation: Free Read ─────────────────────────────
    free_read_handler = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            FreeReadState.WAITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)
            ],
            FreeReadState.WAITING_DOB: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_dob)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    # ─── Conversation: Konsultasi ─────────────────────────────
    consultation_handler = ConversationHandler(
        entry_points=[CommandHandler("konsultasi", cmd_konsultasi)],
        states={
            ConsultationState.CHATTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_consultation_message),
                CommandHandler("selesai", cmd_selesai),
            ],
        },
        fallbacks=[
            CommandHandler("selesai", cmd_selesai),
            CommandHandler("cancel", cancel),
        ],
        allow_reentry=True,
    )

    # ─── Register handlers ───────────────────────────────────
    app.add_handler(free_read_handler)
    app.add_handler(consultation_handler)
    app.add_handler(CommandHandler("help", cmd_help))

    return app
