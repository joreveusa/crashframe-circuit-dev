# ============================================================
#  CrashFrame Circuit — UE5 Content Folder Setup
#  Red Tail Surveying / CrashFrame Circuit Dev Tools
#  Run from PowerShell: .\create_ue5_folders.ps1
# ============================================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CrashFrame Circuit — UE5 Folder Setup      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── 1. Get project path ──────────────────────────────────────
$projectPath = Read-Host "Enter the full path to your UE5 project folder (e.g. C:\Projects\CrashFrameCircuit)"

if (-not (Test-Path $projectPath)) {
    Write-Host "[ERROR] Path not found: $projectPath" -ForegroundColor Red
    Write-Host "        Please check the path and try again." -ForegroundColor Red
    exit 1
}

$contentRoot = Join-Path $projectPath "Content"

if (-not (Test-Path $contentRoot)) {
    Write-Host "[ERROR] No Content folder found at: $contentRoot" -ForegroundColor Red
    Write-Host "        Make sure this is a valid UE5 project folder." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Project root : $projectPath" -ForegroundColor Yellow
Write-Host "Content root : $contentRoot" -ForegroundColor Yellow
Write-Host ""

# ── 2. Define folders + their README descriptions ────────────
$folders = [ordered]@{
    "_Core"                      = @"
# _Core

Global assets shared across the entire project.

**What goes here:**
- `GI_CrashFrame` — the Game Instance Blueprint (persistent game state)
- `GM_CrashFrame` — Game Mode Blueprint
- `PC_CrashFrame` — Player Controller Blueprint
- `GS_CrashFrame` — Game State Blueprint
- `DA_*` — Data Assets (mech stats, weapon stats, arena configs)
- Primary Asset Labels

**Rules:**
- No mech-specific or arena-specific assets here
- Every Blueprint in this folder must compile on its own
"@

    "Mechs/Parts"                = @"
# Mechs/Parts

Static meshes and skeletal meshes that make up mech bodies.

**What goes here:**
- Imported FBX/OBJ skeletal meshes (e.g. `SM_MechTorso_01`, `SK_MechArm_L`)
- Physics Assets auto-generated with each skeletal mesh
- LOD meshes

**Naming convention:**
- Static Mesh: `SM_<Part>_<Variant>`
- Skeletal Mesh: `SK_<Part>_<Variant>`

**Source:** Fab.com, Sketchfab exports, or custom-modeled parts
"@

    "Mechs/Blueprints"           = @"
# Mechs/Blueprints

All mech Blueprints and Blueprint components.

**What goes here:**
- `BP_MechBase` — the parent class all mechs inherit from
- `BP_Mech_<Name>` — individual mech variants (e.g. `BP_Mech_Bruiser`, `BP_Mech_Speeder`)
- `BPC_BoostSystem` — Boost/Thruster component
- `BPC_HeatSystem` — CoreTemp / overheat component
- `BPC_WeaponMount` — weapon attachment component
- `BPC_HealthBar` — mech health component

**Rules:**
- Mech variants must inherit from BP_MechBase, never re-implement base logic
"@

    "Mechs/Materials"            = @"
# Mechs/Materials

Materials and Material Instances for mech meshes.

**What goes here:**
- `M_Mech_Base` — master material with paint color, metallic, wear parameters
- `MI_Mech_<Name>` — material instances per mech variant
- `MF_DamageDecals` — material function for decal damage overlays
- Textures: `T_Mech_<Part>_<Type>` where Type = BC / N / ORM / E

**Texture suffixes:**
| Suffix | Map |
|--------|-----|
| _BC    | Base Color |
| _N     | Normal |
| _ORM   | Occlusion/Roughness/Metallic |
| _E     | Emissive |
"@

    "Weapons/Blueprints"         = @"
# Weapons/Blueprints

All weapon and projectile Blueprints.

**What goes here:**
- `BP_WeaponBase` — parent weapon Blueprint
- `BP_Weapon_<Name>` — specific weapons (e.g. `BP_Weapon_PlasmaRifle`)
- `BP_Projectile_Base` — base projectile with collision + damage
- `BP_Projectile_<Type>` — typed projectiles (plasma, missile, beam)
- `BP_HitEffect_Applier` — component that applies damage + physics impulse on hit

**Damage flow:**
Projectile hits → `ApplyRadialDamage` → Mech `TakeDamage` → CoreTemp increase
"@

    "Weapons/VFX"                = @"
# Weapons/VFX

Niagara systems and materials used only by weapons.

**What goes here:**
- `NS_Muzzle_<WeaponName>` — muzzle flash Niagara systems
- `NS_Projectile_Trail_<Type>` — projectile trail effects
- `NS_Impact_<SurfaceType>` — impact sparks/explosions
- `M_Projectile_<Name>` — projectile mesh materials

**Do NOT put arena/environment VFX here** — those go in VFX/Niagara
"@

    "Arenas/Arena_01"            = @"
# Arenas/Arena_01

All assets specific to Arena 01 (the first playable arena).

**What goes here:**
- Level file: `L_Arena_01` (keep in this folder for discoverability)
- `SM_Arena01_*` — static meshes unique to this arena
- `M_Arena01_*` / `MI_Arena01_*` — arena-specific materials
- `NS_Arena01_*` — arena-specific particle effects (steam, fire)
- `BP_Arena01_*` — arena-specific Blueprints (moving platforms, hazard triggers)

**Sublevel structure (recommended):**
- `L_Arena_01_Geo` — geometry sublevel
- `L_Arena_01_Lighting` — lighting sublevel
- `L_Arena_01_Gameplay` — hazards and gameplay elements
"@

    "Arenas/Shared"              = @"
# Arenas/Shared

Assets reused across multiple arenas.

**What goes here:**
- `SM_Arena_<Part>` — common structural pieces (barriers, ramps, pillars)
- `M_Arena_Base` — master material for arena surfaces
- `BP_Hazard_*` — generic hazard Blueprints
- `DA_Arena_*` — Arena Data Assets (time limits, spawn points config)

**Rule:** If an asset is only in one arena, put it in that arena's folder.
If it appears in 2+ arenas, move it here.
"@

    "Characters/MechPilot"       = @"
# Characters/MechPilot

Assets for the mech pilot character (cockpit view, cutscenes).

**What goes here:**
- `SK_Pilot` — pilot skeletal mesh
- `ABP_Pilot` — pilot Animation Blueprint
- `BP_Pilot` — pilot Blueprint (for first-person cockpit camera)
- `AM_Pilot_*` — pilot Animation Montages (death, eject)
- Pilot textures: `T_Pilot_*`

**Note:** The pilot is not visible during normal gameplay (camera is on the mech).
This folder is for cutscene / lobby / death-cam assets.
"@

    "UI"                         = @"
# UI

All Unreal Motion Graphics (UMG) Widgets and HUD assets.

**What goes here:**
- `WBP_HUD_Main` — the main in-game HUD
- `WBP_HUD_CoreTemp` — CoreTemp / overheat gauge widget
- `WBP_HUD_BoostMeter` — boost fuel bar
- `WBP_HUD_WeaponInfo` — current weapon + ammo display
- `WBP_Menu_Main` — main menu
- `WBP_Menu_MechSelect` — mech selection screen
- `WBP_Scoreboard` — match end scoreboard
- Fonts: `Font_CrashFrame_*`
- UI Textures: `T_UI_*` (icons, frames, backgrounds)

**Tip:** Use `WBP_` prefix for all Widget Blueprints.
"@

    "VFX/Niagara"                = @"
# VFX/Niagara

Environment and gameplay Niagara systems (not weapon-specific).

**What goes here:**
- `NS_Explosion_Mech_*` — mech destruction explosion effects
- `NS_Sparks_Damage_*` — sparks from damaged mechs
- `NS_Smoke_Exhaust` — mech thruster exhaust
- `NS_Debris_*` — debris particle systems post-Chaos destruction
- `NS_Arena_Ambient_*` — arena atmosphere (dust, embers, haze)

**Naming:** `NS_<Category>_<Description>_<Variant>`
"@

    "Audio"                      = @"
# Audio

All audio assets for CrashFrame Circuit.

**What goes here:**
- `SFX_Mech_*` — mech sound effects (movement, impact, boost)
- `SFX_Weapon_*` — weapon fire, reload, impact sounds
- `SFX_UI_*` — menu clicks, alerts, notifications
- `MX_*` — music tracks (combat, menu, victory)
- `ATT_*` — Attenuation settings for 3D sounds
- `SC_*` — Sound Cues (layered/randomized sounds)
- `SM_MetaSound_*` — MetaSound sources

**Formats:**
- SFX: WAV 48kHz/16-bit mono or stereo
- Music: WAV 48kHz/24-bit stereo (or use streaming)
"@

    "Physics"                    = @"
# Physics

Chaos destruction and physics simulation assets.

**What goes here:**
- `GC_Mech_<Part>` — Geometry Collections for destructible mech parts
  - `GC_Mech_Torso`, `GC_Mech_Arm_L`, `GC_Mech_Arm_R`, `GC_Mech_Leg_L`, `GC_Mech_Leg_R`
- `GC_Arena_<Object>` — destructible arena objects (pillars, walls, crates)
- `CF_*` — Chaos Fields (Strain, Anchor, Velocity)
- `PDA_*` — Physical Material assets
- `CC_*` — Chaos Cache assets (pre-baked destruction sequences)

**Key settings for mech parts:**
- Damage Threshold: 500–2000 (depending on part size)
- Mass: Match real-world metal density for satisfying physics
- See: `docs/chaos_physics_guide.md` for full setup instructions
"@
}

# ── 3. Create folders and READMEs ────────────────────────────
$createdCount = 0
$skippedCount = 0

foreach ($folder in $folders.Keys) {
    $fullPath = Join-Path $contentRoot $folder
    $readmePath = Join-Path $fullPath "README.md"

    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  [+] Created  : Content\$folder" -ForegroundColor Green
        $createdCount++
    } else {
        Write-Host "  [~] Exists   : Content\$folder" -ForegroundColor DarkGray
        $skippedCount++
    }

    # Always write/overwrite the README
    $folders[$folder] | Set-Content -Path $readmePath -Encoding UTF8
    Write-Host "       README.md written" -ForegroundColor DarkCyan
}

# ── 4. Summary ───────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              Setup Complete!                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Folders created : $createdCount" -ForegroundColor Green
Write-Host "  Folders existed : $skippedCount" -ForegroundColor DarkGray
Write-Host "  READMEs written : $($folders.Count)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Content root: $contentRoot" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "   1. Copy the ue5_gitignore.txt content into .gitignore at your project root" -ForegroundColor White
Write-Host "   2. Open UE5 Editor — the Content Browser will see all new folders" -ForegroundColor White
Write-Host "   3. Start with _Core: create GI_CrashFrame (Game Instance) first" -ForegroundColor White
Write-Host "   4. See docs\blueprint_cookbook.md for step-by-step Blueprint guides" -ForegroundColor White
Write-Host ""
