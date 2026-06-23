import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random
import math

class YahyaUltimateMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Yahya Yapımı - Ultimate Pro v2")
        self.geometry("550x900")
        ctk.set_appearance_mode("dark")
        
        # --- DEĞİŞKENLER ---
        self.is_cps_active = False     
        self.is_rod_active = False     
        
        self.cps_key = "b"             
        self.rod_key = "y"             
        
        self.cps = 14
        self.rod_select_ms = 45        
        self.rod_cast_ms = 45          
        self.global_ms_offset = 0      
        
        # Dinamik Slotlar (Geliştirildi)
        self.sword_slot = "1"
        self.rod_slot = "3"
        
        self.waiting_for_key = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False
        
        # Pynput Sonsuz Döngü Engelleme Bayrağı (BUG ÇÖZÜMÜ)
        self.ignore_software_click = False

        # İnsansı Ritim İçin Dalgalanma Değişkeni
        self.click_count = 0

        # --- ARAYÜZ ---
        self.label_head = ctk.CTkLabel(self, text="YAHYA YAPIMI", font=("Impact", 35), text_color="#00FF7F")
        self.label_head.pack(pady=10)

        # CPS Paneli
        self.cps_frame = ctk.CTkFrame(self, border_width=1)
        self.cps_frame.pack(pady=5, padx=20, fill="x")
        self.label_cps = ctk.CTkLabel(self.cps_frame, text=f"Saldırı Hızı: {self.cps} CPS", font=("Arial", 13, "bold"))
        self.label_cps.pack(pady=5)
        self.slider_cps = ctk.CTkSlider(self.cps_frame, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps); self.slider_cps.pack(pady=5, padx=10)

        # Slot Ayarları Paneli (YENİ)
        self.slot_frame = ctk.CTkFrame(self, border_width=1)
        self.slot_frame.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(self.slot_frame, text="Slot Ayarları (Klavye Tuşları)", font=("Arial", 12, "bold")).pack(pady=2)
        
        self.inner_slot_frame = ctk.CTkFrame(self.slot_frame, fg_color="transparent")
        self.inner_slot_frame.pack(pady=5)
        
        ctk.CTkLabel(self.inner_slot_frame, text="Kılıç Slotu:").grid(row=0, column=0, padx=5)
        self.entry_sword = ctk.CTkEntry(self.inner_slot_frame, width=40, justify="center")
        self.entry_sword.insert(0, self.sword_slot)
        self.entry_sword.grid(row=0, column=1, padx=5)
        self.entry_sword.bind("<KeyRelease>", lambda e: self.update_slots())

        ctk.CTkLabel(self.inner_slot_frame, text="Olta Slotu:").grid(row=0, column=2, padx=5)
        self.entry_rod = ctk.CTkEntry(self.inner_slot_frame, width=40, justify="center")
        self.entry_rod.insert(0, self.rod_slot)
        self.entry_rod.grid(row=0, column=3, padx=5)
        self.entry_rod.bind("<KeyRelease>", lambda e: self.update_slots())

        # Ofset Paneli
        self.global_frame = ctk.CTkFrame(self, border_width=2, border_color="#FF4500")
        self.global_frame.pack(pady=10, padx=20, fill="x")
        self.lbl_global = ctk.CTkLabel(self.global_frame, text=f"GENEL GECİKME OFSETİ: {self.global_ms_offset}ms", text_color="#FF4500", font=("Arial", 12, "bold"))
        self.lbl_global.pack(pady=5)
        self.sld_global = ctk.CTkSlider(self.global_frame, from_=-50, to=150, command=self.update_global_offset)
        self.sld_global.set(self.global_ms_offset); self.sld_global.pack(pady=5, padx=10)

        # MS Ayarları
        self.ms_frame = ctk.CTkFrame(self, border_width=1)
        self.ms_frame.pack(pady=10, padx=20, fill="x")
        self.lbl_sel = ctk.CTkLabel(self.ms_frame, text=f"Olta Seçim: {self.rod_select_ms}ms"); self.lbl_sel.pack()
        self.sld_sel = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "sel")); self.sld_sel.set(self.rod_select_ms); self.sld_sel.pack(padx=10)
        self.lbl_cast = ctk.CTkLabel(self.ms_frame, text=f"Kılıca Dönüş: {self.rod_cast_ms}ms"); self.lbl_cast.pack()
        self.sld_cast = ctk.CTkSlider(self.ms_frame, from_=10, to=200, command=lambda v: self.update_ms(v, "cast")); self.sld_cast.set(self.rod_cast_ms); self.sld_cast.pack(padx=10)

        # Butonlar
        self.btn_cps_key = ctk.CTkButton(self, text=f"CPS MAKRO TUŞU: {self.cps_key.upper()}", height=40, command=lambda: self.start_binding("cps"))
        self.btn_cps_key.pack(pady=5, padx=20, fill="x")
        self.btn_rod_key = ctk.CTkButton(self, text=f"OTOMATİK KOMBO TUŞU: {self.rod_key.upper()}", height=40, fg_color="#1f538d", command=lambda: self.start_binding("rod"))
        self.btn_rod_key.pack(pady=5, padx=20, fill="x")

        self.start_listeners()

    def update_cps(self, v): self.cps = int(v); self.label_cps.configure(text=f"Saldırı Hızı: {self.cps} CPS")
    def update_global_offset(self, v): self.global_ms_offset = int(v); self.lbl_global.configure(text=f"GENEL GECİKME OFSETİ: {self.global_ms_offset}ms")
    def update_ms(self, v, type):
        val = int(v)
        if type == "sel": self.rod_select_ms = val; self.lbl_sel.configure(text=f"Olta Seçim: {val}ms")
        elif type == "cast": self.rod_cast_ms = val; self.lbl_cast.configure(text=f"Kılıca Dönüş: {val}ms")
    
    def update_slots(self):
        self.sword_slot = self.entry_sword.get() or "1"
        self.rod_slot = self.entry_rod.get() or "3"

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
        if k == self.rod_slot: pass # Algoritma dışı tuşlar engellendi
        if k == self.rod_key: self.is_rod_active = not self.is_rod_active

    def execute_human_click(self):
        """
        Gelişmiş İnsansı Tıklama Mekanizması (Human-like Click).
        Sadece tıklama aralığını değil, basılı tutma (press) ve bırakma (release) 
        sürelerini de mikro düzeyde dinamik olarak simüle eder.
        """
        # 1. Temel süreyi hedef CPS'e göre belirle (Örn: 15 CPS için ~0.066 saniye döngü)
        base_cycle_time = 1.0 / self.cps
        
        # 2. İnsansı Dalgalanma (Fatigue & Ritim Etkisi)
        # Sinüs dalgası kullanarak tıklama hızının insan gibi dalgalanmasını sağlarız
        self.click_count += 1
        wave_modifier = math.sin(self.click_count * 0.1) * (base_cycle_time * 0.08)
        
        # 3. Rastgele Jitter (Gecikme Sapması)
        random_jitter = random.uniform(-base_cycle_time * 0.12, base_cycle_time * 0.12)
        
        # Toplam döngü süresi hesaplanır
        final_cycle_time = max(0.015, base_cycle_time + wave_modifier + random_jitter)
        
        # 4. Basma ve Bırakma Paylaştırılması (İnsanlar tuşa basılı tutar)
        # Tıklama süresinin ortalama %35-%45'i tuşun aşağıda kaldığı süredir
        press_duration = final_cycle_time * random.uniform(0.35, 0.45)
        release_duration = final_cycle_time - press_duration

        # Tıklamayı Gerçekleştir (Sonsuz döngü koruması aktif)
        self.ignore_software_click = True
        self.mouse_controller.press(mouse.Button.left)
        time.sleep(press_duration)
        
        self.mouse_controller.release(mouse.Button.left)
        time.sleep(max(0.002, release_duration))

    def full_auto_rod_engine(self):
        while True:
            if self.is_rod_active and self.left_pressed: # Sadece sol tık basılıyken çalışır (Konforlu PvP)
                sel_delay = max(5, self.rod_select_ms + self.global_ms_offset) / 1000.0
                cast_delay = max(5, self.rod_cast_ms + self.global_ms_offset) / 1000.0
                
                # 1. ADIM: Oltayı Seç ve At
                self.keyboard_controller.press(self.rod_slot); self.keyboard_controller.release(self.rod_slot)
                time.sleep(sel_delay + random.uniform(0.002, 0.007))
                
                self.mouse_controller.click(mouse.Button.right)
                time.sleep(cast_delay + random.uniform(0.002, 0.007))
                
                # 2. ADIM: Kılıca Dön
                self.keyboard_controller.press(self.sword_slot); self.keyboard_controller.release(self.sword_slot)
                time.sleep(0.02 + random.uniform(0.001, 0.004))
                
                # 3. ADIM: Yoğun İnsansı Vuruş (Burst)
                end_time = time.time() + random.uniform(0.65, 0.75) # Burst süresi de sabit değil
                while time.time() < end_time and self.is_rod_active and self.left_pressed:
                    self.execute_human_click()
                
                time.sleep(random.uniform(0.04, 0.08)) # İnsansı refleks duraksaması
            else:
                time.sleep(0.1)

    def click_engine(self):
        while True:
            if self.is_cps_active and self.left_pressed and not self.is_rod_active:
                self.execute_human_click()
            else:
                time.sleep(0.01)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        
        def on_click(x, y, btn, prs):
            if btn == mouse.Button.left:
                # Eğer tıklama bizim yazılımımız tarafından yapıldıysa, bunu yok say
                if self.ignore_software_click:
                    if not prs: # Fare bırakıldığında koruma bayrağını indir
                        self.ignore_software_click = False
                    return
                self.left_pressed = prs
                
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()
        threading.Thread(target=self.full_auto_rod_engine, daemon=True).start()

if __name__ == "__main__":
    app = YahyaUltimateMacro()
    app.mainloop()
                    
