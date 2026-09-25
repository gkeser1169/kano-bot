import os
import requests
import datetime
from google import genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8843267094:AAH1iW-PZjrz1ggrOk3fR3I18GU8ffNx8FQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "921421260")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LAT = 41.081
LON = 28.973
KONUM = "Kağıthane, İstanbul"

def hava_verisi_al():
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Europe%2FIstanbul"
    )
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload, timeout=10)

def ai_brifing_uret(hava_ozeti, tarih, gun_adi):
    prompt = f"""
Sen Tony Stark'ın yapay zeka asistanı JARVIS'sin. Karşındaki kişi senin Efendin ("Efendim" veya "Sayın Gökhan").

GÖREV: Aşağıdaki verilerle son derece KOMPAKT, zeki, hafif iğneleyici ve net bir Telegram sabah brifingi üret.

VERİLER:
- Tarih: {tarih} ({gun_adi}) - {KONUM}
- Sıcaklık / Hissedilen: {hava_ozeti.get('sicaklik')}°C / {hava_ozeti.get('hissedilen')}°C
- Günlük Aralık: {hava_ozeti.get('min_t')}°C - {hava_ozeti.get('max_t')}°C
- Yağış İhtimali: %{hava_ozeti.get('yagis')}
- Rüzgar: {hava_ozeti.get('ruzgar')} km/s

KESİN FORMAT VE KURALLAR:
1. ÇOK KISA OLACAK (En fazla 70-90 kelime, ekranda kaydırma gerektirmemeli). Paragraf döşeme, madde madde geç.
2. Format aynen şu yapıda olsun:
   🎙️ *JARVIS SABAH RAPORU* | {tarih}
   
   • 🌤️ *Atmosfer:* (Sıcaklık ve yağış durumu hakkında 1 kısa, esprili cümle)
   • 🛵 *İki Teker Protokolü:* (Rüzgar/zemin durumuna göre mont/sürüş tavsiyesi - tek cümle)
   • ⚽ *Radar:* (Varsa stadyum/lig gündemi veya günün temposu - tek cümle)
   
   (Kapanışta Tony Stark tarzı tek satırlık havalı bir uğurlama)
3. Telegram Markdown uyumlu olsun (*kalın* için tek yıldız). Asla gereksiz uzatma.
"""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print("Gemini API hatası:", e)
        return None

def calistir():
    tarih = datetime.datetime.now().strftime("%d.%m.%Y")
    gun_adi = datetime.datetime.now().strftime("%A")
    hava = hava_verisi_al()

    hava_ozeti = {}
    if hava:
        hava_ozeti = {
            "sicaklik": hava["current"]["temperature_2m"],
            "hissedilen": hava["current"]["apparent_temperature"],
            "ruzgar": hava["current"]["wind_speed_10m"],
            "min_t": hava["daily"]["temperature_2m_min"][0],
            "max_t": hava["daily"]["temperature_2m_max"][0],
            "yagis": hava["daily"]["precipitation_probability_max"][0]
        }

    mesaj = None
    if GEMINI_API_KEY:
        mesaj = ai_brifing_uret(hava_ozeti, tarih, gun_adi)

    if not mesaj:
        mesaj = (
            f"🎙️ *GÜNAYDIN EFENDİM*\n\n"
            f"📅 Tarih: {tarih}\n"
            f"🌤️ Sıcaklık: {hava_ozeti.get('sicaklik', '--')}°C | Yağış: %{hava_ozeti.get('yagis', '--')}\n"
            f"💨 Rüzgar: {hava_ozeti.get('ruzgar', '--')} km/s\n\n"
            f"Sistemler devrede, verimli bir gün dilerim."
        )

    telegram_gonder(mesaj)
    print("Kompakt brifing gönderildi.")

if __name__ == "__main__":
    calistir()
