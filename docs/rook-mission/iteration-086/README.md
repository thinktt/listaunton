# Local foot finish studies 084-086

Accepted checkpoint 078 and public assets are unchanged. These experiments build on isolated lighting study 082 as a controlled diagnostic, not a revived public checkpoint.

084 changes only foot-band roughness from .25 to .12 and coat roughness from .15 to .06. The mask is a smooth world-height band: rises over .15-.18, remains full through .24, falls to zero at .27. 085 additionally passes the existing shallow wood bump into Coat Normal within the same band. It does not invent or paint a reflection. Pigment, geometry and camera remain unchanged.

086 uses .08/.03 roughness with no coat bump, .04 light height, left 3 W/right 200 W. The narrower real emitter and sharper surface reduce the right glint thickness but lose brightness. At x560/x600 the reference has 3/3 pixels above mean RGB160; 082 has 8/8, 084 has 6/6, 085 has 6/7, and 086 has 5/4. Reference peaks are 232/235.3; 086 is 216.3/206.3. This threshold count is a local diagnostic, not a full reflection-width or match metric. Peak placement is still off by up to two pixels.

84 and 85 are rejected for public promotion. 86 is a promising intermediate, retained for further fitting rather than accepted. The full comparison still exposes cavity/rim highlight differences, a dark shaft and baked pigment illumination; the foot is not the only unresolved defect. The side view retains coherent geometry but contains dark pigment bands and an overly smooth base reflection. All five categories are recorded separately; the one-point provisional lighting gain is subjective and does not change the accepted score.

## Validation and reproduction

Run foot_finish.py for 084/085 and foot_finish_narrow.py for 086 in Blender background mode. They require exact 082 SHA 53e69c58d24339eb28fea503e0140f0420d6a52543494eecbd17972ce84962df. Render with render_saved_trial.py, compare with compare_foot_finish.py and audit_mission.py. All models receive saved receiver validation; 085 receives full geometry/material validation against accepted 078. Scope validation covers all three; it verifies original material nodes/default inputs/packed images/links, world and lights, allowing declared foot-light changes in 086. The final validator also limits added shader outputs to Roughness, Coat Roughness and optional Coat Normal. Earlier 084/085 scope reports precede that extra output restriction; the builder source specifies their connections. These checks do not prove visual fidelity.

086 has independent saved fixed/profile/rear renders, with unchanged source hash after alternate cameras. Fixed and side images were inspected. No new neutral geometry render or public viewer rebuild is claimed: geometry is unchanged and no trial is promoted. Reproduction relies on preserved 082 build inputs, which can be regenerated using foot_flanks_refined.py from checkpoint 078.

Next: tune emitter height and power around the sharper 086 finish while checking both brightness and width; examine whether the remaining glint breakup needs a subtler surface-normal treatment. Do not replace the accepted model until saved validation and fixed/side/viewer synchronization are complete.
