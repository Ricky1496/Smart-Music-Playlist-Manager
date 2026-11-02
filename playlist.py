"""Doubly linked list playlist model for the Smart Music Playlist Manager."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
from typing import Iterator, Optional


class RepeatMode(str, Enum):
    """Playback repeat behavior."""

    OFF = "OFF"
    ONE = "ONE"
    ALL = "ALL"


@dataclass(eq=False)
class SongNode:
    """One song and its links in the doubly linked playlist."""

    song_id: str
    title: str
    artist: str
    duration: float
    prev: Optional[SongNode] = None
    next: Optional[SongNode] = None

    def __post_init__(self) -> None:
        self.song_id = str(self.song_id).strip()
        self.title = self.title.strip()
        self.artist = self.artist.strip()
        if not self.song_id or not self.title or not self.artist:
            raise ValueError("Song ID, title, and artist are required.")
        if self.duration <= 0:
            raise ValueError("Duration must be greater than zero.")


class Playlist:
    """Manage songs using only linked nodes as persistent playlist storage."""

    def __init__(self) -> None:
        self.head: Optional[SongNode] = None
        self.tail: Optional[SongNode] = None
        self.current: Optional[SongNode] = None
        self.size = 0
        self.repeat_mode = RepeatMode.OFF

    def _find_node(self, song_id: str) -> Optional[SongNode]:
        node = self.head
        while node is not None:
            if node.song_id == str(song_id):
                return node
            node = node.next
        return None

    def get_song(self, song_id: str) -> Optional[SongNode]:
        """Return the node with this ID, or None when it is not in the playlist."""
        return self._find_node(song_id)

    def add_song(self, song: SongNode) -> SongNode:
        """Append a song and return its node."""
        if self._find_node(song.song_id):
            raise ValueError(f"Song ID {song.song_id!r} already exists.")
        song.prev = self.tail
        song.next = None
        if self.tail:
            self.tail.next = song
        else:
            self.head = song
        self.tail = song
        self.size += 1
        if self.current is None:
            self.current = song
        return song

    def insert_song(self, song: SongNode, position: int) -> SongNode:
        """Insert at a zero-based position (size means append)."""
        if not 0 <= position <= self.size:
            raise IndexError(f"Position must be between 0 and {self.size}.")
        if self._find_node(song.song_id):
            raise ValueError(f"Song ID {song.song_id!r} already exists.")
        if position == self.size:
            return self.add_song(song)
        if position == 0:
            song.prev = None
            song.next = self.head
            self.head.prev = song  # type: ignore[union-attr]
            self.head = song
        else:
            right = self._node_at(position)
            left = right.prev  # type: ignore[union-attr]
            song.prev, song.next = left, right
            left.next = song  # type: ignore[union-attr]
            right.prev = song  # type: ignore[union-attr]
        self.size += 1
        if self.current is None:
            self.current = song
        return song

    def _node_at(self, position: int) -> SongNode:
        if not 0 <= position < self.size:
            raise IndexError("Position is outside the playlist.")
        if position < self.size // 2:
            node = self.head
            for _ in range(position):
                node = node.next  # type: ignore[union-attr]
        else:
            node = self.tail
            for _ in range(self.size - position - 1):
                node = node.prev  # type: ignore[union-attr]
        return node  # type: ignore[return-value]

    def delete_song(self, song_id: str) -> Optional[SongNode]:
        """Remove by ID and return the detached node, or None when absent."""
        node = self._find_node(song_id)
        if node is None:
            return None
        replacement = node.next or node.prev
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        if self.current is node:
            self.current = replacement
        node.prev = node.next = None
        self.size -= 1
        if not self.size:
            self.head = self.tail = self.current = None
        return node

    def search(self, query: str) -> Iterator[SongNode]:
        """Yield songs whose title or artist contains query, case-insensitively."""
        query = query.strip().casefold()
        node = self.head
        while node:
            if query in node.title.casefold() or query in node.artist.casefold():
                yield node
            node = node.next

    def iter_forward(self) -> Iterator[SongNode]:
        node = self.head
        while node:
            yield node
            node = node.next

    def iter_backward(self) -> Iterator[SongNode]:
        node = self.tail
        while node:
            yield node
            node = node.prev

    def next_song(self) -> Optional[SongNode]:
        """Advance playback according to repeat mode."""
        if self.current is None:
            if self.repeat_mode is RepeatMode.ALL:
                self.current = self.head
            return self.current
        if self.repeat_mode is RepeatMode.ONE:
            return self.current
        if self.current.next:
            self.current = self.current.next
        elif self.repeat_mode is RepeatMode.ALL:
            self.current = self.head
        else:
            self.current = None
        return self.current

    def previous_song(self) -> Optional[SongNode]:
        """Move backward; repeat-all wraps from the first to the last song."""
        if self.current is None:
            self.current = self.tail
            return self.current
        if self.current.prev:
            self.current = self.current.prev
        elif self.repeat_mode is RepeatMode.ALL:
            self.current = self.tail
        else:
            self.current = None
        return self.current

    def shuffle(self, rng: Optional[random.Random] = None) -> None:
        """Reorder existing nodes by relinking pointers, preserving current node."""
        nodes = list(self.iter_forward())
        if len(nodes) < 2:
            return
        (rng or random).shuffle(nodes)
        self.head, self.tail = nodes[0], nodes[-1]
        for index, node in enumerate(nodes):
            node.prev = nodes[index - 1] if index else None
            node.next = nodes[index + 1] if index + 1 < len(nodes) else None

    def reverse(self) -> None:
        """Reverse the order by swapping links on each node in O(n) time."""
        node = self.head
        while node is not None:
            node.prev, node.next = node.next, node.prev
            node = node.prev  # The original next node after swapping.
        self.head, self.tail = self.tail, self.head

    def sort_by(self, field: str = "title") -> None:
        """Sort by title, artist, or duration by relinking existing nodes."""
        if field not in {"title", "artist", "duration"}:
            raise ValueError("Sort field must be title, artist, or duration.")
        nodes = list(self.iter_forward())
        if field == "duration":
            nodes.sort(key=lambda song: song.duration)
        else:
            nodes.sort(key=lambda song: getattr(song, field).casefold())
        if not nodes:
            return
        self.head, self.tail = nodes[0], nodes[-1]
        for index, node in enumerate(nodes):
            node.prev = nodes[index - 1] if index else None
            node.next = nodes[index + 1] if index + 1 < len(nodes) else None

    def set_repeat_mode(self, mode: RepeatMode | str) -> None:
        self.repeat_mode = RepeatMode(mode)

    def validate(self) -> bool:
        """Raise AssertionError if links, endpoints, current, or size disagree."""
        count = 0
        previous = None
        node = self.head
        seen = set()
        while node:
            assert id(node) not in seen, "Cycle detected in forward links."
            seen.add(id(node))
            assert node.prev is previous
            previous = node
            node = node.next
            count += 1
        assert previous is self.tail
        assert count == self.size
        assert (self.head is None) == (self.tail is None)
        assert self.current is None or id(self.current) in seen
        return True
