# USD scenes

The competition scene is built programmatically in `scripts/run_isaac_fr3.py`
(FR3 articulation + obstacles matching `kit_mp_scenes/competition.yaml`), so no
binary `.usd` is committed here.

To save a reusable scene instead:

1. Launch Isaac Sim, run `run_isaac_fr3.py --headless` or open the GUI.
2. Adjust obstacles / lighting as desired.
3. **File → Save As** → `fr3_scene.usd` in this folder.
4. Load it next time with `add_reference_to_stage(usd_path=".../usd/fr3_scene.usd")`.

Keeping the scene as code (the default) keeps it version-controllable and in sync
with the CPU-track scene definition.
