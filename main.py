import customtkinter as ctk
from pynput import mouse, keyboard
import threading
import time
import ctypes
import random

# Windows API / Çekirdek Seviyesi Tıklama Sabitleri
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

class YahyaUltimateMacro(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Ayarları
        self.title("Yahya Yapımı - Ultimate Pro v6 (Kararlı İnsansı Akış)")
        self.geometry("550x950")
        ctk.set_appearance_mode("dark")
        
        # --- DEĞİŞKENLER ---
        self.is_cps_active = False     
        self.is_rod_active = False     
        
        self.cps_key = "b"             
        self.rod_key = "y"             
        
        self.cps = 14
        self.combo_cps = 14            
        self.rod_select_ms = 45        
        self.rod_cast_ms = 45          
        self.global_ms_offset = 0      
        
        self.sword_slot = "1"
        self.rod_slot = "3"

        self.click_mode = "normal"  # "normal" / "human" / "butterfly"
        self.butterfly_toggle = True  # butterfly modunda kısa/uzun döngü sırası

        self.waiting_for_key = None
        self.keyboard_controller = keyboard.Controller()
        self.left_pressed = False
        
        self.ignore_software_click = False

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

        # Kombo CPS Paneli
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

        # Vuruş Modu Paneli
        self.mode_frame = ctk.CTkFrame(self, border_width=1, border_color="#8A2BE2")
        self.mode_frame.pack(pady=5, padx=20, fill="x")
        ctk.CTkLabel(self.mode_frame, text="Vuruş Modu", font=("Arial", 12, "bold")).pack(pady=2)
        self.mode_selector = ctk.CTkSegmentedButton(
            self.mode_frame,
            values=["Normal", "Jitter", "Butterfly"],
            command=self.set_click_mode
        )
        self.mode_selector.set("Normal")
        self.mode_selector.pack(pady=8, padx=10, fill="x")

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
        self.sld_sel = ctk.CTkSlider(self.ms_frame, from_=5, to=200, command=lambda v: self.update_ms(v, "sel")); self.sld_sel.set(self.rod_select_ms); self.sld_sel.pack(padx=10)
        self.lbl_cast = ctk.CTkLabel(self.ms_frame, text=f"Kılıca Dönüş: {self.rod_cast_ms}ms"); self.lbl_cast.pack()
        self.sld_cast = ctk.CTkSlider(self.ms_frame, from_=5, to=200, command=lambda v: self.update_ms(v, "cast")); self.sld_cast.set(self.rod_cast_ms); self.sld_cast.pack(padx=10)

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
        self.sword_slot = (self.entry_sword.get()[:1]) or "1"
        self.rod_slot = (self.entry_rod.get()[:1]) or "3"

    def set_click_mode(self, value):
        mode_map = {"Normal": "normal", "Jitter": "human", "Butterfly": "butterfly"}
        self.click_mode = mode_map.get(value, "normal")
        self.butterfly_toggle = True  # mod değişince baştan başlasın

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

    def execute_real_mouse_click(self, target_cps):
        """
        Üç modlu Syscall vuruş motoru:
        - "normal": tam sabit ritim, jitter yok
        - "human": fark edilmeyecek kadar düşük (+-%1.5) jitter
        - "butterfly": kısa-uzun döngü çiftleriyle butterfly click ritmi,
          ortalama CPS yine slider'a sadık kalır, gecikme neredeyse yok
        """
        # Seçilen CPS için gereken temel döngü süresi (Örn: 14 CPS için ~0.071 saniye)
        base_cycle_time = 1.0 / max(1, target_cps)

        if self.click_mode == "human":
            jitter_range = base_cycle_time * 0.015  # çok düşük, göze çarpmaz
            human_jitter = random.uniform(-jitter_range, jitter_range)
            final_cycle_time = max(0.004, base_cycle_time + human_jitter)

        elif self.click_mode == "butterfly":
            # Butterfly tekniği: hızlı çift vuruş + kısa dinlenme.
            # Kısa döngü %60, uzun döngü %140 -> ortalaması yine base_cycle_time'a eşit,
            # yani toplamda zaman kaybı olmaz, sadece ritim "tık-tık ... tık-tık" olur.
            if self.butterfly_toggle:
                final_cycle_time = max(0.004, base_cycle_time * 0.6)
            else:
                final_cycle_time = max(0.004, base_cycle_time * 1.4)
            self.butterfly_toggle = not self.butterfly_toggle

        else:  # normal
            final_cycle_time = max(0.004, base_cycle_time)

        # Gerçek mouselarda tuşa basılma (hold) ve bırakılma süresi mekaniktir.
        hold_duration = final_cycle_time * 0.35  # Tuşun aşağıda kalma süresi
        release_duration = final_cycle_time - hold_duration  # Tuşun yukarı kalkma süresi

        # Doğrudan Windows Çekirdeğine Gönderim (Syscall)
        self.ignore_software_click = True
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(hold_duration)
        
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(max(0.001, release_duration))

    def fast_right_click(self):
        """Olta için stabil sağ tık çağrısı."""
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        time.sleep(0.015) # Kısa basılı kalma payı
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def click_engine(self):
        """Sol tık vuruş kontrolü. Akış net, kararlı ve slider'a %100 bağlıdır."""
        while True:
            if self.left_pressed:
                if self.is_rod_active:
                    # Kombo aktifse arayüzdeki mavi kaydırıcıyı (Combo CPS) kullanır
                    self.execute_real_mouse_click(target_cps=self.combo_cps)
                elif self.is_cps_active:
                    # Normal makro aktifse üstteki kaydırıcıyı (Normal CPS) kullanır
                    self.execute_real_mouse_click(target_cps=self.cps)
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.01)

    def full_auto_rod_engine(self):
        """Kılıç vuruşları milisaniyesi şaşmadan akarken bu motor arka planda olta döngüsünü yönetir."""
        while True:
            if self.is_rod_active and self.left_pressed:
                sel_delay = max(2, self.rod_select_ms + self.global_ms_offset) / 1000.0
                cast_delay = max(2, self.rod_cast_ms + self.global_ms_offset) / 1000.0
                
                # 1. Oltayı eline al
                self.keyboard_controller.press(self.rod_slot); self.keyboard_controller.release(self.rod_slot)
                time.sleep(sel_delay)
                
                # 2. Oltayı fırlat (Rekt)
                self.fast_right_click()
                time.sleep(cast_delay)
                
                # 3. Kılıca geri dön (Düzgün hasar vermeye devam et)
                self.keyboard_controller.press(self.sword_slot); self.keyboard_controller.release(self.sword_slot)
                
                # İdeal Rekt Combo ritmi beklemesi (0.6 saniye)
                time.sleep(0.6)
            else:
                time.sleep(0.05)

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
    
