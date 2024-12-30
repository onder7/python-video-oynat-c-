import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import PIL.Image, PIL.ImageTk
import time
import os
import numpy as np

class VideoPlayer:
    def __init__(self, window):
        self.window = window
        self.window.title("Gelişmiş Video Oynatıcı")
        self.window.geometry("800x600")

        # Video değişkenleri
        self.cap = None
        self.is_playing = False
        self.total_frames = 0
        self.current_frame = 0
        self.playback_speed = 1.0
        self.is_fullscreen = False
        self.current_effect = 'normal'
        self.playlist = []
        self.current_video_index = -1
        
        # Efekt seçenekleri
        self.effects = {
            'normal': lambda frame: frame,
            'grayscale': lambda frame: cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR),
            'blur': lambda frame: cv2.GaussianBlur(frame, (15, 15), 0),
            'edge': lambda frame: cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 100, 200),
            'sepia': self.sepia_effect
        }
        
        self.create_widgets()
        self.bind_keyboard_shortcuts()

    def create_widgets(self):
        # Ana çerçeve
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Video gösterme alanı
        self.video_frame = ttk.Frame(self.main_frame)
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        self.video_label = tk.Label(self.video_frame, bg='black')
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Kontrol çerçevesi
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=5)

        # Oynatma kontrolleri
        self.play_button = ttk.Button(controls_frame, text="▶", width=3, command=self.toggle_play)
        self.play_button.pack(side=tk.LEFT, padx=5)

        # İlerleme çubuğu
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(controls_frame, from_=0, to=100, 
                                    orient='horizontal',
                                    variable=self.progress_var,
                                    command=self.seek)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Playlist paneli
        self.playlist_frame = ttk.Frame(self.window)
        self.playlist_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_listbox = tk.Listbox(self.playlist_frame, width=40)
        self.playlist_listbox.pack(fill=tk.BOTH, expand=True)
        self.playlist_listbox.bind('<<ListboxSelect>>', self.on_playlist_select)

        # Kontrol paneli
        control_panel = ttk.Frame(self.main_frame)
        control_panel.pack(fill=tk.X, pady=5)

        # Hız kontrolü
        speed_frame = ttk.Frame(control_panel)
        speed_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(speed_frame, text="Hız:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="1.0x")
        speed_menu = ttk.OptionMenu(speed_frame, self.speed_var, "1.0x", 
                                  "0.5x", "1.0x", "1.5x", "2.0x",
                                  command=self.change_speed)
        speed_menu.pack(side=tk.LEFT)

        # Efekt kontrolü
        effect_frame = ttk.Frame(control_panel)
        effect_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(effect_frame, text="Efekt:").pack(side=tk.LEFT)
        self.effect_var = tk.StringVar(value="normal")
        effect_menu = ttk.OptionMenu(effect_frame, self.effect_var, "normal",
                                   "normal", "grayscale", "blur", "edge", "sepia",
                                   command=self.change_effect)
        effect_menu.pack(side=tk.LEFT)

        # Playlist kontrolleri
        playlist_controls = ttk.Frame(control_panel)
        playlist_controls.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(playlist_controls, text="Dosya Ekle", 
                  command=self.add_to_playlist).pack(side=tk.LEFT, padx=2)
        ttk.Button(playlist_controls, text="Listeyi Temizle", 
                  command=self.clear_playlist).pack(side=tk.LEFT, padx=2)

    def toggle_play(self):
        if self.cap is not None:
            self.is_playing = not self.is_playing
            self.play_button.config(text="⏸" if self.is_playing else "▶")

    def seek(self, value):
        if self.cap is not None:
            frame_no = int((float(value) / 100) * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

    def bind_keyboard_shortcuts(self):
        self.window.bind('<space>', lambda e: self.toggle_play())
        self.window.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.window.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.window.bind('<Left>', lambda e: self.seek_relative(-5))
        self.window.bind('<Right>', lambda e: self.seek_relative(5))
        self.window.bind('<Up>', lambda e: self.increase_speed())
        self.window.bind('<Down>', lambda e: self.decrease_speed())

    def sepia_effect(self, frame):
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
        return cv2.transform(frame, sepia_filter)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.window.attributes('-fullscreen', self.is_fullscreen)

    def exit_fullscreen(self):
        self.is_fullscreen = False
        self.window.attributes('-fullscreen', False)

    def change_speed(self, value):
        self.playback_speed = float(value.replace('x', ''))

    def change_effect(self, effect):
        self.current_effect = effect

    def add_to_playlist(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")])
        for file in files:
            self.playlist.append(file)
            self.playlist_listbox.insert(tk.END, os.path.basename(file))
        
        if self.current_video_index == -1 and self.playlist:
            self.current_video_index = 0
            self.play_video(self.playlist[0])

    def clear_playlist(self):
        self.playlist = []
        self.playlist_listbox.delete(0, tk.END)
        self.current_video_index = -1

    def on_playlist_select(self, event):
        selection = self.playlist_listbox.curselection()
        if selection:
            self.current_video_index = selection[0]
            self.play_video(self.playlist[self.current_video_index])

    def play_video(self, file_path):
        if self.cap is not None:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(file_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.is_playing = True
        self.play_button.config(text="⏸")
        self.update_frame()

    def seek_relative(self, seconds):
        if self.cap is not None:
            current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = current_frame + (seconds * self.fps)
            new_frame = max(0, min(new_frame, self.total_frames))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def increase_speed(self):
        speeds = [0.5, 1.0, 1.5, 2.0]
        current = speeds.index(self.playback_speed)
        if current < len(speeds) - 1:
            self.playback_speed = speeds[current + 1]
            self.speed_var.set(f"{self.playback_speed}x")

    def decrease_speed(self):
        speeds = [0.5, 1.0, 1.5, 2.0]
        current = speeds.index(self.playback_speed)
        if current > 0:
            self.playback_speed = speeds[current - 1]
            self.speed_var.set(f"{self.playback_speed}x")

    def update_frame(self):
        if self.cap is not None and self.is_playing:
            ret, frame = self.cap.read()
            if ret:
                # Efekt uygula
                frame = self.effects[self.current_effect](frame)
                
                # Frame'i göster
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = PIL.Image.fromarray(frame)
                
                # Tam ekran modunda boyutu ayarla
                if self.is_fullscreen:
                    screen_width = self.window.winfo_width()
                    screen_height = self.window.winfo_height()
                    image = image.resize((screen_width, screen_height), PIL.Image.LANCZOS)
                
                photo = PIL.ImageTk.PhotoImage(image=image)
                self.video_label.config(image=photo)
                self.video_label.image = photo
                
                # İlerleme çubuğunu güncelle
                progress = (self.cap.get(cv2.CAP_PROP_POS_FRAMES) / self.total_frames) * 100
                self.progress_var.set(progress)
                
                # Oynatma hızına göre bir sonraki frame'i planla
                delay = int(1000 / (self.fps * self.playback_speed))
                self.window.after(delay, self.update_frame)
            else:
                # Video bittiğinde sonraki videoya geç veya başa sar
                if self.current_video_index < len(self.playlist) - 1:
                    self.current_video_index += 1
                    self.play_video(self.playlist[self.current_video_index])
                else:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.is_playing = False
                    self.play_button.config(text="▶")
        else:
            self.window.after(100, self.update_frame)

    def __del__(self):
        if self.cap is not None:
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()
