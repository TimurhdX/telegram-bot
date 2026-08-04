import telebot
import re
import threading
import time
from datetime import datetime
import pytz
import os

BOT_TOKEN = "8609424195:AAG3ya5eic-kwumIVzwOmAA78McaFJkhBfE"
bot = telebot.TeleBot(BOT_TOKEN)

DOSYA_ADI = "toplam.txt"

# Sunucu yeniden başlasa bile veriyi dosyadan oku
def tutar_oku():
    if os.path.exists(DOSYA_ADI):
        try:
            with open(DOSYA_ADI, "r") as f:
                return float(f.read().strip())
        except ValueError:
            return 0.0
    return 0.0

# Yeni tutarı dosyaya yaz
def tutar_kaydet(deger):
    with open(DOSYA_ADI, "w") as f:
        f.write(str(deger))

toplam_tutar = tutar_oku()

def gece_yarisi_sifirla():
    global toplam_tutar
    turkiye_saati = pytz.timezone('Europe/Istanbul')

    while True:
        simdi = datetime.now(turkiye_saati)
        kalan_saniye = ((24 - simdi.hour - 1) * 3600) + ((60 - simdi.minute - 1) * 60) + (60 - simdi.second)

        time.sleep(kalan_saniye)

        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        print("Sistem Bildirimi: Saat 00:00 oldu, toplam tutar otomatik sıfırlandı.")

        time.sleep(2)

threading.Thread(target=gece_yarisi_sifirla, daemon=True).start()

@bot.message_handler(func=lambda message: True)
def mesaj_takip(message):
    global toplam_tutar
    metin = message.text.lower().strip()

    if metin == "toplam gelen tutar nedir":
        bot.reply_to(message, f"📊 Bugün grupta toplanan toplam tutar: {toplam_tutar:,.2f}")
        return

    if metin == "toplamı sıfırla":
        toplam_tutar = 0.0
        tutar_kaydet(0.0)
        bot.reply_to(message, "🔄 Toplam tutar manuel olarak sıfırlandı! Yeni hesaplama başladı.")
        return

    temiz_metin = re.sub(r'(?m)^\d+\.\s*', '', metin)
    parcalar = re.findall(r'\b\d+(?:[\.,]\d+)*[kK]?\b', temiz_metin)

    for parca in parcalar:
        is_k = parca.endswith('k')
        sayi_metni = parca.rstrip('kK').replace('.', '')
        sayi_metni = sayi_metni.replace(',', '.')

        try:
            deger = float(sayi_metni)
            if is_k:
                deger *= 1000
            toplam_tutar += deger
            tutar_kaydet(toplam_tutar)
        except ValueError:
            continue

bot.infinity_polling()
