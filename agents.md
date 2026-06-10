# The Sacred Tech: Chronicles of the Source Code - Agent Architecture & Implementation Plan

"The Sacred Tech" is a retro 2D educational JRPG (Final Fantasy I style) that teaches command line, databases (SQL, NoSQL, Graphs), C++ interop, Docker, multi-head Attention, Transformer training, LoRA fine-tuning, INT8 quantization, Agent loops, Kubernetes, and bare-metal HolyC compilers. Players write code inside a split-screen IDE (Monaco editor layout) to resolve bug bounties, secure databases, lower drawbridges, and defeat gatekeepers.

---

## 1. Technical Architecture & System Ports
The desktop application is built as a single relocatable bundle served offline:

* **Local compiler server (`server/main.py`)**: Runs locally on loopback interface `127.0.0.1:8000`. Exposes REST API endpoints for state saves (`/api/save`) and compilation checks (`/api/compile`).
* **Relational database (`save_data/save_state.db`)**: SQLite database storing JRPG progress (Gold, compute tokens, party levels, unlocked doors).
* **PTY Terminal shell websocket (`/ws/shell`)**: Spawns terminal processes inside the Arch Linux compiler container, proxied directly to the client browser Alt+5 terminal tab.
* **QEMU TempleOS launcher (`server/qemu_launcher.py`)**: Boots headless TempleOS Serials Telnet redirect on loopback port `4444`. bridger websocket `/ws/templeos` routes player commands directly to the virtual serial interface.
* **Tauri & PyInstaller wrapper**: Exposes build scripts to bundle the entire project folder into a standalone single-file double-clickable executable (`Zeus_Assistant`).

---

## 2. Overworld Maps & 8-Bit Pixel Characters
The game world is split into 9 main JRPG maps containing boundary tiles (`1` brick wall, `5` water/swamp), portal warps (`6`), Altars (`4`), chests (`3`), and NPCs (`2`). Emojis are drawn as custom 8x8 pixel-art grids:

1. **Outpost Zero (Chapter 0)**: Starting fortress. Starts in total darkness.
   * **Sentinel Guard (💂)**: Halts the pilgrim; warns about closed-weights compiler locks.
   * **Compiler Smith (⚒️)**: Teaches python syntax loops.
   * **Gitpus (🐙)**: Sits in a puddle warning players about Git merge conflicts.
2. **Alexandria Library (Chapter 1)**: Desert brick ruins scorched by drone strikes.
   * **Scribe Cassia (👩‍🏫)**: Scribe sitting on ash piles analyzing OCR coordinate scrolls.
   * **Ash Pilgrim (🧙)**: Mourns the destruction of open-source knowledge.
   * **Index Clerk (📚)**: Catalogs text matrices.
3. **Relational Meadows (Chapter 2)**: Green plains divided by primary key tables.
   * **Bessie_Table (🐮)**: Cow INNER JOINing grass.
   * **Farmer Join (👨‍🌾)**: Teaches SQL injection patch parameters.
4. **Document Dunes (Chapter 3)**: Canyon where key-value documents are traded.
   * **Dune Merchant (🐫)**: Trades polymorphic JSON.
   * **Redis Spirit (🧞)**: Complains about cache invalidation limits.
5. **Parallel Swamp (Chapter 4)**: Muddy swamp bogs.
   * **Garbage Golem (🤖)**: Sweeps heap and eats dereferenced memory chunks.
   * **Mutex Frog (🐸)**: Locked waiting for thread release.
6. **Graph Gardens (Chapter 12)**: Relationship maze.
   * **Cypher Rabbit (🐰)**: Traverses cabbage node links.
7. **Deployment Cliffs (Chapter 16)**: High windy ridges.
   * **FP16 Parrot (🦜)**: Squawks spelling errors when quantized to INT4.
8. **State Vaults (Chapter 18)**: Grave hollow in Spooky Town.
   * **Bones (💀) & Specter (👻)**: Skeleton programmers guiding you through ReAct loops.
9. **Altar of TempleOS (Chapter 21)**: Sanctuary lined with Terry's Shrines (`🏛️`) and Altar blocks (`4`). High Priest compiles HolyC bare-metal checksums.

---

## 3. Verbatim 22-Chapter Curriculum
Each JRPG area unlocks a distinct sandbox validator checking logic outputs in `/sandbox/test_frameworks/`:

* **Chapter 0: Outpost Zero**: Navigate folders, print redirect streams, update `$PATH` variables.
* **Chapter 1: Alexandria Library**: Matrix binarization filters, row segmentations, and OCR tesseract engines.
* **Chapter 2: Relational Meadows**: SQL primary keys, foreign tables, aggregations, and SQL Injection patch security.
* **Chapter 3: Document Dunes**: Polymorphic JSON objects, dict in-memory caching, and TTL eviction policies.
* **Chapter 4: Parallel Swamp**: Asyncio coordinate loops, multithreading GIL limits, and `threading.Lock` mutex locks.
* **Chapter 5: Iron Peaks**: CPU execution profiling, C++ contiguous arrays, and pybind11 modules.
* **Chapter 6: Docker Relic**: Dockerfiles, mounts, ports, compose files, and `pip-audit` CVE dependency scans.
* **Chapter 7: Whispering Woods**: Subword frequencies, BPE token merges, and padding masks.
* **Chapter 8: Valley of Attention**: Q, K, and V attention projections, scaled dot-product attention, and softmax layers.
* **Chapter 9: Forge of Zeus**: LayerNorm layers, residual skip-connections, PyTorch cross-entropy, and backprop training loops.
* **Chapter 10: Reranking Reefs**: HNSW graphs, vector Cosine similarity, and BM25 hybrid ranking.
* **Chapter 11: API Archipelago**: FastAPI server setups, CORS routers, rate-limiting, and env credential file configurations.
* **Chapter 12: Graph Gardens**: Entity-relationship nodes, Neo4j Cypher shortestPath matching.
* **Chapter 13: Testing Tundra**: Automated translation metrics (BLEU-1 and ROUGE-L).
* **Chapter 14: Fine-Tuning Fiord**: LoRA rank adapters ($W = W_0 + \frac{\alpha}{r} B A$) and parameter merges.
* **Chapter 15: Security Caves**: Prompt jailbreak guardrails, output sanitizers, and JSON schemas.
* **Chapter 16: Deployment Cliffs**: Symmetric INT8 quantization scales ($S = \max(|x|) / 127$) and dequantization.
* **Chapter 17: Agentic Skyway**: Auto function-to-json schema exporters and execution mappings.
* **Chapter 18: State Vaults**: Max step ReAct loop execution and circular lineage recursions.
* **Chapter 19: Kubernetes Citadel**: Resource memory limits, NodePort Services, and Ingress routing rules.
* **Chapter 20: The Grand Assembly**: Integrated pipeline joining OCR, SQLite, Graph databases, and LLM text generation.
* **Chapter 21: Altar of TempleOS**: Headless serial booting telnet streams and bare-metal HolyC compilation checksums.

---

## 4. Engineering Session Log — QoL & Lint Pass (2026-06-10)

This section documents, in detail, the cleanup and quality-of-life work done on branch `claude/affectionate-keller-e00ku3` so future agents understand what changed, why, and what conventions to follow.

### 4.1 Lint & Dead-Code Fixes

**Python (all ruff findings resolved — `ruff check server scripts sandbox` is now clean):**

| File | Fix |
|---|---|
| `server/main.py` | Removed unused `import json` |
| `server/qemu_launcher.py` | Removed unused `buffer` variable in the mock HolyC client thread |
| `sandbox/test_frameworks/ch4_test.py` | Removed unused `import time` |
| `sandbox/test_frameworks/ch6_test.py` | Removed unused `import subprocess` |
| `sandbox/test_frameworks/ch19_test.py` | Removed unused `current_key` variable in the YAML fallback parser |

**JavaScript (`client/app.js`):**

* Removed `formatValidatorHints()` — defined but never called anywhere.
* Removed the dead `currentBgmNode` variable (replaced by real gain-node tracking, see 4.3).
* Removed an unused `chapterNPCs` lookup at the top of `checkInteraction()`.
* Removed the duplicated `palette-selector` "Settings handlers" change-listener block (it was registered twice from two identical copy-pasted sections).

**Note for future agents:** the remaining `no-unused-vars` ESLint warnings (`buyShopItem`, `useInventoryItem`, `setActiveLead`, `executeCombatAction`, `openLibraryBook`, `insertLessonExample`, `applyLessonChapter`) are FALSE POSITIVES — these functions are invoked from generated inline `onclick="..."` HTML and must stay top-level globals. Do not delete them. `app.js` is loaded as a plain (non-module) script for exactly this reason.

### 4.2 Real Bug Fixes

* **Orphaned shell processes (`server/main.py`, `/ws/shell`)**: the PTY subprocess handle was previously dropped (`proc` assigned, never used), so every websocket disconnect leaked a live `bash` process and the handler's `asyncio.gather` never returned. Now the handler uses `asyncio.wait(..., return_when=FIRST_COMPLETED)`, cancels the surviving task, kills/reaps the subprocess, and closes the PTY master fd in a `finally` block. Verified: 3 connect/disconnect cycles leave zero stray bash processes.
* **Deprecated FastAPI startup hook**: migrated `@app.on_event("startup")` to a `lifespan` async context manager passed to `FastAPI(...)`. The QEMU/mock-HolyC boot logic is unchanged.
* **Unwired settings UI (`client/index.html` + `app.js`)**: the Dialogue Speed selector, Focus Controls selector, and Close button existed in HTML with zero JS references. All are now functional (see 4.3). The Focus Controls option label was corrected from "Both (Tab & Escape)" to "Both (Tab & Ctrl+E)" to match actual behavior.

### 4.3 New QoL Features

**Settings persistence (`client/app.js`)**
* All settings live in the `gameSettings` object and persist to `localStorage` under the key `sacredTechSettings` (`loadGameSettings()` / `saveGameSettings()`).
* Persisted fields: `palette`, `dialogueSpeed` (`scroll` | `instant`), `focusKeys` (`both` | `tab`), `bgmVolume` (0–100), `muted` (bool).
* `syncSettingsUI()` pushes loaded values into the settings menu controls at startup; `applyPalette()` applies the body class.

**Dialogue char-scroll**
* `renderDialogueText()` implements retro typewriter scrolling (2 chars / 16 ms tick) when `gameSettings.dialogueSpeed === "scroll"`; instant print otherwise.
* While text is typing, the advance keys first complete the text (`completeDialogueText()`), and only then close the dialogue — standard JRPG behavior. `hideDialogue()` clears any running typing timer.

**Audio: volume, mute, and SFX**
* Settings menu gained a Music Volume slider (`#bgm-volume-slider`) and Mute checkbox (`#mute-audio-toggle`).
* `playBgm()` now sets a per-theme `baseGain` and routes the final gain through `applyBgmVolume()`; the tracked `currentBgmGainNode` lets the slider change volume live mid-track. Slider value 60 (`DEFAULT_BGM_VOLUME`) reproduces the originally-authored loudness.
* New `playSfx(type)` synth blips: `step` (movement), `menu` (tab switch / dialogue open), `hit` (combat start), `coin` (shop purchase), `heal` (item use). All respect mute + volume.
* The global keydown handler resumes a suspended `AudioContext` on first input (browser autoplay policy).

**Held-key movement**
* `DIRECTION_KEYS` maps WASD/arrows to deltas. First press moves immediately; holding repeats every `HELD_MOVE_INTERVAL_MS` (150 ms) via a `requestAnimationFrame` loop (`heldMovementLoop`) instead of relying on OS key-repeat.
* `keyup` removes keys from `heldDirections`; `window blur` clears all held keys to prevent stuck movement.

**Forgiving interact keys**
* Space and `E` now advance dialogue and trigger `checkInteraction()` alongside Enter. Plain `e` interacts; `Ctrl+E` still toggles editor focus (only when Focus Controls is set to "both").
* Keyboard handler now ignores game keys when the event target is an `INPUT`/`TEXTAREA`/`SELECT`, so typing `w` in the terminal/search inputs no longer moves the player.

**Save history loader**
* Server: new `GET /api/saves?limit=N` (id, gold, compute_tokens, unlocked_chapters, state_json of the most recent rows, limit clamped 1–50) and `GET /api/save/{save_id}` (full row, 404 if missing). Every save was already an `INSERT`, so history existed — it just wasn't exposed.
* Client: Settings menu "Load Earlier Save..." button toggles `renderSaveSlotList()`, which lists recent saves (`#id — Ch X, gold, timestamp`) with Load buttons calling `loadSaveById()`.
* `fetchSaveState()` was refactored: the save-application logic is now the reusable `applySaveData(data)`.

**Encounter relief**
* `encounterGraceSteps` (6 steps) is granted after every combat (win via `endCombat()`, loss via the `loseCombat()` warp) — no back-to-back random battles.
* New shop item **Debug Spray** (`debug_spray`, 40 gold): sets `repelSteps = 40`; both counters tick down only on encounter-eligible (grass) tiles and suppress the encounter roll while active.

**Minimap objective marker**
* `getObjectiveMarker()` returns the tile the player should head toward: the Compiler Smith during the Chapter 0 tutorial stage, otherwise the portal tile (tile id `6`) once `isChapterGateOpen()` is true. Returns `null` in dark mode or when the objective is editor work.
* `drawMinimap()` draws a pulsing yellow outline around the marker (pulse animates via the existing 700 ms ambient redraw interval).

**Editor niceties**
* `Ctrl+Enter` inside the code editor triggers Compile & Run (the `run-btn` tooltip already promised this; now it's real).
* New "Reset to Skeleton" button in the editor header fetches `GET /api/code?chapter_id=X&skeleton=1` (new `skeleton` query param on the existing endpoint, which bypasses the saved relic file and returns `get_default_skeleton()`), with a `confirm()` guard before replacing editor contents.

**Styling (`client/style.css`)**: added styles for the volume slider, `#open-save-slots-btn`, `#save-slot-list`, and `.save-slot-row` consistent with the retro panel look.

### 4.4 Deliberately NOT Implemented

* **Fast travel between visited maps** — excluded on purpose: fast travel is a late-game unlock by design. Do not add a free fast-travel system.

### 4.5 Verification Performed

* `ruff check server scripts sandbox` — clean.
* `python3 -m py_compile` on all server/scripts files — clean.
* `node --check client/app.js` — clean; ESLint shows 0 errors (remaining warnings are the inline-onclick false positives noted in 4.1).
* `scripts/full_stack_smoke.py` — all 22 chapter validators PASS, save/load persistence PASS.
* `scripts/first_portal_smoke.py` — all 3 checks PASS.
* Live server boot: `/api/health`, `/api/saves`, `/api/save/{id}`, `/api/code?skeleton=1` all exercised with curl; websocket shell leak fix verified with 3 connect/disconnect cycles (no orphaned bash processes).
