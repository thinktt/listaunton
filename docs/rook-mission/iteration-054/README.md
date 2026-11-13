# Lower pigment surface probe

Mapped fixed-camera pixels to actual saved-model triangle UVs and normals without changing the model. Defects around (483,820), (450,870), and (483,917) lie in the pigment atlas. Atlas samples include [98,16,7] at the upper patch and [45,7,7] at the lower patch. Nearly clipped blue values and red bands occur in pigment before new lighting. The lower rendered brightness is already close to the reference, so an indiscriminate brightness repair is inappropriate. This is a diagnostic, not a candidate or new score. Reproduce with scripts/rook/probe_lower.py.
