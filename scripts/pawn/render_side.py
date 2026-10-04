"""Inspect head seating from level profile without changing the saved camera."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(r/'models/pawn/pawn-rebuilt.blend'))
s=bpy.context.scene;c=s.camera;target=Vector((0,0,1.35));c.location=(0,-12,1.35);c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.shift_x=0;c.data.shift_y=0;c.data.ortho_scale=3.5
s.render.resolution_x=640;s.render.resolution_y=640;s.cycles.samples=24;s.render.filepath=str(r/'assets/pawn/side-seating.png');bpy.ops.render.render(write_still=True)
