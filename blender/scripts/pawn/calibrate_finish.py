"""Render bounded, physical varnish responses and registered surface depth."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from capture_pigment import meridian_samples
from fit_lighting import response
from mission_render import ROOT, BUILD, render, save_json, sha
from polish_trial import open_source


def run(cfg):
    scene, body = open_source(cfg)
    out = BUILD / cfg["measurement"]
    out.mkdir(parents=True, exist_ok=True)
    material = body.data.materials[0]
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    bs = shader.inputs["Roughness"]
    coat = shader.inputs["Coat Roughness"]
    assert not bs.is_linked and not coat.is_linked
    base = bs.default_value
    varnish = coat.default_value
    passes = []
    for suffix, gain in cfg["samples_roughness"].items():
        bs.default_value = base * gain
        coat.default_value = varnish * gain
        target = out / (suffix + ".png")
        render(scene, target)
        passes.append({"name": suffix, "multiplier": gain, "sha256": sha(target)})
    np.save(out / "meridian.npy", meridian_samples(body))
    output = nodes["Material Output"]
    emission = nodes.new("ShaderNodeEmission")
    links.new(nodes.new("ShaderNodeCameraData").outputs["View Z Depth"], emission.inputs["Color"])
    links.new(emission.outputs[0], output.inputs["Surface"])
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    scene.cycles.samples = 12
    scene.cycles.use_denoising = False
    np.save(out / "depth.npy", response(scene, out)[:, :, 0])
    save_json(out / "measurement.json", {
        "source": cfg["source"], "source_sha256": cfg["source_sha256"],
        "reference_sha256": sha(ROOT / "assets/pawn/reference.png"),
        "camera_above_board": 54, "roughness": base, "coat_roughness": varnish,
        "samples": cfg["samples"], "response_passes": passes,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    run(json.loads(args.config.read_text()))
