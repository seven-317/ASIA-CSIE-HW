import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")

        self.root.geometry("400x550")
        self.root.resizable(False, False)

        self.playlist = []
        self.current_song_idx = 0

        pygame.mixer.init()

        self.volume = 50
        pygame.mixer.music.set_volume(self.volume / 100)

        self.seek_offset_sec = 0
        self.is_paused = False

        # repeat mode
        self.repeat_mode = 0
        self.was_playing = False

        # --- UI ---

        self.song_listbox = tk.Listbox(root)
        self.song_listbox.pack(pady=5)
        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

        tk.Button(root, text="Play", command=self.play_music).pack()

        self.pause_button = tk.Button(
            root, text="Pause", command=self.toggle_pause
        )
        self.pause_button.pack()

        tk.Button(root, text="Stop", command=self.stop_music).pack()
        tk.Button(root, text="Previous", command=self.prev_song).pack(pady=2)
        tk.Button(root, text="Next", command=self.next_song).pack(pady=2)

        self.repeat_button = tk.Button(
            root, text="Repeat: Off", command=self.toggle_repeat_mode
        )
        self.repeat_button.pack(pady=5)

        tk.Button(root, text="Add Song", command=self.add_song).pack(pady=5)

        # 音量
        self.volume_scale = tk.Scale(
            root, from_=0, to=100,
            orient=tk.HORIZONTAL,
            label="Volume",
            command=self.change_volume
        )
        self.volume_scale.set(self.volume)
        self.volume_scale.pack()

        # 播放時間顯示
        self.current_time_label = tk.Label(root, text="00:00 / 00:00")
        self.current_time_label.pack(pady=5)

        # 進度條（動態長度）
        self.progress_var = tk.IntVar(value=0)
        self.progress_scale = tk.Scale(
            root,
            from_=0,
            to=0,
            orient=tk.HORIZONTAL,
            label="Progress",
            variable=self.progress_var
        )
        self.progress_scale.pack(fill="x", padx=10)

        self.is_dragging_progress = False
        self.progress_scale.bind("<ButtonPress-1>", self.on_progress_press)
        self.progress_scale.bind("<ButtonRelease-1>", self.on_progress_release)

        self.song_length_sec = 0

        self.update_progress()

    # ---------------- 播放核心 ----------------

    def play_music(self):
        if not self.playlist:
            return

        path = self.playlist[self.current_song_idx]
        self.load_song(path)

    def load_song(self, path):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        # 取得歌曲長度
        sound = pygame.mixer.Sound(path)
        self.song_length_sec = int(sound.get_length())

        self.progress_scale.config(to=self.song_length_sec)
        self.progress_var.set(0)

        self.seek_offset_sec = 0
        self.is_paused = False
        self.pause_button.config(text="Pause")

        self.update_time_label(0)

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

    # ---------------- 清單 ----------------

    def add_song(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MP3 files", "*.mp3")]
        )
        if file_path:
            self.playlist.append(file_path)
            self.song_listbox.insert(tk.END, os.path.basename(file_path))

    def on_song_select(self, event):
        if not self.song_listbox.curselection():
            return
        self.current_song_idx = self.song_listbox.curselection()[0]
        self.load_song(self.playlist[self.current_song_idx])

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

    # ---------------- 重複 ----------------

    def toggle_repeat_mode(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        text = ["Repeat: Off", "Repeat: One", "Repeat: All"]
        self.repeat_button.config(text=text[self.repeat_mode])

    def handle_music_end(self):
        if self.repeat_mode == 0:
            self.stop_music()
        elif self.repeat_mode == 1:
            self.load_song(self.playlist[self.current_song_idx])
        elif self.repeat_mode == 2:
            self.next_song()

    # ---------------- 進度與時間 ----------------

    def update_time_label(self, current_sec):
        m, s = divmod(current_sec, 60)
        tm, ts = divmod(self.song_length_sec, 60)
        self.current_time_label.config(
            text=f"{m:02d}:{s:02d} / {tm:02d}:{ts:02d}"
        )

    def change_volume(self, value):
        pygame.mixer.music.set_volume(int(value) / 100)

    def on_progress_press(self, event):
        self.is_dragging_progress = True

    def on_progress_release(self, event):
        if pygame.mixer.music.get_busy():
            sec = self.progress_var.get()
            self.seek_offset_sec = sec
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=sec)
            self.update_time_label(sec)

        self.is_dragging_progress = False

    def update_progress(self):
        is_playing = pygame.mixer.music.get_busy()

        if self.was_playing and not is_playing and not self.is_paused:
            self.handle_music_end()

        self.was_playing = is_playing

        if is_playing and not self.is_dragging_progress and not self.is_paused:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                sec = self.seek_offset_sec + pos_ms // 1000
                self.progress_var.set(sec)
                self.update_time_label(sec)

        self.root.after(500, self.update_progress)


root = tk.Tk()
MusicPlayer(root)
root.mainloop()
