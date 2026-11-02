# Smart Music Playlist Manager

A desktop playlist application that demonstrates a doubly linked list in
Python. It supports insertion, deletion, search, forward/backward playback,
shuffle by relinking nodes, and OFF / ONE / ALL repeat modes.

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

The app opens with five sample songs. Double-click a row to select it as the
current song. Use **Add song**, **Delete**, **Next**, **Previous**, **Shuffle**,
or the search box to manage playback.

## Run tests

```bash
python -m pytest -q
```

## Project structure

```text
app.py                 Tkinter desktop UI
playlist.py            Doubly linked list model
tests/test_playlist.py Pytest coverage
docs/ALGORITHMS.md     Operation costs and shuffle algorithm
PROJECT_REPORT.md      University project report
screenshots/README.md  Screenshot capture instructions
```

See [PROJECT_REPORT.md](PROJECT_REPORT.md) and [docs/ALGORITHMS.md](docs/ALGORITHMS.md)
for the design and complexity discussion.
