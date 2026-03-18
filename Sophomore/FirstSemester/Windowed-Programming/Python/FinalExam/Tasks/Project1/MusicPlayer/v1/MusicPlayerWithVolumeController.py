import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")

        self.playlist = []
        self.current_song_idx = 0

        pygame.mixer.init()

        self.volume = 50  # NEW
        pygame.mixer.music.set_volume(self.volume / 100)

        self.song_listbox = tk.Listbox(root)
        self.song_listbox.pack()

        self.play_button = tk.Button(
            root, text="Play", command=self.play_music
        )
        self.play_button.pack()

        self.pause_button = tk.Button(
            root, text="Pause", command=self.pause_music
        )
        self.pause_button.pack()

        self.stop_button = tk.Button(
            root, text="Stop", command=self.stop_music
        )
        self.stop_button.pack()

        self.add_song_button = tk.Button(
            root, text="Add Song", command=self.add_song
        )
        self.add_song_button.pack()

        self.volume_scale = tk.Scale(
            root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            label="Volume",
            command=self.change_volume
        )
        self.volume_scale.set(self.volume)
        self.volume_scale.pack()

    def play_music(self):
        if self.playlist:
            pygame.mixer.music.load(
                self.playlist[self.current_song_idx]
            )
            pygame.mixer.music.play()

    def pause_music(self):
        pygame.mixer.music.pause()

    def stop_music(self):
        pygame.mixer.music.stop()

    def add_song(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MP3 files", "*.mp3")]
        )

        if file_path:
            self.playlist.append(file_path)
            self.song_listbox.insert(
                tk.END, os.path.basename(file_path)
            )

    def change_volume(self, value):
        volume = int(value) / 100
        pygame.mixer.music.set_volume(volume)


root = tk.Tk()
music_player = MusicPlayer(root)
root.mainloop()
