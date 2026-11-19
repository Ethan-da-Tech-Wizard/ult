#!/usr/bin/env python3

# ==============================================================================
# Program: simulate_gameplay.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Autonomous player simulation harness verifying end-to-end game progression.
#          Spawns an isolated background backend instance, sequentially steps through all 22
#          chapter gates, executes and validates algorithmic solutions, records step execution
#          latencies, and generates an exhaustive Markdown progression log artifact.
# ==============================================================================

# How this file fits the app: developer tool (not part of CI) that plays through all 22 chapters automatically and writes a Markdown log to save_data/gameplay_progression.md (a tracked file in this repo, so running the script modifies it).
# Caveat: unlike the CI smoke tests it does NOT set ZEUS_SAVE_DB_PATH, so it writes progress into the real save database (save_data/save_state.db) and leaves the game "completed" with extra checkpoint rows; back up or delete the save first if you care about it. The server output pipe is not read.

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

# Repo root and fixed loopback address, as in full_stack_smoke.py.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_URL = "http://127.0.0.1:8000"

# Human-readable title per chapter, used only for the log. Keep in step with CHAPTER_FILENAME_MAP / templates in server/main.py.
# Canonical chapter catalog titles mapping to specific challenge gates
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
    21: "Altar of TempleOS (Bare-metal HolyC compilation checksums)",
}


# Same helper as in full_stack_smoke.py, but also prints the server's error body on HTTP errors for easier debugging.
def request_json(path, method="GET", payload=None, timeout=10):
    """Executes HTTP JSON request against the local backend server."""
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
    """Polls server health endpoint until operational readiness is achieved."""
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


# Walks chapters 0 to 21 and for each: fetch starter code, compile, record time, simulate a save, append a log section. Gold +100 and tokens +50 per chapter are simulation numbers, not the game's real reward formula.
def main():
    """Main simulation driver stepping through all 22 chapter challenges."""
    print("🚀 Starting game server for progression playthrough...")
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR

    # Launch server subprocess with pipe redirection
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT_DIR, "server", "main.py")],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

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

        # Chapter 0's template is intentionally broken, so a known-good solution is submitted instead.
        # Step sequentially through each chapter curriculum
        for ch_id in range(22):
            ch_name = CHAPTER_NAMES.get(ch_id, f"Chapter {ch_id}")
            print(f"🎮 Playing: {ch_name}...")

            # Acquire solution code
            if ch_id == 0:
                code = 'export PATH=$PATH:/usr/local/bin\necho "Booting environment..."\n'
            else:
                code_data = request_json(f"/api/code?chapter_id={ch_id}")
                code = code_data.get("code", "")

            # Compile and validate against test framework
            start_time = time.time()
            result = request_json(
                "/api/compile",
                method="POST",
                payload={"chapter_id": ch_id, "code": code},
            )
            elapsed = time.time() - start_time

            success = result.get("success", False)
            output = result.get("output", "")

            if not success:
                print(f"❌ Failed to solve chapter {ch_id}: {output}")
                return 1

            # Minimal save state is written after every chapter, so the final database row says "chapter 21, color mode".
            # Update progression state variables
            unlocked.append(str(ch_id))
            gold += 100
            tokens += 50

            # Commit updated save state to database
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
                    "screenMode": "color",
                }),
            }
            request_json("/api/save", method="POST", payload=save_payload)

            # Record verification log step
            log_content.append(f"## 🏆 {ch_name}")
            log_content.append(f"- **Compile Status**: `SUCCESS` (Verified in {elapsed:.3f}s)")
            log_content.append("- **Verification Output Log**:")
            log_content.append("```text")
            log_content.append(output.strip())
            log_content.append("```")
            log_content.append(f"- **Progression Status**: Relic Gate unlocked. Gold is now **{gold}**, Compute Tokens: **{tokens}**.")
            log_content.append("\n---\n")

        print("🎉 Simulated play completed successfully!")

        # Log path under save_data/; the directory is created if missing.
        # Persist comprehensive playthrough log to disk
        artifact_path = os.path.join(ROOT_DIR, "save_data", "gameplay_progression.md")
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write("\n".join(log_content))

        print(f"📝 Gameplay progression log saved to: {artifact_path}")
        return 0

    # Always shut the server down, even when a chapter fails.
    finally:
        # Gracefully terminate server subprocess
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
