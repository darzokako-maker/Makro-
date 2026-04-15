import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random

class UltraGamingMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Gemini Macro - Custom Edition")
        self.geometry("500x700")
        ctk.set_appearance_mode("dark")
        
        # Değişkenler
        self.is_running = False
        self.cps = 14
        self.bind_key = "f6"
        self.rod_key = "r"
        self.waiting_for_key = None

        # Olta Özelleştirme Değişkenleri
        self.sword_slot = "1"
        self.rod_slot = "3"
        self.rod_delay = 0.03 # 30ms varsayılan

        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False

        # --- Arayüz Tasarımı ---
        self.label_head = ctk.CTkLabel(self, text="ADVANCED COMBAT", font=("Impact", 32), text_color="#00DBDE")
        self.label_head.pack(pady=10)

        # --- ANA AYARLAR ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=20, fill="x")

        self.label_cps = ctk.CTkLabel(self.main_frame, text=f"Vuruş Hızı: {self.cps} CPS")
        self.label_cps.pack(pady=5)
        self.slider_cps = ctk.CTkSlider(self.main_frame, from_=1, to=20, command=self.update_cps)
        self.slider_cps.set(self.cps)
        self.slider_cps.pack(pady=5)

        self.btn_bind_main = ctk.CTkButton(self.main_frame, text=f"AÇ/KAPAT: {self.bind_key.upper()}", command=lambda: self.start_binding("main"))
        self.btn_bind_main.pack(pady=10, padx=10, fill="x")

        # --- OLTA (ROD) ÖZELLEŞTİRME ---
        self.rod_frame = ctk.CTkFrame(self, border_width=1, border_color="#555")
        self.rod_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.rod_frame, text="OLTA AYARLARI", font=("Arial", 12, "bold")).pack(pady=5)

        # Slot Seçimleri
        self.slot_inner_frame = ctk.CTkFrame(self.rod_frame, fg_color="transparent")
        self.slot_inner_frame.pack(pady=5)

        ctk.CTkLabel(self.slot_inner_frame, text="Kılıç Slot:").grid(row=0, column=0, padx=5)
        self.entry_sword = ctk.CTkEntry(self.slot_inner_frame, width=40, placeholder_text="1")
        self.entry_sword.insert(0, "1")
        self.entry_sword.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.slot_inner_frame, text="Olta Slot:").grid(row=0, column=2, padx=5)
        self.entry_rod = ctk.CTkEntry(self.slot_inner_frame, width=40, placeholder_text="3")
        self.entry_rod.insert(0, "3")
        self.entry_rod.grid(row=0, column=3, padx=5)

        # Gecikme Ayarı (Delay)
        self.label_delay = ctk.CTkLabel(self.rod_frame, text=f"Geçiş Gecikmesi: {int(self.rod_delay*1000)}ms")
        self.label_delay.pack()
        self.slider_delay = ctk.CTkSlider(self.rod_frame, from_=10, to=200, command=self.update_delay)
        self.slider_delay.set(self.rod_delay * 1000)
        self.slider_delay.pack(pady=5)

        self.btn_bind_rod = ctk.CTkButton(self.rod_frame, text=f"OLTA TUŞU: {self.rod_key.upper()}", fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_bind_rod.pack(pady=10, padx=10, fill="x")

        # Durum Göstergesi
        self.label_status = ctk.CTkLabel(self, text="SİSTEM: BEKLEMEDE", text_color="orange", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=20)

        self.start_listeners()

    def update_cps(self, val):
        self.cps = int(val)
        self.label_cps.configure(text=f"Vuruş Hızı: {self.cps} CPS")

    def update_delay(self, val):
        self.rod_delay = int(val) / 1000.0
        self.label_delay.configure(text=f"Geçiş Gecikmesi: {int(val)}ms")

    def start_binding(self, target):
        self.waiting_for_key = target
        if target == "main":
            self.btn_bind_main.configure(text="Tuş Bekleniyor...", fg_color="#702b2b")
        else:
            self.btn_bind_rod.configure(text="Tuş Bekleniyor...", fg_color="#702b2b")

    def on_press(self, key):
        try: k = key.char
        except: k = key.name

        if self.waiting_for_key:
            if self.waiting_for_key == "main":
                self.bind_key = k
                self.btn_bind_main.configure(text=f"AÇ/KAPAT: {self.bind_key.upper()}", fg_color="#3b3b3b")
            else:
                self.rod_key = k
                self.btn_bind_rod.configure(text=f"OLTA TUŞU: {self.rod_key.upper()}", fg_color="#1f538d")
            self.waiting_for_key = None
            return

        if k == self.bind_key:
            self.is_running = not self.is_running
            color = "#00FF7F" if self.is_running else "orange"
            status = "AKTİF" if self.is_running else "BEKLEMEDE"
            self.label_status.configure(text=f"SİSTEM: {status}", text_color=color)

        if k == self.rod_key and self.is_running:
            threading.Thread(target=self.rod_sequence).start()

    def rod_sequence(self):
        # Slotları anlık olarak kutulardan al (Kullanıcı değiştirebilir)
        s_slot = self.entry_sword.get()
        r_slot = self.entry_rod.get()
        
        self.keyboard_controller.press(r_slot)
        self.keyboard_controller.release(r_slot)
        time.sleep(self.rod_delay)
        
        self.mouse_controller.click(mouse.Button.right)
        time.sleep(self.rod_delay)
        
        self.keyboard_controller.press(s_slot)
        self.keyboard_controller.release(s_slot)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left:
                self.left_pressed = pressed
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()

    def click_engine(self):
        while True:
            if self.is_running and self.left_pressed:
                self.mouse_controller.click(mouse.Button.left)
                delay = (1.0 / self.cps) + random.uniform(-0.005, 0.005)
                time.sleep(max(0.01, delay))
            time.sleep(0.001)

if __name__ == "__main__":
    app = UltraGamingMacro()
    app.mainloop()
    
