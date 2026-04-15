import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random

class FullAutoMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Gemini Pro - Full Auto Edition")
        self.geometry("500x700")
        ctk.set_appearance_mode("dark")
        
        # --- DEĞİŞKENLER ---
        self.is_cps_active = False     # Normal Sol Tık Makrosu
        self.is_rod_active = False     # Tam Otomatik Olta + Vuruş Döngüsü
        
        self.cps_key = "b"             
        self.rod_key = "y"             
        
        self.cps = 14
        self.rod_delay = 0.050         # Olta fırlatma süresi (50ms)
        self.sword_slot = "1"
        self.rod_slot = "3"
        
        self.waiting_for_key = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False

        # --- ARAYÜZ ---
        self.label_head = ctk.CTkLabel(self, text="FULL AUTO COMBO", font=("Impact", 30), text_color="#FFD700")
        self.label_head.pack(pady=15)

        # CPS Kontrol
        self.cps_frame = ctk.CTkFrame(self)
        self.cps_frame.pack(pady=10, padx=20, fill="x")
        self.label_cps = ctk.CTkLabel(self.cps_frame, text=f"Vuruş Hızı: {self.cps} CPS")
        self.label_cps.pack()
        self.slider_cps = ctk.CTkSlider(self.cps_frame, from_=1, to=20, command=self.update_cps)
        self.slider_cps.set(self.cps)
        self.slider_cps.pack(pady=5)

        # Tuş Atamaları
        self.btn_cps_key = ctk.CTkButton(self, text=f"SOL TIK MAKRO TUŞU: {self.cps_key.upper()}", command=lambda: self.start_binding("cps"))
        self.btn_cps_key.pack(pady=10, padx=20, fill="x")

        self.btn_rod_key = ctk.CTkButton(self, text=f"OTOMATİK OLTA+VURUŞ TUŞU: {self.rod_key.upper()}", fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_rod_key.pack(pady=10, padx=20, fill="x")

        # Slot ve Gecikme
        self.config_box = ctk.CTkFrame(self)
        self.config_box.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.config_box, text="Kılıç:").grid(row=0, column=0, padx=5)
        self.ent_s = ctk.CTkEntry(self.config_box, width=40); self.ent_s.insert(0, "1"); self.ent_s.grid(row=0, column=1)
        ctk.CTkLabel(self.config_box, text="Olta:").grid(row=0, column=2, padx=5)
        self.ent_r = ctk.CTkEntry(self.config_box, width=40); self.ent_r.insert(0, "3"); self.ent_r.grid(row=0, column=3)

        # Durum Panel
        self.st_cps = ctk.CTkLabel(self, text="DURUM: SOL TIK PASİF", text_color="red")
        self.st_cps.pack()
        self.st_rod = ctk.CTkLabel(self, text="DURUM: OTOMATİK OLTA PASİF", text_color="red")
        self.st_rod.pack()

        self.start_listeners()

    def update_cps(self, v): self.cps = int(v); self.label_cps.configure(text=f"Vuruş Hızı: {self.cps} CPS")
    
    def start_binding(self, target):
        self.waiting_for_key = target
        btn = self.btn_cps_key if target == "cps" else self.btn_rod_key
        btn.configure(text="Tuşa Basın...", fg_color="#702b2b")

    def on_press(self, key):
        try: k = key.char
        except: k = key.name

        if self.waiting_for_key:
            if self.waiting_for_key == "cps":
                self.cps_key = k
                self.btn_cps_key.configure(text=f"SOL TIK MAKRO TUŞU: {self.cps_key.upper()}", fg_color="#3b3b3b")
            else:
                self.rod_key = k
                self.btn_rod_key.configure(text=f"OTOMATİK OLTA+VURUŞ TUŞU: {self.rod_key.upper()}", fg_color="#1f538d")
            self.waiting_for_key = None
            return

        if k == self.cps_key:
            self.is_cps_active = not self.is_cps_active
            self.st_cps.configure(text="DURUM: SOL TIK AKTİF" if self.is_cps_active else "DURUM: SOL TIK PASİF", text_color="green" if self.is_cps_active else "red")

        if k == self.rod_key:
            self.is_rod_active = not self.is_rod_active
            self.st_rod.configure(text="DURUM: OTOMATİK OLTA AKTİF" if self.is_rod_active else "DURUM: OTOMATİK OLTA PASİF", text_color="cyan" if self.is_rod_active else "red")

    def click_engine(self):
        """Bağımsız Sol Tık Motoru (Manuel kullanım için)"""
        while True:
            # Sadece CPS makrosu açıkken ve kullanıcı sol tıka basıyorken çalışır
            if self.is_cps_active and self.left_pressed and not self.is_rod_active:
                self.mouse_controller.click(mouse.Button.left)
                base = 1.0 / self.cps
                time.sleep(base + random.uniform(-0.002, 0.002))
            time.sleep(0.001)

    def full_auto_rod_engine(self):
        """Hem Sağ Tık Hem Sol Tık Yapan Gelişmiş Döngü"""
        while True:
            if self.is_rod_active:
                s, r = self.ent_s.get(), self.ent_r.get()
                
                # 1. Olta Aşaması
                self.keyboard_controller.press(r); self.keyboard_controller.release(r)
                time.sleep(self.rod_delay)
                self.mouse_controller.click(mouse.Button.right) # Olta fırlat
                time.sleep(self.rod_delay)
                
                # 2. Kılıca Dönüş
                self.keyboard_controller.press(s); self.keyboard_controller.release(s)
                time.sleep(0.02)
                
                # 3. Otomatik Vuruş Aşaması (Kılıçtayken 5-6 kez hızlıca vur)
                for _ in range(int(self.cps / 2)): 
                    self.mouse_controller.click(mouse.Button.left)
                    time.sleep(1.0 / self.cps)
                
                # Döngü başa dönmeden önce kısa bekleme
                time.sleep(0.1)
            else:
                time.sleep(0.1)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        def on_click(x, y, btn, prs):
            if btn == mouse.Button.left: self.left_pressed = prs
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()
        threading.Thread(target=self.full_auto_rod_engine, daemon=True).start()

if __name__ == "__main__":
    app = FullAutoMacro()
    app.mainloop()
    
