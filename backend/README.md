# CrashFrame Circuit — Backend API

> Python / Flask REST API powering the CrashFrame Circuit mech arena game.

---

## Project Structure

```
backend/
├── app.py          # Flask app factory & all route handlers
├── models.py       # SQLAlchemy ORM models
├── config.py       # Config class (reads config.json)
├── config.json     # Runtime configuration (edit this!)
├── seed_parts.py   # One-time DB seeder for the parts catalog
├── requirements.txt
└── logs/           # Created automatically on first run
```

---

## Prerequisites

- Python 3.11+
- pip or a virtual-environment manager

---

## Quick Start (Local / SQLite)

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure

Edit **`config.json`** before running anything:

```json
{
  "DATABASE_URL": "sqlite:///crashframe.db",
  "JWT_SECRET_KEY": "replace-with-a-long-random-secret",
  "DEBUG": true,
  "CORS_ORIGINS": ["http://localhost:3000", "http://localhost:5173"],
  "JWT_ACCESS_TOKEN_EXPIRES_HOURS": 24
}
```

> **Important:** Change `JWT_SECRET_KEY` to a strong random value before deploying.  
> Generate one with: `python -c "import secrets; print(secrets.token_hex(32))"`

### 4. Seed the parts catalog

```bash
python seed_parts.py
```

This populates the `mech_parts` table with 18 parts (3 per slot, mixed rarities).  
The script is **idempotent** — safe to run multiple times.

### 5. Start the API server

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/auth/register` | Register a new pilot |
| `POST` | `/api/auth/login` | Login and receive JWT |
| `GET`  | `/api/parts/catalog` | Browse the parts catalog |
| `GET`  | `/api/leaderboard` | Top players by wins |

### Authenticated (Bearer token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/player/<id>/loadout` | Get a player's active loadout |
| `POST` | `/api/player/<id>/loadout` | Update loadout (owner only) |
| `GET`  | `/api/player/<id>/inventory` | List all owned parts |
| `GET`  | `/api/player/<id>/stats` | Aggregate match statistics |

Include the JWT token as a Bearer header:

```
Authorization: Bearer <token>
```

---

## Example Requests

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "IronPilot", "email": "pilot@arena.io", "password": "secure1234"}'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "IronPilot", "password": "secure1234"}'
```

### Browse Catalog (filter by class)

```bash
curl "http://localhost:5000/api/parts/catalog?class=chassis"
```

### Update Loadout

```bash
curl -X POST http://localhost:5000/api/player/1/loadout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "chassis_part_id": "chassis_ironclad_medium",
    "left_arm_id": "left_arm_pulse_cannon",
    "right_arm_id": "right_arm_scattershot",
    "head_id": "head_scout_visor",
    "legs_id": "legs_sprint_striders",
    "backpack_id": "backpack_thruster_pack",
    "paint_primary": "#0d1b2a",
    "paint_secondary": "#e63946",
    "paint_accent": "#457b9d"
  }'
```

---

## Production Deployment (PostgreSQL)

1. Install PostgreSQL and create a database.
2. Update `config.json`:
   ```json
   {
     "DATABASE_URL": "postgresql://user:password@host:5432/crashframe",
     "JWT_SECRET_KEY": "your-production-secret",
     "DEBUG": false,
     "CORS_ORIGINS": ["https://your-frontend-domain.com"]
   }
   ```
3. Run with a production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn "app:create_app()" --bind 0.0.0.0:5000 --workers 4
   ```

---

## Notes

- Passwords are hashed with **Werkzeug's PBKDF2-HMAC-SHA256**.
- JWT tokens expire after the number of hours configured in `JWT_ACCESS_TOKEN_EXPIRES_HOURS` (default: 24).
- All responses are `application/json`.
- Loadout updates validate that part IDs exist in the player's inventory — you must acquire parts before equipping them.
- Logs are written to `logs/crashframe.log` (10 MB rotation, 14-day retention).
