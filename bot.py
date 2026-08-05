import telebot
import re
import threading
import time
from datetime import datetime
import pytz
import os

BOT_TOKEN = "8609424195:AAG3ya5eic-kwumiVZwOmAA78McaFJkhBfE"
bot = telebot.TeleBot(BOT_TOKEN)

DOSYA_ADI = "toplam.txt"

def tutar_oku():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r") as f:
                return float(f.read().strip())
        except ValueError:
            return 0.0
    return 0.0

def tutar_kaydet(deger):
    with open(DOSYA_ADI, "w") as f:
        f.write(str(deger))

toplam_tutar = tutar_oku()

def gece_yarisi_sifirla():
    global toplam_tutar
    turkiye_saati = pytz.timezone('Europe/Istanbul')
    
    while True:
        simdi = datetime.now(turkiye_saati)
        # Gece 00:00:00'a kalan saniyeyi doğru hesaplama
        yarin = simdi.replace(day=simdi.day + 1, hour=0, minute=0, second=0, microsecond=0) if simdi.day < 28 else simdi
        # Güvenli kalan saniye hesabı:
        kalan_saniye = 86400 - (simdi.hour * 3600 + simdi.minute * 60 + simdi.second)
        
        time.sleep(kalan_saniye)
        
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        print("Sistem Bildirimi: Saat 00:00 oldu, toplam tutar otomatik sıfırlandı.")
        time.sleep(5) # Tekrar tetiklenmemesi için kısa bekleme

threading.Thread(target=gece_yarisi_sifirla, daemon=True).start()

# Tutarı sıfırlamak veya öğrenmek için komut
@bot.message_handler(func=lambda message: True)
def mesaj_takip(message):
    global toplam_tutar
    metin = message.text.lower().strip()
    
    if metin == "toplam gelen tutar nedir":
        bot.reply_to(message, f"📊 Bugün grupta toplanan toplam tutar: {toplam_tutar:,.2f}")
        return

    if metin == "/sifirla":
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        bot.reply_to(message, "Sıfırlandı! Bugünün toplamı 0.00 yapıldı.")
        return

    # Sadece içinde "k", "onay" veya net sayılar geçen mesajları yakala
    # (Buraya gruptaki mesaj formatınıza göre ekleme yapabilirsiniz)
    bulunanlar = re.findall(r'(\d+(?:\.\d+)?)\s*(k)?', metin)
    if bulunanlar:
        eklenen = 0.0
        for sayi, k_var in bulunanlar:
            val = float(sayi)
            if k_var:
                val *= 1000
            eklenen += val
        
        toplam_tutar += eklenen
        tutar_kaydet(toplam_tutar)
