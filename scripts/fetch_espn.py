#!/usr/bin/env python3
"""
Build espn_projections.csv from ESPN's public fantasy players endpoint.

ESPN publishes weekly projections for every player with no API key and no
league membership, but the response is ~39MB - far too heavy to pull from a
browser side panel. This runs server-side and emits a slim CSV shaped like
props.csv so the extension can parse both with the same code path.

ESPN stat ids were confirmed empirically against known players rather than
taken from documentation, and cross-check closely against the props feed
(e.g. Jahmyr Gibbs: ESPN 85.03 rush yds / 3.9 rec vs props 85.5 / 4.44).
"""

import csv
import json
import sys
import urllib.request

PLAYERS_URL = (
    "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}"
    "/players?scoringPeriodId={week}&view=kona_player_info"
)
STATE_URL = "https://api.sleeper.app/v1/state/nfl"

# statSourceId 1 = projection (0 = actual). statSplitTypeId 1 = single week.
PROJECTION_SOURCE_ID = 1

POSITIONS = {1: "QB", 2: "RB", 3: "WR", 4: "TE", 5: "K", 16: "DST"}

# ESPN stat id -> our column name, matching props.csv's header.
STAT_MAP = {
    "0": "Attempts",      # pass attempts
    "1": "Comps",         # completions
    "3": "Pass Yards",
    "4": "Pass TDs",
    "20": "Ints",
    "23": "Rush Att",
    "24": "Rush Yards",
    "25": "Rush TDs",
    "42": "Rec Yards",
    "43": "Rec TDs",
    "53": "Receptions",
    "72": "Fumbles",      # fumbles lost
}

COLUMNS = [
    "Player", "Pos", "Attempts", "Comps", "Pass Yards", "Pass TDs", "Ints",
    "Receptions", "Rec Yards", "Rec TDs", "Rush Att", "Rush Yards", "Rush TDs",
    "Fumbles",
]

MIN_ROWS = 200


def fetch_json(url, headers=None, timeout=180):
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def current_week():
    """Ask Sleeper what week it is - ESPN's payload does not say."""
    state = fetch_json(STATE_URL, timeout=30)
    return int(state["season"]), int(state["display_week"] or state["week"] or 1)


def extract(players, week):
    rows = []

    for entry in players:
        player = entry.get("player", entry)
        name = player.get("fullName")
        position = POSITIONS.get(player.get("defaultPositionId"))

        # The feed carries the entire NFL including IDP; keep the positions
        # the extension actually scores.
        if not name or position not in ("QB", "RB", "WR", "TE"):
            continue

        projection = None
        for stat in player.get("stats") or []:
            if (stat.get("statSourceId") == PROJECTION_SOURCE_ID
                    and stat.get("scoringPeriodId") == week
                    and stat.get("stats")):
                projection = stat["stats"]
                break

        if not projection:
            continue

        row = {"Player": name, "Pos": position}
        for stat_id, column in STAT_MAP.items():
            value = projection.get(stat_id)
            row[column] = "" if not value else f"{round(float(value), 2):g}"

        # A row with no offensive volume at all tells the extension nothing.
        if not any(row.get(c) for c in ("Attempts", "Rush Att", "Receptions")):
            continue

        rows.append(row)

    return rows


def main():
    season, week = current_week()
    print(f"Season {season}, week {week}", file=sys.stderr)

    url = PLAYERS_URL.format(season=season, week=week)
    # ESPN needs a filter header or it caps what it returns.
    headers = {
        "x-fantasy-filter": json.dumps(
            {"players": {"filterStatsForTopScoringPeriodIds": {"value": week}}}
        ),
        "User-Agent": "wwo-data-mirror",
    }

    players = fetch_json(url, headers)
    print(f"Fetched {len(players)} players from ESPN", file=sys.stderr)

    rows = extract(players, week)
    print(f"Extracted {len(rows)} offensive players with week {week} projections",
          file=sys.stderr)

    if len(rows) < MIN_ROWS:
        print(f"ERROR: only {len(rows)} rows (expected at least {MIN_ROWS})",
              file=sys.stderr)
        return 1

    with open("espn_projections.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    with open("espn_metadata.json", "w", encoding="utf-8") as handle:
        json.dump({"season": season, "week": week, "row_count": len(rows),
                   "source": "ESPN fantasy players API"}, handle, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
