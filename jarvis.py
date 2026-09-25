import os
import requests
import datetime

# ================= AYARLAR =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8843267094:AAH1iW-PZjrz1ggrOk3fR3I18GU8ffNx8FQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "921421260")

LAT = 41.081
LON = 28.973
KONUM = "Kağıthane"
# ===========================================

GUNLER = {
    0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
    4: "Cuma", 5: "Cumartesi", 6: "Pazar"
}

AYLAR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

def hava_durumu_al():
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

def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload, timeout=10)

def jarvis_rapor():
    simdi = datetime.datetime.now()
    tarih_str = f"{simdi.day} {AYLAR[simdi.month]} {simdi.year} {GUNLER[simdi.weekday()]}"
    
    veri = hava_durumu_al()
    if not veri:
        print("Hava durumu verisi alınamadı.")
        return

    anlik = veri["current"]
    gunluk = veri["daily"]

    sicaklik = round(anlik["temperature_2m"], 1)
    hissedilen = round(anlik["apparent_temperature"], 1)
    max_sicaklik = round(gunluk["temperature_2m_max"][0], 1)
    ruzgar = round(anlik["wind_speed_10m"], 1)
    yagis_ihtimal = gunluk["precipitation_probability_max"][0]

    # Motor & Sürüş Tavsiyesi
    if yagis_ihtimal > 35:
        motor_notu = f"Bugün yağış ihtimali %{yagis_ihtimal}; yollar ıslak veya kaygan olabilir. Virajlara ve takip mesafesine azami dikkat, Efendim."
    else:
        motor_notu = f"Yola çıkmak için harika bir gün. Yağış ihtimali yalnızca %{yagis_ihtimal}, rüzgar ise {ruzgar} km/s ile gayet sakin. Yollar muhtemelen kuru kalacak fakat zırhınız (ekipmanınız) tam olsun, Efendim. 😉"

    # Giyim Tavsiyesi
    if sicaklik < 15:
        giyim_notu = "Sabah serinliği belirgin; rüzgar kesici sağlam bir mont şart. Gün içinde katmanlı giyinmek konforunuzu koruyacaktır."
    else:
        giyim_notu = "Sabahın hafif serinliğine karşı hafif bir rüzgarlık ideal. Öğleden sonra ısınacak havayı düşünerek pratik, katmanlı bir kombin tercih edebilirsiniz."

    # Futbol & Aslanlar Notu
    hafta_sonu_mu = simdi.weekday() in [4, 5, 6]  # Cuma, Cmt, Paz
    if hafta_sonu_mu:
        futbol_notu = "Hafta sonu mesaisi başladı, Aslanlar'ın maç heyecanı ufukta. Özellikle Seyrantepe - Rams Park ve Vadi çevresinde trafik yoğunlaşabilir; rotanızı çizerken aklınızda bulunsun."
    else:
        futbol_notu = "Lig mesaisi sakin ilerliyor, Aslanlar antrenman modunda. Bölge trafiği genel seyrinde akıcı görünüyor."

    mesaj = (
        f"Günaydın Efendim,\n\n"
        f"Bugün *{tarih_str}*, Kağıthane'den sistemlerimi devreye alıyorum. Gününüzün en az zihniniz kadar keskin ve berrak geçmesini dilerim. 😉\n\n"
        f"☀️ *Hava Durumu:* Dışarısı şu an *{sicaklik}°C*, hissedilen *{hissedilen}°C*. Güne serin başlasak da öğleden sonra sıcaklık *{max_sicaklik}°C*'ye kadar yükselecek; sizi tatlı bir hava bekliyor.\n\n"
        f"🏍️ *İki Teker & Sürüş:* {motor_notu}\n\n"
        f"🧥 *Giyim Tavsiyesi:* {giyim_notu}\n\n"
        f"🦁 *Gündem & Futbol:* {futbol_notu}\n\n"
        f"Gününüz kusursuz ve temponuz yüksek olsun, Efendim.\n\n"
        f"Saygılarımla,\n"
        f"*JARVIS*"
    )

    telegram_gonder(mesaj)
    print("Jarvis brifingi gönderildi.")

if __name__ == "__main__":
    jarvis_rapor()
