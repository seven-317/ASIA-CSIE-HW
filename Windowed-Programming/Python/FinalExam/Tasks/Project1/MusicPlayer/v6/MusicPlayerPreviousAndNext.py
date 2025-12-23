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

        # ★ NEW：上一首 / 下一首
        tk.Button(root, text="Previous", command=self.prev_song).pack(pady=2)
        tk.Button(root, text="Next", command=self.next_song).pack(pady=2)

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

        index = self.song_listbox.curselection()[0]
        self.current_song_idx = index

        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playlist[index])
        pygame.mixer.music.play()

        self.seek_offset_sec = 0
        self.progress_var.set(0)
        self.is_paused = False
        self.pause_button.config(text="Pause")

    # ★ NEW：上一首
    def prev_song(self):
        if not self.playlist:
            return

        if self.current_song_idx > 0:
            self.current_song_idx -= 1
        else:
            self.current_song_idx = len(self.playlist) - 1

        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playlist[self.current_song_idx])
        pygame.mixer.music.play()

        self.song_listbox.selection_clear(0, tk.END)
        self.song_listbox.selection_set(self.current_song_idx)

        self.seek_offset_sec = 0
        self.progress_var.set(0)
        self.is_paused = False
        self.pause_button.config(text="Pause")

    # ★ NEW：下一首
    def next_song(self):
        if not self.playlist:
            return

        if self.current_song_idx < len(self.playlist) - 1:
            self.current_song_idx += 1
        else:
            self.current_song_idx = 0

        pygame.mixer.music.stop()
        pygame.mixer.music.load(self.playlist[self.current_song_idx])
        pygame.mixer.music.play()

        self.song_listbox.selection_clear(0, tk.END)
        self.song_listbox.selection_set(self.current_song_idx)

        self.seek_offset_sec = 0
        self.progress_var.set(0)
        self.is_paused = False
        self.pause_button.config(text="Pause")

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
        if pygame.mixer.music.get_busy() and not self.is_dragging_progress and not self.is_paused:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                self.progress_var.set(
                    self.seek_offset_sec + pos_ms // 1000
                )

        self.root.after(500, self.update_progress)


root = tk.Tk()
music_player = MusicPlayer(root)
root.mainloop()
