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
- [x] `enemy_feral.glb` Feral Delver (seed 1)
- [x] `enemy_miner.glb` Hollow Miner (seed 16, skull head and skeleton hands)
- [x] `enemy_druid.glb` Druid Shaman (seed 13, simplified outfit; replaced the Spore Hermit)
- [x] `enemy_jailer.glb` Chain Jailer (seed 24)
- [x] `enemy_stalker.glb` Pale Stalker (seed 1)
- [x] `stalker_bellman.glb` The Bellman (seed 41: a blank ball for a head, bells on the chest)
- [x] `boss_warden.glb` The Crystal Warden (seed 21, crystal mage)
- [x] `boss_lantern.glb` The Lantern Mother (seed 11; lanterns still to be added as props)
- [x] `boss_ossuary.glb` The Ossuary King (seed 11)

Known flaws to revisit:
- Delver: open-toed boots, a wooden handle fused to the left hip, fur collar droops when the arms come down.
- Feral Delver: wrist cords are stiff strands; trouser rags flare when he walks.
- Jailer: rigged with `--no-lift` because his elbows are bent; the mask covers only the lower face (a full mask never came with level arms); wrist chains were dropped from the prompt and need adding as props.
- Hollow Miner: stocky build with a large helmet.
- Ossuary King: the glowing heart pokes out of the ribcage when he leans forward.
- Lantern Mother: the dress hangs to her shins and stretches when she sprints.
- Crystal Warden: his crystals came out dark grey in 3D, not glowing blue; the game should make them glow. He needs a crystal staff in place of the portcullis club.
- Bellman: the ball came out pale yellow, not rusted iron, and the chest bells are small lumps; the blood and stitches from the prompt are missing.
- Bosses and the Bellman are exported at 20,000 triangles.
- Druid Shaman: bare-chested, because the chest wrap in the prompt did not render in the chosen image. Re-roll if she should be covered.
- All enemies use 15,000 triangles; 8,000 broke the meshes. If the laptop struggles with many on screen, add lower-detail versions.

## Other assets

- [x] 7 textures (`tex_*.jpg`)
- [ ] 17 sounds (`sfx_*.ogg`, `amb_*.ogg`)
- [ ] 13 weapons (`weapon_*.glb`), no rig, reduce only
- [ ] 24 props (`prop_*.glb`, `node_*.glb`, `camp_*.glb`), including `prop_lantern.glb` for the Delver's belt
- [ ] 9 material icons (`icon_*.png`)

## Game code

- [x] **Model loader.** The player, five enemies, the Bellman and the Ossuary King load from `assets/`, play idle, walk, jog, roll, hit, death and flask clips, and fall back to the block figures when a file is missing. The player's weapon sits in his right hand.
- [ ] **Real attack, block, climb, mining and sneak animations.** These are simple arm swings for now, waiting on the full animation library.
- [ ] **Model details.** The Chain Jailer has no shield model; enemy weapons (pickaxe, club, bone blade) are not attached; the Bellman's bells do not swing; the Warden's crystals do not glow.
- [ ] **Lower-detail models** if the laptop struggles: every enemy on a level is a 15,000-triangle animated mesh.
- [ ] **Sound loader.** Play `assets/*.ogg` when present, keep the synthesized fallbacks.
- [ ] **Use the textures.** The game still draws with vertex colours.
- [ ] **Quality settings** (Low, Medium, High).
- [ ] **Lighting pass.** The player's back goes almost black at depth 2.
- [ ] **Bosses.** Add the Crystal Warden (depth 2) and Lantern Mother (depth 3) as fights; their models are ready. The depth-4 boss is now the Ossuary King.
- [x] **Rename the placeholder enemies** to the planned roster. The Hollow Miner replaced the flying Cave Mite, so it now walks. The stats line still says "Warden kills" and the Wardenbane sword and Warden's Heart keep their names.
- [ ] Smaller: decide whether touch controls stay; maybe have the Bellman react to the torch.

## Pipeline improvements

- [x] Lift drooping arms level before skinning (handles roughly 5 to 25 degrees; bent elbows still need `--no-lift`).
- [x] Fit the skeleton's shoulders to wide characters, and clean up touching layers so the triangle reduction no longer shreds meshes.
- [x] Keep each limb's skin on its own side and cut lower legs that were generated fused together.
- [ ] Fit hip width and leg length the same way; stocky characters (Miner, Jailer) come out over 2.2 m tall because only the shoulders are matched. The game loader should scale each model to its gameplay height.
- [ ] A reduce-only script for weapons and props.

## Rules to keep

- Free tools and CC0 sources only; log every download in `assets/CREDITS.md`.
- Never use paid Hugging Face services. One 3D model per command, only from an approved image, stop on any quota error.
- Keys go in the environment's secure form or a local `.env`, never in chat or in the repo.
