# SysML v2 highlighting for Marp

The talk deck renders online at
<https://mycr0ft.github.io/sysmlv2transformation/> (GitHub Pages from this
repo, `master` branch root).

A small, reusable Marp slide-deck template that adds real **SysML v2** syntax
highlighting to code fences. Built on [Marp] + [Shiki] using a TextMate grammar
sourced from the [SysML v2 VS Code extension][grammar-src].

---

## What's in here

| File | Purpose |
| --- | --- |
| `transformation.md` | *SysML v2 in a Digital Engineering Workflow: from deployed SysML v1 models to validated, executable digital artifacts* — presentation for the [October SysML v2 Exchange](https://www.incose.org/event/october-sysml-v2-exchange/), over the [umlmeta](https://github.com/mycr0ft/umlmeta) + [sysmlpy](https://github.com/mycr0ft/sysmlpy) toolchain. Build with `npm run build`. |
| `ADVERTISED_TALK.md` | The advertised abstract and speaker bio. The deck is kept aligned to this. |
| `ABSTRACT_COVERAGE.md` | Promise-by-promise map from the abstract to the slide and evidence that pays for it, including the one promise (closed-loop result ingestion) that is *not* implemented. |
| `engine.js` | A custom Marp CLI engine that swaps Marp's default highlight.js for [Shiki][shiki] and registers the SysML v2 grammar. |
| `sysml.tmLanguage.json` | The TextMate grammar that defines SysML v2 tokenization. Pulled from [daltskin/VSCode_SysML_Extension][grammar-src] (MIT). |
| `package.json` | npm scripts and dependencies ([Marp CLI][marp-cli], [Marp Core][marp-core], [Shiki][shiki]). |

---

## Prerequisites (one-time setup)

1. **Install Node.js** (v18 or newer). Download it from <https://nodejs.org/> and
   run the installer for your platform, or use a version manager like
   [`nvm`](https://github.com/nvm-sh/nvm) / [`fnm`](https://github.com/Schniz/fnm).
   Verify it works:

   ```bash
   node --version   # should print v18.x or newer
   npm --version    # should print 9.x or 10.x
   ```

2. **(Optional) Install Chromium for PDF export.** The `pdf` script uses
   Marp CLI's built-in `--pdf` mode, which needs Chromium. On first run Marp
   will offer to download a bundled copy for you automatically, so you can
   usually skip this step. If you'd rather use a system Chromium, install it
   from your package manager and Marp will pick it up.

---

## Install dependencies

### Python / umlmeta / sysmlpy

The XMI reader/writer and vehicle check use `uv` with a locked environment:

```bash
uv sync
PYTHONPATH=$PWD .venv/bin/python check_xmi_vehicle.py
```

This installs `lxml`, `pint`, and the pinned `sysmlpy==0.97.1`. The check
covers the OMG-style XMI path, the Cameo-compatible XMI path, and SysML v2
validation.

### Node / slide deck

From the project folder (the one containing `package.json`), run:

```bash
npm install
```

This downloads Marp CLI, Marp Core, and Shiki into `node_modules/`. You only
need to re-run it when `package.json` changes (e.g. after a `git pull`).

---

## Containerized validation

A reproducible Podman/Docker Compose environment is provided for the Python
pipeline. It includes `umlmeta`, `lxml`, `pint`, and `sysmlpy`:

```bash
podman compose build
podman compose run --rm umlmeta
podman compose run --rm shell
```

The first command runs the complete vehicle check. The second verifies the
installed runtime dependencies. The source directory is mounted into the
container, so generated XMI and SysML artifacts remain in the project folder.

## Cameo-compatible XMI

`umlmeta.xmi_write.write_cameo_xmi(...)` emits a Cameo/MagicDraw-compatible
XMI variant while preserving the original OMG corpus writer. It uses the UML
2.5.1 namespace pair, a real `uml:Model` wrapper containing the user package,
EMF/P10 attributes, and post-root SysML stereotype applications. The
reference behavior and import rationale are documented in
[`docs/CAMEO_XMI.md`](docs/CAMEO_XMI.md).

For reviewed, case-by-case source-model exceptions such as SysML v1
`ProxyPort`, use the optional `mapping_rule` hook documented in
[`docs/MAPPING_RULES.md`](docs/MAPPING_RULES.md).

## Regenerated diagrams

The locked Python environment also includes the open-source
[`diagramboxes`](https://github.com/mycr0ft/diagramboxes) renderer from the repository's current `main` branch. `uv.lock` records the
resolved commit used for the current environment. Use it alongside sysmlpy to
regenerate a structural SVG from the transformed model:

```bash
PYTHONPATH=$PWD .venv/bin/python render_vehicle_diagrams.py
PYTHONPATH=$PWD .venv/bin/python render_vehicle_diagrams.py --view story
```

The default writes the fuller structural SVG with nested parts and boundary
ports. `--view story` writes the compact structural diagram used by the
**The story in one slide** example: `Vehicle`, `wheels[1..4] : Wheel`,
`mass : Kilogram`, and `pwr : PowerIf`. It deliberately omits `Axle` and
`aux`, which are not part of that slide model. Both views also write a
semantic PlantUML source file from sysmlpy. The renderers regenerate layout
from SysML v2 semantics; they do not reproduce Cameo's original coordinates
or connector routing.

## Build / preview commands

All commands are run from the project folder.

```bash
npm run build      # Render transformation.md -> transformation.html
npm run pdf        # Render transformation.md -> transformation.pdf (needs Chromium)
npm run watch      # Re-render transformation.html whenever transformation.md changes
npm run preview    # Start a local web server at http://localhost:8080 and live-preview
```

If you prefer calling Marp CLI directly:

```bash
npm run build
```

Open the resulting `transformation.html` in any browser, or open the preview server
URL printed by `npm run preview`.

---

## How it works

- `sysml.tmLanguage.json` is the TextMate grammar used by the
  [SysML v2 VS Code extension][grammar-src] for syntax highlighting.
- `engine.js` is a Marp CLI custom engine. It loads that grammar into
  [Shiki][shiki] (which natively consumes TextMate grammars — no VS Code
  needed), then overrides `marp.highlighter` so ```` ```sysml ```` code fences
  get real SysML v2 tokenization instead of being left unhighlighted by
  highlight.js.
- Other languages (JavaScript, TypeScript, Python, Bash, JSON, YAML, XML) are
  also loaded so mixed decks keep working normally. Add more in the `langs`
  array in `engine.js`.

---

## Writing slides

Edit `transformation.md`. Marp front-matter goes in the first YAML block:

```markdown
---
marp: true
theme: default      # or uncover, gaia, or a custom theme
paginate: true
---

# Title slide

```sysml
package MyModel {
    part def Foo { attribute x : Real; }
}
```
```

Full Authoring docs:
- **Marp Markdown syntax:** <https://marp.app/docs/>
- **Marp Core / themes / directives:** <https://github.com/marp-team/marp-core>
- **Marp CLI options:** <https://github.com/marp-team/marp-cli>

---

## Updating the grammar

If the upstream extension updates its grammar, re-download it:

```bash
curl -o sysml.tmLanguage.json \
  https://raw.githubusercontent.com/daltskin/VSCode_SysML_Extension/main/syntaxes/sysml.tmLanguage.json
```

---

## Useful links

- [Marp] — the presentation framework this deck is built with
- [Marp CLI][marp-cli] — the command-line renderer (`marp` command, `--html`,
  `--pdf`, `--watch`, `--preview`, etc.)
- [Marp Core][marp-core] — Marp's core Markdown-it pipeline and built-in themes
- [Shiki] — the syntax highlighter used by the custom engine (VS Code's
  highlighter, runs on TextMate grammars)
- [SysML v2 VS Code extension][grammar-src] — source of the bundled
  `sysml.tmLanguage.json` grammar
- [OMG SysML v2 specification][sysml-spec] — the language itself
- [Node.js] — the runtime you need to run `npm` commands

[Marp]: https://marp.app/
[marp-cli]: https://github.com/marp-team/marp-cli
[marp-core]: https://github.com/marp-team/marp-core
[marp-docs]: https://marp.app/docs/
[shiki]: https://shiki.style/
[shiki-docs]: https://shiki.style/
[grammar-src]: https://github.com/daltskin/VSCode_SysML_Extension
[sysml-spec]: https://www.omg.org/spec/SysML/2.0/
[Node.js]: https://nodejs.org/