# Round 6B

The original and black candidate 2 leave a discernible opening between the jaw and breast. The accepted model filled part of that opening and showed a pinched cheek at either end of the eye. This version reshapes the editable head and neck and its two construction meshes.

## Chest

The breast recedes up to 0.157 model units in the unposed anterior direction. The movement falls away laterally in front of the two diagonally carved shoulder bevels. At fixed-view row 545 the chest edge moves from x622 to x602. The registered original is x600 and black 2 is x597.

| Fixed-view rows | Target | Parent mean error | 6B mean error |
| --- | --- | ---: | ---: |
| 540–580 | Original | 18.49 px | 4.05 px |
| 540–580 | Black 2 | 22.44 px | 8.00 px |
| 581–655 | Original | 11.24 px | 7.79 px |
| 581–655 | Black 2 | 14.16 px | 10.71 px |

The lower breast retains more fullness than the references. Keeping the diagonal bevels reduced the chest-edge improvement by 0.37 px in the upper band compared with moving the whole flank. With identical lights the narrower secondary highlight returns to a mean luma of 136 along the reference trace, compared with 93 in the initial cut and 157 in black 2. A small textured glint remains near its lower end. See `accent-comparison.png` with `Full` identifying the delivered version.

## Eyes

Both lid ends now roll into the same fair cheek surface beyond the aperture. The lower lip turns upward slightly before the noseward corner. The separate inset floor, upper eyelid plane and studio reflections retain the parent integration. Direct side rays on the upper skull, after removing its twist, give a near/far aperture overlap of 99.85%, versus 99.50% for the parent. The exposed near inset covers 1,364 samples, versus 1,401. Front-to-rear eye length shortens slightly while the brow-side and cheek-side limits stay at the same height. See `bilateral-eyes.png` for the physical depth on both sides and `carving-study.png` for the two walnut views. The inherited lower-lid reflection still appears fainter than the references in the registered view.

The sharp mane and its poll facet use the accepted geometry, as do the ears, eye insets and turned base. The camera, lights, pigment, UVs, varnish and modeling topology match the parent.

## Outputs and reproduction

The source parent is `parent.blend` with SHA-256 `8a53403942a3e5bea1df92e3f28c9bfd5d80c61a1026a03549f1c21fd4c96cb6`. The delivered `knight.blend` has SHA-256 `c8de5dbdd6019599b74b2f9d12b364b00caba7f38ea28dc348d24a2fdd365254`. Reopening the saved model generated the fixed and registered side at 144 Cycles samples. The image hashes are in `parameters.json`.

From the candidate directory with Blender 5.2 and the external Python runtime available, run:

```powershell
blender -b --python-exit-code 1 -P carve.py -- --build 1 .157 1 --studio --parent-flat --orbit
blender -b --python-exit-code 1 -P verify.py
blender -b --python-exit-code 1 -P bilateral_eye.py -- ../../.. parent.blend eyes-parent
blender -b --python-exit-code 1 -P bilateral_eye.py -- ../../.. knight.blend eyes-B
python -B plot_bilateral_eye.py . parent B
python -B review.py
```

The optional crop comparison runs `carve.py` with `--accents-test --anterior-test` in two separate invocations, then `python -B accents.py`. The source stores all variant settings and uses the same parent lights for each crop.
