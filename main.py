import keyboard
import mouse
import time
import random

# Ayarlar
CLICK_KEY = 'left'  # Hangi tuşa basılınca çalışsın?
CPS = 12             # Saniyedeki tıklama hızı
IS_RUNNING = False   # Başlangıçta kapalı

print(f"Makro Hazır! CPS: {CPS}")
print("Aktif etmek için 'F6' tuşuna basın.")

def toggle_macro():
    global IS_RUNNING
    IS_RUNNING = not IS_RUNNING
    status = "AKTIF" if IS_RUNNING else "KAPALI"
    print(f"Makro durumu: {status}")

# F6 tuşu ile makroyu açıp kapatabilirsin
keyboard.add_hotkey('f6', toggle_macro)

while True:
    if IS_RUNNING:
        # Eğer farenin sol tıkı basılıysa tıklama yap
        if mouse.is_pressed('left'):
            mouse.click('left')
            
            # Rastgele gecikme (Anti-cheat için önemli)
            # 1/CPS yaparak süreyi hesaplıyoruz
            delay = (1.0 / CPS) + random.uniform(-0.01, 0.01)
            time.sleep(max(0.01, delay))
    
    time.sleep(0.001) # CPU kullanımını düşürmek için
  
