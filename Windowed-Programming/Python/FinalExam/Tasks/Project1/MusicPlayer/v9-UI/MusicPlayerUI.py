import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # ===== 播放狀態 =====
        self.playlist = []
        self.current_song_idx = 0
        self.seek_offset_sec = 0
        self.is_paused = False
        self.repeat_mode = 0
        self.was_playing = False
        self.song_length_sec = 0

        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)

        # =========================
        # Spotify 版面結構（Step 1）
        # =========================

        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True)

        # 上半部
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill="both", expand=True)

        # 左側 Sidebar（歌單）
        sidebar_frame = tk.Frame(top_frame, width=200)
        sidebar_frame.pack(side="left", fill="y")

        self.song_listbox = tk.Listbox(sidebar_frame)
        self.song_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

        # 右側 Content（播放資訊）
        content_frame = tk.Frame(top_frame)
        content_frame.pack(side="left", fill="both", expand=True)

        self.current_time_label = tk.Label(
            content_frame,
            text="00:00 / 00:00",
            font=("Segoe UI", 14)
        )
        self.current_time_label.pack(pady=40)

        # =========================
        # 底部播放器（Bottom Bar）
        # =========================

        player_frame = tk.Frame(main_frame)
        player_frame.pack(fill="x")

        # 控制列
        control_frame = tk.Frame(player_frame)
        control_frame.pack(pady=5)

        tk.Button(control_frame, text="⏮", width=4, command=self.prev_song).pack(side="left", padx=4)
        tk.Button(control_frame, text="▶", width=4, command=self.play_music).pack(side="left", padx=4)
        tk.Button(control_frame, text="⏭", width=4, command=self.next_song).pack(side="left", padx=4)

        self.pause_button = tk.Button(
            control_frame, text="Pause", command=self.toggle_pause
        )
        self.pause_button.pack(side="left", padx=6)

        # ✅ Stop（作業要求，不能刪）
        tk.Button(
            control_frame, text="Stop", command=self.stop_music
        ).pack(side="left", padx=6)

        self.repeat_button = tk.Button(
            control_frame, text="Repeat: Off", command=self.toggle_repeat_mode
        )
        self.repeat_button.pack(side="left", padx=6)

        # 進度條
        self.progress_var = tk.IntVar(value=0)
        self.progress_scale = tk.Scale(
            player_frame,
            from_=0,
            to=0,
            orient="horizontal",
            variable=self.progress_var
        )
        self.progress_scale.pack(fill="x", padx=10)

        self.progress_scale.bind("<ButtonPress-1>", self.on_progress_press)
        self.progress_scale.bind("<ButtonRelease-1>", self.on_progress_release)
        self.is_dragging_progress = False

        # 音量
        self.volume_scale = tk.Scale(
            player_frame,
            from_=0,
            to=100,
            orient="horizontal",
            label="Volume",
            command=self.change_volume
        )
        self.volume_scale.set(50)
        self.volume_scale.pack(fill="x", padx=10)

        # 新增歌曲
        tk.Button(
            player_frame, text="Add Song", command=self.add_song
        ).pack(pady=5)

        self.update_progress()

    # ================= 播放邏輯 =================

    def load_song(self, path):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        sound = pygame.mixer.Sound(path)
        self.song_length_sec = int(sound.get_length())

        self.progress_scale.config(to=self.song_length_sec)
        self.progress_var.set(0)

        self.seek_offset_sec = 0
        self.is_paused = False
        self.pause_button.config(text="Pause")
        self.update_time_label(0)

    def play_music(self):
        if not self.playlist:
            return
        self.load_song(self.playlist[self.current_song_idx])

    def toggle_pause(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_button.config(text="Resume")
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_button.config(text="Pause")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.progress_var.set(0)
        self.update_time_label(0)
        self.seek_offset_sec = 0
        self.is_paused = False
        self.pause_button.config(text="Pause")

    def prev_song(self):
        if not self.playlist:
            return
        self.current_song_idx = (
            self.current_song_idx - 1
            if self.current_song_idx > 0
            else len(self.playlist) - 1
        )
        self.load_song(self.playlist[self.current_song_idx])

    def next_song(self):
        if not self.playlist:
            return
        self.current_song_idx = (
            self.current_song_idx + 1
            if self.current_song_idx < len(self.playlist) - 1
            else 0
        )
        self.load_song(self.playlist[self.current_song_idx])

    def toggle_repeat_mode(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        self.repeat_button.config(
            text=["Repeat: Off", "Repeat: One", "Repeat: All"][self.repeat_mode]
        )

    # ================= 清單 =================

    def add_song(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if path:
            self.playlist.append(path)
            self.song_listbox.insert(tk.END, os.path.basename(path))

    def on_song_select(self, event):
        if not self.song_listbox.curselection():
            return
        self.current_song_idx = self.song_listbox.curselection()[0]
        self.load_song(self.playlist[self.current_song_idx])

    # ================= 進度與時間 =================

    def update_time_label(self, sec):
        m, s = divmod(sec, 60)
        tm, ts = divmod(self.song_length_sec, 60)
        self.current_time_label.config(
            text=f"{m:02d}:{s:02d} / {tm:02d}:{ts:02d}"
        )

    def change_volume(self, value):
        pygame.mixer.music.set_volume(int(value) / 100)

    def on_progress_press(self, event):
        self.is_dragging_progress = True

    def on_progress_release(self, event):
        sec = self.progress_var.get()
        self.seek_offset_sec = sec
        pygame.mixer.music.stop()
        pygame.mixer.music.play(start=sec)
        self.update_time_label(sec)
        self.is_dragging_progress = False

    def update_progress(self):
        playing = pygame.mixer.music.get_busy()

        if self.was_playing and not playing and not self.is_paused:
            if self.repeat_mode == 1:
                self.load_song(self.playlist[self.current_song_idx])
            elif self.repeat_mode == 2:
                self.next_song()

        self.was_playing = playing

        if playing and not self.is_dragging_progress and not self.is_paused:
            pos = pygame.mixer.music.get_pos()
            if pos >= 0:
                sec = self.seek_offset_sec + pos // 1000
                self.progress_var.set(sec)
                self.update_time_label(sec)

        self.root.after(500, self.update_progress)


root = tk.Tk()
MusicPlayer(root)
root.mainloop()
