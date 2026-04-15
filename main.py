import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random

class PrecisionMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Gemini Pro - Precision Edition")
        self.geometry("500x700")
        ctk.set_appearance_mode("dark")
        
        # Değişkenler
        self.is_running = False      
        self.is_rod_looping = False  
        self.cps = 14
        self.bind_key = "f6"         
        self.rod_toggle_key = "r"    
        self.waiting_for_key = None

        self.sword_slot = "1"
        self.rod_slot = "3"
        self.rod_delay = 0.045 # 45ms ideal başlangıç

        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False

        # --- Arayüz ---
        self.label_head = ctk.CTkLabel(self, text="PRECISION CLICKER", font=("Impact", 30), text_color="#00BFFF")
        self.label_head.pack(pady=10)

        # CPS Kontrol
        self.label_cps = ctk.CTkLabel(self, text=f"Hedef Hız: {self.cps} CPS")
        self.label_cps.pack()
        self.slider_cps = ctk.CTkSlider(self, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps)
        self.slider_cps.pack(pady=5)

        # Tuş Atamaları
        self.btn_bind_main = ctk.CTkButton(self, text=f"MAKRO AÇ/KAPAT: {self.bind_key.upper()}", command=lambda: self.start_binding("main"))
        self.btn_bind_main.pack(pady=10, padx=20, fill="x")

        self.btn_bind_rod = ctk.CTkButton(self, text=f"OTOMATİK OLTA TUŞU: {self.rod_toggle_key.upper()}", fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_bind_rod.pack(pady=10, padx=20, fill="x")

        # Slot ve Gecikme Ayarları
        self.config_frame = ctk.CTkFrame(self)
        self.config_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.config_frame, text="Kılıç:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_sword = ctk.CTkEntry(self.config_frame, width=40); self.entry_sword.insert(0, "1")
        self.entry_sword.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.config_frame, text="Olta:").grid(row=0, column=2, padx=5)
        self.entry_rod = ctk.CTkEntry(self.config_frame, width=40); self.entry_rod.insert(0, "3")
        self.entry_rod.grid(row=0, column=3, padx=5)

        self.label_delay = ctk.CTkLabel(self.config_frame, text=f"Olta Atma Süresi: {int(self.rod_delay*1000)}ms")
        self.label_delay.grid(row=1, column=0, columnspan=4, pady=5)
        self.slider_delay = ctk.CTkSlider(self.config_frame, from_=20, to=150, command=self.update_delay)
        self.slider_delay.set(self.rod_delay * 1000)
        self.slider_delay.grid(row=2, column=0, columnspan=4, pady=5, padx=10)

        # Durum Panel
        self.label_status = ctk.CTkLabel(self, text="SİSTEM: KAPALI", text_color="red", font=("Arial", 16, "bold"))
        self.label_status.pack(pady=10)
        self.label_rod_status = ctk.CTkLabel(self, text="OLTA DÖNGÜSÜ: PASİF", text_color="gray")
        self.label_rod_status.pack()

        self.start_listeners()

    def update_cps(self, val): self.cps = int(val); self.label_cps.configure(text=f"Hedef Hız: {self.cps} CPS")
    def update_delay(self, val): self.rod_delay = int(val) / 1000.0; self.label_delay.configure(text=f"Olta Atma Süresi: {int(val)}ms")

    def start_binding(self, target):
        self.waiting_for_key = target
        btn = self.btn_bind_main if target == "main" else self.btn_bind_rod
        btn.configure(text="Tuşa Basın...", fg_color="#702b2b")

    def on_press(self, key):
        try: k = key.char
        except: k = key.name

        if self.waiting_for_key:
            if self.waiting_for_key == "main": self.bind_key = k; self.btn_bind_main.configure(text=f"MAKRO AÇ/KAPAT: {self.bind_key.upper()}", fg_color="#3b3b3b")
            else: self.rod_toggle_key = k; self.btn_bind_rod.configure(text=f"OTOMATİK OLTA TUŞU: {self.rod_toggle_key.upper()}", fg_color="#1f538d")
            self.waiting_for_key = None
            return

        if k == self.bind_key:
            self.is_running = not self.is_running
            self.label_status.configure(text="SİSTEM: AKTİF" if self.is_running else "SİSTEM: KAPALI", text_color="green" if self.is_running else "red")

        if k == self.rod_toggle_key and self.is_running:
            self.is_rod_looping = not self.is_rod_looping
            self.label_rod_status.configure(text="OLTA DÖNGÜSÜ: ÇALIŞIYOR" if self.is_rod_looping else "OLTA DÖNGÜSÜ: PASİF", text_color="cyan" if self.is_rod_looping else "gray")

    def rod_loop_worker(self):
        while True:
            if self.is_running and self.is_rod_looping:
                s_slot = self.entry_sword.get()
                r_slot = self.entry_rod.get()
                self.keyboard_controller.press(r_slot); self.keyboard_controller.release(r_slot)
                time.sleep(self.rod_delay)
                self.mouse_controller.click(mouse.Button.right)
                time.sleep(self.rod_delay)
                self.keyboard_controller.press(s_slot); self.keyboard_controller.release(s_slot)
                time.sleep(0.85) # Döngü hızı
            time.sleep(0.1)

    def click_engine(self):
        """Hassas CPS Motoru"""
        while True:
            if self.is_running and self.left_pressed:
                self.mouse_controller.click(mouse.Button.left)
                
                # CPS'e göre ana bekleme süresi
                base_delay = 1.0 / self.cps
                
                # Çok küçük jitter (İsteğin üzerine: CPS'i bozmayacak kadar az)
                # %3 oranında küçük bir sapma ekler (Örn: 14 CPS için +/- 2ms)
                jitter = random.uniform(-(base_delay * 0.03), (base_delay * 0.03))
                
                final_delay = base_delay + jitter
                time.sleep(max(0.001, final_delay))
            else:
                time.sleep(0.01)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left: self.left_pressed = pressed
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()
        threading.Thread(target=self.rod_loop_worker, daemon=True).start()

if __name__ == "__main__":
    app = PrecisionMacro()
    app.mainloop()
    
