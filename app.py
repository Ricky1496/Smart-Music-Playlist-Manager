"""Desktop Playlist Structure Lab: a visual doubly linked list demo."""

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from playlist import Playlist, RepeatMode, SongNode


SAMPLE_SONGS = [
    ("S001", "Midnight City", "M83", 242),
    ("S002", "Dreams", "Fleetwood Mac", 251),
    ("S003", "Blinding Lights", "The Weeknd", 200),
    ("S004", "Electric Feel", "MGMT", 229),
    ("S005", "Sunflower", "Post Malone", 158),
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
    "green": "#16845b",
    "green_soft": "#e5f7ef",
}
SEARCH_PLACEHOLDER = "Search songs by title or artist"


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as minutes and seconds."""
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes}:{remainder:02d}"


class PlaylistApp(tk.Tk):
    """Playlist manager with an interactive node-and-pointer classroom view."""

    CARD_WIDTH = 218
    CARD_HEIGHT = 128
    CARD_GAP = 74

    def __init__(self) -> None:
        super().__init__()
        self.title("Soundwave | Playlist Structure Lab")
        self.geometry("1180x900")
        self.minsize(980, 760)
        self.configure(bg=COLORS["background"])
        self.playlist = Playlist()
        self._refreshing = False
        for song_id, title, artist, duration in SAMPLE_SONGS:
            self.playlist.add_song(SongNode(song_id, title, artist, duration))
        self._build_ui()
        self._log(
            "Ready to explore",
            "Each card is one SongNode. Click a card or a playlist row to move CURRENT. "
            "The arrows and prev/next fields show the links stored in the nodes.",
            "Start here: Next and Previous follow one pointer each, so navigation is O(1).",
        )
        self.refresh()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["surface"],
                        foreground=COLORS["text"], fieldbackground=COLORS["surface"],
                        rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=COLORS["soft"],
                        foreground=COLORS["muted"], font=("Segoe UI", 9, "bold"),
                        padding=(10, 9), relief="flat")
        style.map("Treeview", background=[("selected", COLORS["highlight"])],
                  foreground=[("selected", COLORS["highlight_text"])])
        style.configure("TCombobox", fieldbackground=COLORS["surface"],
                        background=COLORS["surface"], foreground=COLORS["text"],
                        arrowcolor=COLORS["muted"], padding=5)

        header = tk.Frame(self, bg=COLORS["background"], padx=30, pady=18)
        header.pack(fill="x")
        tk.Label(header, text="SOUNDWAVE  /  DATA STRUCTURE CLASSROOM",
                 bg=COLORS["background"], fg=COLORS["accent"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Playlist Structure Lab", bg=COLORS["background"],
                 fg=COLORS["text"], font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(4, 0))
        tk.Label(header, text="Operate a playlist. Watch the doubly linked list change in real time.",
                 bg=COLORS["background"], fg=COLORS["muted"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

        toolbar = tk.Frame(self, bg=COLORS["background"], padx=30)
        toolbar.pack(fill="x", pady=(2, 12))
        self.search_var = tk.StringVar(value=SEARCH_PLACEHOLDER)
        self.search_entry = tk.Entry(
            toolbar, textvariable=self.search_var, bg=COLORS["surface"],
            fg=COLORS["muted"], insertbackground=COLORS["text"], relief="flat",
            font=("Segoe UI", 10), highlightthickness=1,
            highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"],
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.search_entry.bind("<FocusIn>", self._clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_search_placeholder)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh())
        self._button(toolbar, "＋  Add / Insert", self.add_dialog, primary=True).pack(side="left", padx=3)
        self._button(toolbar, "Delete", self.delete_selected).pack(side="left", padx=3)
        self._button(toolbar, "Shuffle", self.shuffle).pack(side="left", padx=3)
        self._button(toolbar, "Reverse", self.reverse).pack(side="left", padx=3)
        self.sort_var = tk.StringVar(value="title")
        ttk.Combobox(toolbar, textvariable=self.sort_var, state="readonly",
                     values=("title", "artist", "duration"), width=9).pack(side="left", padx=(8, 3))
        self._button(toolbar, "Sort", self.sort_playlist).pack(side="left", padx=3)
        self._button(toolbar, "Open", self.load_playlist).pack(side="left", padx=(9, 3))
        self._button(toolbar, "Save", self.save_playlist).pack(side="left", padx=3)

        list_header = tk.Frame(self, bg=COLORS["background"], padx=30)
        list_header.pack(fill="x", pady=(0, 6))
        tk.Label(list_header, text="PLAYLIST", bg=COLORS["background"],
                 fg=COLORS["text"], font=("Segoe UI", 10, "bold")).pack(side="left")
        self.count_label = tk.Label(list_header, text="", bg=COLORS["background"],
                                    fg=COLORS["muted"], font=("Segoe UI", 9))
        self.count_label.pack(side="right")

        list_frame = tk.Frame(self, bg=COLORS["surface"], padx=1, pady=1,
                              highlightthickness=1, highlightbackground=COLORS["border"])
        list_frame.pack(fill="x", padx=30)
        self.table = ttk.Treeview(list_frame, columns=("title", "artist", "duration"),
                                  show="headings", selectmode="browse", height=5)
        for col, label, width in (("title", "TITLE / CURRENT", 430),
                                  ("artist", "ARTIST", 400), ("duration", "TIME", 100)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="center" if col == "duration" else "w",
                              stretch=col != "duration")
        self.table.pack(fill="x", expand=True, padx=1, pady=1)
        self.table.tag_configure("even", background="#ffffff", foreground=COLORS["text"])
        self.table.tag_configure("odd", background="#f8faff", foreground=COLORS["text"])
        self.table.tag_configure("current", background=COLORS["highlight"],
                                 foreground=COLORS["highlight_text"])
        self.table.bind("<<TreeviewSelect>>", self.play_selected)

        structure_header = tk.Frame(self, bg=COLORS["background"], padx=30)
        structure_header.pack(fill="x", pady=(16, 6))
        tk.Label(structure_header, text="LIVE LINKED-LIST STRUCTURE", bg=COLORS["background"],
                 fg=COLORS["text"], font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(structure_header, text="Click a node to make it CURRENT",
                 bg=COLORS["background"], fg=COLORS["muted"],
                 font=("Segoe UI", 9)).pack(side="right")

        diagram_frame = tk.Frame(self, bg=COLORS["surface"], padx=1, pady=1,
                                 highlightthickness=1, highlightbackground=COLORS["border"])
        diagram_frame.pack(fill="x", padx=30)
        self.diagram = tk.Canvas(diagram_frame, height=188, bg=COLORS["surface"],
                                 highlightthickness=0, xscrollincrement=48)
        self.diagram.pack(fill="x", expand=True, padx=4, pady=(5, 0))
        scrollbar = ttk.Scrollbar(diagram_frame, orient="horizontal", command=self.diagram.xview)
        scrollbar.pack(fill="x", padx=4, pady=(0, 4))
        self.diagram.configure(xscrollcommand=scrollbar.set)

        trace_header = tk.Frame(self, bg=COLORS["background"], padx=30)
        trace_header.pack(fill="x", pady=(12, 5))
        tk.Label(trace_header, text="POINTER TRACE", bg=COLORS["background"],
                 fg=COLORS["text"], font=("Segoe UI", 10, "bold")).pack(side="left")
        self.complexity_label = tk.Label(trace_header, text="", bg=COLORS["green_soft"],
                                         fg=COLORS["green"], padx=9, pady=4,
                                         font=("Segoe UI", 8, "bold"))
        self.complexity_label.pack(side="right")
        self.trace = tk.Text(self, height=3, wrap="word", relief="flat", bd=0,
                             bg=COLORS["surface"], fg=COLORS["text"],
                             font=("Segoe UI", 9), padx=12, pady=9,
                             highlightthickness=1, highlightbackground=COLORS["border"])
        self.trace.pack(fill="x", padx=30)
        self.trace.configure(state="disabled")

        footer = tk.Frame(self, bg=COLORS["surface"], padx=18, pady=10,
                          highlightthickness=1, highlightbackground=COLORS["border"])
        footer.pack(fill="x", padx=30, pady=12)
        now = tk.Frame(footer, bg=COLORS["surface"])
        now.pack(side="left", fill="x", expand=True)
        tk.Label(now, text="CURRENT NODE", bg=COLORS["surface"], fg=COLORS["muted"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.now_label = tk.Label(now, text="", bg=COLORS["surface"], fg=COLORS["text"],
                                  font=("Segoe UI", 10, "bold"))
        self.now_label.pack(anchor="w", pady=(2, 0))
        self._button(footer, "◀  Previous", self.previous).pack(side="left", padx=4)
        self._button(footer, "Next  ▶", self.next_song, primary=True).pack(side="left", padx=4)
        tk.Label(footer, text="REPEAT", bg=COLORS["surface"], fg=COLORS["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(10, 5))
        self.repeat_var = tk.StringVar(value=RepeatMode.OFF.value)
        repeat = ttk.Combobox(footer, textvariable=self.repeat_var, state="readonly",
                              values=[mode.value for mode in RepeatMode], width=7)
        repeat.pack(side="left")
        repeat.bind("<<ComboboxSelected>>", self.set_repeat)

    @staticmethod
    def _button(parent, text, command, primary=False):
        bg = COLORS["accent"] if primary else COLORS["soft"]
        fg = "#ffffff" if primary else COLORS["text"]
        active = COLORS["accent_hover"] if primary else "#e2e8f2"
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground=active, activeforeground=fg, relief="flat",
                         padx=10, pady=8, font=("Segoe UI", 8, "bold"),
                         cursor="hand2", borderwidth=0)

    def _clear_search_placeholder(self, _event=None) -> None:
        if self.search_var.get() == SEARCH_PLACEHOLDER:
            self.search_var.set("")
            self.search_entry.configure(fg=COLORS["text"])

    def _restore_search_placeholder(self, _event=None) -> None:
        if not self.search_var.get().strip():
            self.search_var.set(SEARCH_PLACEHOLDER)
            self.search_entry.configure(fg=COLORS["muted"])

    @staticmethod
    def _node_ref(node):
        return "None" if node is None else f"{node.song_id} ({node.title})"

    def _log(self, title: str, detail: str, complexity: str) -> None:
        self.trace.configure(state="normal")
        self.trace.delete("1.0", "end")
        self.trace.insert("1.0", f"{title}\n{detail}")
        self.trace.configure(state="disabled")
        self.complexity_label.configure(text=complexity)

    def refresh(self) -> None:
        selected = self.table.selection()
        selected_id = selected[0] if selected else None
        self._refreshing = True
        self.table.delete(*self.table.get_children())
        query = self.search_var.get().strip()
        if query == SEARCH_PLACEHOLDER:
            query = ""
        songs = self.playlist.search(query) if query else self.playlist.iter_forward()
        for index, song in enumerate(songs):
            marker = "▶  " if song is self.playlist.current else ""
            tag = "current" if song is self.playlist.current else "even" if index % 2 == 0 else "odd"
            self.table.insert("", "end", iid=song.song_id,
                              values=(marker + song.title, song.artist,
                                      format_duration(song.duration)), tags=(tag,))
        if selected_id and self.table.exists(selected_id):
            self.table.selection_set(selected_id)
        self._refreshing = False
        current = self.playlist.current
        self.now_label.configure(text=self._node_ref(current))
        self.count_label.configure(
            text=f"{self.playlist.size} songs   ·   {self.playlist.repeat_mode.value} repeat")
        self._draw_structure()

    def _draw_structure(self) -> None:
        self.diagram.delete("all")
        nodes = list(self.playlist.iter_forward())
        if not nodes:
            self.diagram.create_text(35, 82, anchor="w", fill=COLORS["muted"],
                                     font=("Segoe UI", 11),
                                     text="Empty list   ·   head = tail = current = None   ·   size = 0")
            self.diagram.configure(scrollregion=(0, 0, 760, 180))
            return

        start_x, top_y = 46, 34
        step = self.CARD_WIDTH + self.CARD_GAP
        total_width = start_x + len(nodes) * step + 46
        self.diagram.configure(scrollregion=(0, 0, total_width, 184))

        for index, node in enumerate(nodes):
            x = start_x + index * step
            is_current = node is self.playlist.current
            tag = f"node-{index}"
            border = COLORS["accent"] if is_current else COLORS["border"]
            card_fill = COLORS["highlight"] if is_current else COLORS["surface"]
            title_fill = COLORS["highlight_text"] if is_current else COLORS["text"]
            self.diagram.create_text(x, 13, anchor="w", text="HEAD" if index == 0 else "",
                                     fill=COLORS["accent"], font=("Segoe UI", 8, "bold"))
            self.diagram.create_text(x + self.CARD_WIDTH, 13, anchor="e",
                                     text="TAIL" if index == len(nodes) - 1 else "",
                                     fill=COLORS["accent"], font=("Segoe UI", 8, "bold"))
            self.diagram.create_rectangle(x, top_y, x + self.CARD_WIDTH,
                                         top_y + self.CARD_HEIGHT, fill=card_fill,
                                         outline=border, width=2 if is_current else 1,
                                         tags=(tag,))
            self.diagram.create_text(x + 13, top_y + 17, anchor="w",
                                     text=f"NODE  {node.song_id}", fill=COLORS["muted"],
                                     font=("Segoe UI", 8, "bold"), tags=(tag,))
            if is_current:
                self.diagram.create_text(x + self.CARD_WIDTH - 12, top_y + 17, anchor="e",
                                         text="CURRENT", fill=COLORS["accent"],
                                         font=("Segoe UI", 8, "bold"), tags=(tag,))
            self.diagram.create_text(x + 13, top_y + 43, anchor="w",
                                     text=node.title[:23], fill=title_fill,
                                     font=("Segoe UI", 10, "bold"), tags=(tag,))
            self.diagram.create_text(x + 13, top_y + 64, anchor="w",
                                     text=node.artist[:26], fill=COLORS["muted"],
                                     font=("Segoe UI", 9), tags=(tag,))
            self.diagram.create_text(x + 13, top_y + 96, anchor="w",
                                     text=f"prev  ←  {node.prev.song_id if node.prev else 'None'}",
                                     fill=COLORS["text"], font=("Consolas", 8), tags=(tag,))
            self.diagram.create_text(x + 13, top_y + 113, anchor="w",
                                     text=f"next  →  {node.next.song_id if node.next else 'None'}",
                                     fill=COLORS["text"], font=("Consolas", 8), tags=(tag,))
            self.diagram.tag_bind(
                tag, "<Button-1>", lambda _event, selected=node: self.choose_current(selected))

        center_y = top_y + 70
        for index in range(len(nodes) - 1):
            left = start_x + index * step + self.CARD_WIDTH + 4
            right = start_x + (index + 1) * step - 4
            middle = (left + right) / 2
            self.diagram.create_line(left, center_y - 9, right, center_y - 9,
                                     fill=COLORS["accent"], width=2, arrow="last")
            self.diagram.create_text(middle, center_y - 21, text="next", fill=COLORS["accent"],
                                     font=("Segoe UI", 7, "bold"))
            self.diagram.create_line(left, center_y + 11, right, center_y + 11,
                                     fill=COLORS["green"], width=2, arrow="first")
            self.diagram.create_text(middle, center_y + 24, text="prev", fill=COLORS["green"],
                                     font=("Segoe UI", 7, "bold"))

        self.diagram.create_line(start_x - 27, center_y, start_x - 3, center_y,
                                 fill=COLORS["accent"], width=2, arrow="last")
        tail_x = start_x + (len(nodes) - 1) * step + self.CARD_WIDTH + 3
        self.diagram.create_line(tail_x, center_y, tail_x + 24, center_y,
                                 fill=COLORS["accent"], width=2, arrow="last")

    def _find_song(self, song_id: str):
        return self.playlist.get_song(song_id)

    def choose_current(self, song) -> None:
        old = self.playlist.current
        self.playlist.current = song
        if old is not song:
            self._log("CURRENT pointer moved", f"current now references {self._node_ref(song)}. "
                      "No node links changed; we changed one reference.", "O(1)")
        self.refresh()

    def add_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Add or insert a song")
        dialog.configure(bg=COLORS["background"])
        dialog.resizable(False, False)
        dialog.transient(self)
        fields = {}
        next_number = max(
            [int(node.song_id[1:]) for node in self.playlist.iter_forward()
             if node.song_id.startswith("S") and node.song_id[1:].isdigit()] or [0]
        ) + 1
        defaults = {"id": f"S{next_number:03d}"}
        rows = (("id", "Song ID"), ("title", "Title"), ("artist", "Artist"),
                ("duration", "Duration (seconds)"),
                ("position", f"Position (1 to {self.playlist.size + 1}; blank = end)"))
        for row, (key, label) in enumerate(rows):
            tk.Label(dialog, text=label, bg=COLORS["background"], fg=COLORS["text"],
                     font=("Segoe UI", 9)).grid(row=row, column=0, padx=14, pady=7, sticky="w")
            entry = tk.Entry(dialog, bg=COLORS["surface"], fg=COLORS["text"],
                             insertbackground=COLORS["text"], relief="flat", width=30)
            entry.grid(row=row, column=1, padx=14, pady=7)
            if key in defaults:
                entry.insert(0, defaults[key])
            fields[key] = entry

        def save() -> None:
            try:
                node = SongNode(fields["id"].get(), fields["title"].get(),
                                fields["artist"].get(), float(fields["duration"].get()))
                position_text = fields["position"].get().strip()
                if position_text:
                    position = int(position_text)
                    self.playlist.insert_song(node, position - 1)
                    left, right = node.prev, node.next
                    self._log("Inserted a node", f"At position {position}, set "
                              f"{left.song_id if left else 'head'}.next → {node.song_id} and "
                              f"{right.song_id if right else 'tail'}.prev → {node.song_id}; "
                              "the new node points back and forward to its neighbors.",
                              "O(n) locate + O(1) relink")
                else:
                    old_tail = self.playlist.tail
                    self.playlist.add_song(node)
                    self._log("Appended a node", f"Set {old_tail.song_id if old_tail else 'head'}"
                              f".next → {node.song_id}; new node.prev → "
                              f"{old_tail.song_id if old_tail else 'None'}; tail → {node.song_id}.",
                              "O(n) ID check + O(1) relink")
                self.refresh()
                dialog.destroy()
            except (ValueError, TypeError, IndexError) as error:
                messagebox.showerror("Cannot add song", str(error), parent=dialog)
        self._button(dialog, "Add to playlist", save, primary=True).grid(
            row=len(rows), column=0, columnspan=2, pady=14)
        dialog.grab_set()
        fields["title"].focus_set()

    def delete_selected(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Delete song", "Select a playlist row first.", parent=self)
            return
        node = self._find_song(selected[0])
        if node is None:
            return
        previous_id = node.prev.song_id if node.prev else "None"
        next_id = node.next.song_id if node.next else "None"
        if node.prev and node.next:
            link_change = (f"{previous_id}.next now points to {next_id}, and "
                           f"{next_id}.prev points to {previous_id}.")
        elif node.next:
            link_change = f"head now points to {next_id}, and {next_id}.prev is None."
        elif node.prev:
            link_change = f"tail now points to {previous_id}, and {previous_id}.next is None."
        else:
            link_change = "The only node was removed, so head and tail are now None."
        was_current = node is self.playlist.current
        self.playlist.delete_song(node.song_id)
        self._log("Deleted a node", f"Bypassed {node.song_id}: {link_change} "
                  f"Detached node links were cleared. Current {'moved to its neighbor' if was_current else 'stayed put'}.",
                  "O(n) ID search + O(1) unlink")
        self.refresh()

    def play_selected(self, _event=None) -> None:
        if self._refreshing:
            return
        selected = self.table.selection()
        if selected:
            node = self._find_song(selected[0])
            if node and node is not self.playlist.current:
                self.choose_current(node)

    def next_song(self) -> None:
        old = self.playlist.current
        new = self.playlist.next_song()
        self._log("Moved to next", f"Followed current.next from {self._node_ref(old)} to "
                  f"{self._node_ref(new)}. At the end, repeat mode decides whether to stop or wrap.",
                  "O(1)")
        self.refresh()

    def previous(self) -> None:
        old = self.playlist.current
        new = self.playlist.previous_song()
        self._log("Moved to previous", f"Followed current.prev from {self._node_ref(old)} to "
                  f"{self._node_ref(new)}. At the beginning, repeat mode decides whether to stop or wrap.",
                  "O(1)")
        self.refresh()

    def shuffle(self) -> None:
        current = self.playlist.current
        self.playlist.shuffle()
        self._log("Shuffled the playlist", f"Reordered the existing node references and rebuilt "
                  f"every prev/next link. SongNode objects and CURRENT ({self._node_ref(current)}) "
                  "were preserved.", "O(n) time · O(n) temporary references")
        self.refresh()

    def reverse(self) -> None:
        self.playlist.reverse()
        self._log("Reversed the playlist", "Swapped prev and next on each node, then swapped "
                  "head and tail. The current pointer still refers to the same song node.",
                  "O(n) time · O(1) extra space")
        self.refresh()

    def sort_playlist(self) -> None:
        field = self.sort_var.get()
        self.playlist.sort_by(field)
        self._log("Sorted by " + field, "Sorted temporary node references, then reconnected "
                  "the existing nodes in the new order. Song fields were not swapped.",
                  "O(n log n) sort + O(n) relink")
        self.refresh()

    def set_repeat(self, _event=None) -> None:
        self.playlist.set_repeat_mode(self.repeat_var.get())
        self._log("Repeat mode changed", f"Repeat is now {self.playlist.repeat_mode.value}. "
                  "The selected rule is applied when navigation reaches a list boundary.", "O(1)")
        self.refresh()

    def save_playlist(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self, title="Save playlist", defaultextension=".json",
            filetypes=(("Playlist data", "*.json"), ("All files", "*.*")))
        if not path:
            return
        data = {
            "format": "smart-music-playlist-v1",
            "repeat_mode": self.playlist.repeat_mode.value,
            "current_song_id": self.playlist.current.song_id if self.playlist.current else None,
            "songs": [{"song_id": song.song_id, "title": song.title, "artist": song.artist,
                       "duration": song.duration} for song in self.playlist.iter_forward()],
        }
        try:
            with open(path, "w", encoding="utf-8") as playlist_file:
                json.dump(data, playlist_file, indent=2, ensure_ascii=False)
            self._log("Playlist saved", f"Wrote {self.playlist.size} songs, current song, and "
                      f"repeat mode to {path}.", "O(n) serialization")
        except OSError as error:
            messagebox.showerror("Cannot save playlist", str(error), parent=self)

    def load_playlist(self) -> None:
        path = filedialog.askopenfilename(
            parent=self, title="Open playlist", filetypes=(("Playlist data", "*.json"),
                                                            ("All files", "*.*")))
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as playlist_file:
                data = json.load(playlist_file)
            if not isinstance(data, dict) or not isinstance(data.get("songs"), list):
                raise ValueError("The file must contain a playlist object with a songs array.")
            loaded = Playlist()
            for item in data["songs"]:
                loaded.add_song(SongNode(item["song_id"], item["title"], item["artist"],
                                         float(item["duration"])))
            current_id = data.get("current_song_id")
            if current_id:
                loaded.current = loaded.get_song(current_id)
            loaded.set_repeat_mode(data.get("repeat_mode", RepeatMode.OFF.value))
            self.playlist = loaded
            self.repeat_var.set(loaded.repeat_mode.value)
            self._log("Playlist loaded", f"Rebuilt {loaded.size} SongNode objects and linked "
                      f"them in file order. Current = {self._node_ref(loaded.current)}.",
                      "O(n) node creation and linking")
            self.refresh()
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            messagebox.showerror("Cannot open playlist", str(error), parent=self)


if __name__ == "__main__":
    PlaylistApp().mainloop()
