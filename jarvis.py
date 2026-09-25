import os
import requests
import datetime

# ================= AYARLAR =================
# GitHub Secrets'tan alır; yerelde test için tırnak içine yazabilirsiniz
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8843267094:AAH1iW-PZjrz1ggrOk3fR3I18GU8ffNx8FQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "921421260")

# Kağıthane Koordinatları
LAT = 41.081
LON = 28.973
KONUM = "Kağıthane"
# ===========================================

HAVA_DURUMLARI = {
    0: "Açık / Güneşli ☀️",
    1: "Az Bulutlu 🌤️",
    2: "Parçalı Bulutlu ⛅",
    3: "Bulutlu ☁️",
    45: "Sisli 🌫️",
    51: "Hafif Çiseleme 🌦️",
    61: "Yağmurlu 🌧️",
    63: "Kuvvetli Yağmur 🌧️",
    80: "Sağanak Yağış 🌦️",
    95: "Fırtına ⚡"
}

def hava_verisi_al():
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Europe%2FIstanbul"
    )
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def surus_ve_trafik_analizi(hava):
    if not hava:
        return "Yol verisi okunamadı."
    
    anlik = hava["current"]
    ruzgar = anlik["wind_speed_10m"]
    yagis_ihtimali = hava["daily"]["precipitation_probability_max"][0]
    sicaklik = anlik["temperature_2m"]

    notlar = []
    
    # İki teker & sürüş güvenliği tavsiyeleri
    if yagis_ihtimali > 40:
        notlar.append("⚠️ Zemin ıslak/kaygan olabilir, fren mesafesine ve virajlara dikkat.")
    else:
        notlar.append("✅ Zemin kuru, sürüş için uygun.")

    if ruzgar > 35:
        notlar.append(f"💨 Şiddetli rüzgar ({ruzgar} km/s), açık köprü ve viyadük geçişlerinde dikkat.")
    elif ruzgar > 20:
        notlar.append(f"🍃 Orta kuvvette rüzgar ({ruzgar} km/s).")

    if sicaklik < 12:
        notlar.append("🧥 Hava soğuk, rüzgarlık/koruyucu mont şart.")
    elif sicaklik < 18:
        notlar.append("🌤️ Sabah serin, öğleden sonra ılık. Hafif rüzgarlık yeterli.")

    return "\n".join(notlar)

def mac_durumu_getir():
    # Günün önemli maç takvimine hızlı kontrol
    bugun = datetime.datetime.now().strftime("%A")
    hafta_sonu = bugun in ["Saturday", "Sunday"]
    if hafta_sonu:
        return "⚽ Süper Lig mesaisi aktif. Maç saatine doğru Seyrantepe ve Vadi aksında trafik yoğunluğu oluşabilir."
    return "⚽ Hafta içi fikstürü sakin. Akşam antrenman ve lig hazırlıkları sürüyor."

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload, timeout=10)

def jarvis_sabah_raporu():
    hava = hava_verisi_al()
    tarih = datetime.datetime.now().strftime("%d.%m.%Y")

    if hava:
        anlik = hava["current"]
        gunluk = hava["daily"]
        hava_durumu_str = HAVA_DURUMLARI.get(anlik["weather_code"], "Parçalı Bulutlu ⛅")
        sicaklik = anlik["temperature_2m"]
        hissedilen = anlik["apparent_temperature"]
        min_t = gunluk["temperature_2m_min"][0]
        max_t = gunluk["temperature_2m_max"][0]
        yagis_ihtimal = gunluk["precipitation_probability_max"][0]
    else:
        hava_durumu_str = "Bilinmiyor"
        sicaklik, hissedilen, min_t, max_t, yagis_ihtimal = "--", "--", "--", "--", "--"

    surus_notu = surus_ve_trafik_analizi(hava)
    futbol_notu = mac_durumu_getir()

    rapor = (
        f"🎙️ *GÜNAYDIN EFENDİM, SİSTEMLER DEVREDE*\n"
        f"📅 *{tarih} - Günlük Durum Brifingi*\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌤️ *HAVA DURUMU ({KONUM.upper()})*\n"
        f"• *Durum:* {hava_durumu_str}\n"
        f"• *Sıcaklık:* {sicaklik}°C (Hissedilen: {hissedilen}°C)\n"
        f"• *Günün Aralığı:* {min_t}°C / {max_t}°C\n"
        f"• *Yağış İhtimali:* %{yagis_ihtimal}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛵 *YOL & SÜRÜŞ GÜVENLİĞİ*\n"
        f"{surus_notu}\n"
        f"• *Güzergah:* Cendere ve TEM bağlantıları sabah erken saatlerde akıcı.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🏆 *FUTBOL & GÜNDEM*\n"
        f"{futbol_notu}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🚀 *Gününüz açık ve verimli geçsin.*"
    )

    telegram_gonder(rapor)
    print("Jarvis brifingi Telegram'a iletildi.")

if __name__ == "__main__":
    jarvis_sabah_raporu()
