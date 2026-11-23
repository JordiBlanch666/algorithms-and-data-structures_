"""Sonora's graphical interface (Tkinter) and playback logic."""
from __future__ import annotations

import io
import random
import threading
import time
import tkinter as tk
import wave
from bisect import bisect_right
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import av
import pygame
from mutagen import MutagenError
from PIL import Image, ImageOps, ImageTk

from sonora.audio import decode_to_wav
from sonora.lyrics import fetch_lrclib, parse_lrc_entries
from sonora.metadata import Track, format_time, read_track
from sonora.theme import (
    AAC_TYPES, ACCENT, AUDIO_TYPES, BG, DRM_TYPES, MINT, MUTED, NEON_BLUE, NEON_PINK,
    PANEL, PANEL_LIGHT, TEXT,
)


class SonoraPlayer:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sonora — Music Player")
        self.root.geometry("1220x790")
        self.root.minsize(940, 650)
        self.root.configure(bg=BG)
        self.tracks: list[Track] = []
        self.current_index = -1
        self.position = 0.0
        self.started_at = 0.0
        self.is_playing = False
        self.is_paused = False
        self.shuffle = False
        self.shuffle_queue: list[int] = []
        self.repeat = "off"
        self.is_muted = False
        self._seeking = False
        self._visual_phase = 0
        self._cover_image = None
        self._decoded_audio_path: Path | None = None
        self._tick_after = None
        self._lyrics_entries: list[tuple[float | None, str]] = []
        self._lyric_timestamps: list[float] = []
        self._active_lyric_index = -1
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_playlist())

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._tick()

    def _build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Sonora.Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Sonora.Treeview.Heading",
            background=PANEL,
            foreground=MUTED,
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Sonora.Treeview",
            background=[("selected", "#332044")],
            foreground=[("selected", MINT)],
        )
        style.configure(
            "Sonora.Vertical.TScrollbar",
            background=PANEL_LIGHT,
            troughcolor=PANEL,
            bordercolor=PANEL,
            arrowcolor=NEON_BLUE,
        )

        header = tk.Frame(self.root, bg=BG, padx=28, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="♫", bg=BG, fg=ACCENT, font=("Segoe UI", 25, "bold")).pack(
            side="left"
        )
        tk.Label(
            header, text="SONORA", bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")
        ).pack(side="left", padx=(8, 24))
        tk.Label(
            header,
            text="YOUR MUSIC, YOUR WAY",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")
        search_frame = tk.Frame(header, bg=NEON_BLUE, padx=1, pady=1)
        search_frame.place(relx=0.54, rely=0.5, anchor="center", width=320, height=42)
        search_inner = tk.Frame(search_frame, bg=PANEL)
        search_inner.pack(fill="both", expand=True)
        tk.Label(
            search_inner, text="⌕", bg=PANEL, fg=NEON_BLUE,
            font=("Segoe UI", 19, "bold")
        ).pack(side="left", padx=(10, 4))
        self.search_entry = tk.Entry(
            search_inner,
            textvariable=self.search_var,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 10),
            bd=0,
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self._build_sidebar(body)
        self._build_center(body)
        self._build_lyrics(body)
        self._build_player()

    def _build_sidebar(self, parent: tk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=BG, width=190)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
        sidebar.grid_propagate(False)
        tk.Label(
            sidebar, text="YOUR LIBRARY", bg=BG, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(12, 14))
        self._button(sidebar, "♫   All songs", self.show_library, ACCENT).pack(
            fill="x", pady=3
        )
        tk.Label(
            sidebar, text="MANAGE", bg=BG, fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(30, 12))
        self._button(sidebar, "+   Add songs", self.add_files).pack(fill="x", pady=3)
        self._button(sidebar, "▧   Add folder", self.add_folder).pack(fill="x", pady=3)
        self._button(sidebar, "↥   Open M3U playlist", self.open_m3u).pack(fill="x", pady=3)
        self._button(sidebar, "↧   Save playlist", self.save_m3u).pack(fill="x", pady=3)
        tk.Frame(sidebar, bg=PANEL_LIGHT, height=1).pack(fill="x", pady=22)
        tk.Label(
            sidebar,
            text="MP3 · WAV · OGG · FLAC\nAIFF · M4A · AAC\n\nLyrics are fetched\nfrom LRCLIB.",
            bg=BG,
            fg=MUTED,
            justify="left",
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        self.library_count = tk.Label(
            sidebar, text="0 songs", bg=BG, fg=MINT, font=("Segoe UI", 9, "bold")
        )
        self.library_count.pack(side="bottom", anchor="w", pady=14)

    def _build_center(self, parent: tk.Frame) -> None:
        center = tk.Frame(parent, bg=BG)
        center.grid(row=0, column=1, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)

        hero = tk.Frame(center, bg=PANEL, padx=22, pady=20)
        hero.configure(highlightthickness=1, highlightbackground="#43265e")
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        hero.grid_columnconfigure(1, weight=1)
        self.cover = tk.Canvas(
            hero, width=142, height=142, bg="#322a50", highlightthickness=0
        )
        self.cover.grid(row=0, column=0, rowspan=2, padx=(0, 22))
        self._draw_cover("SONORA")
        tk.Label(
            hero, text="NOW PLAYING", bg=PANEL, fg=MINT,
            font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=1, sticky="sw")
        self.track_title = tk.Label(
            hero, text="Pick a song", bg=PANEL, fg=TEXT,
            font=("Segoe UI", 19, "bold"), anchor="w"
        )
        self.track_title.grid(row=1, column=1, sticky="nw", pady=(6, 2))
        self.track_artist = tk.Label(
            hero, text="Your library is waiting", bg=PANEL, fg=MUTED,
            font=("Segoe UI", 10), anchor="w"
        )
        self.track_artist.grid(row=2, column=1, sticky="nw")
        self.visualizer = tk.Canvas(
            hero, height=42, bg=PANEL, highlightthickness=0
        )
        self.visualizer.grid(row=3, column=1, sticky="ew", pady=(12, 0))
        self._draw_visualizer()

        heading = tk.Frame(center, bg=BG)
        heading.grid(row=1, column=0, sticky="new", pady=(0, 8))
        tk.Label(
            heading, text="Your playlist", bg=BG, fg=TEXT, font=("Segoe UI", 15, "bold")
        ).pack(side="left")
        self.playlist_count = tk.Label(
            heading, text="0 tracks", bg=BG, fg=MUTED, font=("Segoe UI", 9)
        )
        self.playlist_count.pack(side="left", padx=12, pady=(4, 0))

        playlist_actions = tk.Frame(center, bg=BG)
        playlist_actions.grid(row=2, column=0, sticky="ew", pady=(0, 7))
        self._button(
            playlist_actions, "Remove track", self.remove_selected
        ).pack(side="right")
        self._button(
            playlist_actions, "Clear", self.clear_playlist
        ).pack(side="right", padx=6)

        table_frame = tk.Frame(
            center, bg=PANEL, highlightthickness=1, highlightbackground="#282341"
        )
        table_frame.grid(row=3, column=0, sticky="nsew")
        center.grid_rowconfigure(3, weight=1)
        self.playlist = ttk.Treeview(
            table_frame,
            columns=("title", "artist", "duration"),
            show="headings",
            style="Sonora.Treeview",
            selectmode="browse",
        )
        self.playlist.heading("title", text="TITLE")
        self.playlist.heading("artist", text="ARTIST")
        self.playlist.heading("duration", text="DURATION", anchor="e")
        self.playlist.column("title", minwidth=120, width=230, anchor="w")
        self.playlist.column("artist", minwidth=90, width=145, anchor="w")
        self.playlist.column("duration", width=70, anchor="e")
        scroll = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.playlist.yview,
            style="Sonora.Vertical.TScrollbar"
        )
        self.playlist.configure(yscrollcommand=scroll.set)
        self.playlist.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)
        scroll.pack(side="right", fill="y", padx=5, pady=8)
        self.playlist.bind("<Double-1>", self.play_selected)
        self.playlist.bind("<Return>", self.play_selected)

    def _build_lyrics(self, parent: tk.Frame) -> None:
        panel = tk.Frame(
            parent, bg=PANEL, width=280, padx=16, pady=18,
            highlightthickness=1, highlightbackground="#53316d",
        )
        panel.grid(row=0, column=2, sticky="nse", padx=(18, 0))
        panel.grid_propagate(False)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        tk.Label(
            panel, text="Lyrics", bg=PANEL, fg=TEXT, font=("Segoe UI", 14, "bold")
        ).grid(row=0, column=0, sticky="w")
        self.lyrics_text = tk.Text(
            panel,
            bg=PANEL,
            fg="#d2d3e0",
            insertbackground=TEXT,
            relief="flat",
            wrap="word",
            width=28,
            font=("Segoe UI", 13),
            padx=8,
            pady=16,
            state="disabled",
        )
        self.lyrics_text.grid(row=1, column=0, sticky="nsew")
        self.lyrics_text.tag_configure(
            "center", justify="center", spacing1=5, spacing3=9
        )
        self.lyrics_text.tag_configure(
            "active_lyric",
            foreground=MINT,
            font=("Segoe UI", 15, "bold"),
            spacing1=10,
            spacing3=12,
        )
        self._set_lyrics("Select a song to look up its lyrics.")
        search_button_frame = tk.Frame(panel, bg=NEON_PINK, padx=1, pady=1)
        search_button_frame.grid(row=2, column=0, pady=(12, 0))
        self.lyrics_search_button = self._button(
            search_button_frame, "↻   Find lyrics", self.fetch_lyrics, ACCENT
        )
        self.lyrics_search_button.pack(padx=1, pady=1)

    def _build_player(self) -> None:
        dock = tk.Frame(
            self.root, bg=PANEL, padx=25, pady=12,
            highlightthickness=1, highlightbackground="#45305c",
        )
        dock.pack(fill="x", side="bottom")
        upper = tk.Frame(dock, bg=PANEL)
        upper.pack(fill="x")
        self.time_label = tk.Label(
            upper, text="0:00", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)
        )
        self.time_label.pack(side="left", padx=(0, 12))
        self.seek_scale = tk.Scale(
            upper, from_=0, to=100, orient="horizontal", showvalue=False,
            bg=PANEL, fg=ACCENT, troughcolor=PANEL_LIGHT, activebackground=ACCENT,
            highlightthickness=0, sliderlength=15, command=self._preview_seek,
        )
        self.seek_scale.pack(side="left", fill="x", expand=True)
        self.seek_scale.bind("<ButtonPress-1>", self._start_seek)
        self.seek_scale.bind("<ButtonRelease-1>", self._finish_seek)
        self.duration_label = tk.Label(
            upper, text="0:00", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)
        )
        self.duration_label.pack(side="left", padx=(12, 22))

        controls = tk.Frame(dock, bg=PANEL)
        controls.pack(pady=(7, 0))
        self.shuffle_button = self._button(
            controls, "SHUFFLE", self.toggle_shuffle
        )
        self.shuffle_button.pack(side="left", padx=4)
        self._button(controls, "PREVIOUS", self.previous_track).pack(side="left", padx=4)
        self.play_button = self._button(
            controls, "PLAY", self.toggle_play, ACCENT
        )
        self.play_button.pack(side="left", padx=4)
        self._button(controls, "STOP", self.stop_playback).pack(side="left", padx=4)
        self._button(controls, "NEXT", self.next_track).pack(side="left", padx=4)
        self.repeat_button = self._button(
            controls, "REPEAT: OFF", self.toggle_repeat
        )
        self.repeat_button.pack(side="left", padx=4)
        self.mute_button = self._button(
            controls, "MUTE", self.toggle_mute
        )
        self.mute_button.pack(side="left", padx=(12, 4))
        tk.Label(
            controls, text="VOLUME", bg=PANEL, fg=MINT,
            font=("Segoe UI", 8, "bold")
        ).pack(side="left", padx=(8, 4))
        self.volume = tk.Scale(
            controls, from_=0, to=100, orient="horizontal", showvalue=False,
            bg=PANEL, fg=MINT, troughcolor=PANEL_LIGHT, activebackground=MINT,
            highlightthickness=0, sliderlength=13, length=90,
            command=self._set_volume,
        )
        self.volume.set(75)
        self.volume.pack(side="left")

    def _button(
        self, parent: tk.Widget, text: str, command, color: str = PANEL_LIGHT
    ) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=TEXT,
            activebackground=MINT,
            activeforeground=BG,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#47335d" if color == PANEL_LIGHT else color,
            padx=12,
            pady=8,
            cursor="hand2",
            font=("Segoe UI", 8, "bold"),
        )
        button.configure(width=max(8, len(text)))  # fits longer labels like "REPEAT: OFF"
        button.bind(
            "<Enter>",
            lambda _event: button.configure(bg=MINT, fg=BG),
        )
        button.bind(
            "<Leave>",
            lambda _event: button.configure(bg=color, fg=TEXT),
        )
        return button

    def _draw_cover(self, seed: str, image_data: bytes | None = None) -> None:
        self.cover.delete("all")
        self._cover_image = None
        if image_data:
            try:
                image = Image.open(io.BytesIO(image_data))
                image = ImageOps.fit(image.convert("RGB"), (142, 142))
                self._cover_image = ImageTk.PhotoImage(image)
                self.cover.create_image(71, 71, image=self._cover_image)
                return
            except (OSError, ValueError):
                pass
        rng = random.Random(seed)
        colors = [ACCENT, MINT, NEON_PINK, "#ffd166", NEON_BLUE]
        self.cover.create_rectangle(0, 0, 142, 142, fill="#27243c", outline="")
        for i in range(8):
            x = rng.randint(-15, 125)
            y = rng.randint(-15, 125)
            size = rng.randint(18, 55)
            self.cover.create_oval(
                x, y, x + size, y + size, fill=rng.choice(colors), outline=""
            )
        self.cover.create_rectangle(0, 0, 142, 142, fill="#11111b", stipple="gray50")
        self.cover.create_text(
            71, 71, text="♫", fill=TEXT, font=("Segoe UI", 38, "bold")
        )

    def _draw_visualizer(self) -> None:
        self.visualizer.delete("all")
        width = max(1, self.visualizer.winfo_width())
        bars = max(12, min(64, width // 8))
        active = self.is_playing and not self.is_paused
        for index in range(bars):
            if active:
                wave = abs(((index * 17 + self._visual_phase * 7) % 31) - 15) / 15
                height = 5 + wave * (8 + ((index + self._visual_phase) % 5) * 4)
            else:
                height = 4 + (index * 7 % 11)
            x = (index + 0.5) * width / bars
            color = (ACCENT, MINT, NEON_BLUE, NEON_PINK)[index % 4]
            self.visualizer.create_line(
                x, 21 - height / 2, x, 21 + height / 2, fill=color, width=3,
                capstyle=tk.ROUND,
            )
        self._visual_phase += 1

    def _set_lyrics(self, text: str) -> None:
        timed_entries = parse_lrc_entries(text)
        if timed_entries:
            entries: list[tuple[float | None, str]] = timed_entries
        else:
            entries = [
                (None, line.strip())
                for line in text.splitlines()
                if line.strip()
            ]
        self._lyrics_entries = entries
        self._lyric_timestamps = [
            timestamp for timestamp, _ in entries if timestamp is not None
        ]
        self._active_lyric_index = -1
        self.lyrics_text.configure(state="normal")
        self.lyrics_text.delete("1.0", "end")
        for _, line in entries:
            self.lyrics_text.insert("end", f"{line}\n\n", "center")
        if not entries:
            self.lyrics_text.insert("1.0", text, "center")
        self.lyrics_text.configure(state="disabled")

    def _sync_lyrics(self, position: float) -> None:
        if not self._lyric_timestamps:
            return
        active_index = bisect_right(self._lyric_timestamps, position) - 1
        if active_index == self._active_lyric_index:
            return

        self.lyrics_text.configure(state="normal")
        self.lyrics_text.tag_remove("active_lyric", "1.0", "end")
        self._active_lyric_index = active_index
        if active_index >= 0:
            line_number = active_index * 2 + 1
            start = f"{line_number}.0"
            end = f"{line_number}.end"
            self.lyrics_text.tag_add("active_lyric", start, end)
            self.lyrics_text.see(start)
        self.lyrics_text.configure(state="disabled")

    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Add songs",
            filetypes=[
                ("Audio files", " ".join(f"*{ext}" for ext in AUDIO_TYPES)),
                ("All files", "*.*"),
            ],
        )
        self.add_paths(Path(path) for path in paths)

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Add music folder")
        if folder:
            self.add_paths(
                path for path in Path(folder).rglob("*")
                if path.is_file() and path.suffix.lower() in AUDIO_TYPES
            )

    def add_paths(self, paths) -> None:
        known = {track.path.resolve() for track in self.tracks}
        added = 0
        for path in paths:
            if path.suffix.lower() in DRM_TYPES:
                messagebox.showwarning(
                    "DRM-protected file",
                    f"“{path.name}” is protected by Apple DRM and can't be played.",
                )
                continue
            if path.suffix.lower() not in AUDIO_TYPES:
                continue
            try:
                resolved = path.resolve()
                if resolved in known:
                    continue
                self.tracks.append(read_track(resolved))
                known.add(resolved)
                added += 1
            except (MutagenError, OSError, ValueError, TypeError, wave.Error) as error:
                messagebox.showwarning(
                    "Couldn't read the file", f"{path.name}\n\n{error}"
                )
        self.refresh_playlist()
        if added:
            self.library_count.configure(text=f"{len(self.tracks)} songs")
            if self.shuffle:
                self._refill_shuffle_queue()

    def refresh_playlist(self) -> None:
        self.playlist.delete(*self.playlist.get_children())
        query = self.search_var.get().strip().casefold()
        shown = 0
        for index, track in enumerate(self.tracks):
            if query and query not in f"{track.title} {track.artist}".casefold():
                continue
            self.playlist.insert(
                "", "end", iid=str(index),
                values=(track.title, track.artist, format_time(track.duration)),
            )
            shown += 1
        self.playlist_count.configure(text=f"{shown} tracks")
        self.library_count.configure(text=f"{len(self.tracks)} songs")

    def show_library(self) -> None:
        self.search_var.set("")
        self.refresh_playlist()

    def _selected_index(self) -> int | None:
        selection = self.playlist.selection()
        if not selection:
            return None
        return int(selection[0])

    def play_selected(self, _event=None) -> None:
        index = self._selected_index()
        if index is not None:
            self.play_track(index)

    def _remove_decoded_audio(self) -> None:
        if self._decoded_audio_path is None:
            return
        try:
            self._decoded_audio_path.unlink(missing_ok=True)
            self._decoded_audio_path = None
        except OSError as error:
            messagebox.showwarning(
                "Couldn't delete the temporary audio file", str(error)
            )

    def play_track(self, index: int, start: float = 0.0) -> None:
        if not self.tracks:
            return
        index %= len(self.tracks)
        track = self.tracks[index]
        if track.path.suffix.lower() in DRM_TYPES:
            messagebox.showwarning(
                "DRM-protected file",
                f"“{track.path.name}” is protected by Apple DRM and can't be played.",
            )
            return
        decoded_path = None
        try:
            if track.path.suffix.lower() in AAC_TYPES:
                decoded_path = decode_to_wav(track.path)
                playback_path = decoded_path
            else:
                playback_path = track.path
            pygame.mixer.music.load(str(playback_path))
            pygame.mixer.music.play(start=max(0.0, start))
            pygame.mixer.music.set_volume(self._output_volume())
        except (av.error.FFmpegError, OSError, ValueError, pygame.error) as error:
            if decoded_path:
                decoded_path.unlink(missing_ok=True)
            self.is_playing = False
            self.is_paused = False
            self._update_play_button()
            self.current_index = -1
            self.position = 0
            self.track_title.configure(text="Playback failed")
            self.track_artist.configure(text=track.title)
            messagebox.showerror(
                "Playback failed",
                f"Couldn't open “{track.path.name}”.\n"
                "Check that the format is supported.\n\n"
                f"{error}",
            )
            return

        self._remove_decoded_audio()
        self._decoded_audio_path = decoded_path
        self.current_index = index
        if self.shuffle and index in self.shuffle_queue:
            self.shuffle_queue.remove(index)
        self.position = max(0.0, start)
        self.started_at = time.monotonic()
        self.is_playing = True
        self.is_paused = False
        self._update_play_button()
        self.track_title.configure(text=track.title)
        self.track_artist.configure(text=track.artist)
        self._draw_cover(track.title + track.artist, track.cover)
        self._set_lyrics("Looking up lyrics…")
        self.seek_scale.configure(to=max(1, track.duration))
        self.duration_label.configure(text=format_time(track.duration))
        self._select_playlist_row(index)
        self.fetch_lyrics()

    def _select_playlist_row(self, index: int) -> None:
        if self.playlist.exists(str(index)):
            self.playlist.selection_set(str(index))
            self.playlist.focus(str(index))
            self.playlist.see(str(index))

    def toggle_play(self) -> None:
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.started_at = time.monotonic()
            self.is_paused = False
            self.is_playing = True
            self._update_play_button()
        elif self.is_playing:
            self.position += time.monotonic() - self.started_at
            pygame.mixer.music.pause()
            self.is_paused = True
            self._update_play_button()
        elif self.current_index >= 0:
            self.play_track(self.current_index, self.position)
        else:
            index = self._selected_index()
            self.play_track(index if index is not None else 0)

    def _current_position(self) -> float:
        if self.is_playing and not self.is_paused:
            return self.position + time.monotonic() - self.started_at
        return self.position

    def _start_seek(self, _event=None) -> None:
        self._seeking = True

    def _preview_seek(self, value: str) -> None:
        if self._seeking:
            self.time_label.configure(text=format_time(float(value)))

    def _finish_seek(self, _event=None) -> None:
        self._seeking = False
        if self.current_index < 0:
            return
        was_paused = self.is_paused
        position = float(self.seek_scale.get())
        try:
            pygame.mixer.music.play(start=position)
            pygame.mixer.music.set_volume(self._output_volume())
            if was_paused:
                pygame.mixer.music.pause()
        except pygame.error as error:
            messagebox.showerror("Couldn't seek to that position", str(error))
            return
        self.position = position
        self.started_at = time.monotonic()
        self.is_playing = True
        self.is_paused = was_paused
        self._update_play_button()

    def _update_play_button(self) -> None:
        if self.is_paused:
            label = "RESUME"
        elif self.is_playing:
            label = "PAUSE"
        else:
            label = "PLAY"
        self.play_button.configure(text=label)

    def stop_playback(self) -> None:
        pygame.mixer.music.stop()
        self.position = 0
        self.is_playing = False
        self.is_paused = False
        self._update_play_button()
        self.time_label.configure(text="0:00")
        self.seek_scale.set(0)

    def toggle_mute(self) -> None:
        self.is_muted = not self.is_muted
        pygame.mixer.music.set_volume(self._output_volume())
        self.mute_button.configure(
            text="UNMUTE" if self.is_muted else "MUTE",
            fg=MINT if self.is_muted else TEXT,
        )

    def _set_volume(self, value: str) -> None:
        pygame.mixer.music.set_volume(0 if self.is_muted else float(value) / 100)

    def _output_volume(self) -> float:
        return 0 if self.is_muted else self.volume.get() / 100

    def toggle_shuffle(self) -> None:
        self.shuffle = not self.shuffle
        self.shuffle_button.configure(fg=MINT if self.shuffle else TEXT)
        self.shuffle_queue.clear()
        if self.shuffle:
            self._refill_shuffle_queue()

    def toggle_repeat(self) -> None:
        self.repeat = {"off": "all", "all": "one", "one": "off"}[self.repeat]
        labels = {
            "off": "REPEAT: OFF",
            "all": "REPEAT: ALL",
            "one": "REPEAT: ONE",
        }
        self.repeat_button.configure(
            text=labels[self.repeat], fg=MINT if self.repeat != "off" else TEXT
        )

    def next_track(self) -> None:
        if not self.tracks:
            return
        if self.shuffle:
            if not self.shuffle_queue:
                self._refill_shuffle_queue()
            index = self.shuffle_queue.pop(0)
        else:
            index = (self.current_index + 1) % len(self.tracks)
        self.play_track(index)

    def _refill_shuffle_queue(self) -> None:
        self.shuffle_queue = [
            index for index in range(len(self.tracks))
            if index != self.current_index
        ]
        if not self.shuffle_queue and self.tracks:
            self.shuffle_queue = [self.current_index if self.current_index >= 0 else 0]
        random.shuffle(self.shuffle_queue)

    def previous_track(self) -> None:
        if not self.tracks:
            return
        if self._current_position() > 3:
            self.play_track(self.current_index, 0)
            return
        self.play_track((self.current_index - 1) % len(self.tracks))

    def remove_selected(self) -> None:
        index = self._selected_index()
        if index is None:
            return
        if index == self.current_index:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            self._remove_decoded_audio()
            self.is_playing = False
            self.is_paused = False
            self.current_index = -1
            self.position = 0
            self._update_play_button()
            self.time_label.configure(text="0:00")
            self.seek_scale.set(0)
            self.track_title.configure(text="Pick a song")
            self.track_artist.configure(text="Your library is waiting")
            self._set_lyrics("Select a song to look up its lyrics.")
        self.tracks.pop(index)
        self.shuffle_queue = [
            queued - 1 if queued > index else queued
            for queued in self.shuffle_queue
            if queued != index
        ]
        if self.current_index > index:
            self.current_index -= 1
        if self.shuffle and not self.shuffle_queue:
            self._refill_shuffle_queue()
        self.refresh_playlist()

    def clear_playlist(self) -> None:
        if not self.tracks:
            return
        if not messagebox.askyesno("Clear playlist", "Remove all songs?"):
            return
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self._remove_decoded_audio()
        self.tracks.clear()
        self.shuffle_queue.clear()
        self.current_index = -1
        self.position = 0
        self.is_playing = self.is_paused = False
        self._update_play_button()
        self.track_title.configure(text="Pick a song")
        self.track_artist.configure(text="Your library is waiting")
        self._set_lyrics("Select a song to look up its lyrics.")
        self.refresh_playlist()

    def open_m3u(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open playlist",
            filetypes=[("Playlist M3U", "*.m3u *.m3u8"), ("All files", "*.*")],
        )
        if not filename:
            return
        playlist_path = Path(filename)
        paths = []
        try:
            for line in playlist_path.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                path = Path(line)
                paths.append(path if path.is_absolute() else playlist_path.parent / path)
        except OSError as error:
            messagebox.showerror("Couldn't open the playlist", str(error))
            return
        self.add_paths(paths)

    def save_m3u(self) -> None:
        if not self.tracks:
            messagebox.showinfo("Empty playlist", "Add some songs before saving.")
            return
        filename = filedialog.asksaveasfilename(
            title="Save playlist",
            defaultextension=".m3u",
            filetypes=[("Playlist M3U", "*.m3u")],
        )
        if not filename:
            return
        try:
            Path(filename).write_text(
                "#EXTM3U\n" + "\n".join(str(track.path) for track in self.tracks) + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            messagebox.showerror("Couldn't save the playlist", str(error))

    def fetch_lyrics(self) -> None:
        if self.current_index < 0:
            self._set_lyrics("Select a song first.")
            return
        track = self.tracks[self.current_index]
        local_lrc = track.path.with_suffix(".lrc")
        if local_lrc.is_file():
            try:
                # Pass the text with timestamps so the lyrics can be synced.
                self._set_lyrics(local_lrc.read_text(encoding="utf-8-sig"))
                return
            except OSError as error:
                self._set_lyrics(f"Couldn't read the LRC file:\n{error}")
                return
        index = self.current_index
        self._set_lyrics("Looking up lyrics…")
        threading.Thread(
            target=self._request_lyrics, args=(index, track), daemon=True
        ).start()

    def _request_lyrics(self, index: int, track: Track) -> None:
        """Runs in a background thread so the window doesn't freeze."""
        result = fetch_lrclib(track.title, track.artist)
        self.root.after(0, self._show_lyrics_result, index, result)

    def _show_lyrics_result(self, index: int, lyrics: str) -> None:
        if index == self.current_index:
            self._set_lyrics(lyrics)

    def _tick(self) -> None:
        if self.current_index >= 0 and self.is_playing and not self.is_paused:
            current = self._current_position()
            track = self.tracks[self.current_index]
            if track.duration and current >= track.duration - 0.15:
                self._advance_after_end()
            elif not pygame.mixer.music.get_busy() and current > 0.5:
                self._advance_after_end()
            else:
                self.time_label.configure(text=format_time(current))
                self._sync_lyrics(current)
                if not self._seeking:
                    self.seek_scale.set(min(current, track.duration or current))
        self._draw_visualizer()
        self._tick_after = self.root.after(250, self._tick)

    def _advance_after_end(self) -> None:
        if self.repeat == "one":
            self.play_track(self.current_index)
        elif self.shuffle and self.shuffle_queue:
            self.next_track()
        elif self.repeat == "all":
            if self.shuffle:
                self._refill_shuffle_queue()
                self.next_track()
            else:
                self.next_track()
        elif not self.shuffle and self.current_index < len(self.tracks) - 1:
            self.next_track()
        else:
            self.is_playing = False
            self.position = 0
            self._update_play_button()
            self.time_label.configure(text="0:00")
            self.seek_scale.set(0)

    def close(self) -> None:
        if self._tick_after is not None:
            self.root.after_cancel(self._tick_after)
            self._tick_after = None
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self._remove_decoded_audio()
        pygame.mixer.quit()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    SonoraPlayer(root)
    root.mainloop()
