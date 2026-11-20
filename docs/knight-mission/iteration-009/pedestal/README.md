# Pedestal walnut at checkpoint 009

Black candidate 2 shows short dark pores and fine, flowing grain on the front of the turning. Checkpoint 008 carried much of that pattern, but it blended together at the saved camera distance. The 009 trial restores high-frequency modulation in warm midtones. Where the surface turns away, a continuous wood field uses the texture from a quiet patch of the same pedestal. Its coordinates follow the three-dimensional turning around the entire base.

[Fixed-camera crop](fixed.png) · [Actual model profile](profile.png) · [Rear control](rear.png)

The fine variant favors small pores over medium mottling. At full strength it made the grazing highlights on the profile look pitted. The accepted trial interpolates **68%** from the existing pigment to that variant in 8-bit display RGB. Only the pedestal pixels change. The chest edit occupies separate UV islands. Lighting and geometry come from the native Blender scene.

## Replay

With Python, NumPy and Pillow installed, run the following from the repository root. The script loads the accepted 008 mesh, original pigment and selected image from commit `39a1219`. It works in a temporary directory and writes into your nominated output.

```sh
python3 docs/knight-mission/iteration-009/pedestal/replay.py --repo . --out /tmp/knight-pedestal-replay
```

The two outputs are `fine.png`, the full-strength detailed test, and `pigment.png`, the exact 68% pedestal treatment on the 008 atlas. Pass the independently reconstructed 044 chest atlas with `--chest PATH` to reproduce the full 044 texture. To replay from an extracted 008 checkout, use `--assets PATH/TO/assets/knight` in place of `--repo .`. The script checks the hashes of every input, the fine RGB result and the final RGB result. [Input and output hashes](inputs.json) · [Surface isolation check](fine-uv-scope.json)

The original trial’s fixed source render is included because a fresh Blender render can differ slightly in denoising. Its native view and mesh metadata take their values from the parent trial. The depth check, finite grain field and 68% blend are deterministic.
