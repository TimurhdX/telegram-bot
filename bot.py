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
        kalan_saniye = 86400 - (simdi.hour * 3600 + simdi.minute * 60 + simdi.second)
        time.sleep(kalan_saniye)
        
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        time.sleep(5)

threading.Thread(target=gece_yarisi_sifirla, daemon=True).start()

@bot.message_handler(func=lambda message: True)
def mesaj_takip(message):
    global toplam_tutar
    if not message.text:
        return
        
    metin = message.text.lower().strip()
    
    if metin == "toplam gelen tutar nedir":
        bot.reply_to(message, f"📊 Bugün grupta toplanan toplam tutar: {toplam_tutar:,.2f}")
        return

    if metin == "/sifirla":
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        bot.reply_to(message, "Sıfırlandı! Bugünün toplamı 0.00 yapıldı.")
        return

    # Binlik ayırıcı noktaları kaldırıp sayıları yakala (1.200k -> 1200k)
    temiz_metin = metin.replace('.', '')
    bulunanlar = re.findall(r'(\d+)\s*(k)?', temiz_metin)
    
    if bulunanlar:
        eklenen = 0.0
        for sayi, k_var in bulunanlar:
            val = float(sayi)
            if k_var:
                val *= 1000
            eklenen += val
        
        toplam_tutar += eklenen
        tutar_kaydet(toplam_tutar)
        bot.reply_to(message, f"✅ Eklenen: {eklenen:,.2f} | Güncel Toplam: {toplam_tutar:,.2f}")

bot.infinity_polling()
