# CrashFrame Circuit — Blueprint Cookbook

> **Audience:** Solo dev using AI assistance. Zero C++ required.
> **Engine:** Unreal Engine 5.3+
> **Parent project docs:** See also `chaos_physics_guide.md` and `asset_guide.md`

---

## Table of Contents

1. [How to Read This Guide](#1-how-to-read-this-guide)
2. [Creating BP_MechBase from Scratch](#2-creating-bp_mechbase-from-scratch)
3. [Enhanced Input Setup](#3-enhanced-input-setup)
4. [Boost / Thruster Fuel System](#4-boost--thruster-fuel-system)
5. [CoreTemp / Overheat System](#5-coretemp--overheat-system)
6. [Basic Projectile Blueprint](#6-basic-projectile-blueprint)
7. [AI-Assisted Blueprint Tips](#7-ai-assisted-blueprint-tips)

---

## 1. How to Read This Guide

### Node Notation

This cookbook uses a simple arrow notation to describe Blueprint graphs:

```
[NodeName | Input Pin = Value] → [NextNode | Input Pin = Value]
```

- **Square brackets** = a Blueprint node
- **Pipe** (`|`) = node parameters you need to set in the Details panel
- **Arrow** (`→`) = connect via execution wire (white)
- **Data wire connections** are shown as: `Variable Name ──▶ Target Pin`

### Example Read

```
[Event BeginPlay] → [Get Game Instance] → [Cast To GI_CrashFrame]
                                                    │
                                         (As GI Crash Frame) → [Set GameInstance Ref | Target = Self]
```

Means: On Begin Play, get the game instance, cast it, then store the reference.

---

## 2. Creating BP_MechBase from Scratch

`BP_MechBase` is the parent Blueprint all mech variants inherit from. Build this once.

### 2.1 Create the Blueprint

1. **Content Browser** → `Content/Mechs/Blueprints`
2. Right-click → **Blueprint Class**
3. Parent class: **Pawn** (not Character — mechs don't use UE's character movement)
4. Name it: `BP_MechBase`
5. Open it → **Class Defaults** tab

### 2.2 Add Components (Components Panel, top-left)

Add these components in order:

| Component | Name | Notes |
|-----------|------|-------|
| **Capsule Component** | `CollisionCapsule` | Set as Root. Capsule Half Height: 120, Radius: 60 |
| **Skeletal Mesh Component** | `MechMesh` | Attach to Root |
| **Spring Arm** | `CameraArm` | Attach to Root. Arm Length: 600, Socket Offset Z: 150 |
| **Camera** | `FollowCamera` | Attach to CameraArm |
| **Arrow** | `WeaponMountL` | Attach to MechMesh — left weapon socket |
| **Arrow** | `WeaponMountR` | Attach to MechMesh — right weapon socket |
| **Audio Component** | `ThrusterAudio` | Attach to MechMesh — looping engine sound |

### 2.3 Variables to Create

Click **+Variable** in the My Blueprint panel. Create these:

| Variable Name | Type | Category | Default |
|---------------|------|----------|---------|
| `MaxHealth` | Float | Stats | 1000.0 |
| `CurrentHealth` | Float | Stats | 1000.0 |
| `MaxBoostFuel` | Float | Boost | 100.0 |
| `BoostFuel` | Float | Boost | 100.0 |
| `BoostDrainRate` | Float | Boost | 25.0 |
| `BoostRechargeRate` | Float | Boost | 10.0 |
| `BoostForce` | Float | Boost | 4000.0 |
| `MoveSpeed` | Float | Movement | 600.0 |
| `TurnRate` | Float | Movement | 90.0 |
| `CoreTemp` | Float | Heat | 0.0 |
| `MaxCoreTemp` | Float | Heat | 100.0 |
| `OverheatCoolRate` | Float | Heat | 5.0 |
| `bIsBoosting` | Boolean | Boost | false |
| `bIsOverheated` | Boolean | Heat | false |
| `bIsDead` | Boolean | State | false |
| `GameInstanceRef` | Object (GI_CrashFrame) | Refs | — |
| `ActiveWeaponL` | Object (BP_WeaponBase) | Weapons | — |
| `ActiveWeaponR` | Object (BP_WeaponBase) | Weapons | — |

> **Tip:** Right-click any variable → **Expose on Spawn** so child blueprints can set initial values.

### 2.4 Event Graph: BeginPlay

```
[Event BeginPlay]
    → [Get Game Instance]
        → [Cast To GI_CrashFrame]
            │ Success ──→ [Set GameInstanceRef | Target=Self, Value=(As GI Crash Frame)]
            │
            └──→ [Set CurrentHealth | Value = MaxHealth]
                 → [Set BoostFuel | Value = MaxBoostFuel]
                 → [Set CoreTemp | Value = 0.0]
```

### 2.5 Event Graph: TakeDamage (Override)

Search for **Event AnyDamage** (or add via Override → AnyDamage):

```
[Event AnyDamage | Damage, DamageCauser, InstigatedBy]
    → [Branch | Condition: bIsDead]
        │ True ──→ [Return] (do nothing if already dead)
        │
        False ──→ [Set CurrentHealth | Value: CurrentHealth - Damage]
                      → [Clamp Float | Value=CurrentHealth, Min=0, Max=MaxHealth]
                          → [Set CurrentHealth | Value = Clamp result]
                              → [Branch | Condition: CurrentHealth <= 0]
                                  │ True ──→ [Set bIsDead | Value=true]
                                  │          → [Call MechDestroyed] (custom event, see below)
                                  │
                                  False ──→ [Add CoreTemp | Value = Damage * 0.1]
```

**Create Custom Event:** Right-click graph → **Add Custom Event** → name it `MechDestroyed`

```
[Custom Event: MechDestroyed]
    → [Spawn Emitter at Location | Emitter Template: NS_Explosion_Mech_Large, Location: Self Location]
    → [Play Sound at Location | Sound: SFX_Mech_Explode]
    → [Delay | Duration: 2.0]
        → [Destroy Actor]
```

---

## 3. Enhanced Input Setup

Enhanced Input replaces the old Input Action system. It's more powerful and required for UE5.4+.

### 3.1 Create Input Actions

In `Content/_Core`, create these **Input Action** assets (Right-click → Input → Input Action):

| Asset Name | Value Type | Description |
|------------|------------|-------------|
| `IA_Move` | Axis2D (Vector2D) | WASD movement |
| `IA_Look` | Axis2D (Vector2D) | Mouse look |
| `IA_Boost` | Digital (bool) | Shift/L2 — hold to boost |
| `IA_FireL` | Digital (bool) | Left click / L1 — fire left weapon |
| `IA_FireR` | Digital (bool) | Right click / R1 — fire right weapon |
| `IA_LockOn` | Digital (bool) | Middle mouse / R3 — lock on |
| `IA_Dodge` | Digital (bool) | Space / X — quick dodge |

### 3.2 Create Input Mapping Context

Right-click → **Input → Input Mapping Context** → name it `IMC_Mech_KBM` (keyboard/mouse)

Open it and add bindings:

| Action | Key | Modifiers |
|--------|-----|-----------|
| IA_Move | W | Swizzle Input Axis (YXZ) |
| IA_Move | S | Negate + Swizzle |
| IA_Move | A | — |
| IA_Move | D | Negate |
| IA_Look | Mouse X | — |
| IA_Look | Mouse Y | Negate |
| IA_Boost | Left Shift | — |
| IA_FireL | Left Mouse Button | — |
| IA_FireR | Right Mouse Button | — |
| IA_LockOn | Middle Mouse Button | — |
| IA_Dodge | Space Bar | — |

> **Make a second context:** `IMC_Mech_Gamepad` for controller support.

### 3.3 Wire Enhanced Input in BP_MechBase

In **Event BeginPlay**, after the existing nodes, add:

```
[Get Player Controller | Player Index: 0]
    → [Cast To PC_CrashFrame]
        │ Success ──→ [Get Enhanced Input Local Player Subsystem | Target=(As PC_CrashFrame)]
                          → [Add Mapping Context | Mapping Context: IMC_Mech_KBM, Priority: 0]
```

### 3.4 Bind Input Actions in the Event Graph

Right-click → **Enhanced Action Events** → pick each IA:

**Move:**
```
[Enhanced Input Action IA_Move | Action Value]
    → (ActionValue.XY) ──▶ [Add Movement Input | WorldDirection: Forward Vector * X]
    → (ActionValue.XY) ──▶ [Add Movement Input | WorldDirection: Right Vector * Y]
```

**Look (Mouse):**
```
[Enhanced Input Action IA_Look | Action Value]
    → X ──▶ [Add Controller Yaw Input | Val: X * TurnRate * Delta Seconds]
    → Y ──▶ [Add Controller Pitch Input | Val: Y * TurnRate * Delta Seconds]
```

**Boost (hold):**
```
[Enhanced Input Action IA_Boost]
    │ Triggered ──→ [Set bIsBoosting | true] → [Call StartBoost] (custom event)
    │ Completed ──→ [Set bIsBoosting | false] → [Call StopBoost] (custom event)
```

**Fire Left:**
```
[Enhanced Input Action IA_FireL]
    │ Started ──→ [Is Valid | Object: ActiveWeaponL]
                      │ Valid ──→ [Call FireWeapon | Target: ActiveWeaponL]
```

**Fire Right:**
```
[Enhanced Input Action IA_FireR]
    │ Started ──→ [Is Valid | Object: ActiveWeaponR]
                      │ Valid ──→ [Call FireWeapon | Target: ActiveWeaponR]
```

---

## 4. Boost / Thruster Fuel System

The boost system uses a **Timeline** node for smooth fuel drain/recharge curves.

### 4.1 Create the Timeline

In BP_MechBase Event Graph, right-click → **Add Timeline** → name it `TL_BoostFuel`

Inside the timeline editor:
- Click **+Float Track** → name it `FuelValue`
- Add keyframe at Time=0, Value=1.0
- Add keyframe at Time=4.0, Value=0.0
- Set **Length:** 4.0 (4 seconds of full boost before empty)
- Enable **Loop:** No

### 4.2 StartBoost Custom Event

```
[Custom Event: StartBoost]
    → [Branch | Condition: BoostFuel > 5.0]
        │ True ──→ [Branch | Condition: NOT bIsOverheated]
                       │ True ──→ [Play Timeline TL_BoostFuel from Start]
                       │          → [Set ThrusterAudio Volume | Volume: 1.0]
                       │
                       False ──→ [Play Sound 2D | Sound: SFX_UI_BoostBlocked]
        │
        False ──→ [Play Sound 2D | Sound: SFX_UI_BoostEmpty]
```

### 4.3 Timeline Update Pin

The Timeline's **Update** execution pin fires every frame while active:

```
[TL_BoostFuel | Update]
    → (FuelValue) ──▶ [Multiply Float | A: FuelValue, B: MaxBoostFuel]
                           → [Set BoostFuel | Value = result]
    → [Add Force | Target: MechMesh | Force: (ForwardVector * BoostForce * 100)]
    → [Add CoreTemp | Value: 1.5 * Delta Seconds]   ← boosting heats you up
```

### 4.4 StopBoost Custom Event

```
[Custom Event: StopBoost]
    → [Stop Timeline TL_BoostFuel]
    → [Set ThrusterAudio Volume | Volume: 0.3]  ← idle engine sound
    → [Start Boost Recharge] (call another custom event with a timer)
```

### 4.5 Boost Recharge (Tick-based)

In **Event Tick**:

```
[Event Tick | DeltaSeconds]
    → [Branch | Condition: NOT bIsBoosting AND BoostFuel < MaxBoostFuel]
        │ True ──→ [Set BoostFuel | Value: BoostFuel + (BoostRechargeRate * DeltaSeconds)]
                       → [Clamp Float | Value=BoostFuel, Min=0, Max=MaxBoostFuel]
                           → [Set BoostFuel | Value = Clamp result]
```

> **Performance tip:** Consider using a timer instead of Event Tick for the recharge. Right-click → **Set Timer by Function Name**, call it every 0.1s. Less overhead.

---

## 5. CoreTemp / Overheat System

Weapons heating, boosting, and taking damage all raise CoreTemp. At 100, you're locked out of boost and weapons for a cooldown period.

### 5.1 AddCoreTemp Function

Create a new **Function** (not event) called `AddCoreTemp`:

**Input parameter:** `Amount` (Float)

```
[Input: Amount]
    → [Branch | Condition: NOT bIsOverheated]
        │ True ──→ [Set CoreTemp | Value: CoreTemp + Amount]
                       → [Clamp Float | Value=CoreTemp, Min=0, Max=MaxCoreTemp]
                           → [Set CoreTemp | Value = Clamp result]
                               → [Branch | Condition: CoreTemp >= MaxCoreTemp]
                                   │ True ──→ [Call TriggerOverheat]
```

### 5.2 TriggerOverheat Custom Event

```
[Custom Event: TriggerOverheat]
    → [Set bIsOverheated | true]
    → [Play Sound 2D | Sound: SFX_Mech_Overheat_Warning]
    → [Spawn Emitter Attached | Template: NS_Sparks_Damage_Heavy, AttachTo: MechMesh]
    → [Set Timer by Function Name | Function: "BeginCooldown", Time: 3.0, Looping: false]
```

### 5.3 BeginCooldown Function

Create **Function** `BeginCooldown`:

```
[Set CoreTemp | Value: 0.0]
    → [Set bIsOverheated | false]
    → [Play Sound 2D | Sound: SFX_Mech_Cooldown_Complete]
```

### 5.4 Passive Cooling (Event Tick)

CoreTemp slowly drops when you're not overheated:

```
[Event Tick | DeltaSeconds]
    → (existing tick chain...)
    → [Branch | Condition: CoreTemp > 0 AND NOT bIsOverheated]
        │ True ──→ [Set CoreTemp | Value: CoreTemp - (OverheatCoolRate * DeltaSeconds)]
                       → [Clamp Float | Value=CoreTemp, Min=0, Max=MaxCoreTemp]
                           → [Set CoreTemp | Value = Clamp result]
```

### 5.5 Display CoreTemp in HUD

In `WBP_HUD_CoreTemp` Widget Blueprint:

1. Add a **Progress Bar** widget, name it `PB_HeatBar`
2. Bind the **Percent** property:
   - Click the orange **Bind** button on Percent
   - In the binding function:
     ```
     [Get Owning Player Pawn]
         → [Cast To BP_MechBase]
             │ (As BP Mech Base) → [Get CoreTemp]
                                       → [Divide Float | A: CoreTemp, B: MaxCoreTemp]
                                           → [Return Node | Return Value = Divide result]
     ```
3. Set the **Fill Color** binding: lerp from green (0) → orange (0.5) → red (1.0) using a **Linear Color Lerp**

---

## 6. Basic Projectile Blueprint

Create `BP_Projectile_Base` in `Content/Weapons/Blueprints`

### 6.1 Components

| Component | Name | Settings |
|-----------|------|---------|
| **Sphere Collision** | `CollisionSphere` | Root. Radius: 15. Collision: BlockAll |
| **Static Mesh** | `ProjectileMesh` | Attach to Root. Assign small plasma bolt mesh |
| **Projectile Movement** | `ProjectileMovement` | See settings below |

**ProjectileMovement settings:**
- Initial Speed: **5000**
- Max Speed: **5000**
- Gravity Scale: **0.1** (slight arc)
- Homing: Off (for basic. Enable for missiles)

### 6.2 Variables

| Variable | Type | Default |
|----------|------|---------|
| `Damage` | Float | 50.0 |
| `ImpulsePower` | Float | 500.0 |
| `LifeSpan` | Float | 3.0 |
| `HeatGenerated` | Float | 5.0 |
| `InstigatorMech` | Object (BP_MechBase) | — |

### 6.3 Event Graph: BeginPlay

```
[Event BeginPlay]
    → [Set Life Span | Seconds: LifeSpan]
    → [Spawn Emitter Attached | Template: NS_Projectile_Trail_Plasma, AttachTo: ProjectileMesh]
```

### 6.4 Collision: OnHit

Select `CollisionSphere` → Details panel → **Events** → click **+** on **On Component Hit**

```
[On Component Hit | OtherActor, HitResult]
    → [Branch | Condition: OtherActor != InstigatorMech]   ← don't hit yourself
        │ True ──→ [Apply Point Damage | DamagedActor: OtherActor,
                   │                     BaseDamage: Damage,
                   │                     InstigatedBy: InstigatorMech Controller,
                   │                     HitLocation: HitResult.Location]
                   → [Apply Radial Impulse | Target: OtherActor Primitive Component,
                   │                          Origin: HitResult.Location,
                   │                          Radius: 200.0,
                   │                          Strength: ImpulsePower,
                   │                          Falloff: Linear]
                   → [Spawn Emitter at Location | Template: NS_Impact_Metal, Location: HitResult.Location]
                   → [Play Sound at Location | Sound: SFX_Weapon_Impact_Metal]
                   → [Destroy Actor]
```

### 6.5 Spawn the Projectile (from BP_WeaponBase)

In `BP_WeaponBase`, create function `FireWeapon`:

```
[Get World]
    → [Spawn Actor from Class | Class: BP_Projectile_Base,
       SpawnTransform: WeaponMuzzleSocket World Transform]
        → (Return Value) ──▶ [Set Damage | Target=Spawned Projectile, Value: WeaponDamage]
        → (Return Value) ──▶ [Set InstigatorMech | Target=Spawned Projectile, Value: OwnerMech]
```

---

## 7. AI-Assisted Blueprint Tips

### Prompts That Work

When using Gemini, Claude, or ChatGPT for Blueprint help, be specific about node names:

**Good prompt:**
> "In Unreal Engine 5 Blueprint, after [Event BeginPlay], how do I use [Get Game Instance] and [Cast To MyGameInstance] to store a reference? Give me the exact node names and pin connections."

**Good prompt:**
> "What's the difference between [Apply Point Damage] and [Apply Radial Damage] in UE5? Which should I use for a projectile that hits a specific mech part?"

**Good prompt for Gemini:**
> "I'm building a mech combat game in UE5. My BP_MechBase has a float variable called CoreTemp (max 100). Write me the Event Tick Blueprint logic to: 1) passively cool CoreTemp by 5 per second, 2) trigger an overheat state when it hits 100, 3) block the fire action while overheated."

### Screenshot Your Graphs

Before you compile, screenshot complex graphs. If you break something, you can paste the screenshot to an AI and ask: "What's wrong with this Blueprint graph?"

### Use Blueprint Comments

Select a group of nodes → **C** key → add a comment box. Label groups like:
- `// BOOST SYSTEM — drain on hold, recharge on release`
- `// OVERHEAT — blocks weapons and boost above 100 CoreTemp`

AI assistants can read your comments in screenshots and give better advice.

### Collapse Complex Sections

Select nodes → right-click → **Collapse Nodes** → name it descriptively. Keeps your graph readable and makes it easier to describe to an AI.

### Blueprint Interfaces (BPI)

For damage/interaction systems, create a **Blueprint Interface** `BPI_Damageable`:
- Function: `TakeMechDamage(Amount: Float, Source: BP_MechBase)`

Any Blueprint (mech, arena object) that implements this interface can receive damage without casting. Cleaner and faster.

---

*Last updated: CrashFrame Circuit — Pre-Alpha Dev*
*See also: `chaos_physics_guide.md` for Chaos destruction setup*
