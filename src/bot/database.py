"""
Database handler — Supabase Integration
========================================
Menghubungkan bot dengan Supabase untuk menyimpan 
dan menarik memori secara permanen.
"""

import logging
from supabase import create_client, Client
import json
import os

logger = logging.getLogger(__name__)

# Konfigurasi Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase URL atau Key tidak ditemukan. Menggunakan fallback memori lokal (RAM).")
    supabase = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Gagal koneksi ke Supabase: {e}")
        supabase = None


# Fallback lokal jika Supabase bermasalah/belum disetup
_local_memory = {}

def get_user_reading(telegram_id: int) -> dict:
    """Ambil data dari Supabase berdasarkan telegram_id"""
    if supabase is None:
        return _local_memory.get(telegram_id)
        
    try:
        response = supabase.table("clients").select("*").eq("telegram_id", telegram_id).execute()
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            # Pastikan format reading kembali ke int dictionary jika perlu
            return {
                'nama': user_data['nama'],
                'dob': user_data['dob'],
                'reading': user_data['reading_data'], # format JSON dalam db
                'referral': user_data.get('referral_code')
            }
        return None
    except Exception as e:
        logger.error(f"Gagal mengambil obrolan klien {telegram_id}: {e}")
        return _local_memory.get(telegram_id)


def save_user_reading(telegram_id: int, nama: str, dob: str, reading_data: dict, referral: str = None) -> bool:
    """Simpan atau perbarui data ke Supabase"""
    
    # Update memori lokal sebagai backup
    _local_memory[telegram_id] = {
        'nama': nama,
        'dob': dob,
        'reading': reading_data,
        'referral': referral
    }
    
    if supabase is None:
        return True
        
    try:
        payload = {
            "telegram_id": telegram_id,
            "nama": nama,
            "dob": dob,
            "reading_data": reading_data,
            "referral_code": referral
        }
        
        # Upsert: kalau belum ada akan Insert, kalau ada akan Update.
        response = supabase.table("clients").upsert(payload, returning="minimal").execute()
        return True
    except Exception as e:
        logger.error(f"Gagal menyimpan data klien {telegram_id}: {e}")
        return False
