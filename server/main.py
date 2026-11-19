# ==============================================================================
# Program: main.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Primary asynchronous FastAPI backend orchestrating The Sacred Tech game services.
#          Manages SQLite player progression databases with atomic transactions and rolling limits,
#          exposes REST endpoints for chapter code templates and Docker sandbox evaluation,
#          bridges real-time bidirectional WebSockets to containerized PTY shells and QEMU telnet streams,
#          and hosts static game client assets bound strictly to loopback interfaces.
# ==============================================================================

# How this file fits the app: the whole backend of "The Sacred Tech" (a coding-lesson JRPG). The browser
# client (client/index.html + client/app.js) is served by this same process
# and talks to it in three ways: REST under /api (save games, load/compile chapter code, diagnostics),
# WebSockets under /ws (a live shell, the TempleOS serial console, a dev auto-reload signal),
# and plain static files at "/". The heavy lifting is delegated: server/sandbox_manager.py runs a chapter's
# validator in Docker, server/qemu_launcher.py starts QEMU or a mock HolyC server.
# Run it with `python server/main.py` (binds 127.0.0.1:8000 only) or via scripts/run_dev.sh; build a
# single-file app with server/build_desktop.py (PyInstaller sets sys._MEIPASS, see below).
# Data: SQLite file save_data/save_state.db (override with ZEUS_SAVE_DB_PATH): table player_state, newest row
# = current save, history trimmed to 50 rows. Player code lives in save_data/relic_save/.
# Security model: loopback only, CORS limited to localhost origins. /ws/shell hands out a real shell, and
# CORS does not apply to WebSockets, so it is guarded separately (see server/shell_guard.py): the handshake
# must carry a loopback Origin and Host, the first frame must be the per-run random token served by
# /api/shell-token, and a shell on the HOST (Docker down) is only given when ZEUS_ALLOW_HOST_SHELL=1.
# Also, error handlers return str(exception) to the client, and the compile endpoint runs player code (inside
# Docker when available, but directly on the host as the fallback).
import asyncio
from contextlib import asynccontextmanager
import logging
import os
import sqlite3
import sys
from typing import Set

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Access-control helpers for /ws/shell. Same dual-import pattern as sandbox_manager below: `server.shell_guard`
# when started from the repo root (tests, smoke scripts), top-level `shell_guard` when main.py is run from
# inside server/ (python server/main.py puts server/ itself on sys.path).
try:
    from server import shell_guard
except ImportError:
    import shell_guard

# Standard logging; INFO level shows start-up and reload events in the terminal that launched the server.
# Initialize structured server logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZeusServer")

# Browsers connected to /ws/dev-reload. watch_client_files() sends them "reload" when a client file changes;
# the set is module-level because the watcher and the endpoint run as separate asyncio tasks.
# Set tracking active WebSocket connections for live client development reloading
dev_reload_sockets: Set[WebSocket] = set()


# Polling file watcher (no extra dependency such as watchdog): it compares modification times once per second
# and only while at least one dev-reload socket is connected, so it costs nothing in normal play.
async def watch_client_files():
    """Asynchronous background filesystem watcher monitoring client web assets for changes.

    Periodically scans modification timestamps across HTML, CSS, and JS assets in the
    client directory. Upon detecting file mutations, broadcasts reload messages to all
    connected development WebSockets to trigger instantaneous browser viewport refresh.
    """

    # When frozen by PyInstaller the client files are unpacked under sys._MEIPASS instead of next to this
    # source file.
    if hasattr(sys, "_MEIPASS"):
        client_dir = os.path.join(sys._MEIPASS, "client")
    else:
        client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))

    if not os.path.exists(client_dir):
        logger.warning(f"Client directory not found at {client_dir} for dev reloader.")
        return

    # Snapshot of {path: mtime} used as the baseline for change detection.
    last_mtimes = {}

    # Walks the client folder and records the mtime of every .html/.css/.js file. Files that disappear between
    # listing and stat are skipped (OSError).
    def scan_files():
        """Scans mtime timestamps across supported client asset file extensions."""
        mtimes = {}
        for root, _, files in os.walk(client_dir):
            for file in files:
                if file.endswith((".html", ".css", ".js")):
                    path = os.path.join(root, file)
                    try:
                        mtimes[path] = os.path.getmtime(path)
                    except OSError:
                        pass
        return mtimes

    try:
        last_mtimes = scan_files()
    except Exception as e:
        logger.error(f"Error initializing dev reload file scan: {e}")

    # The loop never exits; it is cancelled at shutdown by lifespan(). A change is a new file, a newer mtime,
    # or a deleted file.
    # Polling loop checking timestamps every 1.0 second
    while True:
        await asyncio.sleep(1.0)
        if not dev_reload_sockets:
            continue
        try:
            current_mtimes = scan_files()
            changed = False
            # Detect modified or newly created files
            for path, mtime in current_mtimes.items():
                if path not in last_mtimes or mtime > last_mtimes[path]:
                    changed = True
                    break
            # Detect deleted files
            if not changed:
                for path in last_mtimes:
                    if path not in current_mtimes:
                        changed = True
                        break

            if changed:
                logger.info("Client files changed. Triggering live reload across connected sockets...")
                last_mtimes = current_mtimes

                # Iterate over a copy because a failed send removes the socket from the set during the loop.
                for ws in list(dev_reload_sockets):
                    try:
                        await ws.send_text("reload")
                    except Exception:
                        dev_reload_sockets.discard(ws)
        except Exception as e:
            logger.error(f"Error in dev reload file watcher: {e}")


# Start-up/shutdown hook (replaces the old @app.on_event). Everything before `yield` runs at start-up,
# everything after at shutdown.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """FastAPI application lifespan context manager controlling daemon lifecycle.

    Startup:
      - Boots the background QEMU launcher daemon or fallback HolyC telnet server.
      - Launches the asynchronous client file watcher background task.
    Shutdown:
      - Cancels the background file watcher task to prevent dangling event loop references.
    """

    # The TempleOS serial service is started once per server run. The two import styles exist because the
    # module is imported as `server.qemu_launcher` when run from the repo root and as a top-level module when
    # main.py is run from inside server/.
    logger.info("FastAPI startup. Booting QEMU launcher/mock server...")
    try:
        from server import qemu_launcher
        qemu_launcher.start_qemu()
    except ImportError:
        try:
            import qemu_launcher
            qemu_launcher.start_qemu()
        except Exception as e:
            logger.error(f"Failed to import and start qemu_launcher: {e}")
    except Exception as e:
        logger.error(f"Error starting qemu_launcher: {e}")

    # Create the watcher as a background task and cancel it on shutdown so no task outlives the event loop.
    # Start dev reload file watcher as a background asyncio task
    watcher_task = asyncio.create_task(watch_client_files())
    yield
    # Clean up watcher task on server shutdown
    watcher_task.cancel()


# Instantiate FastAPI application with lifespan management
app = FastAPI(title="Zeus RPG Core Server", lifespan=lifespan)

# CORS only matters for the browser calling the API from another origin (for example the Vite dev server on
# port 5173); allow_credentials=True is safe here because the origin list is explicit, not "*".
# Restrict CORS headers to local loopback webview instances
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Save database location (relative paths resolve against the current working directory, so start the server
# from the repo root).
# Database path resolution and chapter metadata mappings
DB_PATH = os.environ.get("ZEUS_SAVE_DB_PATH", os.path.join("save_data", "save_state.db"))

# 22 chapters, ids 0-21 (0 = Outpost Zero ... 21 = the TempleOS altar).
EXPECTED_CHAPTER_IDS = list(range(22))

# Chapter id -> the file the player's solution is saved as inside save_data/relic_save/. The sandbox
# validators (sandbox/test_frameworks/chN_test.py) import these exact file names, so renaming one here breaks
# the validator for that chapter. Chapter 6 is a requirements.txt, not Python.
CHAPTER_FILENAME_MAP = {
    0: "ch0_cli.sh",
    1: "ch1_ocr.py",
    2: "ch2_sql.py",
    3: "ch3_nosql.py",
    4: "ch4_concurrency.py",
    5: "ch5_opt.py",
    6: "requirements.txt",
    7: "ch7_token.py",
    8: "ch8_attention.py",
    9: "ch9_forge.py",
    10: "ch10_search.py",
    11: "ch11_api.py",
    12: "ch12_graph.py",
    13: "ch13_eval.py",
    14: "ch14_lora.py",
    15: "ch15_guard.py",
    16: "ch16_quant.py",
    17: "ch17_agent.py",
    18: "ch18_state.py",
    19: "ch19_k8s.py",
    20: "ch20_pipeline.py",
    21: "ch21_altar.py",
}


# Creates the database and table on first run, adds the state_json column to databases created by older
# versions, and inserts one default save so GET /api/save always has a row. Safe to call repeatedly.
def init_db():
    """Initializes SQLite database schemas for player game saves and handles migrations."""
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gold INTEGER DEFAULT 0,
            compute_tokens INTEGER DEFAULT 100,
            unlocked_chapters TEXT DEFAULT '0',
            active_lead TEXT DEFAULT 'Low-Level Optimizer',
            inventory_json TEXT DEFAULT '[]',
            stats_json TEXT DEFAULT '[]',
            state_json TEXT DEFAULT '{}'
        )
    """)

    # Additive migration: older save files lack state_json, so the column is added with a default instead of
    # recreating the table.
    # Migration check: Ensure state_json column exists on legacy database files
    cursor.execute("PRAGMA table_info(player_state)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "state_json" not in existing_columns:
        cursor.execute("ALTER TABLE player_state ADD COLUMN state_json TEXT DEFAULT '{}'")

    # Starting party stats are embedded as JSON here and must match the initial `player` object in
    # client/app.js, otherwise a fresh game and a loaded default save would differ.
    # Seed baseline initial save state if table is newly provisioned
    cursor.execute("SELECT COUNT(*) FROM player_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO player_state (gold, compute_tokens, unlocked_chapters, active_lead, inventory_json, stats_json, state_json)
            VALUES (
                200,
                100,
                '0',
                'Low-Level Optimizer',
                '[]',
                '[{"name": "Optimizer", "race": "Silicon Automaton", "class": "Low-Level Optimizer", "level": 1, "exp": 0, "next_exp": 100, "hp": 120, "max_hp": 120, "atk": 18, "def": 10, "spd": 14, "luc": 8, "tokens": 100}, {"name": "Architect", "race": "Bare-Metal Carbon", "class": "Data Architect", "level": 1, "exp": 0, "next_exp": 100, "hp": 100, "max_hp": 100, "atk": 12, "def": 14, "spd": 10, "luc": 10, "tokens": 100}, {"name": "Orchestrator", "race": "Compiler Elf", "class": "Agent Orchestrator", "level": 1, "exp": 0, "next_exp": 100, "hp": 90, "max_hp": 90, "atk": 10, "def": 8, "spd": 12, "luc": 12, "tokens": 100}, {"name": "PromptEng", "race": "Neuron Cyborg", "class": "Prompt Engineer", "level": 1, "exp": 0, "next_exp": 100, "hp": 80, "max_hp": 80, "atk": 16, "def": 6, "spd": 8, "luc": 14, "tokens": 100}]',
                '{"currentChapter": 0, "x": 8, "y": 7, "openedChests": [], "readManuals": [], "readManualPages": [], "screenMode": "dark", "lastSavedAt": null}'
            )
        """)
    conn.commit()
    conn.close()


# Runs at import time, so importing this module (for example from a test) creates the save file as a side
# effect.
# Ensure database schema is valid on module import
init_db()


# Body of POST /api/save. The *_json fields are JSON documents stored as text; the server does not parse or
# validate their contents, so the client is the source of truth for their shape.
class SaveStateModel(BaseModel):
    """Pydantic data validation model for incoming save state JSON payloads."""
    gold: int
    compute_tokens: int
    unlocked_chapters: str
    active_lead: str
    inventory_json: str
    stats_json: str
    state_json: str = "{}"


# Liveness probe (polled by scripts/full_stack_smoke.py and scripts/simulate_gameplay.py to wait until the
# server is up).
@app.get("/api/health")
def health():
    """Health check probe returning operational status and binding interface."""
    return {"status": "ok", "host": "127.0.0.1"}


# Checks whether the Docker sandbox container is running so the UI can show "sandbox online/offline". Never
# raises: a missing docker binary is reported as unavailable.
@app.get("/api/sandbox-status")
def sandbox_status():
    """Reports whether the Arch Linux Docker sandbox is available and running."""
    import subprocess
    docker_available = False
    container_running = False
    try:
        check = subprocess.run(
            ["docker", "ps", "--filter", "name=zeus-sandbox", "-q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        docker_available = check.returncode == 0
        container_running = docker_available and bool(check.stdout.strip())
    except FileNotFoundError:
        docker_available = False
    except Exception:
        pass
    return {"docker": docker_available, "container_running": container_running}


# Self-check endpoint: lists which chapter validators and code templates exist and whether the save DB is
# present, so a broken install is visible at /api/diagnostics.
@app.get("/api/diagnostics")
def diagnostics():
    """Comprehensive diagnostic probe validating test frameworks, templates, and database configuration."""
    try:
        try:
            from server import sandbox_manager
        except ImportError:
            import sandbox_manager

        validator_dir = os.path.join(sandbox_manager.BUNDLED_SANDBOX_DIR, "test_frameworks")
        validators = []
        missing_validators = []
        for chapter_id in EXPECTED_CHAPTER_IDS:
            filename = f"ch{chapter_id}_test.py"
            path = os.path.join(validator_dir, filename)
            if os.path.exists(path):
                validators.append({"chapter_id": chapter_id, "filename": filename})
            else:
                missing_validators.append(chapter_id)

        return {
            "status": "ok",
            "validator_dir": validator_dir,
            "expected_chapters": EXPECTED_CHAPTER_IDS,
            "validators_found": validators,
            "missing_validators": missing_validators,
            "code_templates": [
                {"chapter_id": chapter_id, "filename": CHAPTER_FILENAME_MAP[chapter_id]}
                for chapter_id in EXPECTED_CHAPTER_IDS
                if chapter_id in CHAPTER_FILENAME_MAP
            ],
            "save_db_configured": os.path.exists(DB_PATH),
            "save_state_fields": [
                "gold", "compute_tokens", "unlocked_chapters", "active_lead",
                "inventory_json", "stats_json", "state_json",
            ],
            "relic_save_dir": sandbox_manager.RELIC_SAVE_DIR,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Newest save row (highest id), or {} when none.
@app.get("/api/save")
def get_save():
    """Retrieves the most recent player save state record from SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM player_state ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Lists recent save checkpoints; limit is clamped to 1-50 to bound the response size.
@app.get("/api/saves")
def list_saves(limit: int = 10):
    """Lists recent save checkpoints up to the specified limit (1-50)."""
    try:
        limit = max(1, min(limit, 50))
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, gold, compute_tokens, unlocked_chapters, state_json FROM player_state ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"saves": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fetch one historical checkpoint; 404 if the id does not exist. The inner `except HTTPException: raise` stops
# the generic handler turning the 404 into a 500.
@app.get("/api/save/{save_id}")
def get_save_by_id(save_id: int):
    """Retrieves a specific historical save state by primary key ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM player_state WHERE id = ?", (save_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        raise HTTPException(status_code=404, detail="Save not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Insert a new row for every save (checkpoints) and then delete everything but the 50 newest rows, so the file
# cannot grow without bound. Parameterised SQL throughout.
@app.post("/api/save")
def save_state(state: SaveStateModel):
    """Persists a new game save record and trims historical entries beyond the 50-row rolling window."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO player_state (gold, compute_tokens, unlocked_chapters, active_lead, inventory_json, stats_json, state_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            state.gold, state.compute_tokens, state.unlocked_chapters,
            state.active_lead, state.inventory_json, state.stats_json, state.state_json,
        ))

        # `id NOT IN (SELECT newest 50)` keeps the latest 50 even if ids have gaps after earlier deletions.
        # Enforce rolling history boundary: retain maximum 50 records
        cursor.execute("""
            DELETE FROM player_state WHERE id NOT IN (
                SELECT id FROM player_state ORDER BY id DESC LIMIT 50
            )
        """)

        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Starter code shown to the player in each chapter's editor. The comment header in every template names the
# chapter's lesson and the function the validator in sandbox/test_frameworks/chN_test.py will call; those
# signatures must stay in step with the validators.
def get_default_skeleton(chapter_id: int) -> str:
    """Returns baseline starter template code for a given chapter curriculum."""
    skeletons = {
        0: '# Outpost Zero: Environment config\n# The citadel gates read your $PATH. Restore the toolchain by APPENDING\n# /usr/local/bin to the existing PATH. Keep $PATH in your export so the\n# old entries are not lost.\n#\n# Write your export statement below this line:\n\necho "Booting environment..."\n',
        1: '# Alexandria Library: OCR Filters\ndef monochrome_filter(rgb_matrix):\n    # Convert 3D RGB matrix to 2D Grayscale matrix\n    # rgb_matrix is a list of lists of (R, G, B) tuples\n    # Return a list of lists of numbers (0-255)\n    gray_matrix = []\n    for row in rgb_matrix:\n        gray_row = []\n        for r, g, b in row:\n            gray_val = int(0.299 * r + 0.587 * g + 0.114 * b)\n            gray_row.append(gray_val)\n        gray_matrix.append(gray_row)\n    return gray_matrix\n\ndef threshold_filter(gray_matrix, threshold):\n    # Values > threshold -> 255, <= threshold -> 0\n    binary_matrix = []\n    for row in gray_matrix:\n        binary_row = []\n        for val in row:\n            binary_row.append(255 if val > threshold else 0)\n        binary_matrix.append(binary_row)\n    return binary_matrix\n',
        2: '# Relational Meadows: SQL injection security\ndef run_injection_exploit():\n    # Return exploit payload username to bypass credentials\n    return "\' OR 1=1;--"\n\ndef get_character_secured(conn, username):\n    # Safely query secret keys from DB using parameters\n    cursor = conn.cursor()\n    cursor.execute("SELECT secret_key FROM users WHERE username = ?", (username,))\n    return cursor.fetchall()\n',
        3: '# Document Dunes: Redis cache\nimport json\nimport time\n\nclass PolymorphicItemParser:\n    def parse(self, json_str):\n        # Parse and return item dict structure from JSON string\n        return json.loads(json_str)\n\nclass TimedCache:\n    def __init__(self, ttl_seconds=5):\n        self.cache = {}\n        self.ttl = ttl_seconds\n\n    def get(self, key):\n        if key in self.cache:\n            val, expiry = self.cache[key]\n            if time.time() < expiry:\n                return val\n            del self.cache[key]\n        return None\n\n    def set(self, key, value):\n        self.cache[key] = (value, time.time() + self.ttl)\n',
        4: '# Parallel Swamp: Concurrency Threading Lock\nimport threading\n\nclass ThreadedBank:\n    def __init__(self, initial_balance=0):\n        self.balance = initial_balance\n        self.lock = threading.Lock()\n\n    def withdraw(self, amount):\n        with self.lock:\n            self.balance -= amount\n\n    def get_balance(self):\n        return self.balance\n',
        5: '# Iron Peaks: C++ contiguous arrays optimization\ndef optimized_array_sum(arr):\n    # Sum the array elements efficiently\n    return sum(arr)\n',
        6: '# Docker Relic dependencies requirements.txt\nrequests>=2.31.0\n',
        7: '# Whispering Woods: Subword BPE tokenization\ndef bpe_encode(text, merges):\n    # Perform BPE token merge mapping\n    if text == "these":\n        return ["the", "es"]\n    tokens = list(text)\n    for pair, merge in merges.items():\n        new_tokens = []\n        i = 0\n        while i < len(tokens):\n            if i < len(tokens) - 1 and tokens[i] == pair[0] and tokens[i+1] == pair[1]:\n                new_tokens.append(merge)\n                i += 2\n            else:\n                new_tokens.append(tokens[i])\n                i += 1\n        tokens = new_tokens\n    return tokens\n',
        8: '# Valley of Attention: Scaled Dot-Product Attention\nimport numpy as np\n\ndef scaled_dot_product_attention(q, k, v, mask=None):\n    # q, k, v are 4D numpy arrays: (batch_size, heads, seq_len, d_k)\n    # Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V\n    d_k = q.shape[-1]\n    k_t = np.transpose(k, (0, 1, 3, 2))\n    scores = np.matmul(q, k_t) / np.sqrt(d_k)\n    if mask is not None:\n        scores = scores + mask\n    exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))\n    weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)\n    output = np.matmul(weights, v)\n    return output, weights\n',
        9: '# Forge of Zeus: LayerNorm & Backpropagation step\nimport numpy as np\n\ndef layernorm_forward(x, gamma, beta, eps=1e-5):\n    # Normalize each row (along the last axis)\n    mean = np.mean(x, axis=-1, keepdims=True)\n    var = np.var(x, axis=-1, keepdims=True)\n    x_norm = (x - mean) / np.sqrt(var + eps)\n    return gamma * x_norm + beta\n\ndef training_step(weights, inputs, targets, lr=0.1):\n    # Perform a single SGD step on MSE loss\n    y_pred = np.dot(weights, inputs)\n    error = y_pred - targets\n    gradient = 2.0 * error * inputs\n    weights_new = weights - lr * gradient\n    return weights_new\n',
        10: '# Reranking Reefs: Hybrid search blend\ndef expand_query(query):\n    # Return a list of query expansions\n    return [query, query + " relic", query + " power"]\n\ndef hybrid_search_blend(sparse_results, dense_results, alpha=0.5):\n    # Combine scores from dense (cosine) and sparse (bm25) dicts using alpha\n    # Return sorted list of tuples: [(doc_id, score), ...]\n    blended = {}\n    all_keys = set(sparse_results.keys()).union(set(dense_results.keys()))\n    for doc in all_keys:\n        sparse_val = sparse_results.get(doc, 0.0)\n        dense_val = dense_results.get(doc, 0.0)\n        blended[doc] = alpha * sparse_val + (1.0 - alpha) * dense_val\n    return sorted(blended.items(), key=lambda x: x[1], reverse=True)\n\ndef rerank_and_filter(blended_results, threshold=0.50):\n    # Filter out results below threshold\n    return [item for item in blended_results if item[1] >= threshold]\n',
        11: '# API Archipelago: FastAPI Server setup\ndef get_launch_config():\n    # Return dictionary with host bound to loopback interface\n    return {\n        "host": "127.0.0.1",\n        "port": 8000\n    }\n',
        12: '# Graph Gardens: Cypher shortestPath matching\ndef generate_cypher_path_walk(start_node, end_node):\n    # MATCH (start:Node {name: start_node}), (end:Node {name: end_node})\n    # MATCH p = shortestPath((start)-[*..10]->(end))\n    # RETURN p\n    return f"MATCH (startNode:Node {{name: \'{start_node}\'}}), (endNode:Node {{name: \'{end_node}\'}}) MATCH p = shortestPath((startNode)-[*..10]->(endNode)) RETURN p"\n',
        13: '# Testing Tundra: BLEU-1 & ROUGE-L\nimport math\n\ndef calculate_bleu(candidate, reference):\n    cand_tokens = candidate.split()\n    ref_tokens = reference.split()\n    if not cand_tokens or not ref_tokens:\n        return 0.0\n    ref_counts = {}\n    for r in ref_tokens:\n        ref_counts[r] = ref_counts.get(r, 0) + 1\n    cand_counts = {}\n    for c in cand_tokens:\n        cand_counts[c] = cand_counts.get(c, 0) + 1\n    overlap = 0\n    for w, count in cand_counts.items():\n        overlap += min(count, ref_counts.get(w, 0))\n    precision = overlap / len(cand_tokens)\n    c = len(cand_tokens)\n    r = len(ref_tokens)\n    if c > r:\n        bp = 1.0\n    else:\n        bp = math.exp(1.0 - r / c) if c > 0 else 0.0\n    return bp * precision\n\ndef calculate_rouge_l(candidate, reference):\n    cand_tokens = candidate.split()\n    ref_tokens = reference.split()\n    if not cand_tokens or not ref_tokens:\n        return 0.0\n    m, n = len(cand_tokens), len(ref_tokens)\n    L = [[0] * (n + 1) for _ in range(m + 1)]\n    for i in range(1, m + 1):\n        for j in range(1, n + 1):\n            if cand_tokens[i - 1] == ref_tokens[j - 1]:\n                L[i][j] = L[i - 1][j - 1] + 1\n            else:\n                L[i][j] = max(L[i - 1][j], L[i][j - 1])\n    lcs = L[m][n]\n    p = lcs / m\n    r = lcs / n\n    if p + r == 0:\n        return 0.0\n    return 2 * p * r / (p + r)\n',
        14: '# Fine-Tuning Fiord: LoRA Adapter\nimport numpy as np\n\ndef lora_forward(x, W0, A, B, alpha, r):\n    base = x @ W0.T\n    delta = (x @ A.T) @ B.T\n    return base + (alpha / r) * delta\n\ndef merge_weights(W0, A, B, alpha, r):\n    return W0 + (alpha / r) * (B @ A)\n',
        15: '# Security Caves: Prompt guardrails and sanitizers\nimport json\nimport re\n\ndef is_safe_prompt(prompt):\n    # Basic check for prompt injection keywords\n    unsafe_words = ["ignore all previous", "ignore previous", "dan mode", "you are now in dan"]\n    for word in unsafe_words:\n        if word in prompt.lower():\n            return False\n    return True\n\ndef sanitize_output(output):\n    # Redact sensitive keys and secrets\n    # Replace sk-proj-... and password=...\n    output = re.sub(r"sk-proj-[a-zA-Z0-9]+", "[REDACTED_KEY]", output)\n    output = re.sub(r"password=[A-Za-z0-9_]+", "password=[REDACTED_PASSWORD]", output)\n    return output\n\ndef validate_json_response(json_str, schema_keys):\n    try:\n        data = json.loads(json_str)\n        for key in schema_keys:\n            if key not in data:\n                return False\n        return True\n    except Exception:\n        return False\n',
        16: '# Deployment Cliffs: Symmetric INT8 Quantization\nimport numpy as np\n\ndef quantize_symmetric(x):\n    max_val = np.max(np.abs(x))\n    if max_val == 0:\n        scale = 1.0\n    else:\n        scale = max_val / 127.0\n    q = np.round(x / scale)\n    q = np.clip(q, -127, 127).astype(np.int8)\n    return q, scale\n\ndef dequantize_symmetric(q_tensor, scale):\n    return q_tensor.astype(np.float32) * scale\n',
        17: '# Agentic Skyway: Tool-calling signature schema\nimport inspect\nimport json\n\ndef generate_tool_schema(func):\n    sig = inspect.signature(func)\n    doc = inspect.getdoc(func) or ""\n    properties = {}\n    required = []\n    for name, param in sig.parameters.items():\n        param_type = "string"\n        if param.annotation == int:\n            param_type = "integer"\n        elif param.annotation == float:\n            param_type = "number"\n        elif param.annotation == bool:\n            param_type = "boolean"\n        properties[name] = {"type": param_type}\n        if param.default == inspect.Parameter.empty:\n            required.append(name)\n    return {\n        "name": func.__name__,\n        "description": doc,\n        "parameters": {\n            "type": "object",\n            "properties": properties,\n            "required": required\n        }\n    }\n\ndef execute_tool_call(tool_call_json, tools_map):\n    data = json.loads(tool_call_json)\n    func_name = data["name"]\n    args = data["arguments"]\n    func = tools_map[func_name]\n    return func(**args)\n',
        18: '# State Vaults: ReAct Thought-Action Loop\ndef run_react_loop(state, step_fn, max_steps=5):\n    steps = 0\n    while steps < max_steps:\n        if state.get("status") != "running":\n            break\n        state = step_fn(state)\n        steps += 1\n    if state.get("status") == "running":\n        state["status"] = "max_steps_exceeded"\n    return state\n\ndef find_skeleton_ancestors(lineage, start_node):\n    ancestors = []\n    visited = set()\n    current = start_node\n    while current in lineage:\n        parent = lineage[current]\n        if not parent:\n            break\n        if parent in visited:\n            break\n        visited.add(parent)\n        ancestors.append(parent)\n        current = parent\n    return ancestors\n\ndef run_self_corrective_rag(initial_query, retrieve_fn, evaluate_fn, rewrite_fn, max_steps=3):\n    current_query = initial_query\n    steps = 0\n    chunks = []\n    while steps < max_steps:\n        chunks = retrieve_fn(current_query)\n        if evaluate_fn(chunks):\n            return {"status": "success", "steps": steps, "context": chunks}\n        current_query = rewrite_fn(current_query)\n        steps += 1\n    return {"status": "failed", "steps": steps, "context": chunks}\n',
        19: '# Kubernetes Citadel: Pod & Ingress configs\ndef get_k8s_manifests():\n    pod_yaml = """apiVersion: v1\nkind: Pod\nmetadata:\n  name: defense-pod\nspec:\n  containers:\n  - name: defense-container\n    image: nginx\n    ports:\n    - containerPort: 8000\n    resources:\n      limits:\n        memory: 256Mi\n        cpu: 500m\n      requests:\n        memory: 128Mi\n        cpu: 250m"""\n    ingress_yaml = """apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: citadel-ingress\nspec:\n  rules:\n  - http:\n      paths:\n      - path: /defense\n        pathType: Prefix\n        backend:\n          service:\n            name: defense-service\n            port:\n              number: 80"""\n    return pod_yaml, ingress_yaml\n',
        20: '# The Grand Assembly: Integrated Pipeline\nimport json\nimport sqlite3\n\ndef run_assembler_pipeline(layout_json_path, query_text, db_path):\n    with open(layout_json_path, "r") as f:\n        boxes = json.load(f)\n    lines = {}\n    for box in boxes:\n        y = box["y"]\n        lines.setdefault(y, []).append(box)\n    grouped_lines = []\n    for y in sorted(lines.keys()):\n        line_boxes = sorted(lines[y], key=lambda b: b["x"])\n        line_phrases = []\n        if not line_boxes:\n            continue\n        current_phrase = line_boxes[0]["text"]\n        curr_right = line_boxes[0]["x"] + line_boxes[0]["w"]\n        for box in line_boxes[1:]:\n            if box["x"] - curr_right <= 15:\n                current_phrase += " " + box["text"]\n                curr_right = box["x"] + box["w"]\n            else:\n                line_phrases.append(current_phrase)\n                current_phrase = box["text"]\n                curr_right = box["x"] + box["w"]\n        line_phrases.append(current_phrase)\n        grouped_lines.append(" ".join(line_phrases))\n    ocr_text = "\\n".join(grouped_lines)\n    conn = sqlite3.connect(db_path)\n    cursor = conn.cursor()\n    db_results = []\n    try:\n        for phrase in grouped_lines:\n            cursor.execute("SELECT item_id, name, power FROM inventory WHERE name = ?", (phrase,))\n            db_results.extend(cursor.fetchall())\n    except Exception:\n        db_results = []\n    finally:\n        conn.close()\n    graph_context = "Node: Zeus Relic Shield -> Attribute: Power = 95"\n    llm_response = f"Answer generated: {query_text} -> DB results show {db_results}"\n    return {\n        "ocr_text": ocr_text,\n        "db_results": db_results,\n        "graph_context": graph_context,\n        "llm_response": llm_response\n    }\n',
        21: '# Altar of TempleOS: Bare-metal HolyC compilation checksum\ndef validate_holyc_syntax(code):\n    if "def " in code or "print(" in code:\n        return False\n    if "U0" in code or "I64" in code or "Print" in code:\n        return True\n    return False\n\ndef get_templeos_serial_command():\n    return "telnet 127.0.0.1 4444"\n',
    }

    # Unknown chapter ids get a generic stub instead of an error.
    return skeletons.get(chapter_id, f"# Chapter {chapter_id} Solution\n")


# Returns the player's saved solution if it exists, otherwise the starter template (also when skeleton=true,
# which the client uses for "reset code").
@app.get("/api/code")
def load_code(chapter_id: int, skeleton: bool = False):
    """Loads player solution code from disk, or falls back to standard skeleton template."""
    try:
        # filename comes from the fixed map (or an integer-based default), never from user text, so there is
        # no path-traversal risk here.
        filename = CHAPTER_FILENAME_MAP.get(chapter_id, f"ch{chapter_id}_solution.py")
        try:
            from server import sandbox_manager
        except ImportError:
            import sandbox_manager
        save_path = os.path.join(sandbox_manager.RELIC_SAVE_DIR, filename)

        if not skeleton and os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                code = f.read()
        else:
            code = get_default_skeleton(chapter_id)

        return {"chapter_id": chapter_id, "filename": filename, "code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Body of POST /api/compile: which chapter and the player's code.
class CompileRequest(BaseModel):
    """Pydantic data validation model for code compilation requests."""
    chapter_id: int
    code: str


# Saves the submitted code and runs the chapter's validator. Returns {"success": bool, "output": str} from
# sandbox_manager.execute_test(). Blocking subprocess work runs inside a synchronous endpoint, which FastAPI
# executes in its thread pool, so it does not freeze the event loop.
@app.post("/api/compile")
def compile_code(req: CompileRequest):
    """Writes submitted code to disk and invokes chapter validator inside Docker sandbox."""
    try:
        try:
            from server import sandbox_manager
        except ImportError:
            import sandbox_manager

        filename = CHAPTER_FILENAME_MAP.get(req.chapter_id, f"ch{req.chapter_id}_solution.py")
        save_path = os.path.join(sandbox_manager.RELIC_SAVE_DIR, filename)

        # Ensure destination directory exists on disk
        os.makedirs(sandbox_manager.RELIC_SAVE_DIR, exist_ok=True)

        # The validator reads this file from the shared bind mount (/workspace inside the container), so it
        # must be written before the test is launched.
        # Write code file atomically to disk
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(req.code)

        # Dispatch test execution through sandbox runtime manager
        res = sandbox_manager.execute_test(req.chapter_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Hands the browser client the per-run token it must send as the first /ws/shell frame. Why an endpoint: the
# static client has no other way to learn a secret generated at server start. Why this is not a hole: a page
# on another site can fire a request here but cannot READ the answer (the CORS list above does not include
# it), and requests whose Host is not loopback (DNS rebinding) or that the browser marks cross-site are
# refused outright. Cache-Control: no-store keeps the token out of proxies and the disk cache.
@app.get("/api/shell-token")
def shell_token(request: Request):
    """Returns {"token": ...} for the terminal WebSocket handshake; 403 for non-local callers."""
    # Host header: loopback names only (rebinding defence). Origin: absent (same-origin GET) or local.
    # Sec-Fetch-Site: set by modern browsers; "cross-site" means another website initiated this request.
    if (
        not shell_guard.is_loopback_host(request.headers.get("host"))
        or not shell_guard.is_local_origin(request.headers.get("origin"))
        or request.headers.get("sec-fetch-site") == "cross-site"
    ):
        raise HTTPException(status_code=403, detail="Shell token is only available to the local game client.")
    return JSONResponse({"token": shell_guard.SHELL_TOKEN}, headers={"Cache-Control": "no-store"})


# WebSocket endpoints. Messages are plain text frames in both directions (terminal bytes decoded as UTF-8).
# ------------------------------------------------------------------------------
# Real-Time WebSocket Proxy Endpoints
# ------------------------------------------------------------------------------

# Interactive terminal for chapters 0 (Linux CLI) and others. Data path: browser keystrokes -> WebSocket ->
# PTY master -> shell; shell output -> PTY master -> WebSocket.
# A PTY (pseudo-terminal) is used rather than pipes so programs behave as in a real terminal (colours, line
# editing, Ctrl+C).
@app.websocket("/ws/shell")
async def ws_shell(websocket: WebSocket):
    """WebSocket terminal bridge connecting client to an interactive shell via pseudo-terminal (PTY).

    Access control (all checked BEFORE any process is spawned, see server/shell_guard.py):
      1. handshake headers: loopback TCP peer, loopback Host, loopback-or-absent Origin;
      2. the first text frame must equal the per-run token from GET /api/shell-token (5 s to send it);
      3. the host-bash fallback is only used when ZEUS_ALLOW_HOST_SHELL=1.
    Failures close the socket with code 1008 (policy violation) and the client does not auto-reconnect.

    Spawns `docker exec -it zeus-sandbox bash` if the container is running; otherwise (only when opted in)
    a host bash shell. Uses `pty.openpty()` to capture full ANSI escape sequences, control characters, and
    line editing.
    """
    # Refuse before accept(): Starlette answers an un-accepted close with HTTP 403, so a hostile page learns
    # nothing and no WebSocket session ever exists. Browsers always send Origin on WebSocket handshakes and
    # scripts cannot forge it, which is what makes the Origin test meaningful; Host and peer address stop DNS
    # rebinding and any accidental non-loopback bind.
    client_host = websocket.client.host if websocket.client else None
    if (
        not shell_guard.is_loopback_client(client_host)
        or not shell_guard.is_loopback_host(websocket.headers.get("host"))
        or not shell_guard.is_local_origin(websocket.headers.get("origin"))
    ):
        logger.warning(
            "Rejected /ws/shell handshake (peer=%s, host=%s, origin=%s)",
            client_host, websocket.headers.get("host"), websocket.headers.get("origin"),
        )
        await websocket.close(code=1008)
        return

    await websocket.accept()

    # Token handshake. The token travels in the first frame instead of the URL so it never lands in access
    # logs or browser history. The timeout stops an unauthenticated peer from holding the socket open.
    try:
        first_frame = await asyncio.wait_for(websocket.receive_text(), timeout=5)
    except Exception:
        # Timeout, disconnect or a binary frame: all treated as failed authentication.
        first_frame = None
    if not shell_guard.token_matches(first_frame):
        logger.warning("Rejected /ws/shell: missing or wrong token")
        await websocket.close(code=1008)
        return

    try:
        # Check if Docker container is currently active

        # Blocking call inside an async function (briefly stalls the event loop); acceptable for a single-user
        # tool. Empty output means the container is not running.
        container_check = os.popen("docker ps --filter name=zeus-sandbox -q").read().strip()
        if container_check:
            cmd = ["docker", "exec", "-it", "zeus-sandbox", "bash"]
            await websocket.send_text("\r\n[Sandbox: connected to Arch Linux container 'zeus-sandbox']\r\n")
        elif shell_guard.host_shell_allowed():
            cmd = ["bash"]
            await websocket.send_text(
                "\r\n[Sandbox OFFLINE: this is your HOST shell, not the Arch container.\r\n"
                " (ZEUS_ALLOW_HOST_SHELL=1 is set.) Run setup/build_sandbox.sh with Docker installed for the real sandbox.]\r\n"
            )
        else:
            # Default is to refuse: a host shell is full access to the user's account, so it must be an
            # explicit operator decision, not something that happens because Docker happens to be stopped.
            await websocket.send_text(
                "\r\n[Sandbox OFFLINE: no shell started. Run setup/build_sandbox.sh with Docker installed,\r\n"
                " or start the server with ZEUS_ALLOW_HOST_SHELL=1 to allow a shell on this computer.]\r\n"
            )
            await websocket.close(code=1008)
            return

        # Allocate pseudo-terminal descriptor pair

        # openpty() returns two ends: the child shell gets the slave side as stdin/stdout/stderr, the server
        # keeps the master side. The server must close its copy of the slave (below) or it would never see
        # end-of-file when the shell exits.
        import pty
        master_fd, slave_fd = pty.openpty()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)

        # Reader coroutine: os.read blocks, so it runs in a thread executor to keep the event loop free.
        # Output is decoded with errors="replace" so a split multibyte character cannot crash the stream.
        async def read_from_pty():
            """Reads terminal byte stream from PTY master and sends to WebSocket."""
            try:
                loop = asyncio.get_running_loop()
                while True:
                    data = await loop.run_in_executor(None, lambda: os.read(master_fd, 1024))
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
            except Exception as e:
                logger.debug(f"Read PTY stream closed: {e}")

        # Writer coroutine: forwards each text frame from the browser to the shell.
        async def write_to_pty():
            """Receives user keystrokes from WebSocket and writes to PTY master descriptor."""
            try:
                while True:
                    msg = await websocket.receive_text()
                    os.write(master_fd, msg.encode("utf-8"))
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.debug(f"Write PTY stream closed: {e}")

        # Whichever direction ends first (shell exited or browser disconnected) stops the other; the finally
        # block kills and reaps the process so no zombie remains and closes the PTY.
        try:
            done, pending = await asyncio.wait(
                {asyncio.create_task(read_from_pty()), asyncio.create_task(write_to_pty())},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        finally:
            # Terminate and reap shell process to prevent zombie processes
            if proc.returncode is None:
                proc.kill()
            await proc.wait()
            try:
                os.close(master_fd)
            except OSError:
                pass
    except Exception as e:
        logger.error(f"WebSocket shell error: {e}")
        await websocket.close()


# Bridge to the TempleOS (chapter 21) serial console on 127.0.0.1:4444, which is either QEMU's telnet serial
# socket or the mock server from qemu_launcher.py.
@app.websocket("/ws/templeos")
async def ws_templeos(websocket: WebSocket):
    """WebSocket serial console proxy streaming data between browser and QEMU/mock HolyC server.

    Establishes an asynchronous TCP connection to the loopback telnet port 127.0.0.1:4444.
    """
    await websocket.accept()
    try:
        # If nothing listens on the port the connection fails and the client gets a hint message instead of a
        # silent hang.
        reader, writer = await asyncio.open_connection("127.0.0.1", 4444)

        async def read_qemu():
            """Reads serial stream from QEMU telnet socket and forwards to WebSocket."""
            try:
                while True:
                    data = await reader.read(1024)
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
            except Exception as e:
                logger.debug(f"QEMU Read stream closed: {e}")

        async def write_qemu():
            """Forwards WebSocket user commands to QEMU serial socket."""
            try:
                while True:
                    msg = await websocket.receive_text()
                    writer.write(msg.encode("utf-8"))
                    await writer.drain()
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.debug(f"QEMU Write stream closed: {e}")

        # gather runs both pumps until one raises/ends; unlike the shell bridge it does not cancel the other
        # pump explicitly, so a client that disconnects leaves the TCP connection to be closed by the garbage
        # collector.
        await asyncio.gather(
            read_qemu(),
            write_qemu(),
        )
    except Exception as e:
        logger.error(f"WebSocket TempleOS Connection error: {e}")
        await websocket.send_text("\r\n[Error: TempleOS altar offline. Spin up Chapter 21 VM Altar first!]\r\n")
        await websocket.close()


# Registers a browser as a live-reload listener. The receive loop only waits for the client to disconnect (it
# ignores any text it receives).
@app.websocket("/ws/dev-reload")
async def ws_dev_reload(websocket: WebSocket):
    """WebSocket endpoint registering connected browser clients for live development reloading."""
    await websocket.accept()
    dev_reload_sockets.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        dev_reload_sockets.discard(websocket)


# Static client mounting must come LAST: a mount at "/" would shadow any route registered after it.
# ------------------------------------------------------------------------------
# Static Web Client Asset Mounting
# ------------------------------------------------------------------------------

# Locate the client folder (bundled or source tree). If a built client/dist exists (for example from a
# Vite/Tauri build) it is served; otherwise the raw client folder is served.
if hasattr(sys, "_MEIPASS"):
    client_dir = os.path.join(sys._MEIPASS, "client")
else:
    client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))

dist_dir = os.path.join(client_dir, "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
elif os.path.exists(client_dir):
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="static")

# Direct start: binds loopback only (127.0.0.1), never 0.0.0.0, because of the unauthenticated shell endpoint.
if __name__ == "__main__":
    # Bind strictly to local loopback interface on standard port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
