import tkinter as tk
from tkinter import filedialog
import pygame
import os

BG_MAIN = "#121212"
BG_SECTION = "#181818"
TEXT_MAIN = "#FFFFFF"
TEXT_SUB = "#B3B3B3"
ACCENT = "#1DB954"
FONT = ("Segoe UI", 10)
FONT_LG = ("Segoe UI", 14)


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("800x500")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.playlist = []
        self.current_song_idx = 0
        self.seek_offset_sec = 0
        self.is_paused = False
        self.repeat_mode = 0
        self.was_playing = False
        self.song_length_sec = 0

        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)

        main_frame = tk.Frame(root, bg=BG_MAIN)
        main_frame.pack(fill="both", expand=True)

        top_frame = tk.Frame(main_frame, bg=BG_MAIN)
        top_frame.pack(fill="both", expand=True)

        sidebar_frame = tk.Frame(top_frame, width=200, bg=BG_SECTION)
        sidebar_frame.pack(side="left", fill="y")

        self.song_listbox = tk.Listbox(
            sidebar_frame,
            bg=BG_SECTION,
            fg=TEXT_MAIN,
            selectbackground=ACCENT,
            selectforeground="#000000",
            highlightthickness=0,
            borderwidth=0,
            font=FONT
        )
        self.song_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

        content_frame = tk.Frame(top_frame, bg=BG_MAIN)
        content_frame.pack(side="left", fill="both", expand=True)

        self.current_time_label = tk.Label(
            content_frame,
            text="00:00 / 00:00",
            fg=TEXT_MAIN,
            bg=BG_MAIN,
            font=FONT_LG
        )
        self.current_time_label.pack(pady=40)

        player_frame = tk.Frame(main_frame, bg=BG_SECTION)
        player_frame.pack(fill="x")

        control_frame = tk.Frame(player_frame, bg=BG_SECTION)
        control_frame.pack(pady=5)

        def btn(txt, cmd, accent=False):
            return tk.Button(
                control_frame,
                text=txt,
                command=cmd,
                bg=ACCENT if accent else BG_SECTION,
                fg="#000000" if accent else TEXT_MAIN,
                activebackground=ACCENT,
                activeforeground="#000000",
                relief="flat",
                font=FONT,
                width=4
            )

        btn("⏮", self.prev_song).pack(side="left", padx=4)
        btn("▶", self.play_music, accent=True).pack(side="left", padx=4)
        btn("⏭", self.next_song).pack(side="left", padx=4)

        self.pause_button = btn("Pause", self.toggle_pause)
        self.pause_button.pack(side="left", padx=6)

        btn("Stop", self.stop_music).pack(side="left", padx=6)

        self.repeat_button = btn("Repeat", self.toggle_repeat_mode)
        self.repeat_button.pack(side="left", padx=6)

        self.progress_var = tk.IntVar(value=0)
        self.progress_scale = tk.Scale(
            player_frame,
            from_=0,
            to=0,
            orient="horizontal",
            variable=self.progress_var,
            bg=BG_SECTION,
            fg=TEXT_MAIN,
            troughcolor="#333333",
            highlightthickness=0,
            font=FONT
        )
        self.progress_scale.pack(fill="x", padx=10)

        self.progress_scale.bind("<ButtonPress-1>", self.on_progress_press)
        self.progress_scale.bind("<ButtonRelease-1>", self.on_progress_release)
        self.is_dragging_progress = False

        self.volume_scale = tk.Scale(
            player_frame,
            from_=0,
            to=100,
            orient="horizontal",
            label="Volume",
            bg=BG_SECTION,
            fg=TEXT_SUB,
            troughcolor="#333333",
            highlightthickness=0,
            font=FONT,
            command=self.change_volume
        )
        self.volume_scale.set(50)
        self.volume_scale.pack(fill="x", padx=10)

        tk.Button(
            player_frame,
            text="Add Song",
            command=self.add_song,
            bg=BG_SECTION,
            fg=TEXT_SUB,
            activebackground=BG_SECTION,
            relief="flat",
            font=FONT
        ).pack(pady=5)

        self.update_progress()

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
        if self.playlist:
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
        if self.playlist:
            self.current_song_idx = (self.current_song_idx - 1) % len(self.playlist)
            self.load_song(self.playlist[self.current_song_idx])

    def next_song(self):
        if self.playlist:
            self.current_song_idx = (self.current_song_idx + 1) % len(self.playlist)
            self.load_song(self.playlist[self.current_song_idx])

    def toggle_repeat_mode(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        self.repeat_button.config(
            text=["Repeat", "Repeat One", "Repeat All"][self.repeat_mode]
        )

    def add_song(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if path:
            self.playlist.append(path)
            self.song_listbox.insert(tk.END, os.path.basename(path))

    def on_song_select(self, event):
        if self.song_listbox.curselection():
            self.current_song_idx = self.song_listbox.curselection()[0]
            self.load_song(self.playlist[self.current_song_idx])

    def update_time_label(self, sec):
        m, s = divmod(sec, 60)
        tm, ts = divmod(self.song_length_sec, 60)
        self.current_time_label.config(text=f"{m:02d}:{s:02d} / {tm:02d}:{ts:02d}")

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
