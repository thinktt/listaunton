# Source pixel interpretation

At five sampled pixels, Blender byte-image pixels equal Pillow source RGB divided by 255 (within float precision). Example (483,880): source (161,69,25), Blender (.63137257,.27058825,.09803922). The inverse AgX path therefore receives encoded display values as intended. This check rules out that specific suspected double-transfer bug; it does not validate the approximate inverse BSDF model or prove recovered albedo.
