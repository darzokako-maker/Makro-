import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random

class YahyaMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Yahya Yapımı - Pro Combat")
        self.geometry("550x750")
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
        
        self.sword_slot = "1"
        self.rod_slot = "3"
        
        self.waiting_for_key = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False

        # --- ARAYÜZ TASARIMI ---
        self.label_head = ctk.CTkLabel(self, text="YAHYA YAPIMI", font=("Impact", 35), text_color="#00FF7F")
        self.label_head.pack(pady=10)

        self.sub_head = ctk.CTkLabel(self, text="Professional Gaming Solution", font=("Arial", 12, "italic"), text_color="gray")
        self.sub_head.pack(pady=(0, 10))

        # --- CPS PANELİ ---
        self.cps_frame = ctk.CTkFrame(self, border_width=1, border_color="#333")
        self.cps_frame.pack(pady=5, padx=20, fill="x")
        
        self.label_cps = ctk.CTkLabel(self.cps_frame, text=f"Saldırı Hızı: {self.cps} CPS", font=("Arial", 13, "bold"))
        self.label_cps.pack(pady=5)
        
        self.slider_cps = ctk.CTkSlider(self.cps_frame, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps)
        self.slider_cps.pack(pady=5, padx=10)

        # --- HASSAS MS AYARLARI ---
        self.ms_frame = ctk.CTkFrame(self, border_width=1, border_color="#444")
        self.ms_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.ms_frame, text="MS ZAMANLAMA KONTROLÜ", font=("Arial", 12, "bold"), text_color="#55CCFF").pack(pady=5)

        # Ayar 1
        self.lbl_sel = ctk.CTkLabel(self.ms_frame, text=f"Olta Seçim: {self.rod_select_ms}ms")
        self.lbl_sel.pack()
        self.sld_sel = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "sel"))
        self.sld_sel.set(self.rod_select_ms); self.sld_sel.pack(padx=10)

        # Ayar 2
        self.lbl_cast = ctk.CTkLabel(self.ms_frame, text=f"Kılıca Dönüş: {self.rod_cast_ms}ms")
        self.lbl_cast.pack()
        self.sld_cast = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "cast"))
        self.sld_cast.set(self.rod_cast_ms); self.sld_cast.pack(padx=10)

        # Ayar 3
        self.lbl_loop = ctk.CTkLabel(self.ms_frame, text=f"Döngü Süresi: {self.loop_delay_ms}ms")
        self.lbl_loop.pack()
        self.sld_loop = ctk.CTkSlider(self.ms_frame, from_=300, to=2000, command=lambda v: self.update_ms(v, "loop"))
        self.sld_loop.set(self.loop_delay_ms); self.sld_loop.pack(pady=(0,10), padx=10)

        # --- TUŞ ATAMA ---
        self.btn_cps_key = ctk.CTkButton(self, text=f"CPS MAKRO TUŞU: {self.cps_key.upper()}", 
                                         height=40, font=("Arial", 13, "bold"),
                                         command=lambda: self.start_binding("cps"))
        self.btn_cps_key.pack(pady=5, padx=20, fill="x")

        self.btn_rod_key = ctk.CTkButton(self, text=f"OTOMATİK KOMBO TUŞU: {self.rod_key.upper()}", 
                                         height=40, font=("Arial", 13, "bold"),
                                         fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_rod_key.pack(pady=5, padx=20, fill="x")

        # Durum Panel
        self.st_cps = ctk.CTkLabel(self, text="● CPS PASİF", text_color="red", font=("Arial", 12, "bold"))
        self.st_cps.pack(pady=2)
        self.st_rod = ctk.CTkLabel(self, text="● KOMBO PASİF", text_color="red", font=("Arial", 12, "bold"))
        self.st_rod.pack(pady=2)

        self.start_listeners()

    def update_cps(self, v): self.cps = int(v); self.label_cps.configure(text=f"Saldırı Hızı: {self.cps} CPS")
    
    def update_ms(self, v, type):
        val = int(v)
        if type == "sel": self.rod_select_ms = val; self.lbl_sel.configure(text=f"Olta Seçim: {val}ms")
        elif type == "cast": self.rod_cast_ms = val; self.lbl_cast.configure(text=f"Kılıca Dönüş: {val}ms")
        elif type == "loop": self.loop_delay_ms = val; self.lbl_loop.configure(text=f"Döngü Süresi: {val}ms")

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

        if k == self.cps_key:
            self.is_cps_active = not self.is_cps_active
            self.st_cps.configure(text="● CPS AKTİF" if self.is_cps_active else "● CPS PASİF", text_color="green" if self.is_cps_active else "red")

        if k == self.rod_key:
            self.is_rod_active = not self.is_rod_active
            self.st_rod.configure(text="● KOMBO AKTİF" if self.is_rod_active else "● KOMBO PASİF", text_color="cyan" if self.is_rod_active else "red")

    def click_engine(self):
        while True:
            if self.is_cps_active and self.left_pressed and not self.is_rod_active:
                self.mouse_controller.click(mouse.Button.left)
                base = 1.0 / self.cps
                time.sleep(base + random.uniform(-(base*0.04), (base*0.04)))
            else:
                time.sleep(0.005)

    def full_auto_rod_engine(self):
        while True:
            if self.is_rod_active:
                # 1. Olta (Slot 3)
                self.keyboard_controller.press("3"); self.keyboard_controller.release("3")
                time.sleep(self.rod_select_ms / 1000.0)
                # 2. Sağ Tık
                self.mouse_controller.click(mouse.Button.right)
                time.sleep(self.rod_cast_ms / 1000.0)
                # 3. Kılıç (Slot 1)
                self.keyboard_controller.press("1"); self.keyboard_controller.release("1")
                time.sleep(0.01)
                
                # 4. Otomatik Vuruş (Döngü süresinin belli bir kısmında vurur)
                duration = (self.loop_delay_ms / 1000.0) * 0.7
                end_time = time.time() + duration
                while time.time() < end_time and self.is_rod_active:
                    self.mouse_controller.click(mouse.Button.left)
                    time.sleep(1.0 / self.cps)
                
                # Dinlenme
                time.sleep(0.05)
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
    app = YahyaMacro()
    app.mainloop()
            
