# CrashFrame Circuit Backend API
"""
seed_parts.py — Populate the mech_parts table with the initial catalog.

Usage:
    python seed_parts.py

The script is idempotent: it skips any part whose part_id_str already exists.
"""

import os
import sys
from pathlib import Path

# Ensure the backend directory is on sys.path so we can import app/models
sys.path.insert(0, str(Path(__file__).parent))

os.makedirs("logs", exist_ok=True)

from loguru import logger
from app import create_app
from models import MechPart, db

# ---------------------------------------------------------------------------
# Parts catalog definition
# ---------------------------------------------------------------------------

PARTS: list[dict] = [
    # -----------------------------------------------------------------------
    # CHASSIS (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "chassis_viper_light",
        "name": "Viper-7 Light Frame",
        "part_class": "chassis",
        "rarity": "Common",
        "health_bonus": 80,
        "speed_modifier": 1.35,
        "weight": 0.7,
        "damage_multiplier": 0.9,
        "unlock_cost": 0,
        "description": (
            "A stripped-down racing frame salvaged from the Nuevo Laredo underground circuit. "
            "Sacrifices armour plating for blistering lateral movement. "
            "Favoured by scout pilots who strike from the blind side."
        ),
    },
    {
        "part_id_str": "chassis_ironclad_medium",
        "name": "Ironclad MK-II Medium Frame",
        "part_class": "chassis",
        "rarity": "Common",
        "health_bonus": 160,
        "speed_modifier": 1.0,
        "weight": 1.0,
        "damage_multiplier": 1.0,
        "unlock_cost": 0,
        "description": (
            "The workhorse frame that every arena rookie starts with. "
            "Balanced stat profile allows flexible loadout decisions without "
            "compromising offensive or defensive capability."
        ),
    },
    {
        "part_id_str": "chassis_goliath_heavy",
        "name": "Goliath Siege Frame",
        "part_class": "chassis",
        "rarity": "Rare",
        "health_bonus": 320,
        "speed_modifier": 0.65,
        "weight": 2.0,
        "damage_multiplier": 1.25,
        "unlock_cost": 1800,
        "description": (
            "Originally engineered for orbital construction platforms, the Goliath "
            "can absorb a missile salvo without flinching. Slow, but devastating "
            "in close-quarters crush zones."
        ),
    },

    # -----------------------------------------------------------------------
    # LEFT ARM (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "left_arm_pulse_cannon",
        "name": "Pulse-Fang Cannon",
        "part_class": "left_arm",
        "rarity": "Common",
        "health_bonus": 10,
        "speed_modifier": 1.0,
        "weight": 0.8,
        "damage_multiplier": 1.1,
        "unlock_cost": 400,
        "description": (
            "A rapid-cycling electromagnetic cannon that fires concussive pulse bursts. "
            "High fire rate with moderate single-hit damage. Pairs well with "
            "a heavy right arm to balance burst vs sustained pressure."
        ),
    },
    {
        "part_id_str": "left_arm_shield_bastion",
        "name": "Bastion Reactive Shield",
        "part_class": "left_arm",
        "rarity": "Rare",
        "health_bonus": 60,
        "speed_modifier": 0.9,
        "weight": 1.3,
        "damage_multiplier": 0.6,
        "unlock_cost": 1200,
        "description": (
            "An adaptive energy-barrier shield that disperses kinetic and thermal "
            "impact. Activating it locks your left arm in a blocking stance, "
            "but incoming damage is halved for the duration."
        ),
    },
    {
        "part_id_str": "left_arm_gravehammer",
        "name": "Gravehammer Kinetic Maul",
        "part_class": "left_arm",
        "rarity": "Epic",
        "health_bonus": 0,
        "speed_modifier": 0.85,
        "weight": 1.6,
        "damage_multiplier": 1.75,
        "unlock_cost": 3500,
        "description": (
            "Forbidden in three planetary federations for causing structural collapses. "
            "This gravity-amplified maul channels a compressed singularity field into "
            "every swing, capable of one-shotting lightweight mechs at point-blank range."
        ),
    },

    # -----------------------------------------------------------------------
    # RIGHT ARM (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "right_arm_scattershot",
        "name": "Scattershot Fragmentation Launcher",
        "part_class": "right_arm",
        "rarity": "Common",
        "health_bonus": 10,
        "speed_modifier": 1.0,
        "weight": 0.9,
        "damage_multiplier": 1.05,
        "unlock_cost": 400,
        "description": (
            "A wide-spread fragmentary warhead launcher designed for area denial. "
            "Ineffective at range but lethal in corridor fights where targets "
            "cannot dodge the shrapnel spread pattern."
        ),
    },
    {
        "part_id_str": "right_arm_sniper_railgun",
        "name": "Oblivion-Class Railgun",
        "part_class": "right_arm",
        "rarity": "Rare",
        "health_bonus": 0,
        "speed_modifier": 0.95,
        "weight": 1.1,
        "damage_multiplier": 1.55,
        "unlock_cost": 1500,
        "description": (
            "Magnetically accelerates a tungsten sabot to hypersonic velocity. "
            "Deals catastrophic single-target damage through multiple layers of armour. "
            "Slow reload leaves pilots exposed between shots."
        ),
    },
    {
        "part_id_str": "right_arm_nanoblade_vortex",
        "name": "Nanoblade Vortex Gauntlet",
        "part_class": "right_arm",
        "rarity": "Epic",
        "health_bonus": 20,
        "speed_modifier": 1.1,
        "weight": 0.7,
        "damage_multiplier": 1.4,
        "unlock_cost": 3200,
        "description": (
            "A spinning vortex of self-guided monomolecular blades that shred "
            "armour plating on contact. Controlled remotely by the pilot's neural "
            "link, allowing devastating flanking attacks without direct arm engagement."
        ),
    },

    # -----------------------------------------------------------------------
    # HEAD (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "head_scout_visor",
        "name": "Scout Recon Visor",
        "part_class": "head",
        "rarity": "Common",
        "health_bonus": 15,
        "speed_modifier": 1.05,
        "weight": 0.4,
        "damage_multiplier": 1.0,
        "unlock_cost": 300,
        "description": (
            "A lightweight multi-spectrum visor offering enhanced threat detection "
            "at distance. Auto-highlights enemy weak points through smoke and thermal "
            "interference. Standard issue for light-frame pilots."
        ),
    },
    {
        "part_id_str": "head_fortress_helm",
        "name": "Fortress Siege Helmet",
        "part_class": "head",
        "rarity": "Rare",
        "health_bonus": 80,
        "speed_modifier": 0.92,
        "weight": 1.0,
        "damage_multiplier": 1.0,
        "unlock_cost": 1100,
        "description": (
            "A triple-layered reinforced cranial housing built to survive direct "
            "artillery impact. Houses a redundant targeting computer that keeps "
            "lock-ons active even after sensor array damage."
        ),
    },
    {
        "part_id_str": "head_void_oracle",
        "name": "Void Oracle Neural Crown",
        "part_class": "head",
        "rarity": "Epic",
        "health_bonus": 30,
        "speed_modifier": 1.08,
        "weight": 0.5,
        "damage_multiplier": 1.2,
        "unlock_cost": 4000,
        "description": (
            "Fuses the pilot's consciousness directly with the arena's electromagnetic "
            "field, granting precognitive battlefield awareness. Enemies within 60m "
            "are outlined through walls. Banned from most amateur leagues."
        ),
    },

    # -----------------------------------------------------------------------
    # LEGS (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "legs_sprint_striders",
        "name": "Sprint Strider Bipeds",
        "part_class": "legs",
        "rarity": "Common",
        "health_bonus": 20,
        "speed_modifier": 1.3,
        "weight": 0.6,
        "damage_multiplier": 1.0,
        "unlock_cost": 350,
        "description": (
            "Lightweight carbon-fibre legs with overdrive actuators. "
            "Primarily used for rapid repositioning and hit-and-run tactics. "
            "The spring-loaded thighs also enable a burst-jump dodge mechanic."
        ),
    },
    {
        "part_id_str": "legs_tank_treads",
        "name": "Rampart Heavy Treads",
        "part_class": "legs",
        "rarity": "Rare",
        "health_bonus": 100,
        "speed_modifier": 0.6,
        "weight": 2.2,
        "damage_multiplier": 1.0,
        "unlock_cost": 1400,
        "description": (
            "Converts your mech into a rolling fortress. The wide tread base "
            "prevents knockback from explosive blasts and provides a stable "
            "firing platform for heavy artillery loadouts."
        ),
    },
    {
        "part_id_str": "legs_phantom_stilts",
        "name": "Phantom Gravity Stilts",
        "part_class": "legs",
        "rarity": "Epic",
        "health_bonus": 40,
        "speed_modifier": 1.45,
        "weight": 0.8,
        "damage_multiplier": 1.0,
        "unlock_cost": 3800,
        "description": (
            "Harness fractional anti-gravity to glide across terrain at impossible "
            "angles. Activate Phantom Mode for 4 seconds of near-silent movement — "
            "footstep vibration sensors cannot detect you."
        ),
    },

    # -----------------------------------------------------------------------
    # BACKPACK (3)
    # -----------------------------------------------------------------------
    {
        "part_id_str": "backpack_thruster_pack",
        "name": "Afterburner Thruster Pack",
        "part_class": "backpack",
        "rarity": "Common",
        "health_bonus": 0,
        "speed_modifier": 1.2,
        "weight": 0.7,
        "damage_multiplier": 1.0,
        "unlock_cost": 450,
        "description": (
            "A dual-nozzle chemical thruster array that grants short-duration "
            "aerial boosts. Useful for reaching elevated positions or escaping "
            "grapple attempts. Fuel regenerates over 8 seconds between uses."
        ),
    },
    {
        "part_id_str": "backpack_missile_battery",
        "name": "Hydra-9 Missile Battery",
        "part_class": "backpack",
        "rarity": "Rare",
        "health_bonus": 0,
        "speed_modifier": 0.88,
        "weight": 1.5,
        "damage_multiplier": 1.35,
        "unlock_cost": 2000,
        "description": (
            "A rack of nine self-guided micro-missiles launched in a fan spread. "
            "Excellent for suppressing grouped enemies or applying persistent zone "
            "denial. Reload time requires pilot to seek cover post-volley."
        ),
    },
    {
        "part_id_str": "backpack_aegis_reactor",
        "name": "Aegis Overcharge Reactor",
        "part_class": "backpack",
        "rarity": "Epic",
        "health_bonus": 50,
        "speed_modifier": 1.0,
        "weight": 1.2,
        "damage_multiplier": 1.3,
        "unlock_cost": 4500,
        "description": (
            "A volatile zero-point energy cell that feeds excess power to all "
            "weapon systems simultaneously. Active Overcharge mode surges damage "
            "output by 30% for 10 seconds before requiring a cooldown cycle. "
            "Catastrophic containment failure is… an occupational hazard."
        ),
    },
]

# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------

def seed():
    app = create_app()

    with app.app_context():
        added = 0
        skipped = 0

        for part_data in PARTS:
            existing = MechPart.query.filter_by(part_id_str=part_data["part_id_str"]).first()
            if existing:
                logger.debug(f"Skipping existing part: {part_data['part_id_str']}")
                skipped += 1
                continue

            part = MechPart(**part_data)
            db.session.add(part)
            added += 1
            logger.info(f"  + {part_data['part_class']:10s} [{part_data['rarity']:6s}] {part_data['name']}")

        db.session.commit()
        logger.success(
            f"Seeding complete — {added} part(s) added, {skipped} part(s) already existed."
        )


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    logger.info("=== CrashFrame Circuit — Parts Catalog Seeder ===")
    seed()
