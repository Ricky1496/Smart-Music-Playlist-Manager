# Smart Music Playlist Manager

A classroom-friendly playlist application that turns the doubly linked list
into a live diagram. Operate the playlist and watch `head`, `tail`, `current`,
and every node's `prev` / `next` links update. It supports positional
insertion, deletion, search, reverse, sort, shuffle, repeat modes, and JSON
save/load. The app models playlist navigation; it does not play audio.

## Requirements

- Python 3.10 or newer
- Tkinter (included with most Python distributions; on Debian/Ubuntu install
  `python3-tk` if it is missing)
- pytest for running tests

## Install and run

```bash
git clone https://github.com/Ricky1496/Smart-Music-Playlist-Manager.git
cd Smart-Music-Playlist-Manager
python -m pip install -r requirements.txt
python app.py
```

The app opens with five sample songs. Select a row or click a node card to move
the `current` pointer. Use **Add / Insert** to append or insert at a 1-based
position. **Delete**, **Next**, **Previous**, **Shuffle**, **Reverse**, and
**Sort** update the live structure diagram and explain pointer changes in the
Pointer Trace panel. **Open** and **Save** use a portable JSON playlist file
that preserves song order, current song, and repeat mode.

For a classroom demonstration, start with the list diagram, click a node, insert
before it, delete it, and compare the Pointer Trace after each operation. Then
use **Reverse** and **Shuffle** to show that the nodes themselves are preserved
while their links and order change.

## Run tests

```bash
python -m pytest -q
```

## Project structure

```text
app.py                 Tkinter UI and live structure visualizer
playlist.py            Doubly linked list model
tests/test_playlist.py Pytest coverage
docs/ALGORITHMS.md     Operation costs and shuffle algorithm
PROJECT_REPORT.md      University project report
screenshots/README.md  Screenshot capture instructions
```

See [PROJECT_REPORT.md](PROJECT_REPORT.md) and [docs/ALGORITHMS.md](docs/ALGORITHMS.md)
for the design and complexity discussion.
