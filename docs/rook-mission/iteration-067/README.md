# Neck visibility and pigment diagnosis

The curved front-neck stripe is present in the pigment atlas, not geometry. The older source completion folded camera-projected pigment around unseen surfaces. Seven BVH samples per neck triangle conservatively protect an entire triangle if any sample is visible. This is an approximate visibility classifier, verified with actual renders. Hidden-only repairs preserve the fixed image within one RGB code level but leave the front stripe, showing that protecting all reference-visible pigment prevents this particular repair. Whole-neck studies remove the stripe but change reference-visible grain. No model promoted.

Reproduce with scripts/rook/neck_visibility.py against checkpoint 066. See 068–071 for actual comparisons, not merely the mask.
