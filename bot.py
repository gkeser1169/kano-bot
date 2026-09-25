import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://etkinlik.suricifatih.com/kano-kurek"

def telegram_bildir(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram hatası:", e)

# Cloud Linux için optimize edilmiş Chrome ayarları
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("Siteye bağlanılıyor...")
    driver.get(URL)

    # Tablonun yüklenmesini bekle
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "tr"))
    )
    time.sleep(2)

    satirlar = driver.find_elements(By.TAG_NAME, "tr")
    acik_seanslar = []

    for satir in satirlar:
        metin = satir.text.strip()
        if not metin or "GÜNLÜK KANO" not in metin.upper():
            continue

        butonlar = satir.find_elements(By.TAG_NAME, "button") + satir.find_elements(By.TAG_NAME, "a")
        for b in butonlar:
            if "Başvur" in b.text:
                acik_seanslar.append(metin.splitlines()[0])
                break

    if acik_seanslar:
        mesaj = "🚨 *BOŞ KANO SEANSI BULUNDU!*\n\n"
        for seans in acik_seanslar:
            mesaj += f"✅ {seans}\n"
        mesaj += f"\n🔗 Hemen Başvur: {URL}"
        
        telegram_bildir(mesaj)
        print("Açık seans bulundu ve Telegram'a bildirildi!")
    else:
        print("Şu anda tüm seanslar dolu.")

except Exception as e:
    print("Hata oluştu:", e)

finally:
    driver.quit()
