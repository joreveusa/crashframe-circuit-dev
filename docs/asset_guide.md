# CrashFrame Circuit — Asset Guide

> **Goal:** Build a playable mech arena game using free and AI-assisted assets
> **Principle:** Ship a vertical slice first. Polish visuals later.

---

## Table of Contents

1. [Naming Conventions](#1-naming-conventions)
2. [Free Mech Assets — Where to Find Them](#2-free-mech-assets--where-to-find-them)
3. [Megascans in UE5](#3-megascans-in-ue5)
4. [Free Niagara VFX Packs](#4-free-niagara-vfx-packs)
5. [Sketchfab + Bridge Workflow](#5-sketchfab--bridge-workflow)
6. [AI Concept Art and Texture Generation](#6-ai-concept-art-and-texture-generation)
7. [Audio Assets — Free Sources](#7-audio-assets--free-sources)
8. [Quick Import Checklists](#8-quick-import-checklists)

---

## 1. Naming Conventions

Consistent naming saves hours of frustration. Follow this for every asset you import or create.

### Prefix Table

| Prefix | Asset Type |
|--------|-----------|
| `SM_` | Static Mesh |
| `SK_` | Skeletal Mesh |
| `BP_` | Blueprint (Actor) |
| `BPC_` | Blueprint Component |
| `WBP_` | Widget Blueprint (UMG/UI) |
| `GI_` | Game Instance Blueprint |
| `PC_` | Player Controller Blueprint |
| `GM_` | Game Mode Blueprint |
| `M_` | Material (Master) |
| `MI_` | Material Instance |
| `MF_` | Material Function |
| `T_` | Texture |
| `NS_` | Niagara System |
| `NE_` | Niagara Emitter |
| `SC_` | Sound Cue |
| `SFX_` | Sound Wave (effect) |
| `MX_` | Music track |
| `ATT_` | Sound Attenuation |
| `GC_` | Geometry Collection (Chaos) |
| `ABP_` | Animation Blueprint |
| `AM_` | Animation Montage |
| `AS_` | Animation Sequence |
| `DA_` | Data Asset |
| `DT_` | Data Table |
| `L_` | Level / Map |
| `CF_` | Chaos Field |

### Texture Suffix Table

| Suffix | Channel Content |
|--------|---------------|
| `_BC` | Base Color (albedo) |
| `_N` | Normal Map |
| `_ORM` | Occlusion (R) / Roughness (G) / Metallic (B) |
| `_E` | Emissive |
| `_M` | Mask (grayscale) |
| `_D` | Displacement / Height |

**Full example:**
```
T_Mech_Torso_BC.uasset    ← Torso base color texture
T_Mech_Torso_N.uasset     ← Torso normal map
T_Mech_Torso_ORM.uasset   ← Torso packed ORM
SM_Mech_Torso_01.uasset   ← Torso static mesh variant 01
GC_Mech_Torso.uasset      ← Torso Geometry Collection (Chaos)
```

### Version Numbering

When you have variants, use `_01`, `_02` (zero-padded, not `_1`).

---

## 2. Free Mech Assets — Where to Find Them

### Fab.com (Epic's Asset Marketplace — Best for UE5)

**URL:** https://www.fab.com

Fab replaced the old Marketplace. All "Free" filter assets are fully licensed for your game.

**Search terms that work:**

| Search Term | What You'll Find |
|-------------|-----------------|
| `mech` + Free filter | General mech assets |
| `robot modular` | Modular robot pieces (mix and match) |
| `sci-fi modular kit` | Arena wall/floor kits |
| `military robot` | Heavier, tank-like mechs |
| `humanoid robot` | Biped mech bases |
| `mech skeleton` | Rigged skeletal meshes ready for animation |
| `sci-fi weapons` | Plasma rifles, cannons |
| `space arena` | Arena environment kits |
| `industrial modular` | Gritty warehouse-style arena pieces |

**Top free assets to grab immediately:**
- **"Modular Sci-Fi Corridor"** — reuse for arena walls
- **"Military Weapons Dark"** — free weapon meshes
- **"Infinity Blade: Warriors"** — free Epic characters (use for scale reference)
- **"City Sample Crowds"** — ambient drone meshes for arena atmosphere

**Monthly free assets:** Epic gives away paid assets every month. Claim them even if you don't need them yet.

### Sketchfab (3D Model Library)

**URL:** https://sketchfab.com/3d-models?features=downloadable&sort_by=-likeCount

Filter: **Downloadable** + **Free** + search `mech`

Download in `.glb` or `.fbx` format. See Section 5 for import workflow.

**Quality search terms:**
- `mech battle` — combat-ready designs
- `gundam style mech` — anime-style proportions (fun and readable)
- `heavy mech` — tanky, low designs
- `modular mech` — parts you can mix

> ⚠️ **License check:** Always verify the Sketchfab license. Use only **CC0**, **CC-BY**, or **CC-BY-4.0**. CC-BY requires attribution in your credits. Never use NC (NonCommercial) assets in a commercial game.

### TurboSquid (Some Free)

**URL:** https://www.turbosquid.com/Search/3D-Models/free/mech

Filter by Free + FBX format. Quality varies widely — preview carefully.

### ArtStation Marketplace (Free section)

**URL:** https://www.artstation.com/marketplace/game-dev?section=free

Occasionally has high-quality mech and sci-fi assets.

### Mixamo (Free Animations)

**URL:** https://www.mixamo.com

Free humanoid animations from Adobe. Useful for:
- **Pilot character** animations
- **Bipedal mech** walking/running (if your mech has human proportions)
- Death and stagger animations

Download as FBX with skin. In UE5: import as Skeletal Mesh, then retarget to your mech skeleton using IK Retargeter.

---

## 3. Megascans in UE5

Megascans = photorealistic scanned surfaces from Quixel. **Free for UE5 projects** through the Bridge plugin.

### Setup

1. **Install Bridge:** In UE5 → **Content → Add → Quixel Bridge** (or top menu → **Window → Bridge**)
2. Sign in with your **Epic Games account** (same login as Fab)
3. Search for surfaces, 3D assets, and atlases

### What to Use Megascans For (CrashFrame Circuit)

| Asset Type | Use Case |
|------------|---------|
| **Metal surfaces** | Arena floor, mech hangar texture |
| **Concrete/Brutalist** | Arena walls and pillars |
| **Gravel/Rubble** | Arena ground cover and debris |
| **Rust decals** | Mech damage layering |
| **Carbon fiber** | High-tech mech panel material |

**Search terms:** `brushed metal`, `painted metal`, `industrial floor`, `concrete brutalist`, `sci-fi panel`

### Import Settings (Megascans in UE5)

When Bridge exports to UE5, it auto-creates:
- The texture imports (BC, N, ORM)
- A Material Instance pre-configured

Change these settings after import:
- Texture size: **4096x4096** for hero assets, **2048x2048** for background
- **Compression:** BC7 (default is fine)
- **sRGB:** ✅ for BC/Emissive, ❌ for N/ORM/M

### Using Megascans as Mech Materials

Don't use Megascans textures directly on your mech master material. Instead:

1. Import the Megascan metal texture
2. In `M_Mech_Base` (your master material), add a `Texture Sample Parameter 2D` node named `"PanelTexture"`
3. Create a `MI_Mech_Bruiser` material instance
4. Set `PanelTexture` = the Megascan brushed metal
5. Add a tint parameter on top for team colors / customization

---

## 4. Free Niagara VFX Packs

### From Fab.com

| Search Term | What You Need It For |
|-------------|---------------------|
| `Niagara VFX` + Free | General effects packs |
| `explosion Niagara` | Mech death explosions |
| `fire Niagara` | Post-destruction burning |
| `smoke Niagara` | Damage and thruster exhaust |
| `sparks Niagara` | Impact and damage sparks |
| `plasma Niagara` | Projectile trails |
| `shield Niagara` | Shield hit effects |

**Specific free packs worth grabbing:**
- **"Infinity Blade Effects"** — Epic's own VFX pack (high quality, free)
- **"Realistic Starter VFX Pack"** — fire, smoke, sparks
- **"Advanced Magic Effects"** — energy effects (reskin for plasma weapons)

### From UE5 Content Examples

**Window → Content Examples** (free from Epic):
- Open the **"Niagara"** content example map
- All Niagara systems in it are freely copyable to your project
- Right-click any NS_ asset → **Migrate** → select your project

### Custom VFX Approach

For CrashFrame Circuit-specific effects, start from a template:
1. **Content Browser** → right-click → **Niagara System** → **New System from Selected Emitter**
2. Start from `Sprite Burst Instantaneous` (for impacts) or `Mesh Renderer` (for debris particles)

**CoreTemp heat shimmer effect:**
- Niagara + Post Process Volume with a distortion material
- Ask AI: "How do I create a heat shimmer / heat haze effect in Unreal Engine 5 Niagara for an overheating mech?"

---

## 5. Sketchfab + Bridge Workflow

### Option A: Direct FBX Import (Simplest)

1. Download model from Sketchfab as `.fbx` (select **Original Format** or **FBX**)
2. In UE5 Content Browser → **Import** → select the FBX
3. **FBX Import Options:**
   - Skeletal Mesh: ✅ if it has bones, ❌ if rigid
   - Import Materials: ✅ (creates placeholder materials)
   - Import Textures: ✅
   - Normal Import Method: **Import Normals and Tangents**
   - Transform: Scale X/Y/Z = **1.0** (adjust after if needed — Sketchfab uses cm, UE5 uses cm, usually matches)
4. Review result. Check scale against a default character (~180cm tall). Rescale in Details if needed.

### Option B: Blender Cleanup First (Recommended for Hero Assets)

Sketchfab assets often have:
- Flipped normals
- Too-high polygon counts
- Non-standard bone names

Clean up in Blender (free):
1. Import GLB/FBX into Blender
2. **Fix normals:** Edit Mode → Mesh → Normals → Recalculate Outside
3. **Reduce polygons:** Modifier → Decimate. Target: 10,000–30,000 tris for a mech
4. **Clean materials:** Merge similar materials, remove unused UV maps
5. Export as FBX → import to UE5

### Common Sketchfab Import Issues

| Problem | Fix |
|---------|-----|
| Mesh is tiny (0.01x scale) | At import: set **Import Uniform Scale** to 100 |
| Mesh is huge | Set Import Uniform Scale to 0.01 |
| Textures missing | Check relative paths. Sketchfab FBX often has absolute texture paths — fix in Blender before export |
| Dark/black mesh | Normal map format: Sketchfab uses DirectX normals. In UE5 texture settings: ✅ **Flip Green Channel** |
| Wrong up-axis | At import: set **Transform → Up Axis** to Z |

---

## 6. AI Concept Art and Texture Generation

### Concept Art (Game Design Phase)

Use these tools to visualize mech designs before modeling:

**Midjourney (paid, ~$10/mo):**
```
Prompt formula:
"[style] mech robot, [silhouette description], [color palette], 
concept art, game asset, white background, orthographic view"

Examples:
"heavy armored mech robot, wide shoulders, angular design, 
blue and orange color scheme, concept art, game asset, orthographic view"

"fast scout mech robot, sleek legs, asymmetric weapons, 
dark chrome with green accents, concept art, game character sheet, 
front/side/back view"
```

**Stable Diffusion (free, local):**
- Model: `Dreamshaper XL` or `SDXL`
- Good for rapid iteration
- Use **ControlNet** with a 3D sketch for consistent shapes

**Adobe Firefly (free tier):**
- Good for texture concepts and color palette exploration
- Generates commercially-safe images

### Texture Generation with AI

**For custom mech panel textures:**

Using **Stable Diffusion** with a tiling prompt:
```
"seamless tileable texture, sci-fi metal panel, 
hexagonal bolts, worn paint, PBR diffuse map, 
dark grey, top-down view, [OPTIONS: --tile --ar 1:1]"
```

Then bring into Photoshop / Krita / DaVinci to generate the normal and ORM maps:
- **Normal map:** Filter → 3D → Generate Normal Map (Photoshop) or GIMP NormalMap plugin
- **ORM:** Manual: R=white (full AO), G=roughness (0.5-0.8 for metal), B=metallic (1.0 for metal)

**Better alternative:** Use **Materialize** (free tool) to auto-generate N/ORM from albedo:
- Download: https://boundingboxsoftware.com/materialize/

### AI for Reference Sheets

Ask Gemini or ChatGPT:
> "Generate a CrashFrame Circuit mech design brief for a heavy tank mech called 'Bruiser'. Include: silhouette description, color palette (hex codes), key visual features, inspiration references, and suggested Midjourney prompt."

Use the output to maintain consistency across your AI-generated concepts.

---

## 7. Audio Assets — Free Sources

### Freesound.org

**URL:** https://freesound.org

Filter by **Creative Commons 0** (fully free, no attribution).

Search terms:
- `robot servo` → mech movement sounds
- `metal impact heavy` → mech hit sounds
- `jet thruster` → boost audio
- `explosion mechanical` → weapon impacts
- `electric hum` → ambient mech idle
- `cannon fire` → heavy weapon SFX

### Sonniss GDC Audio Bundle

Every year Sonniss releases a free bundle of pro game audio at GDC.
**URL:** https://sonniss.com/gameaudiogdc (search for the latest year)
These are CC0 — thousands of pro-quality SFX.

### Zapsplat

**URL:** https://www.zapsplat.com (free with account)

Good mechanical and sci-fi SFX library.

### Music

| Source | Style | License |
|--------|-------|---------|
| **Kevin MacLeod (incompetech.com)** | Various | CC-BY |
| **Free Music Archive (freemusicarchive.org)** | Various | Varies (check per track) |
| **Bandcamp free downloads** | Synthwave, industrial | Varies |
| **Pixabay Music** | Electronic | CC0 |

Search for: `synthwave`, `industrial metal`, `cyberpunk`, `mech battle` for CrashFrame's style.

---

## 8. Quick Import Checklists

### ✅ Importing a Static Mesh (Mech Part)

- [ ] FBX exported from source app with Y-up or Z-up checked
- [ ] Import Scale set correctly (check against 180cm reference)
- [ ] Normals import: `Import Normals and Tangents`
- [ ] LODs: Generate LODs in UE5 (Details → LOD → Auto Compute LOD Distances)
- [ ] Collision: Auto-convex collision generated (`SM_` → Details → Collision → Add 6 DOP Simplified)
- [ ] Named correctly: `SM_Mech_<PartName>_<Variant>`
- [ ] Moved to `Content/Mechs/Parts/`

### ✅ Importing a Texture

- [ ] Named with proper suffix (`_BC`, `_N`, `_ORM`, `_E`)
- [ ] sRGB: ✅ for BC and Emissive, ❌ for everything else
- [ ] Compression: `BC7` for color, `BC5` for normal maps, `BC4` for single-channel
- [ ] Mip Maps: ✅ Enabled (except for UI textures — disable mips on those)
- [ ] Max Texture Size: 4096 for hero assets, 2048 for props, 512 for small parts

### ✅ Importing Audio

- [ ] Format: WAV (UE5 converts internally)
- [ ] Sample Rate: 48kHz
- [ ] Bit Depth: 16-bit minimum, 24-bit for music
- [ ] Mono vs Stereo: SFX = Mono (3D spatialized), Music = Stereo (2D)
- [ ] Named: `SFX_Mech_<Action>` or `MX_<TrackName>`
- [ ] Attenuation: Create `ATT_Mech_<Type>` asset for 3D sounds (Inner: 200, Falloff: 2000)

### ✅ Adding a Niagara VFX Pack from Fab

- [ ] Download and install from Fab
- [ ] Add to Project: Fab Library → Add to Project (not Add to Vault)
- [ ] After adding: restart editor
- [ ] Find assets in `Plugins/FabAssets/` or wherever Fab installs
- [ ] Migrate wanted NS_ assets to `Content/VFX/Niagara/`
- [ ] Test in a blank level before integrating

---

*Last updated: CrashFrame Circuit — Pre-Alpha Dev*
*See also: `blueprint_cookbook.md` and `chaos_physics_guide.md`*
