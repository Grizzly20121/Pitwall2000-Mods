# Creating Mod API 1 content

## Mod Creator in 0.4.5.0

The main-menu Mod Creator replaces Race Replay. Create/edit/preview/validate/save your own
car, livery, track or season; Manage My Mods creates editable copies without altering immutable
installations. Export ZIP packages or Install locally to use them through the existing selection.
Publish / Submit prepares a ZIP and opens a GitHub issue form. Attach the ZIP or provide an
immutable release URL. Signing in and maintainer review are separate steps; the game never
claims that preparing a package published it. Updating an existing public mod requires ownership.

Native livery layers support keyboard selection with [ and ], arrow movement, numeric X/Y,
size/rotation, layer ordering and the existing portable format. Both livery entry points share
the same publishing workflow. Imported sprites face downwards in the top-down editor, matching
the game's existing car orientation. Car width/length are metres; the preview grid is one metre.
Custom physics bounds are validated and used by the real driving and projection models.

The source-project Track Editor calls the existing SVG importer. It requires Python with that
importer's NumPy/Shapely dependencies **for authoring**. Players installing compiled track ZIPs
do not need these tools. The technical JSON and route/marker controls expose the importer schema;
source edits, previews, continuity/pit checks and vector tessellation use that same pipeline.
Compilation errors identify the failing technical ID and correction. Do not bypass validation.

The optional manifest `metadata` dictionary records provenance, cutoff dates and explanatory
notes. `authoredIdentity` preserves a mod's supplied names; it does not rename built-in content.
Optional vehicle `customCar` data adds bounded PNG sprite, metric dimensions, speed, acceleration,
braking, grip and DRS settings. Author ZIPs declare game `>=0.4.5.0`. See generated schemas.
The `creator-v1` packaging convention uses sorted entries, fixed timestamps, stored compression
and explicit regular-file attributes; unchanged creations reproduce identical bytes.

Catalog download totals are actual GitHub asset counts. `ratingIssue` points at a public issue
whose +1/-1 reactions supply public votes. Without a personal `PITWALL_GITHUB_TOKEN` environment
variable, voting opens the GitHub page and requires the player to sign in and choose a reaction.
Tokens are never stored in mod packages or shipped with the game. Offline cached totals are dated;
unavailable totals stay unavailable.

Players need only the game and a ZIP. Python and the SVG authoring pipeline are author tools.
Never ask players to install Python, an editor, an importer, a plugin, or source code.

## Start from a working template

Copy one version folder under `examples/`, change its ID and every added content ID, and edit
the JSON. Keep `mod.json` at ZIP root, not inside another folder.
Use `python tools/package.py path/to/folder output.zip` to validate and package.
The utility writes `output.zip.submission.json` with real size and SHA-256.
Run the game's own validator for cross-reference and gameplay validation:

```
Pitwall2000.exe --headless -- --validate-mod=absolute/path/output.zip
```

Install dependencies first through Mods. The command validates in separate temporary storage
and does not alter the player's installed library. The in-game import and selection combination
validation are authoritative. CI checks structure and distribution integrity; a green CI check
is not evidence of a race, a pit stop, or season rollover.

## Manifest fields

See `schemas/mod.schema.json`. Unknown members and required features are rejected.
Explicit JSON null is unsupported: omit optional properties. Numbers must be finite.
The following versions are distinct:

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Manifest shape, currently integer 1 |
| `modApiVersion` | Gameplay content contract, currently integer 1 |
| `version` | Immutable package version: exactly three nonnegative numeric components |
| `gameVersions` | Game compatibility: exactly four numeric components per version |

Constraints accept `*`, exact versions, or space-separated comparisons `>=`, `>`, `<=`, `<`, `=`.
For example `>=0.4.4.0 <0.5.0.0`. Comparisons are numeric by component, so 0.4.10.0 > 0.4.4.0.
There are no prereleases, wildcards inside a version, caret, tilde or OR expressions.
Each component is at most six digits; leading zeroes are forbidden.

| Field | Description |
| --- | --- |
| `id` | Lowercase namespaced key, e.g. `author.package`; never a path |
| `name`, `author` | 1–100 characters each |
| `description` | At most 4000 characters, displayed as inert text |
| `license` | Required redistribution license identifier/text, at most 100 characters |
| `homepage` | Optional HTTPS informational URL; the game does not execute it |
| `preview` | Optional package-relative PNG, e.g. `preview.png` |
| `categories` | Unique values: tracks, vehicles, seasons, liveries, driversTeams, modpacks |
| `content` | Category → explicit JSON entry path; every content category needs a path |
| `dependencies` | Up to 64 `{id, version}` requirements; downloaded only on explicit Install |
| `conflicts` | Up to 64 `{id, version}` incompatible package constraints |
| `replacements` | Up to 64 existing content IDs explicitly replaced by this package |
| `requiredFeatures` | Empty in API 1; unknown required features fail |

New content IDs start with the full package ID plus `.`, such as `author.package.car-1`.
Duplicate IDs, undeclared collisions, missing replacement targets, and two replacements of the
same target fail. A loadout permits one version per package. Deterministic dependency order
places requirements before dependents; cycles and incompatible constraints fail.
A `modpacks` package may contain multiple content categories or be only a dependency collection.
Neither installation order nor filenames select conflict winners.

## Supported content

The generated schemas enumerate all data members and enum choices in the actual runtime contract.
Omitted optional members use the game defaults. The additional semantic limits below apply even
where the structural schema permits a wider value.

**Tracks:** `tracks.json` is an array of `{definition, runtime, geometry}`.
Each layout has its own stable definition ID; use `Circuit — Layout` names.
`definition` supplies ID, name, country/region, measured length (200–30000 metres), default
laps (1–500), and pit limit (20–120 km/h). Do not supply asset paths or executable resources.
`runtime` references the shared SVG importer's compiled TrackSpace JSON, including directed road
samples, widths, increasing progress fractions, pit route, pit-box entry/stop/exit routes, limit
markers, recovery access and three timing sectors ending at 1. The example source.svg and
authoring settings demonstrate the technical IDs; runtime road order defines lap direction.
Grid slots are generated by the existing metric grid-placement routine from the start line.

The authoring bridge uses the game's shared `Tools/track_importer/geometry.py::compile_geometry`.
Authors with the project can run `Tools/build_workshop_examples.py`; player packages contain
the already compiled result. For other authors, copy the complete editable example and adapt
its documented runtime/geometry JSON, or use a compatible external exporter. Validate the result
in-game and run actual laps/pits before submitting.
Artwork uses the existing retained vector canvas: `geometry.json` has `imported: false`, a
viewBox, metresPerUnit, background, and bounded polygon/polyline `shapes`.
Each shape has id/layer, points, fill/stroke (`#RRGGBB` or `none`), width and closed.
No dashed strokes, SVG includes, large-visual indexes, shaders, vector batches or external assets.
These runtime visuals preserve the tactical rendering style. SVG is editable source, not a runtime importer.
API 1 does not introduce new DRS logic, special zones or grade-separation behavior.

**Vehicles:** `vehicles.json` is an array of vehicle definitions. Set stable ID/name,
existing `vehicleClass` and `category`, tier, performance, reliability, engine, brakes,
chassis, suspension, aerodynamics, tyre/fuel use, purchase/resale/running costs and `hasErs`.
Ratings are 0–100, tier 1–20, mass 50–5000 kg, consumption multipliers 0.1–5.
Existing simulation primitives determine category dimensions, mass/dynamics envelope and engine
sound family; a declared mass is descriptive where the existing simulation uses category mass.
The real detailed and accelerated simulation consume performance, reliability, consumption and ERS.
Choose a supported Formula4/3/2/Uno, Gt4/3, Lmp2 or Hypercar primitive for a new named car/class.
There is no arbitrary physics-code SDK or external model/audio loader in API 1.
Vehicle visuals use the existing body representation plus explicit original livery data.
`visualPath` and `aeroUpgradeVisualPath` are unsupported for community packages.
No background race music is introduced.

**Liveries:** entries contain ID/name, an explicit vehicleId, and a design.
Colors are `#RRGGBB`; patterns are Solid, Stripe, Panels, Chevron, Checks, Split, Aurora,
Velocity, Apex, Pulse, Heritage, Spectrum. Use up to 32 original Circle/Rectangle/Triangle/
Text/Line graphics with default font, normalized x/y, width/height in (0,1], rotation ±360,
and text up to 40 characters. Texture/font paths and sponsor decal references are unsupported.
Car designs are copied into game-owned vehicle states and shown in player and AI race views.
One selected livery per target vehicle; overlap is an error.

**Drivers/teams:** `roster.json` has `drivers` and `teams` arrays. Drivers have stable
IDs, names, nationality, age 16–70, 0–100 attributes, salary, development rate 0–3 and optional
eligible series references. Teams supply name/shortName, color, reputation 0–100, starting budget,
two distinct driver IDs and 1–8 vehicle references. Season rosters cannot reuse a driver twice.
These identities enter the existing world/market/standings systems. No portrait or suit feature
is added. New teams become entrants when referenced by a selected season or Sandbox setup.

**Seasons:** `seasons.json` contains championship definitions with ID/name, class/category,
teams, driver pools, points, career requirements, rules and calendar. There must be 1–50
consecutively numbered rounds, unique round IDs, valid track/layout references, ascending day
offsets within 0–350, laps 1–500 or duration up to 86400 seconds, and an even grid of 4–44.
Points are nonnegative integers up to 1000. References resolve against built-in plus selected content.
Each round has 1–4 races. Prestige is 1–100, reputation 0–100, tier 1–20,
staff limit 1–100, facility requirements 0–100 and sponsor quality 0–10
(maximum cannot be below minimum). Entry fee, operating cost and expected team value
are 0–1 billion. Both singular and plural prerequisite fields must resolve.
Custom career calendars take precedence over the ordinary 5/10/15-round preference.
After the last event, the existing season progression can repeat the authored calendar; eligible
built-in or explicitly referenced progression links remain available. Existing saves never migrate
their package versions automatically.

## Storage, bounds and safety

The game uses `user://mods/{installed,staging,cache,profiles}`. Updates install beside old versions.
Saves lock requested selections, dependencies, exact versions, SHA-256, load order, schema and API.
Installed ZIP bytes and extracted inventories are retained to detect tampering.
Old unmodded saves default to an empty lock. Failed recovery never rewrites the save.
Versions referenced by saved careers, backups, Sandbox presets or saved defaults cannot be removed.
Clear unused defaults or delete an unneeded save through normal game controls first.

Allowlist: JSON, PNG and inert SVG. No DLL/EXE, scripts, scenes, resources, shaders, PCK,
symlinks, absolute paths, traversal, alternate streams, Windows devices or case collisions.
ZIP64 and multi-volume archives are unsupported. Limits: 64 MiB compressed; 128 MiB expanded;
512 entries; 16 MiB/file; 200:1 per-entry ratio; JSON depth 32 and 20000 array entries;
PNG 2048×2048 maximum; SVG 2 MiB/10000 elements. Track road/pit ≤20000 points, 2–22 boxes;
visuals ≤2000 shapes/50000 total points/500 labels. Packages contain ≤1000 definitions.
Package assets cannot resolve arbitrary files or network references.

Additional runtime numeric checks apply to the generated structural schemas:

- Vehicle name: 1–100 characters; purchase/resale/running cost: 0–100 million.
  Category and vehicle class must be an existing supported pair.
- Team name: 1–100 characters; short name: 1–40. Driver contract length: 0–120 months;
  historical statistics: 0–10 million. Nonempty team and active-series references must resolve.
- Track name: 1–100 characters; width: 0–200 m (zero delegates to runtime geometry);
  grid row spacing: 5–50 m, front offset: 0–100 m, stagger: 0–30 m.
  Speed multiplier: 0.1–5; acceleration, lateral acceleration and braking: greater than
  zero through 100 m/s²; corners: 0–500; overtaking difficulty: 0–1;
  attack multiplier: 0.1–5; passing lookahead: greater than zero through 20 seconds;
  passing clearance: 0–20 m; wall offset: −1–100 m.
- Track tyre/fuel factors: 0.1–5; wetness: 0–1; grip: 0.1–3; pit loss: 0–300 seconds.
  Speed-profile samples: 0–150 m/s; speed-zone fractions: [0,1), multiplier: (0,5].
  Runtime ideal offsets: ±100 m, clearance: 0–20 m, merge hold: [0,1].
  Optional kerb arrays are empty or match the road sample count, with widths 0–20 m.
- Measured runtime road length must be 200–30000 m with no collapsed consecutive road
  segments; measured pit length must be greater than 20 m through 5000 m.
  Pit-box and apex coordinates use the same bounded point contract as the road.
  Pit-box route-fraction and offset arrays must match; fractions are [0,1] and offsets ±100 m.

Use the exported game's `--validate-mod` command for these semantic checks.
The Python packager checks structural schemas and file safety; it cannot prove a complete
resolved career or race without the game's catalog.

The catalog uses HTTPS GitHub URLs, expected sizes and SHA-256. SHA-256 verifies catalog integrity,
not author trust. The game follows at most five redirects only to the supported GitHub/raw/asset
hosts, uses no credentials, and bounds transfers and retries. Cache dates remain visible offline.
Descriptions are inert text. Preview decoding uses bounded runtime Image/ImageTexture loading;
see [Godot's runtime image API](https://docs.godotengine.org/en/stable/classes/class_image.html).

## Errors and updates

Creator season exports may include `customRules` on each calendar round and
`customFastestLapPoints` on the championship. These optional API 1 fields require
game 0.4.5.0 or later. Round rules keep the authored fuel/tyre multipliers, weather,
temperature, race-control flags, duration and start time in the real race configuration.
Their track, laps, duration and practice/qualifying flags must agree with the calendar.
Timed qualifying converts its minute budget into the existing bounded attempt model
(one attempt per three minutes, clamped to 1–12); it is not a live qualifying clock.
Omit these fields to retain the existing championship defaults.

`Immutable-version conflict` means the same ID/version was rebuilt with different bytes: increment
the version. `Missing ...` names the dependency and constraint to install/import. `Overlapping
replacement target` requires choosing one replacement. `Missing track/layout` requires its package
or a corrected season reference. `Incompatible` identifies the required game range.
Never tell a player to remove missing teams or substitute a different car in a pinned career.

Package deterministically with the supplied utility. Publish release assets first, verify public
bytes without authentication, then update catalog.json with actual URLs, sizes and hashes.
Keep previous assets immutable and available for saved careers.
