"""Unit tests for linked playlist operations and boundary behavior."""

import random

import pytest

from playlist import Playlist, RepeatMode, SongNode


def song(number):
    return SongNode(str(number), f"Song {number}", f"Artist {number}", 180)


def playlist_with_songs(count=3):
    playlist = Playlist()
    for number in range(count):
        playlist.add_song(song(number))
    return playlist


def test_insert_positions_and_bidirectional_traversal():
    playlist = playlist_with_songs(2)
    playlist.insert_song(song(10), 0)
    playlist.insert_song(song(11), 2)
    assert [node.song_id for node in playlist.iter_forward()] == ["10", "0", "11", "1"]
    assert [node.song_id for node in playlist.iter_backward()] == ["1", "11", "0", "10"]
    assert playlist.validate()


def test_insert_invalid_position_and_duplicate_id():
    playlist = playlist_with_songs(1)
    with pytest.raises(IndexError):
        playlist.insert_song(song(2), 3)
    with pytest.raises(ValueError):
        playlist.add_song(song(0))


def test_delete_head_tail_current_and_missing():
    playlist = playlist_with_songs()
    assert playlist.delete_song("0").song_id == "0"
    assert playlist.head.song_id == "1"
    playlist.current = playlist.tail
    assert playlist.delete_song("2").song_id == "2"
    assert playlist.current.song_id == "1"
    assert playlist.delete_song("missing") is None
    assert playlist.validate()


def test_delete_last_song_clears_all_pointers():
    playlist = playlist_with_songs(1)
    playlist.delete_song("0")
    assert (playlist.head, playlist.tail, playlist.current, playlist.size) == (None, None, None, 0)


def test_search_matches_title_or_artist_case_insensitively():
    playlist = playlist_with_songs()
    assert [node.song_id for node in playlist.search("ARTIST 1")] == ["1"]
    assert [node.song_id for node in playlist.search("song")] == ["0", "1", "2"]


def test_next_previous_and_repeat_off_boundaries():
    playlist = playlist_with_songs(2)
    assert playlist.current.song_id == "0"
    assert playlist.next_song().song_id == "1"
    assert playlist.next_song() is None
    assert playlist.previous_song().song_id == "1"
    assert playlist.previous_song().song_id == "0"
    assert playlist.previous_song() is None


def test_repeat_one_and_all():
    playlist = playlist_with_songs(2)
    playlist.set_repeat_mode(RepeatMode.ONE)
    assert playlist.next_song() is playlist.current
    playlist.set_repeat_mode("ALL")
    playlist.current = playlist.tail
    assert playlist.next_song() is playlist.head
    playlist.current = playlist.head
    assert playlist.previous_song() is playlist.tail


def test_shuffle_relinks_same_nodes_and_preserves_links():
    playlist = playlist_with_songs(8)
    original_nodes = {id(node) for node in playlist.iter_forward()}
    current = playlist.current
    playlist.shuffle(random.Random(13))
    nodes = list(playlist.iter_forward())
    assert {id(node) for node in nodes} == original_nodes
    assert len(nodes) == len(original_nodes)
    assert playlist.current is current
    assert nodes[0].prev is None and nodes[-1].next is None
    for left, right in zip(nodes, nodes[1:]):
        assert left.next is right and right.prev is left
    assert playlist.validate()


def test_empty_singleton_shuffle_and_navigation():
    empty = Playlist()
    empty.shuffle()
    assert empty.next_song() is None and empty.previous_song() is None
    singleton = playlist_with_songs(1)
    only_node = singleton.head
    singleton.shuffle(random.Random(1))
    assert singleton.head is singleton.tail is only_node
    assert singleton.next_song() is None
    singleton.set_repeat_mode("ALL")
    assert singleton.next_song() is only_node


def test_reverse_relinks_nodes_and_preserves_current_identity():
    playlist = playlist_with_songs(4)
    original_nodes = list(playlist.iter_forward())
    playlist.current = original_nodes[2]
    playlist.reverse()
    assert list(playlist.iter_forward()) == list(reversed(original_nodes))
    assert list(playlist.iter_backward()) == original_nodes
    assert playlist.current is original_nodes[2]
    assert playlist.validate()


def test_sort_relinks_nodes_without_replacing_them():
    playlist = playlist_with_songs(4)
    nodes = {id(node) for node in playlist.iter_forward()}
    playlist.current = playlist.tail
    playlist.sort_by("artist")
    assert [node.artist for node in playlist.iter_forward()] == [
        "Artist 0", "Artist 1", "Artist 2", "Artist 3"
    ]
    assert {id(node) for node in playlist.iter_forward()} == nodes
    assert playlist.current.song_id == "3"
    assert playlist.validate()
    with pytest.raises(ValueError):
        playlist.sort_by("album")
