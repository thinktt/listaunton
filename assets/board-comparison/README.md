# Board comparison

These two 659 × 202 images are screenshots supplied by Toby on 2026-11-13:

- `original-lineup.png` shows the original Lichess pieces: black king, black
  queen, white bishop, black knight, black rook and black pawn.
- `empty-board.png` shows the same board area without the pieces.

Their SHA-256 hashes are `8a32cd5aacfa0ec7bfa3eacd4ce3a38efe14a2281d924a5ddd62dd0ae6497227`
and `8c1beb81c5fe4cbd59385046551519c2469d054fca87db8c21278446e6aaab8f`, respectively.

The comparison composites the six current saved Blender renders, each from its
54° reference camera. The king's base is calibrated to approximately 86 pixels
wide in the original screenshot. Other pieces are uniformly scaled to the
current chosen side-view heights relative to the king, then centered on the same
projected foot line. Their widths and silhouettes are not individually fitted
to the screenshot. The soft contact shadows are a browser approximation.

The screenshot and camera angle leave room for interpretation; matching this
view does not establish the hidden shape or true physical dimensions of the
original pieces. Rebuild the page with `python3 scripts/build_set_comparison.py`
after accepted model renders or camera data change.
