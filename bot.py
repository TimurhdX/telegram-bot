import telebot
import re
import threading
import time
from datetime import datetime
import pytz
import os

BOT_TOKEN = "8609424195:AAFhOhNGd4YQ633zQ81CYtWoRi_tWuYAr_w"
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
    
    # Toplam sorgulama
    if metin == "toplam gelen tutar nedir":
        bot.reply_to(message, f"📊 Bugün grupta toplanan toplam tutar: {toplam_tutar:,.2f} TL")
        return

    # Manuel sıfırlama komutu
    if metin == "/sifirla":
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        bot.reply_to(message, "🔄 Sıfırlandı! Bugünün toplamı 0.00 TL yapıldı.")
        return

    # 1. Satır başındaki sıra numaralarını (1., 2), 3-) temizle
    satirlar = metin.split('\n')
    eklenen_toplam = 0.0

    for satir in satirlar:
        # Satır başındaki sıra numarasını sil
        temiz_satir = re.sub(r'^\s*\d+[\.\)\-]\s*', '', satir.strip())
        
        # TL, TRY veya K ile biten ya da noktayla binlik yazılmış tutarları bul
        # Örnekler: 200.000, 200k, 150 tl, 1.500 try, 500000
        bulunanlar = re.findall(r'(\d+(?:\.\d+)*)\s*(k|tl|try)?', temiz_satir)
        
        for sayi_str, birim in bulunanlar:
            # Noktaları kaldır (200.000 -> 200000)
            saf_sayi = float(sayi_str.replace('.', ''))
            
            # K var ise 1000 ile çarp
            if birim == 'k':
                saf_sayi *= 1000
                
            eklenen_toplam += saf_sayi

    if eklenen_toplam > 0:
        toplam_tutar += eklenen_toplam
        tutar_kaydet(toplam_tutar)
        bot.reply_to(message, f"✅ Eklenen: {eklenen_toplam:,.2f} TL | Güncel Toplam: {toplam_tutar:,.2f} TL")

bot.infinity_polling()
