# Win With Odds Data Repository

Automated data cache for Sleeper Prop Extension.

## Purpose

This repository automatically fetches player prop projections from Win With Odds and makes them available via GitHub's CDN. This prevents rate limiting and improves performance for extension users.

## Data Files

- **props.csv** - Player prop projections (updated every 12 hours)
- **metadata.json** - Information about when data was last updated

## Update Schedule

Data is automatically fetched every 12 hours at:
- 00:00 UTC (7pm EST / 4pm PST)
- 12:00 UTC (7am EST / 4am PST)

## Usage

Extensions and applications can fetch the latest data from:

```
https://raw.githubusercontent.com/[YOUR_USERNAME]/wwo_data/main/props.csv
https://raw.githubusercontent.com/[YOUR_USERNAME]/wwo_data/main/metadata.json
```

Replace `[YOUR_USERNAME]` with your GitHub username.

## Manual Update

You can manually trigger a data fetch from the [Actions tab](../../actions/workflows/fetch-wwo-data.yml) by clicking "Run workflow".

## Data Source

Data is sourced from: https://winwithodds.com/download/downloadable_props.csv
