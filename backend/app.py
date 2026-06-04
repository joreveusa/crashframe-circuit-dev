# CrashFrame Circuit Backend API

import sys
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from loguru import logger
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models import (
    MatchStats,
    MechLoadout,
    MechPart,
    Player,
    PlayerInventory,
    db,
)

# ---------------------------------------------------------------------------
# Loguru setup — remove default handler and add a clean, coloured stdout one
# ---------------------------------------------------------------------------
logger.remove()
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
        "<level>{message}</level>"
    ),
    level="DEBUG",
    colorize=True,
)
logger.add(
    "logs/crashframe.log",
    rotation="10 MB",
    retention="14 days",
    level="INFO",
    encoding="utf-8",
)


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for all /api/* routes
    CORS(
        app,
        resources={r"/api/*": {"origins": Config.CORS_ORIGINS}},
        supports_credentials=True,
    )

    # Init extensions
    db.init_app(app)
    JWTManager(app)

    with app.app_context():
        db.create_all()
        logger.info("Database tables verified / created.")

    # Register blueprints / routes
    _register_routes(app)

    return app


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _json_error(message: str, status: int = 400, **extra) -> tuple:
    """Return a standardised JSON error response."""
    body = {"error": message, "status": status}
    body.update(extra)
    return jsonify(body), status


def _player_or_404(player_id: int):
    """Return Player row or raise a 404 JSON response."""
    player = db.session.get(Player, player_id)
    if player is None:
        return None, _json_error("Player not found", 404)
    return player, None


def _owner_required(f):
    """Decorator: ensure the JWT identity matches the requested player_id route param."""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_id = int(get_jwt_identity())
        player_id = kwargs.get("player_id")
        if player_id is not None and current_id != int(player_id):
            return _json_error("Forbidden — you can only access your own data.", 403)
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def _register_routes(app: Flask) -> None:  # noqa: C901

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "CrashFrame Circuit API"}), 200

    # ------------------------------------------------------------------
    # Auth — Register
    # ------------------------------------------------------------------
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.get_json(silent=True)
        if not data:
            return _json_error("Request body must be JSON.")

        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not username or not email or not password:
            return _json_error("username, email, and password are required.")

        if len(password) < 8:
            return _json_error("Password must be at least 8 characters.")

        if Player.query.filter_by(username=username).first():
            return _json_error("Username already taken.", 409)

        if Player.query.filter_by(email=email).first():
            return _json_error("Email already registered.", 409)

        player = Player(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(player)
        db.session.flush()  # get player.id before commit

        # Create a blank loadout for the new pilot
        loadout = MechLoadout(player_id=player.id)
        db.session.add(loadout)
        db.session.commit()

        token = create_access_token(identity=str(player.id))
        logger.info(f"New pilot registered: {username} (id={player.id})")

        return jsonify({"message": "Registration successful", "token": token, "player": player.to_dict()}), 201

    # ------------------------------------------------------------------
    # Auth — Login
    # ------------------------------------------------------------------
    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.get_json(silent=True)
        if not data:
            return _json_error("Request body must be JSON.")

        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return _json_error("username and password are required.")

        player = Player.query.filter_by(username=username).first()
        if player is None or not check_password_hash(player.password_hash, password):
            return _json_error("Invalid credentials.", 401)

        token = create_access_token(identity=str(player.id))
        logger.info(f"Pilot logged in: {username} (id={player.id})")

        return jsonify({"message": "Login successful", "token": token, "player": player.to_dict()}), 200

    # ------------------------------------------------------------------
    # Player — Loadout GET
    # ------------------------------------------------------------------
    @app.route("/api/player/<int:player_id>/loadout", methods=["GET"])
    @jwt_required()
    def get_loadout(player_id: int):
        player, err = _player_or_404(player_id)
        if err:
            return err

        loadout = player.loadout
        if loadout is None:
            return _json_error("Loadout not found for this player.", 404)

        return jsonify({"loadout": loadout.to_dict()}), 200

    # ------------------------------------------------------------------
    # Player — Loadout POST (update)
    # ------------------------------------------------------------------
    @app.route("/api/player/<int:player_id>/loadout", methods=["POST"])
    @_owner_required
    def update_loadout(player_id: int):
        player, err = _player_or_404(player_id)
        if err:
            return err

        data = request.get_json(silent=True)
        if not data:
            return _json_error("Request body must be JSON.")

        loadout = player.loadout
        if loadout is None:
            loadout = MechLoadout(player_id=player_id)
            db.session.add(loadout)

        allowed_slots = {
            "chassis_part_id",
            "left_arm_id",
            "right_arm_id",
            "head_id",
            "legs_id",
            "backpack_id",
            "paint_primary",
            "paint_secondary",
            "paint_accent",
        }

        # Validate that part slots reference parts in the player's inventory
        part_slots = {k for k in allowed_slots if k not in {"paint_primary", "paint_secondary", "paint_accent"}}
        owned_part_ids = {inv.part_id for inv in player.inventory}

        for slot in part_slots:
            if slot in data and data[slot] is not None:
                if data[slot] not in owned_part_ids:
                    return _json_error(
                        f"Part '{data[slot]}' for slot '{slot}' is not in your inventory.", 422
                    )

        for field in allowed_slots:
            if field in data:
                setattr(loadout, field, data[field])

        loadout.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        logger.debug(f"Loadout updated for player {player_id}")

        return jsonify({"message": "Loadout updated", "loadout": loadout.to_dict()}), 200

    # ------------------------------------------------------------------
    # Player — Inventory
    # ------------------------------------------------------------------
    @app.route("/api/player/<int:player_id>/inventory", methods=["GET"])
    @jwt_required()
    def get_inventory(player_id: int):
        player, err = _player_or_404(player_id)
        if err:
            return err

        # Enrich inventory items with full part details
        inventory_items = []
        for inv in player.inventory:
            part = MechPart.query.filter_by(part_id_str=inv.part_id).first()
            item = inv.to_dict()
            item["part_details"] = part.to_dict() if part else None
            inventory_items.append(item)

        return jsonify({"inventory": inventory_items, "total": len(inventory_items)}), 200

    # ------------------------------------------------------------------
    # Player — Stats
    # ------------------------------------------------------------------
    @app.route("/api/player/<int:player_id>/stats", methods=["GET"])
    @jwt_required()
    def get_stats(player_id: int):
        player, err = _player_or_404(player_id)
        if err:
            return err

        matches = player.match_stats

        totals = {
            "kills": sum(m.kills for m in matches),
            "deaths": sum(m.deaths for m in matches),
            "assists": sum(m.assists for m in matches),
            "wins": sum(m.wins for m in matches),
            "losses": sum(m.losses for m in matches),
            "matches_played": len(matches),
        }

        total_matches = totals["wins"] + totals["losses"]
        totals["win_rate"] = (
            round(totals["wins"] / total_matches * 100, 1) if total_matches > 0 else 0.0
        )
        totals["kd_ratio"] = (
            round(totals["kills"] / max(totals["deaths"], 1), 2)
        )

        return jsonify(
            {
                "player": player.to_dict(),
                "aggregate_stats": totals,
                "match_history": [m.to_dict() for m in matches],
            }
        ), 200

    # ------------------------------------------------------------------
    # Parts Catalog
    # ------------------------------------------------------------------
    @app.route("/api/parts/catalog", methods=["GET"])
    def get_catalog():
        part_class = request.args.get("class")
        rarity = request.args.get("rarity")

        query = MechPart.query

        if part_class:
            query = query.filter_by(part_class=part_class)
        if rarity:
            query = query.filter_by(rarity=rarity)

        parts = query.order_by(MechPart.part_class, MechPart.rarity, MechPart.name).all()

        # Group by class for convenience
        catalog: dict = {}
        for part in parts:
            catalog.setdefault(part.part_class, []).append(part.to_dict())

        return jsonify({"catalog": catalog, "total": len(parts)}), 200

    # ------------------------------------------------------------------
    # Leaderboard
    # ------------------------------------------------------------------
    @app.route("/api/leaderboard", methods=["GET"])
    def get_leaderboard():
        try:
            limit = min(int(request.args.get("limit", 25)), 100)
        except (TypeError, ValueError):
            limit = 25

        # Aggregate stats per player using subquery
        from sqlalchemy import func

        rows = (
            db.session.query(
                Player.id,
                Player.username,
                Player.level,
                Player.xp,
                func.coalesce(func.sum(MatchStats.kills), 0).label("total_kills"),
                func.coalesce(func.sum(MatchStats.deaths), 0).label("total_deaths"),
                func.coalesce(func.sum(MatchStats.wins), 0).label("total_wins"),
                func.coalesce(func.sum(MatchStats.losses), 0).label("total_losses"),
            )
            .outerjoin(MatchStats, MatchStats.player_id == Player.id)
            .group_by(Player.id)
            .order_by(
                func.coalesce(func.sum(MatchStats.wins), 0).desc(),
                Player.xp.desc(),
            )
            .limit(limit)
            .all()
        )

        board = []
        for rank, row in enumerate(rows, start=1):
            total_matches = row.total_wins + row.total_losses
            board.append(
                {
                    "rank": rank,
                    "player_id": row.id,
                    "username": row.username,
                    "level": row.level,
                    "xp": row.xp,
                    "total_kills": row.total_kills,
                    "total_deaths": row.total_deaths,
                    "total_wins": row.total_wins,
                    "total_losses": row.total_losses,
                    "win_rate": (
                        round(row.total_wins / total_matches * 100, 1)
                        if total_matches > 0
                        else 0.0
                    ),
                    "kd_ratio": round(row.total_kills / max(row.total_deaths, 1), 2),
                }
            )

        return jsonify({"leaderboard": board, "count": len(board)}), 200

    # ------------------------------------------------------------------
    # Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return _json_error("Endpoint not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return _json_error("Method not allowed.", 405)

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled server error")
        return _json_error("Internal server error. Check logs for details.", 500)

    logger.info("All routes registered.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    os.makedirs("logs", exist_ok=True)
    app = create_app()
    logger.info("Starting CrashFrame Circuit API…")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
    )
