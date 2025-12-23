import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")

        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.playlist = []
        self.current_song_idx = 0

        pygame.mixer.init()

        self.volume = 50
        pygame.mixer.music.set_volume(self.volume / 100)

        self.seek_offset_sec = 0
        self.is_paused = False

        # ★ 重複播放模式
        # 0: 不重複, 1: 單曲重複, 2: 清單重複
        self.repeat_mode = 0

        # ★ 用來判斷「是否剛剛在播放」
        self.was_playing = False

        # 歌曲清單
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

        # 重複播放模式切換
        self.repeat_button = tk.Button(
            root, text="Repeat: Off", command=self.toggle_repeat_mode
        )
        self.repeat_button.pack(pady=5)

        tk.Button(root, text="Add Song", command=self.add_song).pack(pady=5)

        self.volume_scale = tk.Scale(
            root, from_=0, to=100,
            orient=tk.HORIZONTAL,
            label="Volume",
            command=self.change_volume
        )
        self.volume_scale.set(self.volume)
        self.volume_scale.pack()

        self.progress_var = tk.IntVar(value=0)
        self.progress_scale = tk.Scale(
            root,
            from_=0,
            to=300,
            orient=tk.HORIZONTAL,
            label="Progress (seconds)",
            variable=self.progress_var
        )
        self.progress_scale.pack(fill="x", padx=10)

        self.is_dragging_progress = False
        self.progress_scale.bind("<ButtonPress-1>", self.on_progress_press)
        self.progress_scale.bind("<ButtonRelease-1>", self.on_progress_release)

        self.update_progress()

    # ---------------- 播放控制 ----------------

    def play_music(self):
        if self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_song_idx])
            pygame.mixer.music.play()

            self.seek_offset_sec = 0
            self.is_paused = False
            self.pause_button.config(text="Pause")

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
        self.seek_offset_sec = 0
        self.is_paused = False
        self.pause_button.config(text="Pause")

    # ---------------- 播放清單 ----------------

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
        self._play_current_song()

    def prev_song(self):
        if not self.playlist:
            return

        if self.current_song_idx > 0:
            self.current_song_idx -= 1
        else:
            self.current_song_idx = len(self.playlist) - 1

        self._play_current_song()

    def next_song(self):
        if not self.playlist:
            return

        if self.current_song_idx < len(self.playlist) - 1:
            self.current_song_idx += 1
        else:
            self.current_song_idx = 0

        self._play_current_song()

    def _play_current_song(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playlist[self.current_song_idx])
        pygame.mixer.music.play()

        self.song_listbox.selection_clear(0, tk.END)
        self.song_listbox.selection_set(self.current_song_idx)

        self.seek_offset_sec = 0
        self.progress_var.set(0)
        self.is_paused = False
        self.pause_button.config(text="Pause")

    # ---------------- 重複播放 ----------------

    def toggle_repeat_mode(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3

        if self.repeat_mode == 0:
            self.repeat_button.config(text="Repeat: Off")
        elif self.repeat_mode == 1:
            self.repeat_button.config(text="Repeat: One")
        elif self.repeat_mode == 2:
            self.repeat_button.config(text="Repeat: All")

    def handle_music_end(self):
        if self.repeat_mode == 0:
            self.stop_music()
        elif self.repeat_mode == 1:
            self._play_current_song()
        elif self.repeat_mode == 2:
            self.next_song()

    # ---------------- 進度與音量 ----------------

    def change_volume(self, value):
        pygame.mixer.music.set_volume(int(value) / 100)

    def on_progress_press(self, event):
        self.is_dragging_progress = True

    def on_progress_release(self, event):
        if pygame.mixer.music.get_busy():
            target_sec = self.progress_var.get()
            self.seek_offset_sec = target_sec
            pygame.mixer.music.stop()
            pygame.mixer.music.play(start=target_sec)

        self.is_dragging_progress = False

    def update_progress(self):
        is_playing = pygame.mixer.music.get_busy()

        # ★ 偵測「播放結束」
        if self.was_playing and not is_playing and not self.is_paused:
            self.handle_music_end()

        self.was_playing = is_playing

        if is_playing and not self.is_dragging_progress and not self.is_paused:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                self.progress_var.set(
                    self.seek_offset_sec + pos_ms // 1000
                )

        self.root.after(500, self.update_progress)


root = tk.Tk()
music_player = MusicPlayer(root)
root.mainloop()
