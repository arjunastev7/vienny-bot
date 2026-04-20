"""
Quick Test — Jalankan ini untuk langsung lihat hasil formula.
Caranya: buka PowerShell → python quick_test.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.formulas.manutiras import calculate


def test_one(nama, dob, expected_label=""):
    """Test satu nama dan tampilkan hasilnya."""
    print(f"\n{'='*60}")
    print(f"  {nama}")
    print(f"  DOB: {dob}  {expected_label}")
    print(f"{'='*60}")

    r = calculate(nama, dob)
    d = r.to_dict()

    print(f"  TIME         : {r.time_str}")
    print(f"  Acoustic Root: {r.ar_str}")
    print(f"  Heart Desire : {r.hd_str}")
    print(f"  Personality  : {r.personality_str}")
    print(f"  Balance      : {r.balance_str}")
    print(f"  Maturity     : {r.maturity_str}")
    print(f"  FMEI         : F={r.fmei_f} M={r.fmei_m} E={r.fmei_e} I={r.fmei_i}")
    print(f"  Karmic Grid  : {r.karmic_grid}")
    print(f"  Karmic Lesson: angka {r.karmic_lessons} (energi yang hilang)")
    print(f"  Sync Bracket : [{r.sync_bracket}]")
    print()


if __name__ == "__main__":
    print("\n🔮 MANUTIRAS FORMULA ENGINE — Quick Test")
    print("=========================================\n")

    # ─── Data yang sudah TERVERIFIKASI 100% ───────────────────

    test_one("Vienny Aulia Zahra", "02/11/1988",
             "(expected: T=21/3, AR=25/7, HD=10/1, P=15/6, B=13/4, M=1)")

    test_one("Panji Wellyanto", "27/09/1989",
             "(expected: T=27/9, AR=6, HD=2, P=13/4, B=12/3, M=15/6)")

    test_one("Naora Novanty Shadzani", "22/11/2014",
             "(expected: T=40/4, AR=26/8, HD=24/6, P=20/2, B=11, M=12/3)")

    test_one("Zayn Mohammad Dian Aulia", "28/01/2023",
             "(expected: T=9/9, AR=17/8, HD=22, P=22, B=17/8, M=17/8)")

    test_one("Nova Puspitasari", "15/11/1990",
             "(expected: T=18/9, AR=12/3, HD unverified)")

    test_one("Erny Dwi Lestari", "25/11/1999",
             "(expected: T=19/1, AR=20/2)")

    test_one("Chintya Elta Ridayanti", "21/08/1999",
             "(expected: T=12/3, AR=30/3, Sync=[0])")

    test_one("Falysha Aviena Hakim", "11/04/2024",
             "(expected: T=23/5, AR=22 master, B=15/6)")

    # ─── Coba nama BARU (belum ada di data) ──────────────────

    print("\n🆕 TEST NAMA BARU (hasil bisa kamu cek manual):")
    print("=" * 60)

    test_one("Sari Dewi Purnama", "01/05/1995", "(nama baru — cek manual)")

    print("\n✅ SELESAI! Kalau hasil di atas cocok dengan expected → formula BENAR.")
    print("Kalau ada yang tidak cocok → screenshot dan kirim ke Antigravity.")
