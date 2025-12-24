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
FONT_TITLE = ("Segoe UI", 16, "bold")


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Music Player")
        self.root.geometry("800x520")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_MAIN)

        self.playlist = []
        self.current_song_idx = 0
        self.seek_offset_sec = 0
        self.is_paused = False
        self.repeat_mode = 0
        self.was_playing = False
        self.song_length_sec = 0

        self.full_song_title = ""
        self.marquee_index = 0
        self.marquee_job = None
        self.marquee_active = False
        self.marquee_display_len = 28

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
            selectbackground=BG_SECTION,
            selectforeground=TEXT_MAIN,
            highlightthickness=0,
            borderwidth=0,
            font=FONT
        )
        self.song_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

        content_frame = tk.Frame(top_frame, bg=BG_MAIN)
        content_frame.pack(side="left", fill="both", expand=True)

        self.song_title_var = tk.StringVar(value="")
        self.song_title_label = tk.Label(
            content_frame,
            textvariable=self.song_title_var,
            fg=ACCENT,
            bg=BG_MAIN,
            font=FONT_TITLE,
            anchor="w"
        )
        self.song_title_label.pack(pady=(25, 5), padx=20, anchor="w")

        self.current_time_label = tk.Label(
            content_frame,
            text="00:00 / 00:00",
            fg=TEXT_MAIN,
            bg=BG_MAIN,
            font=FONT_LG
        )
        self.current_time_label.pack(pady=(5, 5))

        self.play_state_label = tk.Label(
            content_frame,
            text="Stopped",
            fg=TEXT_SUB,
            bg=BG_MAIN,
            font=FONT
        )
        self.play_state_label.pack()

        player_frame = tk.Frame(main_frame, bg=BG_SECTION)
        player_frame.pack(fill="x")

        control_frame = tk.Frame(player_frame, bg=BG_SECTION)
        control_frame.pack(pady=5)

        def btn(txt, cmd, accent=False, wide=False):
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
                width=7 if wide else 4,
                padx=8 if wide else 0
            )

        btn("⏮", self.prev_song).pack(side="left", padx=4)
        btn("▶", self.play_music, accent=True).pack(side="left", padx=4)
        btn("⏭", self.next_song).pack(side="left", padx=4)

        self.pause_button = btn("Pause", self.toggle_pause, wide=True)
        self.pause_button.pack(side="left", padx=6)

        btn("Stop", self.stop_music, wide=True).pack(side="left", padx=6)

        self.repeat_button = btn("Repeat", self.toggle_repeat_mode, wide=True)
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
        self.set_play_state("Playing")
        self.highlight_current_song()

        self.set_song_title(os.path.basename(path))
        self.start_marquee_if_needed()

    def play_music(self):
        if self.playlist:
            self.load_song(self.playlist[self.current_song_idx])

    def toggle_pause(self):
        if not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_button.config(text="Resume")
            self.set_play_state("Paused")
            self.stop_marquee()
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.set_play_state("Playing")
            self.start_marquee_if_needed()

    def stop_music(self):
        pygame.mixer.music.stop()
        self.progress_var.set(0)
        self.update_time_label(0)
        self.seek_offset_sec = 0
        self.is_paused = False
        self.pause_button.config(text="Pause")
        self.set_play_state("Stopped")
        self.stop_marquee()

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

    def set_song_title(self, title):
        self.full_song_title = title
        self.song_title_var.set(title)
        self.marquee_index = 0

    def start_marquee_if_needed(self):
        if len(self.full_song_title) > self.marquee_display_len:
            self.marquee_active = True
            self.update_marquee()

    def update_marquee(self):
        if not self.marquee_active or self.is_paused:
            return

        text = self.full_song_title + "   "
        length = len(text)
        start = self.marquee_index
        end = start + self.marquee_display_len

        self.song_title_var.set((text * 2)[start:end])
        self.marquee_index = (self.marquee_index + 1) % length
        self.marquee_job = self.root.after(200, self.update_marquee)

    def stop_marquee(self):
        if self.marquee_job:
            self.root.after_cancel(self.marquee_job)
            self.marquee_job = None
        self.marquee_active = False

    def add_song(self):
        path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if path:
            self.playlist.append(path)
            self.song_listbox.insert(tk.END, os.path.basename(path))

    def on_song_select(self, event):
        if self.song_listbox.curselection():
            self.current_song_idx = self.song_listbox.curselection()[0]
            self.load_song(self.playlist[self.current_song_idx])

    def highlight_current_song(self):
        for i in range(self.song_listbox.size()):
            self.song_listbox.itemconfig(i, fg=TEXT_MAIN)
        self.song_listbox.itemconfig(self.current_song_idx, fg=ACCENT)

    def set_play_state(self, state):
        self.play_state_label.config(text=state)

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
