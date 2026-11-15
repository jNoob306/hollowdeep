# Hollowdeep: still to do

A running list so nothing gets forgotten. Tick items off as they are done. The longer background for each is in `HANDOFF.md`.

## Waiting on you

- [ ] **Sounds.** Run `tools/fetch_sounds.py` on your laptop (Freesound refuses the cloud session), audition the candidates, then upload the `assets` folder here. Steps: install Python and ffmpeg, put the key in `.env`, then `shortlist`, `pick`, `build`.
- [ ] **Full animation library.** Download the free standard Universal Animation Library from https://quaternius.itch.io/universal-animation-library and upload the zip. The 21 clips we have lack sword attacks, block, climb, mining, sneak, crawl and zombie walks.
- [ ] **Real-browser check on the laptop.** Frame rate, how dark the cave is, bell loudness and direction, whether the Bellman chase feels fair. None of this can be judged from the cloud.
- [ ] **Texture picks.** Look at wet rock (reads as cut stone blocks) and rust (bright orange on pale metal) and say whether to swap them.
- [ ] **Optional tidy-up.** `quaternius.com` is on the environment's allowed list but turned out not to be needed.

## Characters

Image approved by you → 3D model → rigged GLB in `assets/`.

- [x] `player.glb` The Delver (seed 5)
- [ ] `enemy_feral.glb` Feral Delver
- [ ] `enemy_miner.glb` Hollow Miner
- [ ] `enemy_hermit.glb` Spore Hermit
- [ ] `enemy_jailer.glb` Chain Jailer
- [ ] `enemy_stalker.glb` Pale Stalker
- [ ] `stalker_bellman.glb` The Bellman
- [ ] `boss_warden.glb` The Crystal Warden
- [ ] `boss_lantern.glb` The Lantern Mother
- [ ] `boss_ossuary.glb` The Ossuary King

Known flaws to revisit on the Delver: open-toed boots, a wooden handle fused to the left hip, fur collar droops when the arms come down.

## Other assets

- [x] 7 textures (`tex_*.jpg`)
- [ ] 17 sounds (`sfx_*.ogg`, `amb_*.ogg`)
- [ ] 13 weapons (`weapon_*.glb`), no rig, reduce only
- [ ] 24 props (`prop_*.glb`, `node_*.glb`, `camp_*.glb`), including `prop_lantern.glb` for the Delver's belt
- [ ] 9 material icons (`icon_*.png`)

## Game code

- [ ] **Model loader.** Load `assets/<name>.glb`, map clips to states with crossfades, attach weapons to the hand bone, fall back to the block figures when a file is missing. Until this exists none of the models appear in the game.
- [ ] **Sound loader.** Play `assets/*.ogg` when present, keep the synthesized fallbacks.
- [ ] **Use the textures.** The game still draws with vertex colours.
- [ ] **Quality settings** (Low, Medium, High).
- [ ] **Lighting pass.** The player's back goes almost black at depth 2.
- [ ] **Bosses.** Add the Crystal Warden (depth 2) and Lantern Mother (depth 3); rename the depth-4 boss to the Ossuary King.
- [ ] **Rename the placeholder enemies** to the planned roster.
- [ ] Smaller: decide whether touch controls stay; maybe have the Bellman react to the torch.

## Pipeline improvements

- [ ] Handle images whose arms are below horizontal (rotate the mesh arms up before skinning), so fewer images have to be re-rolled.
- [ ] A reduce-only script for weapons and props.

## Rules to keep

- Free tools and CC0 sources only; log every download in `assets/CREDITS.md`.
- Never use paid Hugging Face services. One 3D model per command, only from an approved image, stop on any quota error.
- Keys go in the environment's secure form or a local `.env`, never in chat or in the repo.
