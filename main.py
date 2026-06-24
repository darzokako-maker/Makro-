import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import random
import math
import ctypes

# Windows API / Syscall Tıklama Sabitleri
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

class YahyaUltimateMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Yahya Yapımı - Ultimate Pro v4 (Syscall Edition)")
        self.geometry("550x950")
        ctk.set_appearance_mode("dark")
        
        # --- DEĞİŞKENLER ---
        self.is_cps_active = False     
        self.is_rod_active = False     
        
        self.cps_key = "b"             
        self.rod_key = "y"             
        
        self.cps = 14
        self.combo_cps = 12            
        self.rod_select_ms = 45        
        self.rod_cast_ms = 45          
        self.global_ms_offset = 0      
        
        self.sword_slot = "1"
        self.rod_slot = "3"
        
        self.waiting_for_key = None
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False
        
        self.ignore_software_click = False
        self.click_count = 0

        # --- ARAYÜZ ---
        self.label_head = ctk.CTkLabel(self, text="YAHYA YAPIMI", font=("Impact", 35), text_color="#00FF7F")
        self.label_head.pack(pady=10)

        # Normal CPS Paneli
        self.cps_frame = ctk.CTkFrame(self, border_width=1)
        self.cps_frame.pack(pady=5, padx=20, fill="x")
        self.label_cps = ctk.CTkLabel(self.cps_frame, text=f"Normal Saldırı Hızı: {self.cps} CPS", font=("Arial", 13, "bold"))
        self.label_cps.pack(pady=5)
        self.slider_cps = ctk.CTkSlider(self.cps_frame, from_=1, to=30, command=self.update_cps)
        self.slider_cps.set(self.cps); self.slider_cps.pack(pady=5, padx=10)

        # Kombo CPS Paneli (Rekt Esnasındaki Vuruş Ayarı)
        self.combo_cps_frame = ctk.CTkFrame(self, border_width=1, border_color="#1f538d")
        self.combo_cps_frame.pack(pady=5, padx=20, fill="x")
        self.label_combo_cps = ctk.CTkLabel(self.combo_cps_frame, text=f"Kombo Vuruş Hızı (Kılıç Hasarı): {self.combo_cps} CPS", font=("Arial", 13, "bold"), text_color="#63B8FF")
        self.label_combo_cps.pack(pady=5)
        self.slider_combo_cps = ctk.CTkSlider(self.combo_cps_frame, from_=1, to=30, command=self.update_combo_cps, button_color="#1f538d")
        self.slider_combo_cps.set(self.combo_cps); self.slider_combo_cps.pack(pady=5, padx=10)

        # Slot Ayarları Paneli
        self.slot_frame = ctk.CTkFrame(self, border_width=1)
        self.slot_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.slot_frame, text="Slot Ayarları (Klavye Tuşları)", font=("Arial", 12, "bold")).pack(pady=2)
        self.inner_slot_frame = ctk.CTkFrame(self.slot_frame, fg_color="transparent")
        self.inner_slot_frame.pack(pady=5)
        
        ctk.CTkLabel(self.inner_slot_frame, text="Kılıç Slotu:").grid(row=0, column=0, padx=5)
        self.entry_sword = ctk.CTkEntry(self.inner_slot_frame, width=40, justify="center")
        self.entry_sword.insert(0, self.sword_slot); self.entry_sword.grid(row=0, column=1, padx=5)
        self.entry_sword.bind("<KeyRelease>", lambda e: self.update_slots())

        ctk.CTkLabel(self.inner_slot_frame, text="Olta Slotu:").grid(row=0, column=2, padx=5)
        self.entry_rod = ctk.CTkEntry(self.inner_slot_frame, width=40, justify="center")
        self.entry_rod.insert(0, self.rod_slot); self.entry_rod.grid(row=0, column=3, padx=5)
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

    def update_cps(self, v): self.cps = int(v); self.label_cps.configure(text=f"Normal Saldırı Hızı: {self.cps} CPS")
    def update_combo_cps(self, v): self.combo_cps = int(v); self.label_combo_cps.configure(text=f"Kombo Vuruş Hızı (Kılıç Hasarı): {self.combo_cps} CPS")
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
        if k == self.rod_key: self.is_rod_active = not self.is_rod_active

    def execute_syscall_click(self, target_cps):
        """
        Donanım / Sürücü katmanını bypass eden alt seviye işletim sistemi çağrısı (Syscall benzeri).
        İnsansı ritim ve dinamik basılı tutma sürelerini içerir.
        """
        base_cycle_time = 1.0 / target_cps
        
        self.click_count += 1
        wave_modifier = math.sin(self.click_count * 0.15) * (base_cycle_time * 0.07)
        random_jitter = random.uniform(-base_cycle_time * 0.10, base_cycle_time * 0.10)
        
        final_cycle_time = max(0.010, base_cycle_time + wave_modifier + random_jitter)
        press_duration = final_cycle_time * random.uniform(0.35, 0.45)
        release_duration = final_cycle_time - press_duration

        # Doğrudan Win32 API Çekirdek Giriş Enjeksiyonu (Anti-Cheat Bypass)
        self.ignore_software_click = True
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(press_duration)
        
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(max(0.002, release_duration))

    def execute_syscall_right_click(self):
        """Olta atmak için kullanılan güvenli sağ tık çağrısı."""
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(random.uniform(0.015, 0.025)) # Kısa basılı tutma payı
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def full_auto_rod_engine(self):
        """
        Mükemmel Rekt Döngüsü: Olta atılırken kılıç vuruşları (Sol Tık) kesilmez.
        Sistem arkada sürekli kılıçla düzgün hasar çıkartırken eşzamanlı olta fırlatır.
        """
        while True:
            if self.is_rod_active and self.left_pressed:
                sel_delay = max(5, self.rod_select_ms + self.global_ms_offset) / 1000.0
                cast_delay = max(5, self.rod_cast_ms + self.global_ms_offset) / 1000.0
                
                # [REKT BAŞLANGICI] Kılıçla vurmaya devam ederken bir yandan oltaya geçiş sinyali gönder
                self.keyboard_controller.press(self.rod_slot); self.keyboard_controller.release(self.rod_slot)
                time.sleep(sel_delay + random.uniform(0.002, 0.005))
                
                # Oltayı fırlat (Rakibi sersemlet)
                self.execute_syscall_right_click()
                time.sleep(cast_delay + random.uniform(0.002, 0.005))
                
                # Hemen kılıç slotuna geri dön
                self.keyboard_controller.press(self.sword_slot); self.keyboard_controller.release(self.sword_slot)
                
                # [DÜZGÜN HASAR PENCERESİ] Olta isabet etti, şimdi ayarlanan Kombo CPS ile rüzgar gibi esme vakti
                end_time = time.time() + random.uniform(0.70, 0.85)
                while time.time() < end_time and self.is_rod_active and self.left_pressed:
                    self.execute_syscall_click(target_cps=self.combo_cps)
                
                time.sleep(random.uniform(0.03, 0.06)) # Kısa insansı nefeslenme gecikmesi
            else:
                time.sleep(0.1)

    def click_engine(self):
        while True:
            # Normal makro modu açıkken ve kombo modu aktif değilken düzgün sol tık makrosu
            if self.is_cps_active and self.left_pressed and not self.is_rod_active:
                self.execute_syscall_click(target_cps=self.cps)
            else:
                time.sleep(0.01)

    def start_listeners(self):
        keyboard.Listener(on_press=self.on_press).start()
        
        def on_click(x, y, btn, prs):
            if btn == mouse.Button.left:
                if self.ignore_software_click:
                    if not prs:
                        self.ignore_software_click = False
                    return
                self.left_pressed = prs
                
        mouse.Listener(on_click=on_click).start()
        threading.Thread(target=self.click_engine, daemon=True).start()
        threading.Thread(target=self.full_auto_rod_engine, daemon=True).start()

if __name__ == "__main__":
    app = YahyaUltimateMacro()
    app.mainloop()
                
