# The Sacred Tech

An educational browser JRPG that uses programming challenges, shell commands, SQL, and systems concepts as progression mechanics.

**Status:** Educational game prototype  
**Built with:** Python, FastAPI, browser JavaScript

[Project guide](docs/PROJECT_GUIDE.md) · [Every file explained](docs/FILE_GUIDE.md) · [Licenses and dependencies](docs/LICENSE_REVIEW.md)

## Start here

- [PROJECT_NOTES.md](PROJECT_NOTES.md) — Preserved detailed setup, usage, architecture, and development notes from the earlier README.
- [scripts/run_dev.sh](scripts/run_dev.sh) — Command-line automation for run dev; review prerequisites and side effects before executing.
- [requirements.txt](requirements.txt) — Python dependency requirements and optional dependency groups; install with the project’s documented interpreter and environment.

[Detailed setup, usage, and development notes](PROJECT_NOTES.md) preserve the previous project documentation.

## Repository layout

| Path | Role |
| --- | --- |
| [.github/](.github/) | GitHub workflow and contributor configuration (2 tracked entries). |
| [build/](build/) | Build definitions or checked-in build support (13 tracked entries). |
| [client/](client/) | Project-specific client components (6 tracked entries). |
| [docs/](docs/) | Project documentation, decisions, and reference material (5 tracked entries). |
| [sandbox/](sandbox/) | Project-specific sandbox components (23 tracked entries). |
| [save_data/](save_data/) | Project-specific save data components (2 tracked entries). |
| [scripts/](scripts/) | Build, launch, maintenance, and verification commands (5 tracked entries). |
| [server/](server/) | Project-specific server components (4 tracked entries). |
| [setup/](setup/) | Project-specific setup components (6 tracked entries). |

## Scope and current limits

Optional container and terminal integrations have a larger trust boundary than the basic browser game. Read the documented tiers before enabling them.

## License

Original project code retains **MIT** terms in [LICENSE](LICENSE). Third-party libraries, media, data, models, and tools retain their own terms. See the [license review](docs/LICENSE_REVIEW.md) and [dependency inventory](docs/DEPENDENCIES.csv).
