# Reproducing the rejected base-finish studies

Start from `history/bishop-mission-015/bishop-rebuilt.blend` and its adjacent
atlas. Read `reproduction.json` for the commands, source hashes and prerequisite
surface capture. Run in an isolated copy. These studies do not replace the
accepted bishop or change its reference registration.

The 127–129 image sheets compare real BSDF crops at fixed registration. Their
provisional lights and roughness fields are not full model proposals. Study 130
separates pigment and relief for diagnosis; its emission pass is not a beauty
render. Study 131 captures actual response fields for the two rejected atlas
trials. Trials 132 and 133 each save/reopen their scene and render at 512 samples.
Their full-image comparisons, atlas data and measurements are retained here.

The initial probe script rejected Blender's compressed `custom_normal`
attribute. The corrected splitter reconstructs actual corner-normal vectors
and checks their error directly; the successful terminal run is the evidence
recorded here. The .19-height receiver admitted foot spill and is rejected;
the subsequent .42-height receiver is still only an unsaved diagnostic.

To compare the diagnostic glint images, crop the unchanged 1254px frames at
`[460, 920, 690, 1090]`. The saved `isolation-comparison.png` enlarges those
crops uniformly by two, with labels; it does not alter the model or reference.

The public checkpoint remains 015. Rejected scenes have no approval for
promotion, and no model/texture/light changes are pending acceptance.

The local `.gitattributes` preserves measurement JSON bytes, including their
original line endings, so recorded hashes remain valid after checkout.
