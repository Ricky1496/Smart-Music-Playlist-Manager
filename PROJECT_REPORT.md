# Project Report: Smart Music Playlist Manager

## Objective

Build an interactive music playlist manager that demonstrates a doubly linked
list in a practical desktop application.

## Problem statement

A playlist needs efficient movement in either direction, insertion and removal
of songs, and predictable behavior at its beginning and end. A doubly linked
list directly models these operations without using Python's built-in list as
the persistent playlist structure.

## Data structure

Each `SongNode` stores `song_id`, `title`, `artist`, `duration`, `prev`, and
`next`. The `Playlist` maintains `head`, `tail`, `current`, and `size`. Every
insert, delete, and shuffle preserves reciprocal links and updates endpoints.

## Algorithms

Append and delete locate IDs by traversal. Positional insertion walks from the
closer endpoint. Search scans title and artist without modifying links.
Playback follows the current node's neighbors and applies OFF, ONE, or ALL
repeat rules at boundaries. Shuffle randomizes temporary references to nodes,
then rebuilds links; it never exchanges song fields between nodes.

## Implementation

`playlist.py` contains the independent model. `app.py` provides a Tkinter
interface with sample songs, search, add/delete, selection playback, next and
previous navigation, shuffle, and repeat selection. `tests/test_playlist.py`
uses pytest to cover insertion, deletion, traversals, playback, repeat modes,
shuffle node identity and links, and empty/singleton cases.

## Conclusion

The project makes linked-list pointer changes visible through playlist
operations and a usable desktop interface. The model is independent from Tkinter
so its behavior can be tested without a display server.
