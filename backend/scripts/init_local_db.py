"""Initialize local SQLite database with all tables and sample seed data.

Runs without needing Docker or a PostgreSQL server, creating `cleanair.db` locally.
"""
import sqlite3
import uuid
from datetime import datetime, date

db_path = "cleanair.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Users
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    hashed_password TEXT,
    is_anonymous INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    is_verified INTEGER NOT NULL DEFAULT 0,
    preferred_language TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. User Profiles
cur.execute("""
CREATE TABLE IF NOT EXISTS user_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    latitude REAL DEFAULT 18.52,
    longitude REAL DEFAULT 73.85,
    city TEXT DEFAULT 'Pune',
    state TEXT DEFAULT 'Maharashtra',
    country TEXT DEFAULT 'India',
    pin_code TEXT DEFAULT '411001',
    has_children INTEGER DEFAULT 1,
    has_elderly INTEGER DEFAULT 0,
    has_asthma_respiratory INTEGER DEFAULT 1,
    has_pregnancy INTEGER DEFAULT 0,
    household_size INTEGER DEFAULT 3,
    home_type TEXT DEFAULT 'apartment',
    cooking_fuel TEXT DEFAULT 'lpg',
    has_kitchen_exhaust INTEGER DEFAULT 1,
    num_windows INTEGER DEFAULT 4,
    heating_type TEXT DEFAULT 'none',
    commute_mode TEXT DEFAULT 'two_wheeler_petrol',
    commute_distance_km REAL DEFAULT 10.0,
    budget_level TEXT DEFAULT 'medium',
    available_devices TEXT DEFAULT '["n95_mask", "purifier"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# 3. AQI Readings
cur.execute("""
CREATE TABLE IF NOT EXISTS aqi_readings (
    id TEXT PRIMARY KEY,
    lat_rounded REAL NOT NULL,
    lon_rounded REAL NOT NULL,
    station_id TEXT DEFAULT 'pune_central',
    source TEXT DEFAULT 'open_meteo',
    observed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aqi INTEGER DEFAULT 184,
    aqi_category TEXT DEFAULT 'Moderate',
    pm25 REAL DEFAULT 64.5,
    pm10 REAL DEFAULT 108.2,
    no2 REAL DEFAULT 38.6,
    so2 REAL DEFAULT 12.0,
    co REAL DEFAULT 1.2,
    o3 REAL DEFAULT 24.0,
    temperature_c REAL DEFAULT 24.2,
    humidity_pct REAL DEFAULT 58.0,
    wind_speed_ms REAL DEFAULT 1.8,
    temperature_inversion INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 4. Daily Plans
cur.execute("""
CREATE TABLE IF NOT EXISTS daily_plans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan_date DATE DEFAULT (date('now')),
    plan_json TEXT NOT NULL,
    total_pm25_reduction_ug_m3_h REAL DEFAULT 85.0,
    total_co2e_avoided_kg REAL DEFAULT 4.2,
    llm_model_used TEXT DEFAULT 'gemini-1.5-flash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# 5. Communities
cur.execute("""
CREATE TABLE IF NOT EXISTS communities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    community_type TEXT DEFAULT 'neighbourhood',
    city TEXT DEFAULT 'Pune',
    is_public INTEGER DEFAULT 1,
    member_count INTEGER DEFAULT 12,
    total_co2e_avoided_kg REAL DEFAULT 148.5,
    total_pm25_reduction_ug_m3_h REAL DEFAULT 1240.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 6. Community Members
cur.execute("""
CREATE TABLE IF NOT EXISTS community_members (
    id TEXT PRIMARY KEY,
    community_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    weekly_score REAL DEFAULT 45.0,
    total_score REAL DEFAULT 180.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Seed Sample Demo User & Community
demo_user_id = str(uuid.uuid4())
cur.execute("INSERT OR IGNORE INTO users (id, email, is_anonymous) VALUES (?, ?, ?)",
            (demo_user_id, "demo@cleanair.local", 1))

cur.execute("""
INSERT OR IGNORE INTO user_profiles 
(id, user_id, city, state, latitude, longitude, has_children, has_asthma_respiratory)
VALUES (?, ?, 'Pune', 'Maharashtra', 18.52, 73.85, 1, 1)
""", (str(uuid.uuid4()), demo_user_id))

cur.execute("""
INSERT OR IGNORE INTO aqi_readings 
(id, lat_rounded, lon_rounded, aqi, aqi_category, pm25, pm10, no2, temperature_inversion)
VALUES (?, 18.52, 73.85, 184, 'Moderate', 64.5, 108.2, 38.6, 1)
""", (str(uuid.uuid4()),))

cur.execute("""
INSERT OR IGNORE INTO communities (id, name, description, city, member_count, total_co2e_avoided_kg)
VALUES (?, 'Pune Clean Air Action Club', 'Neighbourhood collective reducing winter vehicle emissions in Kothrud & Shivajinagar', 'Pune', 28, 342.8)
""", (str(uuid.uuid4()),))

conn.commit()
conn.close()
print("Local database created and seeded: cleanair.db")
