# Round 14A · Walnut on the hanging mane

The broad mane face now turns into a single carved hollow at the fixed angle. The surface carries broken, mostly crosswise walnut figure around the rear and onto the opposite flank. The color comes from a continuous three-dimensional billet sampled on the existing mane. Its material coordinates use the model's rest position. Both source images serve only as visual and numerical references.

| Fixed-view measure | Original black | Black 2 | Parent 13A | 14A |
| --- | ---: | ---: | ---: | ---: |
| Relative darkness on the old arc | −8.4% | −3.7% | 26.8% | −6.3% |
| Rear face luminance | 30.7 | 39.9 | 23.7 | 39.5 |
| Inside face luminance | 23.4 | 26.3 | 29.4 | 31.2 |
| True hollow luminance | 9.1 | 9.3 | 7.7 | 9.0 |
| Fine grain contrast | 0.006 | 0.100 | 0.061 | 0.093 |
| Grain direction in the registered image | — | 1.0° | −86.0° | −0.5° |

The relative darkness compares the old line with its two neighboring samples eight pixels away. A negative value places the center above their mean. Emission alone measures 33.6% in the parent and 2.0% in 14A. The interior blade remains about five luminance levels lighter than Black 2. The small source sprite resolves the sweep and the hollow. Its low resolution gives little evidence for pore direction.

At board scale the distinction is a brighter strip of exposed wood behind the single dark cut. On the true reverse the wood reads as a continuous end section. Individual marks break and change direction with the turn. The opposite lip stays legible in the even-light pass. [Registered detail](mane-study.png) · [Fixed and side](pair.png) · [100-pixel board](board.png) · [Five-angle studio, pigment, clay and uniform-light views](all-around.png)

## Native and viewer checks

The reopened scene contains the same mesh, material graph settings, lighting and registered camera as its parent. The standard viewer export produced byte-identical geometry, varnish and camera files, with 156,861 vertices and 288,430 triangles. The fixed and side render alpha channels each match the parent's every pixel. The albedo changes 456,395 texels in the mane and its filtering gutter. Other mesh UVs and their two-texel guard are protected. At 254 duplicated UV vertices on the broad face, the median and 95th-percentile luminance mismatches are 0.50 and 1.82 / 255. A few seam points reach 8.07 / 255. [Atlas footprint](chart.json) · [Boundary samples](seams.json) · [Native comparison](native-check.json) · [Viewer export](export-check.json) · [Alpha comparison](silhouette.json)

| File | SHA-256 |
| --- | --- |
| Frozen knight.blend | a08cb00185833a97345896465de520efe5d3e0532bccfae61fdde8d1bf4cf734 |
| Packed atlas and external pigment.png | c3633caf6a78e89d25cf3cbfe7fc85b19cf50830165d57108663450d6a174ece |
| Reopened 144-sample wood.png | 11555f7e66cdad1cfbad318894e53ffeccaf47f238791c8c7cd5e0fe88f556e9 |
| Reopened 144-sample wood-side.png | 2463d590450044cb283ce34902937a3cf8f6c4b7e2d3b6dfa18c0ebf4bc247d1 |
| Parent release scene | eaecb543e309c713db12fc83888bb2ffc0142686a06917ee6c76d24e7d2b2188 |
| Parent atlas | 1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b |

## Reproduction

The trial folder contains the frozen input scene, atlas and release renders. The staged project supplies its standard rendering and viewer-export scripts. From the trial directory run the following commands in order with Blender 5.2.2 and Python with NumPy and Pillow. Blender serialization can change the scene's binary digest on a fresh save. The external atlas is deterministic.

~~~text
blender -b --factory-startup --python-exit-code 2 --python sampling.py
python billet.py 1.02
blender -b --factory-startup --python-exit-code 2 --python scene.py -- freeze
blender -b --factory-startup --python-exit-code 2 --python scene.py -- render
blender -b --factory-startup --python-exit-code 2 --python scene.py -- turn
blender -b --factory-startup --python-exit-code 2 --python export_check.py
python seams.py
python evidence.py
python pair.py
~~~

The billet uses axial vessels, variable growth increments, mottled pores and a gentle longitudinal tone change. Both flanks share the field. The central back crosses the grain naturally. The fade runs over rest heights 1.82–2.37 at the seat and 4.31–4.76 under the upper poll. The atlas uses the original UV charts, with three texels of filtering space and a paired-edge correction. The unaltered parent remains visible at the ends of the blend. The native mesh and both material files are saved at full precision. [Field and parameters](billet.py) · [UV edge filtering](join.py) · [Image and bake counts](billet.json) · [Appearance measurements](appearance.json)
