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
