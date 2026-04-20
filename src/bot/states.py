"""
Conversation States (FSM)
==========================
State machine untuk mengatur alur percakapan bot.
"""

from enum import IntEnum, auto


class FreeReadState(IntEnum):
    """State untuk alur FREE basic read"""
    WAITING_NAME = auto()     # Bot minta nama
    WAITING_DOB = auto()      # Bot minta tanggal lahir
    PROCESSING = auto()       # Sedang hitung & generate


class ConsultationState(IntEnum):
    """State untuk alur konsultasi BERBAYAR"""
    WAITING_PAYMENT = auto()   # Menunggu pembayaran
    WAITING_PROBLEM = auto()   # Menunggu klien cerita masalah
    CHATTING = auto()          # Sesi aktif — boleh tanya jawab
