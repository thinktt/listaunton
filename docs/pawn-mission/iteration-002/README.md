# Pawn checkpoint 002

This lighting pass starts from the first accepted walnut pawn (51743ba).
The three marks on the head of the original black sprite recur in the
selected enlargement. Checkpoint 001 reproduced their locations but added
a fourth reflection and rendered smooth spots over the grain.

Trial 007 couples shallow pigment relief to the body and varnish normals.
Trial 008 sizes elliptical area lights from the change in reflected surface
rays across each intended highlight. Trial 009 confines those beams and
adds adjustable cores and adjacent base reflectors. All emitters are ordinary
Cycles area lights. Energies are fitted from isolated, colored material
responses through the saved AgX display transform. Actual full renders and
side inspections determine acceptance. The diffuse atlas stays at v2.

The head now has three textured glints. Socket and base reflections are
closer to the reference but the lower flared base has two broad patches and
the stem has a thin unwanted vertical streak. The foot recess is too bright.
Both originals and the selected reference support a darker groove. Its
center should be examined before fitting more lights. The trial scorecard
records individual gains and regressions.

To reproduce the accepted scene from tracked inputs:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/fit_lighting.py -- docs/pawn-mission/iteration-002/reproduction.json
```

The saved material reopens with verified packed pixels. The archived control
model, relief parameters and fitted light descriptions reproduce the fixed
render to at most one RGB level with identical alpha. The evaluated mesh
and UV binary are byte-identical to checkpoint 001. The small IoU difference
comes from different render sampling. The standalone review offers fixed,
rotating and registered side comparisons using this same model.
