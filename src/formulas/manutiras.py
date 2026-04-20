"""
Manutiras (Mahasabdha) Formula Engine
======================================
Semua 10 formula yang sudah terverifikasi 100% dari data sampel.
Formula tersembunyi di sini — tidak pernah di-expose ke client.

Formula yang di-SKIP (belum terpecahkan):
  - Endcode / Harani
  - Synchronicity %
  - Coherence
"""

from dataclasses import dataclass
from typing import Optional


# ─── PYTHAGOREAN TABLE ─────────────────────────────────────────────────────────
# Verified: A-I=1-9, J-R=1-9, S-Z=1-8
# Y selalu dihitung sebagai VOKAL

PYTHAGOREAN: dict[str, int] = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOWELS = set('AEIOUY')  # Y selalu vokal dalam sistem Manutiras
MASTER_NUMBERS = {11, 22, 33}


# ─── HELPERS ───────────────────────────────────────────────────────────────────

def letter_value(ch: str) -> int:
    """Konversi satu huruf ke nilai Pythagorean. Return 0 jika bukan huruf."""
    return PYTHAGOREAN.get(ch.upper(), 0)


def reduce_number(n: int, preserve_master: bool = True) -> int:
    """
    Reduce angka ke single digit.
    Jika preserve_master=True dan n adalah master number (11, 22, 33), PERTAHANKAN.
    """
    if preserve_master and n in MASTER_NUMBERS:
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
        if preserve_master and n in MASTER_NUMBERS:
            return n
    return n


def reduce_year(year: int) -> int:
    """Reduce tahun: jumlahkan semua digit, reduce ke single digit (pertahankan master)."""
    s = sum(int(d) for d in str(year))
    return reduce_number(s)


def word_values(word: str) -> list[int]:
    """Return list nilai Pythagorean untuk setiap huruf dalam kata."""
    return [letter_value(ch) for ch in word.upper() if ch.isalpha()]


def reduce_word_sum(word: str) -> int:
    """Jumlahkan semua nilai huruf dalam satu kata, lalu reduce (pertahankan master)."""
    total = sum(word_values(word))
    return reduce_number(total)


def parse_name(full_name: str) -> list[str]:
    """Split nama jadi list kata, buang spasi berlebih."""
    return [w for w in full_name.strip().split() if w]


def format_result(raw: int, reduced: int) -> str:
    """Format output: '18/9' jika raw != reduced, atau '9' jika sama / master."""
    if raw == reduced or raw in MASTER_NUMBERS:
        return str(raw)
    return f"{raw}/{reduced}"


# ─── DATACLASS OUTPUT ──────────────────────────────────────────────────────────

@dataclass
class ManutriasResult:
    nama: str
    dob: str  # format: DD/MM/YYYY

    # Core numbers (raw/reduced)
    time_raw: int
    time_reduced: int

    ar_raw: int
    ar_reduced: int

    hd_raw: int
    hd_reduced: int

    personality_raw: int
    personality_reduced: int

    balance_raw: int
    balance_reduced: int

    maturity_raw: int
    maturity_reduced: int

    # FMEI
    fmei_f: int  # Finance (count)
    fmei_m: int  # Marriage (count)
    fmei_e: int  # Expression (count)
    fmei_i: int  # Identity (count)

    # Karmic Lesson: grid [0-8] = frekuensi angka 1-9
    karmic_grid: list[int]
    karmic_lessons: list[int]  # angka yang frekuensinya 0

    # Synchronicity
    sync_bracket: int  # |Time_reduced - AR_reduced|

    # ─── Properties untuk display ───

    @property
    def time_str(self) -> str:
        return format_result(self.time_raw, self.time_reduced)

    @property
    def ar_str(self) -> str:
        return format_result(self.ar_raw, self.ar_reduced)

    @property
    def hd_str(self) -> str:
        return format_result(self.hd_raw, self.hd_reduced)

    @property
    def personality_str(self) -> str:
        return format_result(self.personality_raw, self.personality_reduced)

    @property
    def balance_str(self) -> str:
        return format_result(self.balance_raw, self.balance_reduced)

    @property
    def maturity_str(self) -> str:
        return format_result(self.maturity_raw, self.maturity_reduced)

    def to_dict(self) -> dict:
        """Konversi ke dict untuk dikirim ke Gemini API."""
        return {
            "nama": self.nama,
            "dob": self.dob,
            "time": self.time_str,
            "time_value": self.time_reduced,
            "acoustic_root": self.ar_str,
            "ar_value": self.ar_reduced,
            "heart_desire": self.hd_str,
            "hd_value": self.hd_reduced,
            "personality": self.personality_str,
            "personality_value": self.personality_reduced,
            "balance": self.balance_str,
            "balance_value": self.balance_reduced,
            "maturity": self.maturity_str,
            "maturity_value": self.maturity_reduced,
            "fmei": {
                "finance": self.fmei_f,
                "marriage": self.fmei_m,
                "expression": self.fmei_e,
                "identity": self.fmei_i,
            },
            "karmic_lessons": self.karmic_lessons,
            "karmic_grid": self.karmic_grid,
            "synchronicity_bracket": self.sync_bracket,
        }


# ─── FORMULA ENGINE ────────────────────────────────────────────────────────────

class ManutriasEngine:
    """
    Engine utama untuk kalkulasi semua formula Manutiras.
    Semua metode adalah pure functions — tidak ada side effects.
    """

    def calculate(self, full_name: str, dob: str) -> ManutriasResult:
        """
        Hitung semua formula Manutiras.

        Args:
            full_name: Nama lengkap sesuai KTP (boleh huruf kapital/kecil)
            dob: Tanggal lahir format DD/MM/YYYY

        Returns:
            ManutriasResult dengan semua nilai terisi
        """
        # Parse DOB
        day, month, year = self._parse_dob(dob)

        # Parse nama
        words = parse_name(full_name)

        # Hitung semua formula
        time_raw, time_reduced = self._calc_time(day, month, year)
        ar_raw, ar_reduced = self._calc_ar(words)
        hd_raw, hd_reduced = self._calc_hd(words)
        pers_raw, pers_reduced = self._calc_personality(words)
        bal_raw, bal_reduced = self._calc_balance(words)
        mat_raw, mat_reduced = self._calc_maturity(time_reduced, ar_reduced)
        fmei = self._calc_fmei(words)
        karmic_grid, karmic_lessons = self._calc_karmic(words)
        sync_bracket = self._calc_sync_bracket(time_reduced, ar_reduced)

        return ManutriasResult(
            nama=full_name.strip(),
            dob=dob,
            time_raw=time_raw,
            time_reduced=time_reduced,
            ar_raw=ar_raw,
            ar_reduced=ar_reduced,
            hd_raw=hd_raw,
            hd_reduced=hd_reduced,
            personality_raw=pers_raw,
            personality_reduced=pers_reduced,
            balance_raw=bal_raw,
            balance_reduced=bal_reduced,
            maturity_raw=mat_raw,
            maturity_reduced=mat_reduced,
            fmei_f=fmei['F'],
            fmei_m=fmei['M'],
            fmei_e=fmei['E'],
            fmei_i=fmei['I'],
            karmic_grid=karmic_grid,
            karmic_lessons=karmic_lessons,
            sync_bracket=sync_bracket,
        )

    # ─── FORMULA 1: TIME ─────────────────────────────────────────────────────

    def _parse_dob(self, dob: str) -> tuple[int, int, int]:
        """Parse DD/MM/YYYY → (day, month, year) sebagai integer."""
        parts = dob.strip().split('/')
        if len(parts) != 3:
            raise ValueError(f"Format DOB salah: '{dob}'. Gunakan DD/MM/YYYY")
        return int(parts[0]), int(parts[1]), int(parts[2])

    def _calc_time(self, day: int, month: int, year: int) -> tuple[int, int]:
        """
        TIME = Day_reduced + Month_reduced + Year_reduced
        Master number (11, 22, 33) dipertahankan di setiap komponen.
        """
        d = reduce_number(day)
        m = reduce_number(month)
        y = reduce_year(year)

        raw = d + m + y
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 2: ACOUSTIC ROOT (AR) ───────────────────────────────────────

    def _calc_ar(self, words: list[str]) -> tuple[int, int]:
        """
        AR = sum(reduce(word) for word in words), lalu reduce total.
        Y dihitung sebagai huruf biasa (bukan vokal khusus) di AR.
        """
        word_sums = [reduce_word_sum(w) for w in words]
        raw = sum(word_sums)
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 3: HEART DESIRE (HD) ────────────────────────────────────────

    def _calc_hd(self, words: list[str]) -> tuple[int, int]:
        """
        HD = sum(reduce(vowels_in_word) for word in words)
        Vokal: A, E, I, O, U, Y — Y selalu dihitung vokal!
        """
        totals = []
        for word in words:
            vowel_vals = [letter_value(ch) for ch in word.upper()
                          if ch.upper() in VOWELS]
            total = sum(vowel_vals)
            totals.append(reduce_number(total))

        raw = sum(totals)
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 4: PERSONALITY ───────────────────────────────────────────────

    def _calc_personality(self, words: list[str]) -> tuple[int, int]:
        """
        Personality = sum(reduce(consonants_in_word) for word in words)
        Konsonan = semua huruf KECUALI A, E, I, O, U, Y
        Y BUKAN konsonan dalam sistem ini.
        """
        totals = []
        for word in words:
            cons_vals = [letter_value(ch) for ch in word.upper()
                         if ch.upper() not in VOWELS and ch.isalpha()]
            total = sum(cons_vals)
            totals.append(reduce_number(total))

        raw = sum(totals)
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 5: BALANCE ───────────────────────────────────────────────────

    def _calc_balance(self, words: list[str]) -> tuple[int, int]:
        """
        Balance = sum(value(first_letter_of_word) for word in words)
        """
        initials = [letter_value(w[0]) for w in words if w]
        raw = sum(initials)
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 6: MATURITY ─────────────────────────────────────────────────

    def _calc_maturity(self, time_reduced: int, ar_reduced: int) -> tuple[int, int]:
        """
        Maturity = TIME_reduced + AR_reduced
        Jika AR adalah master number, tetap dipertahankan.
        """
        raw = time_reduced + ar_reduced
        reduced = reduce_number(raw)
        return raw, reduced

    # ─── FORMULA 7: FMEI ─────────────────────────────────────────────────────

    def _calc_fmei(self, words: list[str]) -> dict[str, int]:
        """
        FMEI = jumlah huruf per kategori nilai Pythagorean:
          F (Finance):    nilai {4, 5}  → huruf D,E,M,N,V,W
          M (Marriage):   nilai {1, 8}  → huruf A,H,J,Q,S,Z
          E (Expression): nilai {2,3,6} → huruf B,C,F,K,L,O,T,U,X
          I (Identity):   nilai {7, 9}  → huruf G,I,P,R,Y
        Cross-check: F+M+E+I = total huruf dalam nama (tanpa spasi)
        """
        counts = {'F': 0, 'M': 0, 'E': 0, 'I': 0}
        for word in words:
            for ch in word.upper():
                if not ch.isalpha():
                    continue
                val = letter_value(ch)
                if val in {4, 5}:
                    counts['F'] += 1
                elif val in {1, 8}:
                    counts['M'] += 1
                elif val in {2, 3, 6}:
                    counts['E'] += 1
                elif val in {7, 9}:
                    counts['I'] += 1
        return counts

    # ─── FORMULA 8: KARMIC LESSON ─────────────────────────────────────────────

    def _calc_karmic(self, words: list[str]) -> tuple[list[int], list[int]]:
        """
        Karmic Lesson = frekuensi kemunculan nilai 1-9 dalam seluruh nama.
        Grid: [freq_1, freq_2, freq_3, freq_4, freq_5, freq_6, freq_7, freq_8, freq_9]
        Karmic Lessons = angka dengan frekuensi 0 (dalam bahasa energi: "energi yang hilang")
        """
        freq = [0] * 9  # index 0 = nilai 1, index 8 = nilai 9
        for word in words:
            for ch in word.upper():
                if ch.isalpha():
                    val = letter_value(ch)
                    if 1 <= val <= 9:
                        freq[val - 1] += 1

        lessons = [i + 1 for i, count in enumerate(freq) if count == 0]
        return freq, lessons

    # ─── FORMULA 9: SYNCHRONICITY BRACKET ────────────────────────────────────

    def _calc_sync_bracket(self, time_reduced: int, ar_reduced: int) -> int:
        """
        Sync bracket [X] = |TIME_reduced - AR_reduced|
        [0] = sinkronisasi sempurna (nama & takdir selaras total)
        """
        t = time_reduced if time_reduced not in MASTER_NUMBERS else time_reduced % 9 or 9
        a = ar_reduced if ar_reduced not in MASTER_NUMBERS else ar_reduced % 9 or 9
        return abs(t - a)


# ─── FACTORY / SINGLETON ───────────────────────────────────────────────────────

_engine = ManutriasEngine()


def calculate(full_name: str, dob: str) -> ManutriasResult:
    """
    Public API — satu-satunya fungsi yang perlu dipanggil dari luar modul ini.

    Args:
        full_name: Nama lengkap (e.g. "Vienny Aulia Zahra")
        dob: Tanggal lahir (e.g. "02/11/1988")

    Returns:
        ManutriasResult — semua nilai terisi

    Raises:
        ValueError: jika format DOB salah
    """
    return _engine.calculate(full_name, dob)
