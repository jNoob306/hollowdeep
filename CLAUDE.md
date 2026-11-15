# Hollowdeep: project guide for Claude Code

> **First session, required:** after you have read and reviewed the project files the user gives you (`index.html`, `HANDOFF.md`, `docs/ASSETS.md`, `tests/`) and reported back on them, **remind the user to set up the automated asset pipeline**. Walk them through the "What the user needs to provide" checklist in `HANDOFF.md` → "Automated asset pipeline". Do this before starting other work, unless they say to skip it. Once the setup is done, delete this note from `CLAUDE.md` so the reminder doesn't repeat.

Hollowdeep is a 3D roguelike extraction dungeon crawler that runs in the browser. You enter procedurally generated maze caves, mine and loot, and must climb out of an exit shaft to keep your backpack. Dying loses it. Materials are used to craft gear at camp.

It is hosted as a **static Hugging Face Space** (`README.md` holds the Space config front matter). Read `HANDOFF.md` for the history, decisions and next steps.

## Files

- `index.html` is the whole game: HTML, CSS and one `<script type="module">`. Three.js 0.160.0 comes from jsDelivr through an import map. There are no other runtime files yet.
- `README.md` is the Space config and player-facing description. Keep its front matter (`sdk: static`, `app_file: index.html`).
- `docs/ASSETS.md` lists every art, sound and texture asset, with generation prompts, the free open-source pipeline and the expected file names.
- `tests/` holds headless logic tests that run without a GPU (see Testing).

## Hard constraints from the user

- Free and open-source tools only. No Adobe and no Mixamo. The asset pipeline is FLUX.1 schnell, then TRELLIS.2, then Mesh2Motion with the Quaternius CC0 animations, plus Blender.
- The target hardware is a **thin laptop with integrated graphics** and possibly an Xbox One running the Edge browser. Keep it WebGL2 through Three.js, not WebGPU-only. Keep draw calls and lights low.
- The **Xbox controller is the primary input**. Keyboard and mouse must keep working. Touch controls still exist but are low priority.
- Characters must stay humanoid (2 arms, 2 legs, 1 head) so free auto-riggers work. Extra parts such as bells and lanterns are rigid attachments animated in code.
- User preference: when you update code, end the response with a one-line summary of the change and attach the updated project zip.

## Code map (sections in `index.html`, in order)

1. **Util and RNG.** `mulberry32`, value noise, seed parsing. The seed is shown in base 36.
2. **Data tables.** `MATS`, `WEAPONS`, `ARMORS`, `UPGRADES`, `ENEMIES` (attack definitions use windup, active and recover phases), `NODE_W`, `SPAWN_W`, and the per-depth palettes. Add content here.
3. **Level generation.** `generateLevel` retries `tryGen` on a 44x44 grid (`GW`, `GH`) of 3 m cells (`CS`). It carves a jittered 10x10 depth-first maze with 13% extra loops, 3 chambers and corner rounding, then:
   - flood-fills and connects regions;
   - places the start (level 1 is always the cave mouth on the top edge, entry only);
   - places the descent, 1 to 3 exit shafts favouring dead ends, resource nodes, chests and enemies, plus the Bellman from depth 2;
   - adds the boss cavern on depth 4.

   Generation is deterministic per seed. Don't use `Math.random` in generation.
4. **World queries.** Grid collision (`blocked`, `moveCircle`), `floorH` and `ceilH` from noise, and `los`.
5. **Save and load.** `localStorage` key `hollowdeep_save`, version 1, wrapped in try/catch.
6. **Renderer and mesh building.** `buildLevel` merges floor, ceiling and noise-displaced wall sheets per 11x11-cell chunk into vertex-coloured meshes. Exit shafts get a light cone and a ladder, rope or roots. Entity models are built from primitives (`buildPlayerModel`, `buildEnemyModel`).
7. **Audio.** Everything is synthesized with Web Audio. The Bellman's bell runs through a lowpass filter and an HRTF `PannerNode`; `updateListener` follows the camera.
8. **Input.** Keyboard and mouse (pointer lock), touch, and the Gamepad API in standard mapping (Xbox names) all feed one `input` object plus `pressed` flags.
9. **Combat, player, lock-on, enemy AI** (state machines and a BFS flow field toward the player), and **the Bellman** (`updateBellman`, `makeNoise`, `fieldTo`).
10. **Run flow, fixed 60 Hz step, camera** (over the shoulder, with collision pull-in), **render-side animation, HUD, map, camp and crafting UI.**

`window.__hd` is a debug handle used by the tests. Keep it, or update the tests if you change it.

## Testing

```bash
pip install playwright && playwright install chromium   # once
./tests/run_tests.sh            # or: CHROME=/path/to/chrome ./tests/run_tests.sh
```

`make_stub.py` swaps Three.js for a no-op proxy, so game logic runs headless. The tests check:

- generation (connectivity, determinism, exit counts, Bellman spawns);
- the core loop (move, roll, attack, mine, descend, extract, craft, save);
- Xbox controller input through a mocked `navigator.getGamepads`;
- the boss, death, and the Bellman (hunt, chase, fatal grab, roll dodge, stagger, staying out of the boss cavern).

**Rendering and audio have never been seen or heard.** The build environment had no GPU and no CDN access. Verify visuals in a real browser: serve the folder (`python3 -m http.server`) and open it in Chrome or Edge.
