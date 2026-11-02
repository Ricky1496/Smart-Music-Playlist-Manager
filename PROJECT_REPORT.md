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
insert, delete, reverse, sort, and shuffle preserves reciprocal links and
updates endpoints. Song duration is stored in seconds.

## Algorithms

Append and delete locate IDs by traversal. Positional insertion walks from the
closer endpoint. Search scans title and artist without modifying links.
Playback follows the current node's neighbors and applies OFF, ONE, or ALL
repeat rules at boundaries. Shuffle randomizes temporary references to nodes,
then rebuilds links; it never exchanges song fields between nodes. Reverse
swaps both links on each node and then swaps the endpoints. Sort orders
temporary node references and reconnects the existing nodes in the new order.

## Implementation

`playlist.py` contains the independent model. `app.py` provides a Tkinter
interface with sample songs, search, append and positional insert, deletion,
next and previous navigation, shuffle, reverse, sort by title/artist/duration,
OFF / ONE / ALL repeat, and JSON save/load. The live structure view draws each
node and its links. A pointer trace describes each operation and its time cost.
`tests/test_playlist.py` covers insertion, deletion, traversal, navigation,
repeat modes, shuffle, reverse, sort, and edge cases.

## Conclusion

The project makes linked-list pointer changes visible and interactive, giving
students a way to connect abstract operations with their effects on nodes and
endpoints. The model remains independent from Tkinter so core behavior can be
tested without a display server. Audio output is outside the project's scope.
