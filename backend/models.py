# CrashFrame Circuit Backend API

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Player(db.Model):
    """Registered pilot who commands a mech in the arena."""

    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    credits = db.Column(db.Integer, nullable=False, default=1000)
    xp = db.Column(db.Integer, nullable=False, default=0)
    level = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    loadout = db.relationship(
        "MechLoadout", back_populates="player", uselist=False, cascade="all, delete-orphan"
    )
    inventory = db.relationship(
        "PlayerInventory", back_populates="player", cascade="all, delete-orphan"
    )
    match_stats = db.relationship(
        "MatchStats", back_populates="player", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "credits": self.credits,
            "xp": self.xp,
            "level": self.level,
            "created_at": self.created_at.isoformat(),
        }


class MechLoadout(db.Model):
    """The active mech configuration for a player.  One per player."""

    __tablename__ = "mech_loadouts"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False, unique=True, index=True
    )

    # Part slot references (store the part_id_str strings for easy lookup)
    chassis_part_id = db.Column(db.String(64), nullable=True)
    left_arm_id = db.Column(db.String(64), nullable=True)
    right_arm_id = db.Column(db.String(64), nullable=True)
    head_id = db.Column(db.String(64), nullable=True)
    legs_id = db.Column(db.String(64), nullable=True)
    backpack_id = db.Column(db.String(64), nullable=True)

    # Cosmetics
    paint_primary = db.Column(db.String(7), nullable=False, default="#1a1a2e")
    paint_secondary = db.Column(db.String(7), nullable=False, default="#e94560")
    paint_accent = db.Column(db.String(7), nullable=False, default="#0f3460")

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    player = db.relationship("Player", back_populates="loadout")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "chassis_part_id": self.chassis_part_id,
            "left_arm_id": self.left_arm_id,
            "right_arm_id": self.right_arm_id,
            "head_id": self.head_id,
            "legs_id": self.legs_id,
            "backpack_id": self.backpack_id,
            "paint_primary": self.paint_primary,
            "paint_secondary": self.paint_secondary,
            "paint_accent": self.paint_accent,
            "updated_at": self.updated_at.isoformat(),
        }


class PlayerInventory(db.Model):
    """Tracks every mech part a player owns."""

    __tablename__ = "player_inventory"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False, index=True
    )
    part_id = db.Column(db.String(64), nullable=False)
    acquired_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    player = db.relationship("Player", back_populates="inventory")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "part_id": self.part_id,
            "acquired_at": self.acquired_at.isoformat(),
        }


class MatchStats(db.Model):
    """One row per match played by a player."""

    __tablename__ = "match_stats"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False, index=True
    )
    kills = db.Column(db.Integer, nullable=False, default=0)
    deaths = db.Column(db.Integer, nullable=False, default=0)
    assists = db.Column(db.Integer, nullable=False, default=0)
    wins = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)
    match_date = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    player = db.relationship("Player", back_populates="match_stats")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "player_id": self.player_id,
            "kills": self.kills,
            "deaths": self.deaths,
            "assists": self.assists,
            "wins": self.wins,
            "losses": self.losses,
            "match_date": self.match_date.isoformat(),
        }


class MechPart(db.Model):
    """Defines a part in the global parts catalog."""

    __tablename__ = "mech_parts"

    id = db.Column(db.Integer, primary_key=True)
    part_id_str = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128), nullable=False)
    part_class = db.Column(db.String(32), nullable=False)   # chassis, left_arm, right_arm, head, legs, backpack
    rarity = db.Column(db.String(16), nullable=False, default="Common")  # Common, Rare, Epic
    health_bonus = db.Column(db.Integer, nullable=False, default=0)
    speed_modifier = db.Column(db.Float, nullable=False, default=1.0)
    weight = db.Column(db.Float, nullable=False, default=1.0)
    damage_multiplier = db.Column(db.Float, nullable=False, default=1.0)
    unlock_cost = db.Column(db.Integer, nullable=False, default=500)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "part_id_str": self.part_id_str,
            "name": self.name,
            "part_class": self.part_class,
            "rarity": self.rarity,
            "health_bonus": self.health_bonus,
            "speed_modifier": self.speed_modifier,
            "weight": self.weight,
            "damage_multiplier": self.damage_multiplier,
            "unlock_cost": self.unlock_cost,
            "description": self.description,
        }
