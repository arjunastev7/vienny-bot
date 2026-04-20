"""
Unit Tests — Manutiras Formula Engine
========================================
Test cases dari data sampel yang sudah terverifikasi 100%.
Jalankan: python -m pytest tests/test_manutiras.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.formulas.manutiras import calculate


# ─── TEST CASES (dari verified data) ──────────────────────────────────────────

class TestTime:
    """Verifikasi formula TIME dari 5 kasus + 6 kasus dataset kedua"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.time_str == "21/3", f"TIME: {r.time_str}"

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.time_str == "27/9"

    def test_naora_shadzani(self):
        r = calculate("Naora Novanty Shadzani", "22/11/2014")
        assert r.time_str == "40/4"

    def test_zayn(self):
        r = calculate("Zayn Mohammad Dian Aulia", "28/01/2023")
        # raw=9, reduced=9 → format: "9" (app shows "9/9" tapi nilai sama)
        assert r.time_raw == 9
        assert r.time_reduced == 9

    def test_nova(self):
        r = calculate("Nova Puspitasari", "15/11/1990")
        assert r.time_str == "18/9"

    def test_erny(self):
        r = calculate("Erny Dwi Lestari", "25/11/1999")
        assert r.time_str == "19/1"

    def test_mikayla(self):
        # 22+8+3=33 → master number dipertahankan di reduced juga
        r = calculate("Mikayla Sarada Azkadina", "22/08/2019")
        assert r.time_raw == 33
        assert r.time_reduced == 33  # 33 = master, tidak di-reduce ke 6

    def test_halvyna(self):
        r = calculate("Halvyna Faizan Hakim", "12/04/2024")
        assert r.time_str == "15/6"

    def test_falysha(self):
        # Day 11 = master number
        r = calculate("Falysha Aviena Hakim", "11/04/2024")
        assert r.time_str == "23/5"


class TestAR:
    """Verifikasi formula Acoustic Root"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.ar_str == "25/7"

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.ar_str == "6"

    def test_nova(self):
        r = calculate("Nova Puspitasari", "15/11/1990")
        assert r.ar_str == "12/3"

    def test_falysha_master(self):
        # AR = 22 (master)
        r = calculate("Falysha Aviena Hakim", "11/04/2024")
        assert r.ar_str == "22"

    def test_naora_shadzani(self):
        r = calculate("Naora Novanty Shadzani", "22/11/2014")
        assert r.ar_str == "26/8"

    def test_zayn(self):
        r = calculate("Zayn Mohammad Dian Aulia", "28/01/2023")
        assert r.ar_str == "17/8"


class TestHeartDesire:
    """Verifikasi formula Heart Desire (vokal + Y)"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.hd_str == "10/1"

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.hd_str == "2"

    def test_naora_novia(self):
        r = calculate("Naora novia amanda", "22/11/2014")
        assert r.hd_str == "18/9"

    def test_zayn_master(self):
        # HD = 22 (master)
        r = calculate("Zayn Mohammad Dian Aulia", "28/01/2023")
        assert r.hd_str == "22"

    def test_erny_y_as_vowel(self):
        # Erny: Y dihitung vokal
        r = calculate("Erny Dwi Lestari", "25/11/1999")
        assert r.hd_str == "18/9"


class TestPersonality:
    """Verifikasi formula Personality (konsonan, Y bukan konsonan)"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.personality_str == "15/6"

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.personality_str == "13/4"

    def test_zayn_master(self):
        r = calculate("Zayn Mohammad Dian Aulia", "28/01/2023")
        assert r.personality_str == "22"

    def test_naora_novia(self):
        r = calculate("Naora novia amanda", "22/11/2014")
        assert r.personality_str == "18/9"


class TestBalance:
    """Verifikasi formula Balance (huruf pertama setiap kata)"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.balance_str == "13/4"

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.balance_str == "12/3"

    def test_nova(self):
        r = calculate("Nova Puspitasari", "15/11/1990")
        assert r.balance_str == "12/3"

    def test_halvyna_master(self):
        # H(8) + F(6) + H(8) = 22
        r = calculate("Halvyna Faizan Hakim", "12/04/2024")
        assert r.balance_str == "22"

    def test_naora_shadzani_master(self):
        # N(5) + N(5) + S(1) = 11
        r = calculate("Naora Novanty Shadzani", "22/11/2014")
        assert r.balance_str == "11"


class TestMaturity:
    """Verifikasi formula Maturity = TIME + AR"""

    def test_vienny(self):
        # TIME=3, AR=7 → 3+7=10→1
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.maturity_raw == 10
        assert r.maturity_reduced == 1

    def test_panji(self):
        # TIME=9, AR=6 → 15→6
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.maturity_str == "15/6"

    def test_nova(self):
        # TIME=9, AR=3 → 12→3
        r = calculate("Nova Puspitasari", "15/11/1990")
        assert r.maturity_str == "12/3"


class TestFMEI:
    """Verifikasi formula FMEI Classification"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.fmei_f == 4
        assert r.fmei_m == 6
        assert r.fmei_e == 2
        assert r.fmei_i == 4

    def test_zayn(self):
        r = calculate("Zayn Mohammad Dian Aulia", "28/01/2023")
        assert r.fmei_f == 7
        assert r.fmei_m == 8
        assert r.fmei_e == 3
        assert r.fmei_i == 3

    def test_fmei_sum_equals_total_letters(self):
        """Cross-check: F+M+E+I = total huruf dalam nama"""
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        total = r.fmei_f + r.fmei_m + r.fmei_e + r.fmei_i
        name_len = len("ViennyAuliaZahra")  # tanpa spasi
        assert total == name_len


class TestKarmicLesson:
    """Verifikasi formula Karmic Lesson (frequency grid)"""

    def test_vienny(self):
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.karmic_grid == [4, 0, 2, 1, 3, 0, 1, 2, 3]
        assert 2 in r.karmic_lessons  # angka 2 tidak muncul → karmic lesson
        assert 6 in r.karmic_lessons  # angka 6 tidak muncul → karmic lesson

    def test_panji(self):
        r = calculate("Panji Wellyanto", "27/09/1989")
        assert r.karmic_grid == [3, 1, 2, 0, 4, 1, 2, 0, 1]
        assert 4 in r.karmic_lessons
        assert 8 in r.karmic_lessons


class TestSyncBracket:
    """Verifikasi formula Synchronicity bracket"""

    def test_vienny(self):
        # TIME=3, AR=7 → |3-7|=4
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        assert r.sync_bracket == 4

    def test_chintya(self):
        # TIME=3, AR=3 → |3-3|=0 (sempurna!)
        r = calculate("Chintya Elta Ridayanti", "21/08/1999")
        assert r.sync_bracket == 0

    def test_erny(self):
        # TIME=1, AR=2 → |1-2|=1
        r = calculate("Erny Dwi Lestari", "25/11/1999")
        assert r.sync_bracket == 1

    def test_nova(self):
        # TIME=9, AR=3 → |9-3|=6
        r = calculate("Nova Puspitasari", "15/11/1990")
        assert r.sync_bracket == 6


class TestIntegration:
    """End-to-end integration test"""

    def test_full_calculation_vienny(self):
        """Test lengkap untuk nama Vienny Aulia Zahra"""
        r = calculate("Vienny Aulia Zahra", "02/11/1988")
        d = r.to_dict()

        assert d["nama"] == "Vienny Aulia Zahra"
        assert d["time"] == "21/3"
        assert d["acoustic_root"] == "25/7"
        assert d["heart_desire"] == "10/1"
        assert d["personality"] == "15/6"
        assert d["balance"] == "13/4"
        assert d["maturity"] == "10/1"
        assert d["fmei"]["finance"] == 4
        assert d["fmei"]["marriage"] == 6
        assert d["synchronicity_bracket"] == 4

    def test_invalid_dob_format(self):
        with pytest.raises(ValueError):
            calculate("Test Nama", "1988-02-11")  # format salah
