# Testing bjj-match-study

Static site (vanilla JS, no build) that lists BJJ match breakdowns and a viewer page that renders a per-match markdown analysis.

## Serve locally
```bash
python3 -m http.server 8000  # run from repo root
# then open http://localhost:8000/
```
No auth or secrets required. No dev server watcher — reload the browser after edits.

## Data model (as of the manifest refactor)
- `analysis/*.md` — one markdown file per match (source of truth for the human-written analysis, timestamps, labels).
- `analysis/index.json` — generated manifest, single source of truth for the home grid. Regenerated via `python scripts/build_manifest.py`. CI (`.github/workflows/manifest.yml`) fails on a stale manifest.
- `index.html` fetches ONLY `analysis/index.json` at load. It must not fetch individual `analysis/*.md` files.
- `viewer/index.html` still fetches a single `analysis/*.md` based on the `path` URL param and the YouTube video id from the `id` param.

## Quick assertions (DevTools console)
Verify the home page is genuinely manifest-driven:
```js
const entries = performance.getEntriesByType('resource').map(e => e.name).filter(n => n.includes('/analysis/'));
({
  cards: document.querySelectorAll('.video-card').length,
  manifestRequests: entries.filter(n => n.endsWith('/analysis/index.json')).length, // must be 1
  markdownRequests: entries.filter(n => n.endsWith('.md')).length,                   // must be 0
});
```
If `markdownRequests` > 0 on the home page, the refactor has regressed (the old code path fetched ~46 markdown files on load).

Verify a filter actually narrows the grid:
```js
const all = document.querySelectorAll('.video-card');
const visible = [...all].filter(c => c.style.display !== 'none');
({ total: all.length, visible: visible.length, pill: document.querySelector('.active-filter')?.textContent?.trim() });
```

## Viewer URL contract
Clicking a card navigates to:
```
viewer/index.html?id=<youtubeVideoId>&path=<url-encoded path to analysis/*.md>
```
The viewer reads `id` to mount the YouTube iframe and `path` to fetch + render the markdown.

Stable test match with a known submission finish: **Tainan Dalpra vs Elijah Dorsey** — video id `pKYaDrC9PeQ`, markdown contains a `07:48` armbar timestamp in the Match Breakdown.

## Adding a match (doubles as a manifest regression test)
1. Drop a new `.md` file in `analysis/` matching existing schema.
2. Run `python scripts/build_manifest.py` to regenerate `analysis/index.json`.
3. Commit both files. Omitting step 2 will fail CI (`manifest.yml` runs `--check`).

## Known gaps / follow-ups (might be fixed in future — check first)
- Viewer might not render a **Submissions** tag group even though the manifest/markdown contain submission labels. A workaround is to read them from the Label List section directly.
- Filter state is not reflected in the URL, so filtered views are not shareable/bookmarkable yet.

## Recording checklist when testing UI
- Maximize Chrome: `wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz` before `record_start`.
- Annotate at least: setup (page loaded), test_start per assertion group, assertion with `passed`/`failed` and a concise description.

## Devin Secrets Needed
None. The app is a public static site with no backend or auth.
