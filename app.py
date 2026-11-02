"""Tkinter desktop interface for the Smart Music Playlist Manager."""

import tkinter as tk
from tkinter import messagebox, ttk

from playlist import Playlist, RepeatMode, SongNode


SAMPLE_SONGS = [
    ("S001", "Midnight City", "M83", 4.03),
    ("S002", "Dreams", "Fleetwood Mac", 4.18),
    ("S003", "Blinding Lights", "The Weeknd", 3.20),
    ("S004", "Electric Feel", "MGMT", 3.49),
    ("S005", "Sunflower", "Post Malone", 2.38),
]

COLORS = {
    "background": "#f4f6fb",
    "surface": "#ffffff",
    "text": "#172033",
    "muted": "#667085",
    "accent": "#4f46e5",
    "accent_hover": "#4338ca",
    "soft": "#eef2f8",
    "border": "#e3e8f0",
    "highlight": "#e9edff",
    "highlight_text": "#312e81",
}
SEARCH_PLACEHOLDER = "Search by song title or artist"


def format_duration(seconds: float) -> str:
    minutes, remainder = divmod(int(seconds * 60), 60)
    return f"{minutes}:{remainder:02d}"


class PlaylistApp(tk.Tk):
    """A compact desktop player for a linked-list playlist."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Soundwave | Smart Playlist")
        self.geometry("900x620")
        self.minsize(760, 520)
        self.configure(bg=COLORS["background"])
        self.playlist = Playlist()
        for song_id, title, artist, duration in SAMPLE_SONGS:
            self.playlist.add_song(SongNode(song_id, title, artist, duration))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            rowheight=40,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["soft"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            padding=(12, 11),
            relief="flat",
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["highlight"])],
            foreground=[("selected", COLORS["highlight_text"])],
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface"],
            background=COLORS["surface"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["muted"],
            padding=6,
        )

        top = tk.Frame(self, bg=COLORS["background"], padx=32, pady=24)
        top.pack(fill="x")
        tk.Label(top, text="SOUNDWAVE  /  YOUR MUSIC LIBRARY",
                 bg=COLORS["background"], fg=COLORS["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(top, text="Smart Music Playlist", bg=COLORS["background"],
                 fg=COLORS["text"], font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(6, 0))

        controls = tk.Frame(self, bg=COLORS["background"], padx=32)
        controls.pack(fill="x", pady=(4, 16))
        self.search_var = tk.StringVar()
        search = tk.Entry(
            controls,
            textvariable=self.search_var,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.search_entry = search
        search.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 10))
        search.insert(0, SEARCH_PLACEHOLDER)
        search.bind("<FocusIn>", self._clear_search_placeholder)
        search.bind("<FocusOut>", self._restore_search_placeholder)
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        self._button(controls, "＋  Add song", self.add_dialog, primary=True).pack(side="left", padx=4)
        self._button(controls, "Delete", self.delete_selected).pack(side="left", padx=4)
        self._button(controls, "⇄  Shuffle", self.shuffle).pack(side="left", padx=4)

        table_frame = tk.Frame(self, bg=COLORS["surface"], padx=1, pady=1,
                               highlightthickness=1, highlightbackground=COLORS["border"])
        table_frame.pack(fill="both", expand=True, padx=32)
        table_inner = tk.Frame(table_frame, bg=COLORS["surface"])
        table_inner.pack(fill="both", expand=True, padx=1, pady=1)
        table_frame.configure(bg=COLORS["surface"])
        self.table = ttk.Treeview(table_inner, columns=("title", "artist", "duration"),
                                  show="headings", selectmode="browse")
        for col, label, width in (("title", "TITLE", 360), ("artist", "ARTIST", 260),
                                  ("duration", "TIME", 100)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="w" if col != "duration" else "center",
                              stretch=col != "duration")
        self.table.configure(height=12)
        self.table.pack(fill="both", expand=True)
        self.table.tag_configure("even", background="#ffffff", foreground=COLORS["text"])
        self.table.tag_configure("odd", background="#f8faff", foreground=COLORS["text"])
        self.table.tag_configure("current", background=COLORS["highlight"],
                                 foreground=COLORS["highlight_text"])
        self.table.bind("<Double-1>", self.play_selected)

        bottom = tk.Frame(self, bg=COLORS["surface"], padx=20, pady=15,
                          highlightthickness=1, highlightbackground=COLORS["border"])
        bottom.pack(fill="x", padx=32, pady=18)
        now_panel = tk.Frame(bottom, bg=COLORS["surface"])
        now_panel.pack(side="left", fill="x", expand=True, anchor="w")
        tk.Label(now_panel, text="NOW PLAYING", bg=COLORS["surface"], fg=COLORS["muted"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.now_label = tk.Label(now_panel, text="", bg=COLORS["surface"],
                                  fg=COLORS["text"], font=("Segoe UI", 11, "bold"))
        self.now_label.pack(anchor="w", pady=(3, 0))
        self._button(bottom, "◀  Previous", self.previous).pack(side="left", padx=5)
        self._button(bottom, "▶  Next", self.next_song, primary=True).pack(side="left", padx=5)
        tk.Label(bottom, text="REPEAT", bg=COLORS["surface"], fg=COLORS["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(16, 6))
        self.repeat_var = tk.StringVar(value=RepeatMode.OFF.value)
        repeat = ttk.Combobox(bottom, textvariable=self.repeat_var, state="readonly",
                              values=[mode.value for mode in RepeatMode], width=7)
        repeat.pack(side="left")
        repeat.bind("<<ComboboxSelected>>", self.set_repeat)

    @staticmethod
    def _button(parent, text, command, primary=False):
        background = COLORS["accent"] if primary else COLORS["soft"]
        foreground = "#ffffff" if primary else COLORS["text"]
        hover = COLORS["accent_hover"] if primary else "#e2e8f2"
        return tk.Button(parent, text=text, command=command, bg=background,
                         fg=foreground, activebackground=hover, activeforeground=foreground,
                         relief="flat", padx=14, pady=10, font=("Segoe UI", 9, "bold"),
                         cursor="hand2", borderwidth=0)

    def _clear_search_placeholder(self, _event=None) -> None:
        if self.search_var.get() == SEARCH_PLACEHOLDER:
            self.search_var.set("")
            self.search_entry.configure(fg=COLORS["text"])

    def _restore_search_placeholder(self, _event=None) -> None:
        if not self.search_var.get().strip():
            self.search_var.set(SEARCH_PLACEHOLDER)
            self.search_entry.configure(fg=COLORS["muted"])

    def refresh(self) -> None:
        self.table.delete(*self.table.get_children())
        query = self.search_var.get().strip()
        if query == SEARCH_PLACEHOLDER:
            query = ""
        songs = self.playlist.search(query) if query else self.playlist.iter_forward()
        for index, song in enumerate(songs):
            marker = "▶  " if song is self.playlist.current else ""
            self.table.insert("", "end", iid=song.song_id,
                              values=(marker + song.title, song.artist, format_duration(song.duration)),
                              tags=("current" if song is self.playlist.current
                                    else "even" if index % 2 == 0 else "odd",))
        current = self.playlist.current
        self.now_label.config(text=(f"{current.title}  ·  {current.artist}"
                                    if current else "Nothing playing"))

    def add_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add a song")
        dialog.configure(bg=COLORS["background"])
        dialog.resizable(False, False)
        fields = {}
        for row, (key, label) in enumerate((("id", "Song ID"), ("title", "Title"),
                                             ("artist", "Artist"), ("duration", "Duration (minutes)"))):
            tk.Label(dialog, text=label, bg=COLORS["background"], fg=COLORS["text"]).grid(
                row=row, column=0, padx=14, pady=8, sticky="w")
            entry = tk.Entry(dialog, bg=COLORS["surface"], fg=COLORS["text"],
                             insertbackground=COLORS["text"], relief="flat")
            entry.grid(row=row, column=1, padx=14, pady=8)
            fields[key] = entry

        def save() -> None:
            try:
                song = SongNode(fields["id"].get(), fields["title"].get(), fields["artist"].get(),
                                float(fields["duration"].get()))
                self.playlist.add_song(song)
                self.refresh()
                dialog.destroy()
            except (ValueError, TypeError) as error:
                messagebox.showerror("Cannot add song", str(error), parent=dialog)
        self._button(dialog, "Add to playlist", save, primary=True).grid(row=4, column=0, columnspan=2, pady=14)

    def delete_selected(self) -> None:
        selected = self.table.selection()
        if selected:
            self.playlist.delete_song(selected[0])
            self.refresh()

    def play_selected(self, _event=None) -> None:
        selected = self.table.selection()
        if selected:
            self.playlist.current = self.playlist._find_node(selected[0])
            self.refresh()

    def next_song(self) -> None:
        self.playlist.next_song()
        self.refresh()

    def previous(self) -> None:
        self.playlist.previous_song()
        self.refresh()

    def shuffle(self) -> None:
        self.playlist.shuffle()
        self.refresh()

    def set_repeat(self, _event=None) -> None:
        self.playlist.set_repeat_mode(self.repeat_var.get())


if __name__ == "__main__":
    PlaylistApp().mainloop()
