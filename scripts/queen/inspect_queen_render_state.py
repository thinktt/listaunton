from pathlib import Path
import bpy,json
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/queen-mission/169-finial-atlas/queen.blend'),load_ui=False)
s=bpy.context.scene
names=['seed','use_animated_seed','samples','use_adaptive_sampling','adaptive_threshold','adaptive_min_samples','use_denoising','denoiser','denoising_input_passes','denoising_prefilter','denoising_quality','denoising_use_gpu','use_light_tree','use_auto_scrambling_distance','scrambling_distance','use_path_guiding','device','glossy_bounces']
props={n:getattr(s.cycles,n,'unavailable') for n in names}
print('RENDER_STATE',json.dumps({'cycles':props,'frame':s.frame_current,'resolution':[s.render.resolution_x,s.render.resolution_y],'persistent_data':s.render.use_persistent_data,'compositor':s.use_nodes}),flush=True)
