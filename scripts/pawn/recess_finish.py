"""Grade the narrow turned recess in local lathe coordinates across all azimuths."""
from pathlib import Path
import argparse
import json
ROOT = Path(__file__).resolve().parents[2]


def stain(source, measurement, config, output):
    import numpy as np
    from PIL import Image
    from derive_wood import display, linear
    profile = np.load(measurement / "meridian.npy")
    source_rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32) / 255
    v = 1 - (np.arange(len(source_rgb)) + .5) / len(source_rgb)
    z = np.interp(v, profile[:, 0], profile[:, 2])
    knots, gains = np.array(config["pigment_gain"]).T
    gain = np.interp(z, knots, gains)
    pigment = linear(source_rgb) * gain[:, None, None]
    Image.fromarray(np.uint8(np.rint(255 * np.clip(display(pigment), 0, 1)))).save(output)


def add_finish(material, config):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    coords = nodes.new("ShaderNodeTexCoord")
    split = nodes.new("ShaderNodeSeparateXYZ")
    links.new(coords.outputs["Object"], split.inputs[0])
    mask = nodes.new("ShaderNodeValToRGB")
    mask.name = "Polish accessible to the lathe groove"
    ramp = mask.color_ramp
    ramp.interpolation = "EASE"
    knots = config["gloss_gain"]
    for index, (z, gain) in enumerate(knots):
        point = ramp.elements[0] if index == 0 else ramp.elements[-1] if index == 1 else ramp.elements.new(z)
        point.position = z
        point.color = (gain, gain, gain, 1)
    links.new(split.outputs["Z"], mask.inputs["Fac"])
    for name in ("Coat Weight", "Specular IOR Level"):
        socket = shader.inputs[name]
        assert not socket.is_linked
        factor = nodes.new("ShaderNodeMath")
        factor.operation = "MULTIPLY"
        factor.label = name + " in the recessed cut"
        factor.inputs[1].default_value = socket.default_value
        links.new(mask.outputs["Color"], factor.inputs[0])
        links.new(factor.outputs[0], socket)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    stain(ROOT / cfg["base_texture"], ROOT / cfg["measurement"], cfg, ROOT / cfg["texture"])
