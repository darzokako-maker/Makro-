import customtkinter as ctk
import threading
import time
import random
import mouse
import keyboard

class MacroApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Gemini Macro - Pro")
        self.geometry("400x350")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Değişkenler
        self.is_running = False
        self.macro_key = "f6"  # Varsayılan başlatma tuşu
        self.cps = 12
        self.waiting_for_key = False

        # --- Arayüz Elemanları ---
        self.label_title = ctk.CTkLabel(self, text="SONOYUNCU MAKRO", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # CPS Kaydırıcı (Slider)
        self.label_cps = ctk.CTkLabel(self, text=f"CPS: {self.cps}")
        self.label_cps.pack()
        self.slider_cps = ctk.CTkSlider(self, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps)
        self.slider_cps.pack(pady=10)

        # Tuş Atama Butonu
        self.btn_bind = ctk.CTkButton(self, text=f"Tuş Ata: {self.macro_key.upper()}", 
                                      command=self.start_binding)
        self.btn_bind.pack(pady=10)

        # Durum Göstergesi
        self.label_status = ctk.CTkLabel(self, text="DURUM: BEKLEMEDE", text_color="orange")
        self.label_status.pack(pady=10)

        # Makro Motorunu Başlat
        threading.Thread(target=self.macro_engine, daemon=True).start()
        
        # Tuş Dinleyiciyi Başlat
        keyboard.on_press(self.on_key_event)

    def update_cps(self, value):
        self.cps = int(value)
        self.label_cps.configure(text=f"CPS: {self.cps}")

    def start_binding(self):
        self.waiting_for_key = True
        self.btn_bind.configure(text="Bir tuşa basın...")

    def on_key_event(self, event):
        if self.waiting_for_key:
            self.macro_key = event.name
            self.btn_bind.configure(text=f"Tuş Ata: {self.macro_key.upper()}")
            self.waiting_for_key = False
        elif event.name == self.macro_key:
            self.toggle_macro()

    def toggle_macro(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.label_status.configure(text="DURUM: AKTİF", text_color="green")
        else:
            self.label_status.configure(text="DURUM: BEKLEMEDE", text_color="orange")

    def macro_engine(self):
        while True:
            if self.is_running:
                # Sadece sol tık basılıyken çalışsın derseniz:
                if mouse.is_pressed("left"):
                    mouse.click("left")
                    # CPS hesaplama ve Jitter (Rastgelelik)
                    delay = (1.0 / self.cps) + random.uniform(-0.005, 0.005)
                    time.sleep(max(0.001, delay))
            time.sleep(0.001)

if __name__ == "__main__":
    app = MacroApp()
    app.mainloop()
    
