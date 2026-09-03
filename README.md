# wwo_data

Public data mirror for the **DraftCompass - Lineup Analyzer** browser extension.

A GitHub Action refreshes `props.csv` 8 times a day from Win With Odds so that
extension users pull from this repo instead of hammering the source site.

| File | Purpose |
| --- | --- |
| `props.csv` | Prop-derived weekly stat projections, one row per player. |
| `metadata.json` | When the props data was last refreshed, the source URL, and the row count. |
| `espn_projections.csv` | ESPN's own weekly projections, same column shape as `props.csv`. |
| `espn_metadata.json` | Season, week and row count for the ESPN pull. |

## Consumed by

The extension fetches the raw URL directly:

```
https://raw.githubusercontent.com/Louieza23/wwo_data/main/props.csv
```

**This repo must stay public.** `raw.githubusercontent.com` returns 404 for
private repos, which silently blanks out the extension's PROPS column.

## Source

- Page: <https://www.winwithodds.com/weekly_full_stats>
- Download: <https://www.winwithodds.com/download/downloadable_props.csv>

Note the `www.` prefix — the bare `winwithodds.com` host 301-redirects, so the
fetch must follow redirects (`curl -L`).

## CSV columns

```
Player, Pos, Attempts, Comps, Pass Yards, Pass TDs, Ints, Receptions,
Rec Yards, Rec TDs, Rush Yards, Rush TDs, Fumbles, Projections,
Ceiling, Floor, Actuals, Rank
```

Positions covered are QB, RB, WR, TE and FB only — there is no K or DST data.
The extension keys off the header names, so added columns are safe; renamed or
removed ones are not.

## Refresh workflow

`.github/workflows/fetch-wwo-data.yml` runs every 3 hours (plus a random 0-15
minute jitter) and can be triggered manually from the Actions tab. Before
promoting a download it validates that the payload is not an HTML page, that the
header starts with `Player,Pos`, and that there are at least 100 data rows. It
commits only when `props.csv` actually changed.
