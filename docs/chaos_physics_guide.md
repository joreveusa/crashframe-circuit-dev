# CrashFrame Circuit — Chaos Physics Destruction Guide

> **Engine:** Unreal Engine 5.3+
> **Feature:** Chaos Destruction (built-in, no plugins needed)
> **Goal:** Satisfying mech part destruction with flying debris, proper physics, and good performance

---

## Table of Contents

1. [Overview — How Chaos Works](#1-overview--how-chaos-works)
2. [Convert a Static Mesh to a Geometry Collection](#2-convert-a-static-mesh-to-a-geometry-collection)
3. [Fracture Modes — Choosing the Right Pattern](#3-fracture-modes--choosing-the-right-pattern)
4. [Geometry Collection Settings](#4-geometry-collection-settings)
5. [Chaos Fields Setup](#5-chaos-fields-setup)
6. [Blueprint: Triggering Destruction](#6-blueprint-triggering-destruction)
7. [Debris Cleanup System](#7-debris-cleanup-system)
8. [Performance Settings](#8-performance-settings)
9. [Mech Part Destruction — Specific Values](#9-mech-part-destruction--specific-values)
10. [Common Mistakes and Fixes](#10-common-mistakes-and-fixes)

---

## 1. Overview — How Chaos Works

Chaos Destruction has three layers:

```
Static Mesh (source)
    ↓ Fracture Editor
Geometry Collection (GC) — pre-computed fracture pattern stored as asset
    ↓ In level
Geometry Collection Component — the runtime simulation
    ↓ Triggered by
Damage Threshold exceeded → chunks break free → Chaos Physics simulates debris
```

**Key terms:**
- **Geometry Collection (GC):** The fracture asset. Lives in `Content/Physics/`
- **Damage Threshold:** How much force/damage before a chunk breaks off
- **Cluster:** Group of chunks that break together (useful for mech limbs)
- **Strain Field:** External field that can weaken specific regions before impact

---

## 2. Convert a Static Mesh to a Geometry Collection

### Step-by-Step in Editor

1. **Import your mech mesh** into `Content/Mechs/Parts/` as usual (FBX import)

2. **Open the Fracture Editor:**
   - Top menu bar → **Fracture** (if not visible: **Edit → Editor Preferences → Experimental → enable Fracture**)

3. **Place the mesh in your level** (drag from Content Browser to viewport)

4. **Select the Static Mesh actor** in the viewport

5. **In the Fracture Editor toolbar**, click **New** (or **"Generate"**):
   - This creates a new **Geometry Collection** asset
   - Save location: `Content/Physics/GC_Mech_<PartName>` (e.g., `GC_Mech_Torso`)

6. **The actor in your level is now replaced** with a Geometry Collection Component

7. **Save the GC asset** — it now contains both the visual mesh and the fracture data

> **Tip:** Always work on a **copy** of the original mesh. Keep the unfractured `SM_*` version in `Content/Mechs/Parts/` for reference and LOD use.

---

## 3. Fracture Modes — Choosing the Right Pattern

In the Fracture Editor, select your GC and choose a fracture mode:

### Uniform Voronoi (Best for mech torsos and large pieces)

- **What it does:** Random scattered fracture points — natural-looking breaks
- **Settings:**
  - Minimum Sites: **20**
  - Maximum Sites: **40**
- **When to use:** Mech torso, large armor plates

### Clustered Voronoi (Best for mech limbs)

- **What it does:** Creates groups of chunks — the arm breaks into 3-4 large pieces, each of which shatters further
- **Settings:**
  - Cluster Sites: **4** (the "limb segments")
  - Sites per Cluster: **8-15**
- **When to use:** Arms, legs (break at joint, then shatter)

### Plane Cut (Best for clean armor splits)

- **What it does:** Slices the mesh with flat planes
- **Settings:** Set plane normal direction manually
- **When to use:** Armor panels, shields, flat surfaces

### Brick (Avoid for organic mech parts)

- **When to use:** Arena walls, concrete pillars only

### Multi-Level Fracture (For hero destruction moments)

Run fracture twice:
1. First pass: Clustered Voronoi (4 clusters) — the "limb breaks"
2. Select **child chunks** only → second pass: Uniform Voronoi (15 sites) — the "chunks shatter"

Result: Arm breaks at elbow, then each half crumbles. Expensive but spectacular.

---

## 4. Geometry Collection Settings

Select the **Geometry Collection Component** in the Details panel:

### Damage Settings

| Setting | Mech Torso | Mech Arm/Leg | Small Part |
|---------|-----------|--------------|------------|
| **Damage Threshold** | 1500 | 800 | 300 |
| **Enable Damage** | ✅ | ✅ | ✅ |
| **Max Level** | 2 | 2 | 1 |
| **Critical Depth** | 1 | 1 | 0 |

**Damage Threshold explained:** This is the minimum impulse (in UE units) needed to break the first cluster level. A plasma rifle hit should apply ~600 impulse. So an arm (threshold 800) takes 2 hits, a torso (1500) takes 3-4.

### Simulation Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Simulation Type** | Dynamic | Simulates under physics |
| **Object Type** | Rigid | For solid metal parts |
| **Mass as Density** | ✅ Enabled | More realistic |
| **Density** | 7.8 (steel) | g/cm³ — UE will scale by volume |
| **Linear Damping** | 0.01 | Very little drag (space-like arenas) |
| **Angular Damping** | 0.01 | Chunks tumble naturally |
| **Collision Type** | Use Complex As Simple | Until performance issues arise |
| **Cull Size** | 5.0 | Chunks smaller than 5cm disappear |

### Remove On Sleep Settings

| Setting | Value |
|---------|-------|
| **Remove Pieces On Sleep** | ✅ Enabled |
| **Sleep Velocity Threshold** | 5.0 |
| **Sleep Timer** | 2.0 seconds |

This auto-removes debris that has stopped moving — critical for performance.

---

## 5. Chaos Fields Setup

Fields let you control destruction from Blueprints — weakening specific areas, applying velocity, or anchoring parts.

### Placing a Field

1. In the viewport, right-click → **Place Actor** → search for `Field System Actor`
2. **Or** just reference fields from Blueprint using Blueprint nodes (preferred for dynamic use)

### Strain Field (Weaken Before Impact)

A Strain Field reduces the Damage Threshold of chunks within its radius. Use this right before a big hit for dramatic effect.

**In Blueprint (before applying damage):**
```
[Construct Object from Class | Class: Radial Falloff]
    │ Radius: 300.0
    │ Magnitude: 0.5   ← reduces threshold by 50%
    │ Position: HitLocation
    └─▶ [Apply Physics Field | Target: GeometryCollectionComponent,
                              Field: RadialFalloff,
                              ObjectType: ClusterCrumbling,
                              FieldType: SamplerType_Default]
```

### Anchor Field (Keep Part of the Mesh Static)

Useful for: keeping the mech's remaining torso stuck to the arena floor while the upper half explodes.

In the **Fracture Editor**, select the bottom chunks → right-click → **Set Initial State: Sleeping / Kinematic**. These won't simulate until explicitly woken.

### Velocity Field (Blast Direction)

Apply directional velocity to all chunks in a radius on destruction:

```
[Construct Object from Class | Class: Radial Vector]
    │ Magnitude: 2000.0
    │ Position: ExplosionOrigin
    └─▶ [Apply Physics Field | FieldType: LinearVelocity]
```

---

## 6. Blueprint: Triggering Destruction

### Method 1: Apply Radial Impulse (Easiest)

On `BP_Projectile_Base` → **OnComponentHit**:

```
[Get Component by Class | Class: Geometry Collection Component | Target: OtherActor]
    → [Is Valid]
        │ Valid ──→ [Apply External Strain | Target: GCComponent,
                    Location: HitResult.Location,
                    Radius: 200.0,
                    Propagation Depth: 2,
                    Strain: 800.0]    ← must exceed Damage Threshold to break
                    → [Apply Radial Impulse | Target: GCComponent,
                       Origin: HitResult.Location,
                       Radius: 300.0,
                       Strength: 500000.0,   ← very high — Chaos needs large impulse values
                       Falloff: Constant,
                       Velocity Change: false]
```

> **Why so large?** Chaos impulses work in kg·cm/s. For a 100kg arm chunk, 500,000 gives it a satisfying launch. Experiment with values.

### Method 2: Damage-Based Breaking (Clean Architecture)

In `BP_MechBase` → `TakeDamage` → after health update:

```
[Get Component by Class | Class: Geometry Collection Component | Target: Self]
    → [Is Valid]
        │ Valid ──→ [Branch | Condition: Damage > 300.0]  ← only big hits cause fracture
                       │ True ──→ [Apply External Strain | Strain: Damage * 2.0,
                                   Location: HitResult.Location,
                                   Radius: 150.0]
```

### Method 3: Scripted Destruction (Cinematic)

For death sequence — guaranteed destruction regardless of physics:

```
[Custom Event: MechDestroyed]
    → [Get All Components by Class | Class: Geometry Collection Component]
        → [For Each Loop | Array: Return Value]
            │ Loop Body ──→ [Apply External Strain | Target: Array Element,
                             Strain: 99999.0,      ← guaranteed break all clusters
                             Radius: 10000.0]
                             → [Apply Radial Impulse | Strength: 1000000.0, Radius: 500.0]
```

---

## 7. Debris Cleanup System

Without cleanup, every mech death leaves chunks forever. This tanks performance.

### 7.1 Auto-Remove on Sleep (Built-In)

Already configured in Geometry Collection settings (Section 4). Chunks sleeping for 2+ seconds auto-remove.

### 7.2 Blueprint: Timed Cleanup

In `BP_MechBase` → `MechDestroyed` event:

```
[Custom Event: MechDestroyed]
    → (existing explosion effects...)
    → [Set Timer by Function Name | Function: "CleanupDebris", Time: 5.0, Looping: false]
```

**CleanupDebris function:**
```
[Get All Components by Class | Class: Geometry Collection Component | Target: Self]
    → [For Each Loop]
        → [Destroy Component | Target: Array Element]
```

### 7.3 Debris Cap System (Global)

In `GI_CrashFrame` (Game Instance), add:

- Variable: `ActiveDebrisPieces` (Integer, default 0)
- Variable: `MaxDebrisPieces` (Integer, default 200)

When a GC spawns chunks → increment. When CleanupDebris fires → decrement.

If `ActiveDebrisPieces >= MaxDebrisPieces` → trigger immediate cleanup on oldest GC.

> **Simpler approach for solo dev:** Start with just the sleep-based cleanup. Add the cap system only if you're seeing performance drops.

---

## 8. Performance Settings

### Project Settings (Edit → Project Settings → Chaos)

| Setting | Recommended | Notes |
|---------|-------------|-------|
| **Max Cluster Level** | 2 | Higher = more fracture stages = more expensive |
| **Chaos Default Replication** | Off | Enable only for multiplayer |
| **Max Geometry Collection Sim Particles** | 500 | Hard cap on simultaneous debris chunks |
| **Minimum Debris Volume** | 50 cm³ | Chunks smaller than this are auto-culled |

### Per-GC Performance Tips

- **Use LOD on GC chunks:** In Fracture Editor → View → enable LOD. Set LOD1 at 15m, LOD2 at 40m.
- **Reduce site count for off-screen mechs:** Far mechs can use a simpler GC with 8 sites instead of 40.
- **Cache destruction:** For hero moments (boss death), use **Chaos Cache** to pre-bake the simulation. Plays back as animation — zero runtime cost.

### What to Avoid

| ❌ Don't | ✅ Do Instead |
|----------|--------------|
| Fracture with 200+ sites | Max 40 sites per GC |
| Leave debris forever | Use 5-second cleanup timer |
| Use Chaos on every destructible | Only mech parts + key arena objects |
| Run Chaos on distant mechs | Switch to `SM_Mech_Dead` (static broken mesh) at 50m+ |

---

## 9. Mech Part Destruction — Specific Values

### Geometry Collection Setup Per Part

| Part | GC Name | Sites | Damage Threshold | Mass (kg) | Impulse Strength |
|------|---------|-------|-----------------|-----------|-----------------|
| Torso | `GC_Mech_Torso` | 30–40 | 1500 | 800 | 800,000 |
| Arm (L or R) | `GC_Mech_Arm` | 15–20 | 800 | 200 | 400,000 |
| Leg (L or R) | `GC_Mech_Leg` | 15–20 | 800 | 350 | 400,000 |
| Shoulder Pad | `GC_Mech_Shoulder` | 8–12 | 300 | 50 | 200,000 |
| Head/Cockpit | `GC_Mech_Head` | 10–15 | 600 | 100 | 300,000 |
| Weapon Mount | `GC_Mech_WeaponMount` | 5–8 | 400 | 80 | 250,000 |

### Weapon Damage vs. Part Threshold

| Weapon | Damage | Impulse Applied | Can Break Arm? | Can Break Torso? |
|--------|--------|-----------------|----------------|-----------------|
| Plasma Rifle (light) | 50 HP | 600 strain | 1 hit | 3 hits |
| Cannon (medium) | 120 HP | 1200 strain | 1 hit | 2 hits |
| Missile | 200 HP | 2000 strain | 1 hit | 1 hit |
| Melee Slam | 300 HP | 3000 strain | 1 hit | 1 hit |

---

## 10. Common Mistakes and Fixes

### ❌ Problem: Nothing breaks when hit

**Cause:** Damage Threshold too high, or `Apply External Strain` strain value too low.

**Fix:**
1. Select GC in level → Details → **Damage Threshold** — try lowering to 100 temporarily to test.
2. In Blueprint, print the Strain value you're sending: `Print String | InString: Strain value`.
3. Remember: `Apply Radial Impulse` alone doesn't break Chaos clusters — you must also call `Apply External Strain`.

---

### ❌ Problem: Entire mesh explodes at once (no staged breaking)

**Cause:** Max Cluster Level is 0 or the GC only has one fracture level.

**Fix:**
1. In Fracture Editor → select all chunks → **Cluster** them into groups of 4–6.
2. Check `Max Level` in GC settings — set to **2**.
3. Verify you used **Clustered Voronoi** for first fracture pass.

---

### ❌ Problem: Chunks fly backward (wrong impulse direction)

**Cause:** Impulse origin is behind the mesh.

**Fix:** Use `HitResult.ImpactNormal * -1` as the impulse direction, and place the `Apply Radial Impulse` origin at `HitResult.Location` (the point of impact, not the projectile's start).

---

### ❌ Problem: Performance drops to 15 FPS when two mechs die

**Cause:** Too many debris chunks simulating simultaneously.

**Fix (quick):**
1. Reduce site count per GC to **15 max**.
2. Enable **Remove On Sleep** (5cm velocity threshold, 1.5s timer).
3. Add cleanup timer: destroy all GC components 4 seconds after death.

**Fix (proper):**
- Implement the debris cap system from Section 7.3.
- Enable `Cull Size: 5.0` to auto-remove tiny chips.

---

### ❌ Problem: UE5 crashes when loading the level with many GCs

**Cause:** Too many Geometry Collections in one level.

**Fix:**
- Use level streaming — load arena objects via sublevel, unload when not in arena.
- Keep only 2–3 mechs' worth of GCs in memory at once (object pooling).

---

### ❌ Problem: GC chunks fall through the floor

**Cause:** Collision preset mismatch.

**Fix:** In the GC's Details → **Chaos Physics** → set **Collision Group** to `0`. Ensure arena floor has `BlockAll` collision. If still clipping: increase `Default Broadphase Settings → Min Cells Per Axis` in Project Settings.

---

*Last updated: CrashFrame Circuit — Pre-Alpha Dev*
*See also: `blueprint_cookbook.md` for Blueprint trigger setup*
