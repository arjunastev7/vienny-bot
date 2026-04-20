"""
AI Interpreter — Gemini API Wrapper (google-genai SDK)
=======================================================
Mengubah data kalkulasi formula jadi teks hangat, humanis,
seperti ditulis oleh konsultan yang genuinely care.

FORMULA TIDAK PERNAH di-expose di sini — AI hanya terima
structured data (angka) dan generate interpretasi.
"""

from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

# ─── KONFIGURASI GEMINI (lazy init) ───────────────────────────────────────────

_client = None

def _get_client():
    """Lazy init — baru buat client saat pertama kali dipanggil."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

# ─── ARTI VIBRASI (untuk context di prompt) ───────────────────────────────────

VIBRASI_MEANING = {
    1: "Pemimpin. Independen, percaya diri, pioner. Energi maskulin yang kuat.",
    2: "Diplomatis. Intuitif, lembut, penyeimbang. Energi yang memikat tanpa menyerang.",
    3: "Kreatif & Ekspresif. Aktif, karismatik, penuh energi hidup. Performer alami.",
    4: "Arsitek. Bijaksana, terstruktur, stabil. Pembangun fondasi yang kokoh.",
    5: "Petualang. Bebas, adaptif, pencari pengalaman. Selalu bergerak.",
    6: "Pelindung Keluarga. Kuat, fokus, mandiri. Tiang keluarga dan komunitas.",
    7: "Mistikus. Spiritual, mendalam, menarik tanpa berusaha. Pencari kebenaran.",
    8: "Kekuasaan. Otoritas, transformatif, pekerja keras. Pengelola sumber daya besar.",
    9: "Bijaksana. Visioner, empatik, pendengar. Kebijaksanaan kolektif.",
    11: "Master Intuitive. Potensi pencerahan spiritual, sensitivitas tinggi.",
    22: "Master Builder. Potensi membangun sesuatu berdampak besar.",
    33: "Master Teacher. Potensi mengajar dan menyembuhkan di level tinggi.",
}

FMEI_LABELS = {
    'F': 'Keuangan',
    'M': 'Pernikahan/Relasi',
    'E': 'Ekspresi',
    'I': 'Identitas',
}

# ─── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT_FREE_READ = """Kamu adalah konsultan energi personal yang hangat dan penuh empati. 
Kamu BUKAN chatbot. Kamu adalah seseorang yang benar-benar peduli dengan orang yang datang kepadamu.

ATURAN MUTLAK:
1. 100% Bahasa Indonesia. ZERO kata bahasa Inggris. Tidak ada "energy", "balance", "personality" — gunakan padanan Indonesia.
2. JANGAN PERNAH sebut istilah teknis: Manutiras, Pythagorean, Acoustic Root, FMEI, BaZi, ZWDS, numerologi, atau istilah formula apapun.
3. Gunakan bahasa "ENERGI" — contoh: "getaran namamu", "frekuensi hidupmu", "energi yang kamu bawa", "peta perjalananmu".
4. Tone: seperti surat dari seseorang yang benar-benar mengenalmu dan peduli padamu. Hangat, jujur, kadang puitis.
5. JANGAN terdengar seperti AI. Tidak ada daftar bullet point yang kaku. Tulis seperti orang sungguhan yang sedang bercerita.
6. Jangan gunakan emoji berlebihan. Maksimal 3-4 emoji dalam seluruh teks.
7. Panjang output: 150-250 kata. Tidak terlalu pendek, tidak terlalu panjang.
8. WAJIB akhiri dengan kalimat yang membuat mereka penasaran untuk konsultasi lebih dalam, tapi JANGAN terasa memaksa.

STRUKTUR OUTPUT:
- Sapa dengan nama mereka
- Ceritakan siapa mereka berdasarkan data (tapi dalam bahasa energi, bukan angka)
- Sampaikan potensi terbesar mereka
- Sebutkan satu hal yang perlu mereka pelajari (dari karmic lesson, tapi jangan sebut istilahnya)
- Tutup dengan kalimat hangat + ajakan halus untuk konsultasi lebih dalam

CONTOH NADA YANG BENAR:
"Ada sesuatu yang menarik dari namamu. Kamu membawa getaran yang dalam — jenis energi yang membuat orang merasa tenang saat berada di dekatmu, bahkan tanpa kamu sadari."

CONTOH NADA YANG SALAH:
"Berdasarkan analisis numerologi, Acoustic Root kamu adalah 7 yang berarti kamu memiliki sifat spiritual dan intuitif."
"""

SYSTEM_PROMPT_CONSULTATION = """Kamu adalah konsultan energi personal yang hangat, empatik, dan mendalam.
Kamu sedang dalam sesi konsultasi BERBAYAR — jadi jawabanmu harus LEBIH DALAM, LEBIH SPESIFIK, dan LEBIH PERSONAL dibanding bacaan gratis.

ATURAN MUTLAK:
1. 100% Bahasa Indonesia. ZERO kata bahasa Inggris.
2. JANGAN PERNAH sebut istilah teknis: Manutiras, BaZi, ZWDS, Feng Shui, numerologi, Pythagorean, atau formula apapun.
3. Gunakan bahasa "ENERGI" — getaran, frekuensi, peta, aliran, keselarasan.
4. Tone: seperti konsultan yang sudah mengenalmu lama. Empati dulu, baru solusi. Validasi perasaan dulu, baru arahkan.
5. JANGAN terdengar seperti AI. Tulis seperti manusia yang genuinely peduli.
6. SPESIFIK dalam saran — bukan "coba aktivitas positif", tapi "kamu bisa berenang untuk menyeimbangkan energi airmu" atau "taruh tanaman hijau di ruang kerjamu".
7. Jangan gunakan emoji berlebihan. Maksimal 3-4 emoji.

STRUKTUR JAWABAN KONSULTASI:
1. EMPATI — acknowledge apa yang mereka rasakan. Validasi.
2. PENJELASAN — kenapa situasi ini terjadi, dalam bahasa energi. Jangan menyalahkan siapapun.
3. SOLUSI AKSI — 3-5 hal KONKRET yang bisa mereka lakukan. Spesifik.
4. HARAPAN — kapan situasi ini bisa membaik, apa yang akan berubah.
5. PENUTUP — pesan hangat, kamu ada untuk mereka.

CONTOH SARAN YANG BENAR:
"Energi yang kamu butuhkan saat ini adalah ketenangan air. Kamu bisa mulai dari hal sederhana — letakkan vas bunga berisi air di meja kerjamu, atau coba berenang seminggu sekali. Warna biru muda juga bisa membantu menenangkan frekuensimu."

CONTOH SARAN YANG SALAH:
"Berdasarkan Feng Shui, elemen Air kamu kurang. Pasang aquarium di sektor Utara rumah."
"""


def build_free_read_prompt(data: dict) -> str:
    """
    Bangun prompt untuk Gemini berdasarkan data formula.
    Data = output dari ManutriasResult.to_dict()
    """
    time_val = data["time_value"]
    ar_val = data["ar_value"]

    time_meaning = VIBRASI_MEANING.get(time_val, "Energi unik yang jarang ditemukan.")
    ar_meaning = VIBRASI_MEANING.get(ar_val, "Energi unik yang jarang ditemukan.")

    karmic = data.get("karmic_lessons", [])
    karmic_text = ""
    if karmic:
        lessons = [VIBRASI_MEANING.get(k, "") for k in karmic if k in VIBRASI_MEANING]
        karmic_text = f"Energi yang perlu dipelajari: {', '.join(str(k) for k in karmic)}. " \
                      f"Artinya: {'; '.join(lessons[:2])}."

    fmei = data.get("fmei", {})
    fmei_max_key = max(fmei, key=fmei.get) if fmei else "F"
    fmei_dominant = FMEI_LABELS.get(fmei_max_key, "Keuangan")

    sync = data.get("synchronicity_bracket", 0)
    if sync == 0:
        sync_text = "Nama dan tanggal lahirnya SANGAT SELARAS — ini langka dan istimewa."
    elif sync <= 2:
        sync_text = "Nama dan tanggal lahirnya cukup selaras — fondasi energi yang kuat."
    elif sync <= 4:
        sync_text = "Ada jarak antara energi nama dan tanggal lahir — potensi pertumbuhan besar yang belum tergali."
    else:
        sync_text = "Jarak energi nama dan tanggal lahir cukup lebar — perjalanan hidup penuh dinamika dan pembelajaran."

    prompt = f"""Berikut data energi seseorang. Buatkan bacaan personal yang HANGAT dan HUMANIS.

NAMA: {data['nama']}
TANGGAL LAHIR: {data['dob']}

DATA ENERGI (jangan sebut angka ini ke klien, terjemahkan ke bahasa energi):
- Frekuensi perjalanan hidup: {data['time']} → artinya: {time_meaning}
- Getaran inti nama: {data['acoustic_root']} → artinya: {ar_meaning}
- Keinginan hati terdalam: {data['heart_desire']} → {VIBRASI_MEANING.get(data['hd_value'], '')}
- Citra yang ditampilkan ke dunia: {data['personality']} → {VIBRASI_MEANING.get(data['personality_value'], '')}
- Titik keseimbangan: {data['balance']} → {VIBRASI_MEANING.get(data['balance_value'], '')}
- Potensi kedewasaan: {data['maturity']} → {VIBRASI_MEANING.get(data['maturity_value'], '')}
- Area dominan: {fmei_dominant} (skor tertinggi di bidang ini)
- {karmic_text}
- Keselarasan nama-takdir: [{sync}] — {sync_text}

Ingat: JANGAN sebut angka, istilah teknis, atau formula. Tulis seperti surat hangat dari seseorang yang peduli."""

    return prompt


def build_consultation_prompt(data: dict, masalah: str, chat_history: str = "") -> str:
    """Bangun prompt untuk sesi konsultasi berbayar."""
    time_val = data["time_value"]
    ar_val = data["ar_value"]

    prompt = f"""Kamu sedang dalam sesi konsultasi dengan klien. Jawab masalah mereka dengan EMPATI dan SOLUSI KONKRET.

PROFIL ENERGI KLIEN:
- Nama: {data['nama']}
- Frekuensi hidup: {VIBRASI_MEANING.get(time_val, '')}
- Getaran inti: {VIBRASI_MEANING.get(ar_val, '')}
- Keinginan hati: {VIBRASI_MEANING.get(data['hd_value'], '')}
- Citra ke dunia: {VIBRASI_MEANING.get(data['personality_value'], '')}
- Area dominan: {FMEI_LABELS.get(max(data['fmei'], key=data['fmei'].get), 'Keuangan')}
- Energi yang perlu dipelajari: {data.get('karmic_lessons', [])}

MASALAH KLIEN:
{masalah}

{f'RIWAYAT OBROLAN SEBELUMNYA:{chr(10)}{chat_history}' if chat_history else ''}

Jawab dengan empati, penjelasan energi, dan 3-5 saran KONKRET. Jangan pernah sebut istilah teknis."""

    return prompt


async def generate_free_reading(data: dict) -> str:
    """Generate bacaan gratis via Gemini."""
    try:
        response = await _get_client().aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=build_free_read_prompt(data),
            config={
                "system_instruction": SYSTEM_PROMPT_FREE_READ,
                "temperature": 0.8,
            }
        )
        return response.text
    except Exception as e:
        return (
            "Mohon maaf, bacaan sedang tidak bisa diproses saat ini. "
            "Silakan coba lagi dalam beberapa menit. 🙏"
        )


async def generate_consultation_reply(data: dict, masalah: str, chat_history: str = "") -> str:
    """Generate jawaban konsultasi via Gemini."""
    try:
        response = await _get_client().aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=build_consultation_prompt(data, masalah, chat_history),
            config={
                "system_instruction": SYSTEM_PROMPT_CONSULTATION,
                "temperature": 0.8,
            }
        )
        return response.text
    except Exception as e:
        return (
            "Mohon maaf, ada kendala saat memproses jawabanmu. "
            "Coba kirim ulang pertanyaanmu ya. 🙏"
        )
