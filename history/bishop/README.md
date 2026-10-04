# Bishop reconstruction passes

Each archived pass contains its editable radial profile, neutral render, comparison report and original-white boundary overlay. The live builder and model are in `scripts/bishop` and `models/bishop`; history files are evidence, not an alternate build pipeline.

- **01-first-cut:** Established the turned construction and genuine Boolean slit. The initial mitre was too tall behind its finial and the base shoulder intruded into the neck.
- **02-proportions:** Shortened the mitre and lowered the base shoulder. Original-white silhouette IoU reached 0.9738. Internal landmark inspection showed that the socket lip and foot groove still needed adjustment.
- **03-internal-landmarks:** Widened and steepened the slit and adjusted socket, collars and groove. The shoulder rose too far in projection, so the next pass restored its measured contour.
- **Current:** Retains the improved slit and socket, restores the shoulder, and balances the foot groove against the original boundary. Topology, positive volumes, slot ray probes, export hashes and viewer camera regression pass. Original-white IoU is about 0.9626; the selected candidate differs slightly in outline. This metric is not proof of internal or unseen shape.
