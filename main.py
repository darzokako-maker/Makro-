import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random

class YahyaUltimateMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Yahya Yapımı - Ultimate Pro")
        self.geometry("550x850")
        ctk.set_appearance_mode("dark")
        
        # --- DEĞİŞKENLER ---
        self.is_cps_active = False     
        self.is_rod_active = False     
        
        self.cps_key = "b"             
        self.rod_key = "y"             
        
        self.cps = 14
        self.rod_select_ms = 45        
        self.rod_cast_ms = 45          
        self.loop_delay_ms = 850
        self.global_ms_offset = 0      # Genel MS Artışı/Azalışı
        
        self.sword_slot = "1"
        self.rod_slot = "3"
        
        self.waiting_for_key = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False

        # --- ARAYÜZ ---
        self.label_head = ctk.CTkLabel(self, text="YAHYA YAPIMI", font=("Impact", 35), text_color="#00FF7F")
        self.label_head.pack(pady=10)

        # --- CPS PANELİ ---
        self.cps_frame = ctk.CTkFrame(self, border_width=1)
        self.cps_frame.pack(pady=5, padx=20, fill="x")
        self.label_cps = ctk.CTkLabel(self.cps_frame, text=f"Saldırı Hızı: {self.cps} CPS", font=("Arial", 13, "bold"))
        self.label_cps.pack(pady=5)
        self.slider_cps = ctk.CTkSlider(self.cps_frame, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps); self.slider_cps.pack(pady=5, padx=10)

        # --- GENEL MS AYARI (EKSTRA) ---
        self.global_frame = ctk.CTkFrame(self, border_width=2, border_color="#FF4500")
        self.global_frame.pack(pady=10, padx=20, fill="x")
        self.lbl_global = ctk.CTkLabel(self.global_frame, text=f"GENEL GECİKME OFSETİ: {self.global_ms_offset}ms", text_color="#FF4500", font=("Arial", 12, "bold"))
        self.lbl_global.pack(pady=5)
        self.sld_global = ctk.CTkSlider(self.global_frame, from_=-50, to=150, command=self.update_global_offset)
        self.sld_global.set(self.global_ms_offset); self.sld_global.pack(pady=5, padx=10)
        ctk.CTkLabel(self.global_frame, text="(Tüm gecikmelere eklenir/çıkarılır)", font=("Arial", 10)).pack()

        # --- ÖZEL MS AYARLARI ---
        self.ms_frame = ctk.CTkFrame(self, border_width=1)
        self.ms_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_sel = ctk.CTkLabel(self.ms_frame, text=f"Olta Seçim: {self.rod_select_ms}ms"); self.lbl_sel.pack()
        self.sld_sel = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "sel")); self.sld_sel.set(self.rod_select_ms); self.sld_sel.pack(padx=10)

        self.lbl_cast = ctk.CTkLabel(self.ms_frame, text=f"Kılıca Dönüş: {self.rod_cast_ms}ms"); self.lbl_cast.pack()
        self.sld_cast = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "cast")); self.sld_cast.set(self.rod_cast_ms); self.sld_cast.pack(padx=10)

        # --- KONTROL TUŞLARI ---
        self.btn_cps_key = ctk.CTkButton(self, text=f"CPS MAKRO TUŞU: {self.cps_key.upper()}", height=40, command=lambda: self.start_binding("cps"))
        self.btn_cps_key.pack(pady=5, padx=20, fill="x")

        self.btn_rod_key = ctk.CTkButton(self, text=f"OTOMATİK KOMBO TUŞU: {self.rod_key.upper()}", height=40, fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_rod_key.pack(pady=5, padx=20, fill="x")

        # Durum Panel
        self.st_cps = ctk.CTkLabel(self, text="● CPS PASİF", text_color="red", font=("Arial", 12, "bold")).pack()
        self.st_rod = ctk.CTkLabel(self, text="● KOMBO PASİF", text_color="red", font=("Arial", 12, "bold")).pack()

        self.start_listeners()

    def update_cps(self, v): self.cps = int(v); self.label_cps.configure(text=f"Saldırı Hızı: {self.cps} CPS")
    def update_global_offset(self, v): self.global_ms_offset = int(v); self.lbl_global.configure(text=f"GENEL GECİKME OFSETİ: {self.global_ms_offset}ms")
    
    def update_ms(self, v, type):
        val = int(v)
        if type == "sel": self.rod_select_ms = val; self.lbl_sel.configure(text=f"Olta Seçim: {val}ms")
        elif type == "cast": self.rod_cast_ms = val; self.lbl_cast.configure(text=f"Kılıca Dönüş: {val}ms")
        elif type == "loop": self.loop_delay_ms = val

    def start_binding(self, target):
        self.waiting_for_key = target
        btn = self.btn_cps_key if target == "cps" else self.btn_rod_key
        btn.configure(text="TUŞ BEKLENİYOR...", fg_color="#702b2b")

    def on_press(self, key):
        try: k = key.char
        except: k = key.name
        if self.waiting_for_key:
            if self.waiting_for_key == "cps": self.cps_key = k; self.btn_cps_key.configure(text=f"CPS MAKRO TUŞU: {self.cps_key.upper()}", fg_color="#3b3b3b")
            else: self.rod_key = k; self.btn_rod_key.configure(text=f"OTOMATİK KOMBO TUŞU: {self.rod_key.upper()}", fg_color="#1f538d")
            self.waiting_for_key = None
            return
        if k == self.cps_key: self.is_cps_active = not self.is_cps_active
        if k == self.rod_key: self.is_rod_active = not self.is_rod_active

    def full_auto_rod_engine(self):
        while True:
            if self.is_rod_active:
                # Toplam Gecikme = Ayar + Global Ofset
                sel_delay = max(5, self.rod_select_ms + self.global_ms_offset)
                cast_delay = max(5, self.rod_cast_ms + self.global_ms_offset)
                
                self.keyboard_controller.press("3"); self.keyboard_controller.release("3")
                time.sleep(sel_delay / 1000.0)
                
                self.mouse_controller.click(mouse.Button.right)
                time.sleep(cast_delay / 1000.0)
                
                self.keyboard_controller.press("1"); self.keyboard_controller.release("1")
                time.sleep(0.02)
                
                # Otomatik Vuruş
                end_time = time.time() + 0.6
                while time.time() < end_time and self.is_rod_active:
                    self.mouse_controller.click(mouse.Button.left)
                    time.sleep(1.0 / self.cps)
                time.sleep(0.1)
            else:
                time.sleep(0.1)

    def click_engine(self):
        while True:
            if self.is_cps_active and self.left_pressed and not self.is_rod_active:
                self.mouse_controller.click(mouse.Button.left)
                base = 1.0 / self.cps
                time.sleep(base + random.uniform(-(base*0.04), (base*0.04)))
            time.sleep(0.005)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        def on_click(x, y, btn, prs):
            if btn == mouse.Button.left: self.left_pressed = prs
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()
        threading.Thread(target=self.full_auto_rod_engine, daemon=True).start()

if __name__ == "__main__":
    app = YahyaUltimateMacro()
    app.mainloop()
    
