# Algorithms and complexity

The playlist's persistent song storage is a doubly linked list. `head`, `tail`,
`current`, and `size` are maintained as the list changes. Search and ID lookup
walk the links; there is no parallel collection used as the playlist store.

| Operation | Time | Extra space | Notes |
|---|---:|---:|---|
| Append | O(n) | O(1) | Duplicate-ID check scans first; link update is O(1). |
| Insert at position | O(n) | O(1) | Traversal starts at the nearer endpoint. |
| Delete by ID | O(n) | O(1) | Lookup scans; unlinking is O(1). |
| Search title/artist | O(n) | O(1) | Yields matching nodes one at a time. |
| Forward/backward display | O(n) | O(1) | Visits each node once. |
| Next/previous | O(1) | O(1) | Neighbor link or repeat wrap. |
| Shuffle | O(n) expected | O(n) | Shuffles temporary node references, then relinks nodes. Song data is not swapped. |
| Reverse | O(n) | O(1) | Swap `prev` and `next` on each node, then exchange `head` and `tail`. |
| Sort | O(n log n) | O(n) | Sort temporary node references, then relink existing nodes. |
| Save/load JSON | O(n) | O(n) | Serialize song fields or rebuild nodes and links from saved records. |

## Shuffle procedure

1. Walk from `head` and collect references to each existing node.
2. Randomize that temporary sequence.
3. Set `head` and `tail` from its endpoints.
4. Reassign each node's `prev` and `next` to its neighbors.

This preserves node identity and the `current` node while ensuring each node
appears exactly once in the resulting chain.

## Reverse procedure

1. Visit each node and exchange its `prev` and `next` references.
2. Exchange the playlist's `head` and `tail` references.

The `current` pointer still refers to the same node object; only its neighbors
change.

## Sort procedure

1. Collect references to the existing nodes in temporary storage.
2. Sort those references by title, artist, or duration.
3. Reassign `head`, `tail`, `prev`, and `next` to reflect the new order.

This operation changes list order without copying or swapping song records.
