# Pitwall 2000 Mods

Public distribution metadata and original creations for Pitwall 2000's data-only Mod API 1.
The game source remains in its separate private repository.

The v0.4.5.0 featured catalog replaces the original demonstration listings with six native,
editable, text-free liveries (28 shapes each) and **Realistic Formula 1 Season**. `void_58` is
a fictional author identity used for this release. The season contains the verified official
standings through 25 October 2026 and transparent game estimates for performance. Its metadata
records sources, dates and exact-layout calendar omissions. It starts a new championship at zero points.

Public download counts come from GitHub release assets; likes/dislikes come from the catalog's
rating issue reactions. Missing counts are unavailable. Publishing a user creation prepares a
validated ZIP and opens a submission form; it requires authentication and maintainer review.
Old example sources and immutable releases remain available for existing saves. Their historical
catalog is archived in `archive/catalog-examples-v1.json`; they are no longer default listings.

`featured/` contains original geometric configurations and sourced factual data, with no private
game source, shipped sprite artwork, reference photographs, sponsor logos or embedded credentials.

The live catalog is [catalog.json](https://raw.githubusercontent.com/Grizzly20121/Pitwall2000-Mods/main/catalog.json).
ZIP downloads live in [versioned Releases](https://github.com/Grizzly20121/Pitwall2000-Mods/releases).
Installed packages work offline, without an account or API token.

Start with [the creator guide](CREATOR_GUIDE.md) and copy a complete example folder as a template.
Examples cover a race circuit with pits, a vehicle, paint, teams/drivers, a championship,
a dependency collection, a mixed package, and a side-by-side vehicle update.
These are fictional, purpose-built examples, not real teams, licensed vehicles, or shipped game assets.

`examples/` and `authoring/` are original CC0-1.0 teaching material.
The small creator utilities are MIT licensed; see [LICENSE](LICENSE).
Schemas describe the data interface and are CC0-1.0.
Do not infer any license for the separate game or third-party community packages.

Submit through an Issue or PR using [CONTRIBUTING.md](CONTRIBUTING.md).
There is no player upload endpoint, rating service, payment backend, or token in the game.
