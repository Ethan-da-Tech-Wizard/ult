# License review — The Sacred Tech

Reviewed 2026-10-12. Original project code retains **MIT** terms in [LICENSE](../LICENSE).

The owner selected MIT for previously unlicensed original code. Existing licenses were preserved. This choice does not relicense copied code, dependencies, datasets, model weights, fonts, logos, or game assets.

## Preserved notices

- [LICENSE](../LICENSE)

## Dependency evidence

[DEPENDENCIES.csv](DEPENDENCIES.csv) lists 8 manifest and lockfile records. Repeated packages can appear under different manifests, versions, or development scopes. Registry metadata is evidence, not a replacement for the actual license text. For unpinned ranges, `metadata_version` is the version inspected and is not a claim about every install. Go and system/build tools can require notices beyond package-manager metadata.

| Component | Declared version | License evidence |
| --- | --- | --- |
| crates.io: tauri | 1.5 | [Apache-2.0 OR MIT](https://crates.io/api/v1/crates/tauri) |
| crates.io: serde | 1.0 | [MIT OR Apache-2.0](https://crates.io/api/v1/crates/serde) |
| crates.io: serde_json | 1.0 | [MIT OR Apache-2.0](https://crates.io/api/v1/crates/serde_json) |
| crates.io: tauri-build | 1.5 | [Apache-2.0 OR MIT](https://crates.io/api/v1/crates/tauri-build) |
| PyPI: fastapi | >=0.111.0 | [MIT](https://pypi.org/pypi/fastapi/json) |
| PyPI: uvicorn | >=0.30.0 | [BSD-3-Clause](https://pypi.org/pypi/uvicorn/json) |
| PyPI: pydantic | >=2.7.0 | [MIT](https://pypi.org/pypi/pydantic/json) |
| PyPI: numpy | >=1.26.0 | [BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0](https://pypi.org/pypi/numpy/json) |

## Project-specific considerations

Optional container and terminal integrations have a larger trust boundary than the basic browser game. Read the documented tiers before enabling them. The root checkout is the standalone application. A historical nested checkout is retained separately and is excluded from the tracked application.

## Remaining work before binary distribution

No unresolved registry-license lookup remains in the listed package records. System packages, downloaded tools/models, optional plugins, release binaries, and externally obtained assets need a build-specific inventory. This source review is not a blanket legal certification or a claim that every release artifact has been audited.
