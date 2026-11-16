# Handoff: Hollowdeep (from Claude app chat, 2026-11-15)

## Current state

The game is playable end to end: camp → cave → exit shaft or death → camp → crafting → next run. Version 2 added maze caves and the Bellman. Every piece of logic passes `tests/run_tests.sh`. **Nobody has seen it render or heard its audio yet**, so the first job is a real-browser check.

### Features in the code

- **Caves:** 4 depth levels of seeded maze caves. Level 1 starts at the cave mouth, which is entry only. You go down through descent holes; there is no way back up.
- **Exit shafts:** 3, 2, 2, then 1 per level, favouring dead ends. They are found by drifting dust that flows toward them, a cone of daylight, and wind audio that grows louder near them. Extracting is a 3-second climb that taking damage interrupts.
- **Combat:**
  - light and heavy attacks, a roll with invincibility frames, blocking that drains stamina, and a flask;
  - lock-on with target switching, telegraphed enemy attacks, hit stop and screen shake;
  - an equip-load system that changes roll speed.
- **Enemies:** 5 placeholder types (crawler, swarm, spitter, shield brute, elite) and the final boss, the Hollow Warden. The boss has 2 phases and 4 attacks: sweep, slam, charge and a phase-2 projectile volley.
- **The Bellman (stalker):**
  - It appears from depth 2, is unkillable, and heavy attacks only stagger it.
  - It hunts by noise. Mining is loudest (radius 26), then chests (18), combat (16), blocking (14), running (9) and rolling (8).
  - It chases on sight within 22 m and a frontal cone. It walks at 2.9 m/s, hunts at 3.6 and chases at 4.3; the player runs at 5.2.
  - Its grab is fatal, with a 0.95 s wind-up during which the bell rattles; a roll dodges it.
  - Its bell rings each step through a 3D panner and sounds muffled when there's no line of sight. It goes silent while listening.
  - It stays out of the boss cavern.
- **Sneaking:** hold C, or push the controller stick lightly.
- **Camp:** a stash, crafting (8 weapons, 4 armours, upgrades for flask charges, flask potency, backpack and torch), gear equipping, run stats, and seeds (custom or the last one). Saved to localStorage.
- **Input:** Xbox controller (also navigates menus), keyboard and mouse, and touch.

### Xbox mapping

- **Movement:** left stick moves (push lightly to sneak), right stick turns the camera.
- **Actions:** RB light attack, RT heavy attack, B roll, LB block, X flask, A interact.
- **Lock-on:** R3 locks on; flick the right stick or press D-pad left/right to switch target.
- **Other:** View or Y opens the map, Menu pauses.

## Model loader (added in Claude Code)

All ten characters are generated, rigged and in `assets/`. The game loads eight of them (the Crystal Warden and Lantern Mother have models but no fight yet). See `CLAUDE.md` for how the loader works and `TODO.md` for what is left.

The shared skeleton has these 21 clips: `Idle_Loop`, `Walk_Loop`, `Jog_Fwd_Loop`, `Sprint_Loop`, `Roll`, `Hit_Chest`, `Death01`, `Consume`, `Chest_Open`, `Jump_Start`, `Jump_Loop`, `Jump_Land`, `Dance_Loop`, `Swim_Fwd_Loop`, `Swim_Idle_Loop` and six `Pistol_*` clips. There are no melee, block, climb, mining or sneak clips, so the game fakes those with arm swings.

## Decisions made with the user

- **Look:** an over-the-shoulder, Souls-like third-person camera, not top-down.
- **Hardware:** a thin laptop, and maybe an Xbox One in the Edge browser. Don't depend on WebGPU. Phones are no longer a target.
- **Assets:** free and open-source tools only (no Adobe or Mixamo). Every character is humanoid for auto-rigging. Weapons are separate props attached to the hand bone.
- **Maps:** maze-like caves with loops, so the player can escape the Bellman.
- **Planned roster** (see `docs/ASSETS.md`; still placeholders in code):

  | Planned asset | Replaces in code |
  | --- | --- |
  | Feral Delver | `crawler` |
  | Hollow Miner, in groups | `swarm` (the mites) |
  | Druid Shaman (replaced the Spore Hermit) | `spitter` |
  | Chain Jailer | `brute` |
  | Pale Stalker | `elite` |

- **Planned bosses:**
  - The Crystal Warden at depth 2 and the Lantern Mother at depth 3. **Neither exists in code yet.**
  - The Ossuary King at depth 4 replaces the Hollow Warden. The heart drop and the Wardenbane recipe can be renamed to match.

## Next steps, in priority order

1. **Real-browser check.** Run `python3 -m http.server` in the project folder and open it in Chrome on the user's thin laptop. Check:
   - frame rate;
   - lighting and readability, since the cave may be too dark or too bright (tune the hemisphere light, torch intensity and fog);
   - camera collision in 6 m corridors;
   - how loud the bell is and its panning direction;
   - whether the Bellman chase feels fair.
2. **Quality settings** (Low, Medium, High, chosen automatically and changeable in a menu). Scale the pixel ratio, dust count, light count, shadows and fog distance.
3. **A GLB asset loader.**
   - Add `"three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"` to the import map and use `GLTFLoader` with `AnimationMixer`.
   - Look for `assets/<name>.glb` (file names in `docs/ASSETS.md`) and fall back to the current primitive models when a file is missing.
   - Map clip names to states (idle, walk, run, roll, attacks, block, hit, death, climb) with crossfades.
   - Attach `weapon_*.glb` to the right-hand bone.
   - The Bellman's bell and the Lantern Mother's lanterns are rigid props animated in code.
4. **Visual pass for integrated graphics:**
   - triplanar procedural rock (noise normal perturbation in a custom `MeshLambert`/`MeshStandard` `onBeforeCompile`);
   - cheap bloom on glowing crystals and fungus, wet specular, light shafts at exits;
   - optional CC0 textures (`tex_*.jpg`) when present.
5. **Bosses:** add the Crystal Warden and the Lantern Mother at depths 2 and 3 (guaranteed arenas like the depth-4 one), and rename the depth-4 boss to the Ossuary King.
6. **Sound files:** load `sfx_*.ogg` and `amb_*.ogg` from `assets/` when present, and keep the synthesized fallbacks.
7. **Smaller items:**
   - flask-drinking animation fallback;
   - decide whether touch controls stay;
   - possibly have the Bellman react to the player's torch.

## Automated asset pipeline (to set up with the user)

The user wants the asset work in `docs/ASSETS.md` automated rather than done by hand. Everything must use free, open-source tools or CC0 sources. Build it as scripts in `tools/` that write into `assets/`, and keep a log of what was downloaded and from where (`assets/CREDITS.md`, even for CC0).

### What the user needs to provide (walk them through this)

- [ ] **A Hugging Face access token** with read and inference permissions, from Settings → Access Tokens. They have a Pro account, which gives more ZeroGPU time.
- [ ] **A Freesound API key** from a free account (freesound.org → API → apply for a key).
- [ ] **Blender** installed (free). Note the path to the `blender` executable.
- [ ] **Python 3** with `pip install gradio_client requests python-dotenv`.
- [ ] Permission for Claude Code to run commands and download files.
- [ ] Tokens stored in a local `.env` file (`HF_TOKEN=…`, `FREESOUND_KEY=…`) that is added to `.gitignore` and **never** uploaded to the Space. They should not paste tokens into chat.

### Scripts to build

1. **`tools/fetch_textures.py`**
   - Use the public Poly Haven API (`api.polyhaven.com`), falling back to ambientCG.
   - For each texture in `docs/ASSETS.md`, search, pick a fitting CC0 texture, and download the 1K colour, normal and roughness maps.
   - Save them as `assets/tex_<name>_color|normal|rough.jpg`.
   - No key is needed.
2. **`tools/fetch_sounds.py`**
   - Use the Freesound API (APIv2 text search, filtered with `license:"Creative Commons 0"`) and the HQ OGG/MP3 previews, which need only the API key.
   - Trim, fade, normalize, convert to mono OGG with ffmpeg, and keep files under 10 s except loops.
   - Kenney audio packs (CC0 zip downloads) are a second source.
   - Let the user audition a shortlist for the important ones, the bell sounds especially.
3. **`tools/generate_models.py`**
   - For each entry, call FLUX.1 schnell on Hugging Face through `gradio_client` with the prompt from `docs/ASSETS.md`, and save the image.
   - Call the TRELLIS.2 Space (`microsoft/TRELLIS.2`) with that image and save the GLB.
   - Show the images to the user and get approval before the 3D step: it costs GPU quota, and a bad image means a bad model.
4. **`tools/rig_character.py`**, run headless as `blender -b -P tools/rig_character.py -- in.glb out.glb`. This replaces the manual Mesh2Motion step.
   - Import the TRELLIS mesh, then decimate it to the triangle budget for its type.
   - Import the Quaternius Universal Animation Library skeleton (CC0, free standard version from quaternius.com or itch.io).
   - Scale and align that skeleton to the T-pose mesh using bounding-box proportions (head, shoulders, hips, knees).
   - Parent the mesh with automatic weights.
   - Copy in the needed clips (idle, walk, run, roll, attacks, block, hit, death, and so on). They play directly because the skeleton is the same.
   - Export one GLB with all clips.
   - Render a few preview frames per character (idle, walk, attack) for the user to approve. Expect some re-runs, for bad elbows or skirts and capes deforming badly.
5. **Weapons and props** run through `generate_models.py` and a decimate-only Blender script, with no rig.

Order of work: textures and sounds first (cheap, no GPU quota), then the Delver as a pilot through the full model pipeline, then the rest in batches.

## Gotchas

- `tests/make_stub.py` rewrites the jsDelivr Three.js URL with a regex. Keep the import map URL format, or update the regex.
- The tests read internals through `window.__hd`. If you rename state, update `tests/*.py`.
- Text ids are not relevant here. Game data is plain JS objects, and content is data-driven.
- Pointer lock: losing it pauses the game, by design.
- The Hugging Face Space embeds the app in an iframe. If the gamepad or pointer lock don't work there, use the Space's direct `*.static.hf.space` link. This is untested.
- Hugging Face upload: put `index.html` and `README.md` at the Space root, and assets in `assets/`.
