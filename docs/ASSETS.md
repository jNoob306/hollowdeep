# Hollowdeep Art Asset Guide

As of 2026-11-15. This is the same content as the shared doc "Hollowdeep Art Asset Guide".

## How to make each asset

Every 3D asset goes through the same free pipeline: generate an image, turn it into a 3D model, add a skeleton and animations (characters only), then upload the GLB to the Space's `assets` folder.

1. **Generate the image** with FLUX.1 [schnell] on Hugging Face. Paste the prompt exactly as written. For characters, also generate a back view by adding "back view".
2. **Turn it into 3D** with the TRELLIS.2 demo on Hugging Face. Upload the image and download the GLB.
3. **Reduce the triangle count if needed** in Blender (Decimate modifier).
4. **Rig and animate characters** in Mesh2Motion (in the browser):
   - import the GLB and choose the human skeleton;
   - fit it to the body;
   - tick the animations you need from the Quaternius library;
   - export one GLB with every clip inside.

   Props and weapons skip this step.
5. **Name the file** as listed in the checklist and upload it to `assets/`.

| Asset type | Triangles | Texture size |
| --- | --- | --- |
| Player | about 15,000 | 1K |
| Enemies | about 15,000 | 1K |
| The Bellman and bosses | about 20,000 | 2K |
| Weapons | 1,000 to 2,000 | 512 |
| Props | 500 to 3,000 | 512 to 1K |

Rules for every character image:

- Full body, front view, strict T-pose: arms fully extended, level with the ground, elbows straight; legs straight and slightly apart. The skeleton's rest pose is a T-pose, so the closer the image, the better the rig.
- Plain light grey background, flat lighting, no shadows.
- Empty open hands with five fingers. Weapons and held items (lanterns included) are separate files; anything named in the prompt tends to end up in a hand.
- No long capes, no hoods, no robes or tunics hiding the legs, no hair over the face. Write "bare head" instead of "hood down".
- Two arms, two legs, one head. Extra shapes stay rigid.

| Tool | Used for | License |
| --- | --- | --- |
| [FLUX.1 schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) | Images | Apache 2.0 |
| [TRELLIS.2](https://huggingface.co/spaces/microsoft/TRELLIS.2) | Image to 3D | MIT |
| [Mesh2Motion](https://mesh2motion.org) | Skeleton and animations | Open source |
| [Quaternius Universal Animation Library 1 and 2](https://quaternius.com/packs/universalanimationlibrary.html) | Animation clips | CC0 |
| [Blender](https://www.blender.org) | Reducing triangles, fixes | Free, open source |
| [Poly Haven](https://polyhaven.com), [ambientCG](https://ambientcg.com) | Textures | CC0 |
| [Freesound](https://freesound.org) (CC0 filter), [Kenney](https://kenney.nl) | Sound | CC0 |

## Main character: The Delver (`player.glb`)

```text
Tall weathered cave hunter and survivor, lean and hardened, long legs, realistic adult human proportions, mid-40s, short grey-streaked hair, scarred stubbled face, tired sharp eyes, bare head with no hood, layered patched leather armor over wool, fur-lined collar, leather bracers, wrapped forearms, belt with pouches and a coiled rope, bone and tooth trinkets, short hip-length tunic, trousers, knee-high wrapped boots. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```

**Animations:** idle, walk, run, dodge roll, light attack, heavy attack, block, hit reaction, death, climb, mining or digging. Drinking the flask isn't in the library, so the game reuses a similar clip.

## Enemies

| Enemy | Role in the game | Replaces in code | File | Weapon file |
| --- | --- | --- | --- | --- |
| Feral Delver | Fast and weak | `crawler` | `enemy_feral.glb` | none |
| Hollow Miner | Basic melee, groups of 2 to 3 | `swarm` | `enemy_miner.glb` | `weapon_pickaxe.glb` |
| Druid Shaman | Ranged spore and curse caster | `spitter` | `enemy_druid.glb` | none |
| Chain Jailer | Shielded brute | `brute` | `enemy_jailer.glb` | `weapon_celldoor.glb`, `weapon_club.glb` |
| Pale Stalker | Elite | `elite` | `enemy_stalker.glb` | `weapon_boneblade.glb` |

### Feral Delver
```text
Feral starving cave explorer gone mad, gaunt emaciated man, torn filthy shirt and trousers, bare dirty feet, long matted hair tied back, wild wide eyes, cracked lips, broken leather straps hanging, grime-covered skin. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```
**Animations:** crawl, fast crawl or run, lunge attack, hit reaction, death.

### Hollow Miner
```text
Undead miner with a bare bone skull for a head and bare skeleton hands, tall thin adult build, empty dark eye sockets, exposed teeth, bony skeletal fingers, the rest of the body fully covered by clothes, dented metal mining helmet with a dead candle stub, long-sleeved torn canvas work shirt, leather suspenders, patched canvas trousers, heavy work boots, coal dust and grime. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```
**Animations:** zombie idle, zombie walk, overhead swing, hit reaction, death.

### Druid Shaman
```text
Feral female cave druid shaman, tall lean adult woman, fierce gaunt face with white bone-ash war paint and dark sunken eyes, long dark hair tied back in braids away from the face, a headdress of small deer antlers and bones, short ragged fur mantle over the shoulders only, chest wrap and a short hip-length hide tunic, bare arms wrapped in leather cord with bone bracelets, necklaces of teeth, feathers and small bones, a belt of hanging pouches and dried herbs, hide leggings, bare feet, faint green glowing spore dust on her hands. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```
**Animations:** idle, walk, throw or spell cast, hit reaction, death.

### Chain Jailer
```text
Tall heavyset human prison jailer, wide shoulders and a thick waist, bald head fully enclosed in a smooth riveted iron mask covering the entire face and chin with only two eye slits, no beard, no hair, heavy leather butcher's apron spattered and smeared with dried and fresh blood, worn over a bare torso, bare thick arms and bare back covered in heavy old scars and whip marks, blood on the forearms and hands, iron shackle cuffs on both wrists with no chains, bloodstained trousers and heavy boots. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```
**Animations:** idle with shield, heavy walk, block, downward smash, hit reaction, death.

### Pale Stalker
```text
Eyeless cave-dwelling humanoid, tall and thin with long limbs, smooth pale translucent skin with visible veins, smooth face where eyes should be, large ears, sharp teeth, bone armor plates strapped to shoulders and shins, loincloth of pale hide, bone trinkets. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game character, muted earthy colors, highly detailed
```
**Animations:** sneak or crouch walk, sword slash, jump attack, hit reaction, death.

## The Bellman, the stalker (`stalker_bellman.glb`)

```text
Gaunt giant figure with its entire head sealed inside a cracked rusted iron church bell, the bell resting on its shoulders, very tall thin body, long arms with oversized grey hands, ragged sackcloth wrapped around the torso, rusted chains looped around the waist, bare grey legs and feet. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy horror game character, highly detailed
```
**Animations:** slow zombie walk, idle, a head-tilt or look-around idle for listening, a grab or two-handed reach, and a hit reaction for the stagger.

If the bell comes out warped, generate the figure "hooded in ragged sackcloth" instead and make the bell as `prop_bell.glb`. The code attaches it to the head and swings it.

## Bosses

| Boss | Depth | File | Weapon file |
| --- | --- | --- | --- |
| The Crystal Warden | 2 | `boss_warden.glb` | `weapon_portcullis.glb` |
| The Lantern Mother | 3 | `boss_lantern.glb` | none |
| The Ossuary King | 4 (final) | `boss_ossuary.glb` | none |

### The Crystal Warden
```text
Towering armored knight boss overgrown with glowing blue crystals, crystal shards bursting through the shoulder plates, back and helmet, cracked ancient plate armor, glowing blue light leaking from the cracks and visor, tattered short tabard to the waist, massive gauntlets, armored legs fully visible. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game boss, highly detailed
```
**Animations:** heavy idle, heavy walk, two-handed overhead slam, sweeping swing, jump attack, roar, death.

### The Lantern Mother
```text
Tall emaciated female boss figure, very long thin arms and clawed fingers, torn grey burial veil over a skeletal face, faint orange glow from the mouth and eyes, iron hooks in her back with several small lanterns hanging on short chains, tattered short burial dress above the knees, bare bony legs, cracked grey skin. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game boss, highly detailed
```
**Animations:** idle, slow walk, claw swipe, scream, spell cast, death. If the lanterns come out warped, generate her without them; the code hangs copies of `prop_lantern.glb` from her back.

### The Ossuary King
```text
Giant humanoid boss made of hundreds of fused human bones and skulls, hulking shoulders and long heavy arms, a ribcage chest with a glowing red heart-like ember inside, a crowned skull head with a rusted iron crown, tattered royal cloth strips at the waist, thick bone legs, red light glowing between the bones. Full body, front view, strict T-pose character reference sheet, both arms fully extended straight out sideways at a 90 degree angle to the body, arms perfectly horizontal and parallel to the ground, elbows straight, palms facing down, legs straight and slightly apart, empty open hands with five fingers each, holding nothing, no cape, plain light grey background, flat even lighting, no shadows, realistic dark fantasy game boss, highly detailed
```
**Animations:** idle, heavy walk, punch, ground slam, charge or run, roar, death. Phase 2 reuses these clips faster, with a brighter glow.

## Weapons

```text
[SUBJECT], single isolated game weapon prop, side view, laid flat, plain light grey background, flat even lighting, no shadows, realistic dark fantasy, weathered, highly detailed
```

| Weapon | Used by | Subject | File |
| --- | --- | --- | --- |
| Rusty Sword | Player (start) | rusted pitted short sword with a leather-wrapped grip | `weapon_rusty.glb` |
| Iron Sword | Player | plain forged iron longsword with a simple crossguard | `weapon_iron.glb` |
| Silver Blade | Player | slim bright silver sword with engraved fuller | `weapon_silverblade.glb` |
| Wardenbane | Player | dark sword with a glowing red ember set in the crossguard and bone grip | `weapon_warden.glb` |
| Bone Axe | Player | crude axe with a jawbone blade lashed to a wooden haft | `weapon_boneaxe.glb` |
| Silver Greataxe | Player | large two-handed silver axe with a long wooden haft | `weapon_greataxe.glb` |
| Iron Spear | Player | long wooden spear with an iron leaf-shaped head | `weapon_spear.glb` |
| Crystal Pike | Player | long pike with a glowing blue crystal spearhead | `weapon_pike.glb` |
| Pickaxe | Hollow Miner | rusted mining pickaxe with a cracked wooden handle | `weapon_pickaxe.glb` |
| Cell-door shield | Chain Jailer | small rusted iron prison cell door with bars, used as a shield | `weapon_celldoor.glb` |
| Iron club | Chain Jailer | heavy iron-banded wooden club | `weapon_club.glb` |
| Bone blade | Pale Stalker | long curved blade carved from a single bone | `weapon_boneblade.glb` |
| Portcullis club | The Crystal Warden | broken rusted iron portcullis section used as a giant club | `weapon_portcullis.glb` |

## Props and set dressing

The cave walls, stalactites, fog, light shafts, dust and the exit ladders, ropes and roots are drawn in code.

```text
[SUBJECT], single isolated game prop, three-quarter view, plain light grey background, flat even lighting, no shadows, realistic dark fantasy, weathered, muted earthy colors, highly detailed
```

| Group | Subject | File |
| --- | --- | --- |
| Mine | wooden mine support frame with two posts and a crossbeam | `prop_support.glb` |
| Mine | rusted mine cart on short rails | `prop_cart.glb` |
| Mine | broken wooden ladder with missing rungs | `prop_ladder_broken.glb` |
| Mine | wooden pulley with a frayed rope | `prop_pulley.glb` |
| Mine | length of hanging rusted chain | `prop_chain.glb` |
| Remains | human skeleton slumped sitting against a rock | `prop_skeleton.glb` |
| Remains | pile of human bones and skulls | `prop_bones.glb` |
| Remains | abandoned bedroll beside a cold campfire ring | `prop_bedroll.glb` |
| Remains | rusted iron lantern | `prop_lantern.glb` |
| Remains | torn leather-bound journal | `prop_journal.glb` |
| Resources | iron ore vein in a rock chunk | `node_iron.glb` |
| Resources | silver ore vein in a rock chunk | `node_silver.glb` |
| Resources | glowing blue crystal cluster | `node_glow.glb` |
| Resources | chunk of glowing orange amber in stone | `node_amber.glb` |
| Resources | cluster of glowing green cave mushrooms | `node_fungus.glb` |
| Lore | hanging iron gibbet cage | `prop_cage.glb` |
| Lore | broken stone bell-tower ruin | `prop_belltower.glb` |
| Lore | throne made of bones and skulls | `prop_bonethrone.glb` |
| Loot | iron-banded wooden chest | `prop_chest.glb` |
| Loot | leather satchel | `prop_satchel.glb` |
| Camp | weathered canvas tent | `camp_tent.glb` |
| Camp | stone campfire ring with logs | `camp_fire.glb` |
| Camp | anvil beside a wooden workbench | `camp_bench.glb` |
| Camp | wooden weapon rack | `camp_rack.glb` |

## Textures

Download at 1K from Poly Haven or ambientCG (CC0). Keep the color, normal and roughness maps as JPG.

| Texture | What to search for | Files |
| --- | --- | --- |
| Rock wall | rock face, cliff, cave wall | `tex_rock_color.jpg`, `tex_rock_normal.jpg`, `tex_rock_rough.jpg` |
| Cave floor | gravel, mud, rocky ground | `tex_floor_*.jpg` |
| Wet rock | wet stone, river rock | `tex_wetrock_*.jpg` |
| Crystal | crystal, quartz, ice | `tex_crystal_*.jpg` |
| Mine timber | old wood planks | `tex_wood_*.jpg` |
| Rusted iron | rusty metal | `tex_rust_*.jpg` |
| Moss | moss, mossy rock | `tex_moss_*.jpg` |

AI alternative (seams likely, and no normal or roughness maps):
```text
Seamless tileable texture of [SUBJECT], top-down orthographic view, flat even lighting, no shadows, no perspective, highly detailed, realistic, 1024x1024
```

## Sound

From Freesound (license filter: Creative Commons 0) or Kenney's audio packs. Save as OGG, mono, under 10 seconds except the loops.

| Sound | Used for | File |
| --- | --- | --- |
| Heavy distant bell toll | The Bellman, level start | `sfx_bell_toll.ogg` |
| Single cracked bell clank | The Bellman, each step | `sfx_bell_step.ogg` |
| Rapid bell rattle | The Bellman, grab wind-up | `sfx_bell_shake.ogg` |
| Heavy chain drag | The Bellman, moving | `sfx_chain_drag.ogg` |
| Water drips (loop) | Cave ambience | `amb_drips.ogg` |
| Distant low rumble | Cave ambience | `amb_rumble.ogg` |
| Wind through a shaft (loop) | Near exit shafts | `amb_wind.ogg` |
| Low dark drone (loop) | Music bed | `amb_drone.ogg` |
| Torch crackle (loop) | Player's torch | `amb_torch.ogg` |
| Footsteps on stone | Player | `sfx_step_stone.ogg` |
| Footsteps on gravel | Player | `sfx_step_gravel.ogg` |
| Pickaxe hitting rock | Mining | `sfx_mine.ogg` |
| Sword swing and hit | Combat | `sfx_swing.ogg`, `sfx_hit.ogg` |
| Metal shield clang | Blocking | `sfx_clang.ogg` |
| Undead groan | Feral Delver, Hollow Miner | `sfx_groan.ogg` |
| Wet screech | Spore Hermit, Pale Stalker | `sfx_screech.ogg` |

## Material icons

128x128 PNG from FLUX:
```text
Game inventory icon of [MATERIAL], centered, single object, dark fantasy style, soft rim light, plain dark background, square
```

| Material | Description | File |
| --- | --- | --- |
| Stone | a rough grey stone chunk | `icon_stone.png` |
| Iron Ore | a rust-orange iron ore nugget | `icon_iron.png` |
| Bone | a single old bone | `icon_bone.png` |
| Hide | a folded piece of tanned animal hide | `icon_hide.png` |
| Cave Fungus | a glowing green cave mushroom | `icon_fungus.png` |
| Silver Ore | a pale silver ore nugget | `icon_silver.png` |
| Glowcrystal | a glowing blue crystal shard | `icon_glow.png` |
| Deep Amber | a glowing orange amber stone | `icon_amber.png` |
| Warden's Heart | a glowing red ember heart encased in bone | `icon_heart.png` |

## Checklist

- [ ] `player.glb`
- [ ] `enemy_feral.glb`, `enemy_miner.glb`, `enemy_druid.glb`, `enemy_jailer.glb`, `enemy_stalker.glb`
- [ ] `stalker_bellman.glb` (plus `prop_bell.glb` only if the bell is made separately)
- [ ] `boss_warden.glb`, `boss_lantern.glb`, `boss_ossuary.glb`
- [ ] 13 weapon files (`weapon_*.glb`)
- [ ] 24 prop files (`prop_*.glb`, `node_*.glb`, `camp_*.glb`)
- [ ] 7 textures, 3 maps each (`tex_*.jpg`)
- [ ] 16 sounds (`sfx_*.ogg`, `amb_*.ogg`)
- [ ] 9 material icons (`icon_*.png`)
