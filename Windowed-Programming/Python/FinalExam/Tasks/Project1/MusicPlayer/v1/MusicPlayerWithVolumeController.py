import tkinter as tk
from tkinter import filedialog
import pygame
import os


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")

        # 初始化歌曲清單與目前播放索引
        self.playlist = []
        self.current_song_idx = 0

        # 初始化 Pygame mixer
        pygame.mixer.init()

        # 預設音量（50%）
        self.volume = 50  # NEW
        pygame.mixer.music.set_volume(self.volume / 100)  # NEW

        # 歌曲清單顯示區
        self.song_listbox = tk.Listbox(root)
        self.song_listbox.pack()

        # 播放按鈕
        self.play_button = tk.Button(
            root, text="Play", command=self.play_music
        )
        self.play_button.pack()

        # 暫停按鈕
        self.pause_button = tk.Button(
            root, text="Pause", command=self.pause_music
        )
        self.pause_button.pack()

        # 停止按鈕
        self.stop_button = tk.Button(
            root, text="Stop", command=self.stop_music
        )
        self.stop_button.pack()

        # 新增歌曲按鈕
        self.add_song_button = tk.Button(
            root, text="Add Song", command=self.add_song
        )
        self.add_song_button.pack()

        # 音量控制滑桿（0 ~ 100）  # NEW
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
        """播放目前選取的歌曲"""
        if self.playlist:
            pygame.mixer.music.load(
                self.playlist[self.current_song_idx]
            )
            pygame.mixer.music.play()

    def pause_music(self):
        """暫停播放"""
        pygame.mixer.music.pause()

    def stop_music(self):
        """停止播放"""
        pygame.mixer.music.stop()

    def add_song(self):
        """加入 MP3 歌曲到播放清單"""
        file_path = filedialog.askopenfilename(
            filetypes=[("MP3 files", "*.mp3")]
        )

        if file_path:
            self.playlist.append(file_path)
            self.song_listbox.insert(
                tk.END, os.path.basename(file_path)
            )

    def change_volume(self, value):
        """調整音量（0~100 -> 0.0~1.0）"""  # NEW
        volume = int(value) / 100
        pygame.mixer.music.set_volume(volume)


# 建立 Tkinter 視窗
root = tk.Tk()

# 建立音樂播放器物件
music_player = MusicPlayer(root)

# 啟動主事件迴圈
root.mainloop()
