import os
import sys
import sqlite3
import json
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ZeusServer")

app = FastAPI(title="Zeus RPG Core Server")

# Bind strictly to local loopback interface for safety
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join("save_data", "save_state.db")

# Initialize database schemas
def init_db():
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
            stats_json TEXT DEFAULT '{}'
        )
    """)
    # Insert default state if empty
    cursor.execute("SELECT COUNT(*) FROM player_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO player_state (gold, compute_tokens, unlocked_chapters, active_lead, inventory_json, stats_json)
            VALUES (
                200, 
                100, 
                '0', 
                'Low-Level Optimizer', 
                '[]', 
                '{"Optimizer": {"hp": 120, "max_hp": 120, "atk": 18, "def": 10, "spd": 14, "luc": 8}, "Architect": {"hp": 100, "max_hp": 100, "atk": 12, "def": 14, "spd": 10, "luc": 10}, "Orchestrator": {"hp": 90, "max_hp": 90, "atk": 10, "def": 8, "spd": 12, "luc": 12}, "PromptEng": {"hp": 80, "max_hp": 80, "atk": 16, "def": 6, "spd": 8, "luc": 14}}'
            )
        """)
    conn.commit()
    conn.close()

init_db()

class SaveStateModel(BaseModel):
    gold: int
    compute_tokens: int
    unlocked_chapters: str
    active_lead: str
    inventory_json: str
    stats_json: str

@app.get("/api/health")
def health():
    return {"status": "ok", "host": "127.0.0.1"}

@app.get("/api/save")
def get_save():
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

@app.post("/api/save")
def save_state(state: SaveStateModel):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO player_state (gold, compute_tokens, unlocked_chapters, active_lead, inventory_json, stats_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (state.gold, state.compute_tokens, state.unlocked_chapters, state.active_lead, state.inventory_json, state.stats_json))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CompileRequest(BaseModel):
    chapter_id: int
    code: str

@app.post("/api/compile")
def compile_code(req: CompileRequest):
    try:
        # Import sandbox manager dynamically or at header
        from server import sandbox_manager
        
        # Map chapter to default filename
        filename_map = {
            0: "ch0_cli.sh",
            1: "ch1_ocr.py",
            2: "ch2_sql.py",
            3: "ch3_nosql.py",
            4: "ch4_concurrency.py",
            5: "ch5_opt.py",
            6: "ch6_docker.py",
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
        
        filename = filename_map.get(req.chapter_id, f"ch{req.chapter_id}_solution.py")
        save_path = os.path.join(sandbox_manager.RELIC_SAVE_DIR, filename)
        
        # Ensure directory exists
        os.makedirs(sandbox_manager.RELIC_SAVE_DIR, exist_ok=True)
        
        # Write player's code file to disk
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(req.code)
            
        # Run test execution inside container (or local fallback)
        res = sandbox_manager.execute_test(req.chapter_id)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket proxy routing for local Docker container bash terminal
@app.websocket("/ws/shell")
async def ws_shell(websocket: WebSocket):
    await websocket.accept()
    # Spawns a shell inside the Arch container via Docker
    # Fallback to local bash shell if Docker container isn't online yet
    try:
        # Check if container is running
        container_check = os.popen("docker ps --filter name=zeus-sandbox -q").read().strip()
        if container_check:
            cmd = ["docker", "exec", "-it", "zeus-sandbox", "bash"]
        else:
            cmd = ["bash"]

        # Run process with pseudo-terminal binding
        import pty
        master_fd, slave_fd = pty.openpty()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True
        )
        os.close(slave_fd)

        async def read_from_pty():
            try:
                loop = asyncio.get_running_loop()
                while True:
                    # Non-blocking read from pty master
                    data = await loop.run_in_executor(None, lambda: os.read(master_fd, 1024))
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
            except Exception as e:
                logger.error(f"Read PTY error: {e}")

        async def write_to_pty():
            try:
                while True:
                    msg = await websocket.receive_text()
                    os.write(master_fd, msg.encode("utf-8"))
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"Write PTY error: {e}")

        await asyncio.gather(
            read_from_pty(),
            write_to_pty()
        )
    except Exception as e:
        logger.error(f"WebSocket shell error: {e}")
        await websocket.close()

# WebSocket proxy routing for TempleOS serial console (QEMU)
@app.websocket("/ws/templeos")
async def ws_templeos(websocket: WebSocket):
    await websocket.accept()
    # Bridging websocket data streams directly to the running QEMU TempleOS instance
    try:
        # Check if QEMU instance is running and socket is available
        # We will mount QEMU stdin/stdout or use a TCP socket redirected by QEMU
        # For simplicity, we connect to a QEMU telnet redirect socket on loopback port 4444
        reader, writer = await asyncio.open_connection("127.0.0.1", 4444)
        
        async def read_qemu():
            try:
                while True:
                    data = await reader.read(1024)
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
            except Exception as e:
                logger.error(f"QEMU Read error: {e}")
                
        async def write_qemu():
            try:
                while True:
                    msg = await websocket.receive_text()
                    writer.write(msg.encode("utf-8"))
                    await writer.drain()
            except WebSocketDisconnect:
                pass
            except Exception as e:
                logger.error(f"QEMU Write error: {e}")

        await asyncio.gather(
            read_qemu(),
            write_qemu()
        )
    except Exception as e:
        logger.error(f"WebSocket TempleOS Connection error: {e}")
        await websocket.send_text("\r\n[Error: TempleOS altar offline. Spin up Chapter 21 VM Altar first!]\r\n")
        await websocket.close()

# Mount client build outputs (static files)
# If index.html is built, server serves it at root path
if hasattr(sys, '_MEIPASS'):
    client_dir = os.path.join(sys._MEIPASS, "client")
else:
    client_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client"))

dist_dir = os.path.join(client_dir, "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")
elif os.path.exists(client_dir):
    app.mount("/", StaticFiles(directory=client_dir, html=True), name="static")

if __name__ == "__main__":
    # Force strict local loopback binding
    uvicorn.run(app, host="127.0.0.1", port=8000)
