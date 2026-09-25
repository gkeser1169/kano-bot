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
Sen Tony Stark'ın sadık, yüksek zekalı, hafif iğneleyici ve esprili asistanı JARVIS'sin. Karşındaki kişi senin Efendin ("Efendim" veya "Sayın Gökhan").

GÖREV: Aşağıdaki güncel verileri kullanarak dengeli uzunlukta (yaklaşık 120-150 kelime), zevkle okunan, sinematik ve samimi bir Telegram sabah brifingi hazırla.

VERİLER:
- Tarih: {tarih} ({gun_adi}) - Konum: {KONUM}
- Sıcaklık / Hissedilen: {hava_ozeti.get('sicaklik')}°C / {hava_ozeti.get('hissedilen')}°C
- Günün Uç Değerleri: En düşük {hava_ozeti.get('min_t')}°C, en yüksek {hava_ozeti.get('max_t')}°C
- Yağış Olasılığı: %{hava_ozeti.get('yagis')}
- Rüzgar: {hava_ozeti.get('ruzgar')} km/s

YAPI VE TON KURALLARI:
1. Hitap: Karizmatik ve hafif takılmalı bir açılış yap.
2. Atmosfer & İki Teker: Havayı kuru hava bülteni gibi verme. İki tekerle (scooter/motor) Kağıthane - Cendere hattında yola çıkacak birine mont seçimi, zemin ve rüzgar durumu üzerinden akıllıca tavsiye ver.
3. Gündem & Şehir: Günün temposuna, maç takvimine veya İstanbul trafiğine dair küçük, esprili bir dokunuş ekle.
4. Çıkış: Motive edici, Tony Stark filmlerindeki gibi şık bir veda cümlesiyle bitir.
5. Telegram Markdown formatında olsun (*kalın* için tek yıldız kullan). Aşırı kısa kuru bir liste olmasın, akıcı mini paragraflar ve şık emojiler barındırsın; ancak destan da yazmasın.
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
    print("Dengeli brifing iletildi.")

if __name__ == "__main__":
    calistir()
