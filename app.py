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
        self.configure(bg="#10141f")
        self.playlist = Playlist()
        for song_id, title, artist, duration in SAMPLE_SONGS:
            self.playlist.add_song(SongNode(song_id, title, artist, duration))
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#1b2231", foreground="#edf2f7",
                        fieldbackground="#1b2231", rowheight=34, borderwidth=0)
        style.configure("Treeview.Heading", background="#242d40", foreground="#9caefc",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#4d5fe8")])

        top = tk.Frame(self, bg="#10141f", padx=28, pady=22)
        top.pack(fill="x")
        tk.Label(top, text="SOUNDWAVE", bg="#10141f", fg="#8d9cff",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(top, text="Smart Music Playlist", bg="#10141f", fg="white",
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(4, 0))

        controls = tk.Frame(self, bg="#10141f", padx=28)
        controls.pack(fill="x", pady=(0, 14))
        self.search_var = tk.StringVar()
        search = tk.Entry(controls, textvariable=self.search_var, bg="#1b2231", fg="white",
                          insertbackground="white", relief="flat", font=("Segoe UI", 11))
        search.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        search.insert(0, "Search title or artist")
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        self._button(controls, "＋  Add song", self.add_dialog, primary=True).pack(side="left", padx=4)
        self._button(controls, "Delete", self.delete_selected).pack(side="left", padx=4)
        self._button(controls, "⇄  Shuffle", self.shuffle).pack(side="left", padx=4)

        table_frame = tk.Frame(self, bg="#10141f", padx=28)
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=("title", "artist", "duration"),
                                  show="headings", selectmode="browse")
        for col, label, width in (("title", "TITLE", 360), ("artist", "ARTIST", 260),
                                  ("duration", "TIME", 100)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="w" if col != "duration" else "center")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<Double-1>", self.play_selected)

        bottom = tk.Frame(self, bg="#1b2231", padx=26, pady=18)
        bottom.pack(fill="x", padx=28, pady=18)
        self.now_label = tk.Label(bottom, text="", bg="#1b2231", fg="white",
                                  font=("Segoe UI", 12, "bold"))
        self.now_label.pack(side="left", fill="x", expand=True, anchor="w")
        self._button(bottom, "◀  Previous", self.previous).pack(side="left", padx=5)
        self._button(bottom, "▶  Next", self.next_song, primary=True).pack(side="left", padx=5)
        tk.Label(bottom, text="REPEAT", bg="#1b2231", fg="#9da9bf",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(18, 6))
        self.repeat_var = tk.StringVar(value=RepeatMode.OFF.value)
        repeat = ttk.Combobox(bottom, textvariable=self.repeat_var, state="readonly",
                              values=[mode.value for mode in RepeatMode], width=7)
        repeat.pack(side="left")
        repeat.bind("<<ComboboxSelected>>", self.set_repeat)

    @staticmethod
    def _button(parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, bg="#5d6df0" if primary else "#293246",
                         fg="white", activebackground="#7885ff", activeforeground="white",
                         relief="flat", padx=13, pady=9, font=("Segoe UI", 9, "bold"), cursor="hand2")

    def refresh(self) -> None:
        self.table.delete(*self.table.get_children())
        query = self.search_var.get().strip()
        if query == "Search title or artist":
            query = ""
        songs = self.playlist.search(query) if query else self.playlist.iter_forward()
        for song in songs:
            marker = "▶  " if song is self.playlist.current else ""
            self.table.insert("", "end", iid=song.song_id,
                              values=(marker + song.title, song.artist, format_duration(song.duration)))
        current = self.playlist.current
        self.now_label.config(text=(f"NOW PLAYING    {current.title}  ·  {current.artist}"
                                    if current else "NOW PLAYING    Nothing playing"))

    def add_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add a song")
        dialog.configure(bg="#1b2231")
        dialog.resizable(False, False)
        fields = {}
        for row, (key, label) in enumerate((("id", "Song ID"), ("title", "Title"),
                                             ("artist", "Artist"), ("duration", "Duration (minutes)"))):
            tk.Label(dialog, text=label, bg="#1b2231", fg="white").grid(row=row, column=0, padx=14, pady=8, sticky="w")
            entry = tk.Entry(dialog, bg="#293246", fg="white", insertbackground="white", relief="flat")
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
