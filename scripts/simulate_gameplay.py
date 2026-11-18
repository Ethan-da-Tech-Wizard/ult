#!/usr/bin/env python3
# Program: ult - simulate_gameplay.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Simulates a full playthrough: starts the server, solves all 22 chapters through the API while saving progress, and writes a Markdown progression log to save_data.
"""Simulated gameplay loop for the game server."""
# ─────────────────────────────────────────────────────────────────────────────
# simulate_gameplay.py — Simulated Gameplay Loop for The Sacred Tech
# ─────────────────────────────────────────────────────────────────────────────
# ---- Imports ----
import os
import sys
import json
import time
import tempfile
import subprocess
import urllib.request
import urllib.error

# Repository root (one level above scripts/).
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Address the server listens on.
BASE_URL = "http://127.0.0.1:8000"

# List of chapter titles from game data
CHAPTER_NAMES = {
    0: "Outpost Zero (CLI Path Setup)",
    1: "Alexandria Library (OCR Grayscale & Binary Threshold)",
    2: "Relational Meadows (SQL Parameterization & Injections)",
    3: "Document Dunes (Redis Cache eviction & TTL)",
    4: "Parallel Swamp (Mutex Concurrency Locks)",
    5: "Iron Peaks (C++ Contiguous Array sums)",
    6: "Docker Relic (Security Dependency Audits)",
    7: "Whispering Woods (Byte Pair Encoding tokenizers)",
    8: "Valley of Attention (Scaled Dot-Product Attention layers)",
    9: "Forge of Zeus (Layer Normalization & SGD updates)",
    10: "Reranking Reefs (Advanced Hybrid Vector search)",
    11: "API Archipelago (Secure loopback bindings)",
    12: "Graph Gardens (Neo4j Cypher shortestPath matching)",
    13: "Testing Tundra (NLP BLEU & ROUGE metrics)",
    14: "Fine-Tuning Fiord (LoRA Adapter forward weights)",
    15: "Security Caves (Prompt guardrails & secret redactions)",
    16: "Deployment Cliffs (Symmetric INT8 Quantization)",
    17: "Agentic Skyway (JSON Schema function introspection)",
    18: "State Vaults (Corrective Agentic RAG ReAct Loops)",
    19: "Kubernetes Citadel (Pod specs & Ingress route bounds)",
    20: "The Grand Assembly (Integrated multi-modal proximity pipeline)",
    21: "Altar of TempleOS (Bare-metal HolyC compilation checksums)"
}

def request_json(path, method="GET", payload=None, timeout=10):
    """Send an HTTP request and return the decoded JSON body; prints and re-raises HTTP errors."""
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        raise e

def wait_for_server(proc, timeout=15):
    """Poll /api/health until ok; raise RuntimeError if the server exits early or times out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Server exited early with code {proc.poll()}")
        try:
            health = request_json("/api/health", timeout=1)
            if health.get("status") == "ok":
                return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError("Server did not become healthy in time.")

def main():
    """Play every chapter in order and write the log; returns 0 on success, 1 if a chapter fails."""
    print("🚀 Starting game server for progression playthrough...")
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR
    
    # Run the server in a subprocess
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT_DIR, "server", "main.py")],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Collect the Markdown lines for the playthrough log.
    log_content = []
    log_content.append("# 🎮 The Sacred Tech: Complete Gameplay Playthrough Log")
    log_content.append(f"\n*Simulated Playthrough Date: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
    log_content.append("This document records the exact progression, dialog, and validation traces as a simulated player advances through all 22 gates to the Altar of TempleOS.")
    log_content.append("\n---\n")

    try:
        wait_for_server(proc)
        print("✅ Server active. Starting chapter-by-chapter progression...")

        unlocked = []
        gold = 200
        tokens = 100

        # Solve each of the 22 chapters in turn.
        for ch_id in range(22):
            ch_name = CHAPTER_NAMES.get(ch_id, f"Chapter {ch_id}")
            print(f"🎮 Playing: {ch_name}...")
            
            # Fetch default code/solution
            if ch_id == 0:
                code = 'export PATH=$PATH:/usr/local/bin\necho "Booting environment..."\n'
            else:
                code_data = request_json(f"/api/code?chapter_id={ch_id}")
                code = code_data.get("code", "")
                
            # Compile and validate
            # Time the validation call for the log.
            start_time = time.time()
            result = request_json(
                "/api/compile",
                method="POST",
                payload={"chapter_id": ch_id, "code": code}
            )
            elapsed = time.time() - start_time
            
            success = result.get("success", False)
            output = result.get("output", "")
            
            if not success:
                print(f"❌ Failed to solve chapter {ch_id}: {output}")
                return 1

            # Update progression state
            # Update simulated progression: unlock the chapter and award gold and tokens.
            unlocked.append(str(ch_id))
            gold += 100
            tokens += 50
            
            # Save state
            # Persist the simulated state through the save API.
            save_payload = {
                "gold": gold,
                "compute_tokens": tokens,
                "unlocked_chapters": ",".join(unlocked),
                "active_lead": "Low-Level Optimizer",
                "inventory_json": json.dumps([f"contract:{ch_id}"]),
                "stats_json": json.dumps([]),
                "state_json": json.dumps({
                    "currentChapter": ch_id + 1 if ch_id < 21 else 21,
                    "x": 10,
                    "y": 10,
                    "screenMode": "color"
                })
            }
            request_json("/api/save", method="POST", payload=save_payload)
            
            # Document the step
            log_content.append(f"## 🏆 {ch_name}")
            log_content.append(f"- **Compile Status**: `SUCCESS` (Verified in {elapsed:.3f}s)")
            log_content.append("- **Verification Output Log**:")
            log_content.append("```text")
            log_content.append(output.strip())
            log_content.append("```")
            
            # Reward text simulated
            log_content.append(f"- **Progression Status**: Relic Gate unlocked. Gold is now **{gold}**, Compute Tokens: **{tokens}**.")
            log_content.append("\n---\n")

        print("🎉 Simulated play completed successfully!")
        
        # Save gameplay log as artifact
        # Write the finished log to save_data/gameplay_progression.md.
        artifact_path = os.path.join(ROOT_DIR, "save_data", "gameplay_progression.md")
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_content))
            
        print(f"📝 Gameplay progression log saved to: {artifact_path}")
        
    # Always stop the server, killing it if it does not exit within 5 seconds.
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    sys.exit(main())
