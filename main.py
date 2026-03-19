import customtkinter as ctk
from PIL import Image
import os
import database
from timer_logic import PomodoroLogic

RENKLER = {
    "ANA_ARKA_PLAN": "#252525",      # Pencere genel rengi
    "PANEL_ARKA_PLAN": "#252525",    # Ayarlar kutusu rengi
    "BUTON_BASLAT": "#2ecc71",       # Başlat/Devam Et 
    "BUTON_DURAKLAT": "#f39c12",     # Duraklat 
    "BUTON_SIFIRLA": "#e74c3c",      # Sıfırla 
    "YAZI_ANA": "#ffffff",           # Genel yazı rengi
    "YAZI_VURGU": "#3498db",         # Döngü sayısı rengi
    "ILERLEME_CUBUGU": "#2ecc71",    # Progress bar dolum rengi
    "GECMIS_GUN_BUTON": "#34495e",   # Geçmişteki gün butonları
    "GECMIS_GUN_HOVER": "#2c3e50",   # Gün butonuna gelince
    "GECMIS_KART_IC": "#2c3e50"      # Seans kartlarının içi
}

class PomodoroApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Pomodoro")
        self.geometry("600x950")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color=RENKLER["ANA_ARKA_PLAN"])
        
        self.logic = PomodoroLogic()
        self.remaining_secs = 0
        self.total_work_secs = 0
        self.timer_id = None
        self.completed_cycles = 0 
        
        self.saved_work_mins = 25
        self.saved_break_mins = 5
        self.saved_fig_set = "Kurbağa"
        
        database.init_db() 
        
        
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        self.show_timer_page()

    def clear_container(self):
       
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def play_notification(self, notify_type="work_done"):
      
        sound = "Glass" if notify_type == "work_done" else "Hero"
        os.system(f'afplay /System/Library/Sounds/{sound}.aiff')


    def show_timer_page(self):
        self.clear_container()
        
     
        if not self.logic.is_running and self.remaining_secs <= 0:
            self.settings_frame = ctk.CTkFrame(self.main_container, fg_color=RENKLER["PANEL_ARKA_PLAN"])
            self.settings_frame.pack(pady=20, padx=30, fill="x")
            
            
            ctk.CTkLabel(self.settings_frame, text="İş (DK)").grid(row=0, column=0, padx=20)
            self.entry_work = ctk.CTkEntry(self.settings_frame, width=80)
            self.entry_work.insert(0, str(self.saved_work_mins))
            self.entry_work.grid(row=1, column=0, padx=20, pady=10)

           
            ctk.CTkLabel(self.settings_frame, text="Mola (DK)").grid(row=0, column=1, padx=20)
            self.entry_break = ctk.CTkEntry(self.settings_frame, width=80)
            self.entry_break.insert(0, str(self.saved_break_mins))
            self.entry_break.grid(row=1, column=1, padx=20, pady=10)

       
            self.figure_option = ctk.CTkOptionMenu(self.settings_frame, values=["Kurbağa", "Penguen", "Kedi", "Köpek"])
            self.figure_option.set(self.saved_fig_set)
            self.figure_option.grid(row=1, column=2, padx=20)

       
        self.figure_label = ctk.CTkLabel(self.main_container, text="")
        self.figure_label.pack(pady=10)
        
        
        self.timer_label = ctk.CTkLabel(self.main_container, text=self.logic.format_time(self.remaining_secs), font=("Helvetica", 90, "bold"), text_color=RENKLER["YAZI_ANA"])
        self.timer_label.pack(pady=0)
        
        
        self.cycle_display = ctk.CTkLabel(self.main_container, text=f"Tamamlanan Döngü: {self.completed_cycles}", 
                                           font=("Helvetica", 16, "bold"), text_color=RENKLER["YAZI_VURGU"])
        self.cycle_display.pack(pady=5)

      
        self.progress = ctk.CTkProgressBar(self.main_container, width=450, height=15, progress_color=RENKLER["ILERLEME_CUBUGU"])
        self.progress_label = ctk.CTkLabel(self.main_container, text="Odaklanma: %0", font=("Arial", 14, "italic"))
        
        if self.logic.is_running:
            self.progress.pack(pady=10)
            self.progress_label.pack()

      
        btn_txt = "DURAKLAT" if self.logic.is_running else ("DEVAM ET" if self.remaining_secs > 0 else "ODAKLANMAYA BAŞLA")
        btn_col = RENKLER["BUTON_DURAKLAT"] if self.logic.is_running else RENKLER["BUTON_BASLAT"]

        self.btn_main = ctk.CTkButton(self.main_container, text=btn_txt, command=self.toggle_session, 
                                       fg_color=btn_col, font=("Helvetica", 18, "bold"), height=60)
        self.btn_main.pack(pady=10)

        
        self.btn_history = ctk.CTkButton(self.main_container, text="📊 GEÇMİŞ KAYITLAR", command=self.show_history_page, fg_color=RENKLER["GECMIS_GUN_BUTON"])
        self.btn_history.pack(pady=5)

        self.btn_reset = ctk.CTkButton(self.main_container, text="DÖNGÜYÜ SIFIRLA", command=self.reset_timer, fg_color=RENKLER["BUTON_SIFIRLA"])
        self.btn_reset.pack(pady=5)

        self.update_image_display()


    def show_history_page(self):
        self.clear_container()
        
        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(pady=20, fill="x")
       
        ctk.CTkButton(header, text="← GERİ", width=70, command=self.show_timer_page, fg_color=RENKLER["GECMIS_GUN_BUTON"]).place(x=20, y=0)
        ctk.CTkLabel(header, text="ÇALIŞMA GEÇMİŞİ", font=("Helvetica", 22, "bold")).pack()

        scroll = ctk.CTkScrollableFrame(self.main_container, width=550, height=700, fg_color="transparent")
        scroll.pack(pady=10, padx=20, fill="both", expand=True)

        data = database.get_all_sessions()
        
   
        grouped = {}
        for w, b, f, d_str in data:
            day = d_str[:10]
            if day not in grouped: grouped[day] = []
            grouped[day].append((w, b, f, d_str))

        for day, sessions in grouped.items():
           
            day_btn = ctk.CTkButton(scroll, text=f"📅 {day} ({len(sessions)} Seans)", 
                                     fg_color=RENKLER["GECMIS_GUN_BUTON"], hover_color=RENKLER["GECMIS_GUN_HOVER"],
                                     font=("Arial", 14, "bold"), anchor="w", height=45)
            day_btn.pack(pady=5, fill="x")

            session_frame = ctk.CTkFrame(scroll, fg_color="transparent")

          
            def toggle(f=session_frame):
                if f.winfo_viewable(): f.pack_forget()
                else: f.pack(fill="x", padx=10, pady=2)

            day_btn.configure(command=toggle)

            for w, b, f, d_full in sessions:
                card = ctk.CTkFrame(session_frame, fg_color=RENKLER["GECMIS_KART_IC"], corner_radius=10)
                card.pack(pady=4, fill="x")
              
                ctk.CTkLabel(card, text=f"⏰ {d_full[11:16]}\n👾 {f.upper()}", justify="left").pack(side="left", padx=15, pady=8)
               
                ctk.CTkLabel(card, text=f"🚀 {w} dk / ☕ {b} dk", justify="right", text_color=RENKLER["BUTON_BASLAT"]).pack(side="right", padx=15, pady=8)

  
    def update_image_display(self):
        if self.remaining_secs <= 0 and not self.logic.is_running:
            path = os.path.join("assets", "start.png")
        else:
            elapsed = self.total_work_secs - self.remaining_secs
            is_break = (self.logic.mode == "break")
            stage = self.logic.get_figure_stage(elapsed, self.total_work_secs, is_break)
            path = os.path.join("assets", self.saved_fig_set, "mola.png" if stage == "break_form" else f"{stage}.png")

        try:
            raw = Image.open(path)
            img = ctk.CTkImage(light_image=raw, dark_image=raw, size=(500, 500))
            self.figure_label.configure(image=img, text="")
        except:
            self.figure_label.configure(text="[PNG Bulunamadı]")

    def toggle_session(self):
        if not self.logic.is_running:
            if self.remaining_secs <= 0:
              
                self.saved_work_mins = int(self.entry_work.get())
                self.saved_break_mins = int(self.entry_break.get())
                self.saved_fig_set = self.figure_option.get()
                self.total_work_secs = self.saved_work_mins * 60
                self.remaining_secs = self.total_work_secs
            
            self.logic.is_running = True
            self.show_timer_page() 
            self.tick()
        else:
            self.logic.is_running = False
            if self.timer_id: self.after_cancel(self.timer_id)
            self.show_timer_page()

    def tick(self):
        if self.remaining_secs >= 0 and self.logic.is_running:
            self.timer_label.configure(text=self.logic.format_time(self.remaining_secs))
            if self.logic.mode == "work":
                p_val = (self.total_work_secs - self.remaining_secs) / self.total_work_secs
                self.progress.set(p_val)
                self.progress_label.configure(text=f"Odaklanma: %{int(p_val * 100)}")
            
            self.update_image_display()
            self.remaining_secs -= 1
            self.timer_id = self.after(1000, self.tick)
            
        elif self.remaining_secs < 0:
          
            if self.logic.mode == "work":
                self.play_notification("work_done")
                self.logic.mode = "break"
                self.remaining_secs = self.saved_break_mins * 60
                self.show_timer_page()
                self.tick() 
            else:
        
                self.completed_cycles += 1
                database.save_session(self.saved_work_mins, self.saved_break_mins, self.saved_fig_set)
                self.play_notification("break_done")
                self.logic.mode = "work"
                self.remaining_secs = self.saved_work_mins * 60
                self.show_timer_page()
                self.tick()

    def reset_timer(self):
        self.logic.is_running = False
        if self.timer_id: self.after_cancel(self.timer_id)
        self.remaining_secs = 0
        self.completed_cycles = 0
        self.show_timer_page()

if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()


