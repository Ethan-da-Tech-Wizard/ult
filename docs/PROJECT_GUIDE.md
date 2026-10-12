# The Sacred Tech

An educational browser JRPG that uses programming challenges, shell commands, SQL, and systems concepts as progression mechanics.

**Status:** Educational game prototype  
**Built with:** Python, FastAPI, browser JavaScript

## Reading order

1. Read the root README for project purpose and setup navigation.
2. Follow the entry points below to find the implementation.
3. Use the file guide to locate individual modules, tests, assets, and configuration.
4. Check component licenses before redistributing dependencies or assets.

## Important paths

- [PROJECT_NOTES.md](../PROJECT_NOTES.md) — Preserved detailed setup, usage, architecture, and development notes from the earlier README.
- [scripts/run_dev.sh](../scripts/run_dev.sh) — Command-line automation for run dev; review prerequisites and side effects before executing.
- [requirements.txt](../requirements.txt) — Python dependency requirements and optional dependency groups; install with the project’s documented interpreter and environment.

## Structure

| Path | Role |
| --- | --- |
| [.github/](../.github/) | GitHub workflow and contributor configuration (2 tracked entries). |
| [build/](../build/) | Build definitions or checked-in build support (13 tracked entries). |
| [client/](../client/) | Project-specific client components (6 tracked entries). |
| [docs/](../docs/) | Project documentation, decisions, and reference material (5 tracked entries). |
| [sandbox/](../sandbox/) | Project-specific sandbox components (23 tracked entries). |
| [save_data/](../save_data/) | Project-specific save data components (2 tracked entries). |
| [scripts/](../scripts/) | Build, launch, maintenance, and verification commands (5 tracked entries). |
| [server/](../server/) | Project-specific server components (4 tracked entries). |
| [setup/](../setup/) | Project-specific setup components (6 tracked entries). |

## Scope

Optional container and terminal integrations have a larger trust boundary than the basic browser game. Read the documented tiers before enabling them. The root checkout is the standalone application. A historical nested checkout is retained separately and is excluded from the tracked application.

## Maintaining the guide

The file catalog is a source-inspection snapshot, not proof that every runtime path works. Update it when moving files or changing module responsibilities. The 2026-10-12 documentation review did not run every application, deploy services, or validate all historical performance claims.
