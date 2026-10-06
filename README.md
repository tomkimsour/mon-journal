# Robotics & AI arXiv Briefing

A daily briefing of new arXiv papers in **cs.RO** and **cs.AI**, published as a static site with an RSS feed.

A small Python pipeline (stdlib only) fetches the arXiv `/new` listings, deduplicates them, and sorts
papers into keyword buckets. A Claude Code agent then reads the day's papers and writes a structured
JSON briefing: clusters, thesis, insights, must-reads and per-paper summaries. The pipeline validates
that JSON against the fetched papers and renders the HTML. After each finished week the agent also writes a weekly recap.

## How it works

```
python3 -m briefing fetch      arXiv /new pages  ->  data/DATE/papers.json   (deterministic)
python3 -m briefing digest     papers.json       ->  compact text for the agent
         agent (prompts/briefing.md)             ->  data/DATE/briefing.json
                                                     data/weekly/WEEK.json
python3 -m briefing validate   rejects unknown paper ids, missing fields, wrong dates
python3 -m briefing build      all JSON          ->  posts/, index.html, feed.xml, assets/
```

The briefing date is the announcement date printed on the arXiv listing page, so reruns and
weekends never produce duplicate or mislabelled days. `fetch` reports `"status": "exists"` when
arXiv has not announced anything new.

## Repository layout

```
config.toml            site settings, arXiv categories, buckets and their keywords
prompts/briefing.md    agent instructions: run procedure, editorial method, JSON schemas
.claude/commands/      /briefing slash command for Claude Code
briefing/              pipeline package (fetch, classify, validate, render, feed, CLI)
tests/                 pytest suite with a real arXiv listing fixture
data/                  fetched snapshots and agent-written briefings (source of truth)
posts/ index.html feed.xml assets/   generated site (rebuilt by `build`)
```

## Running a briefing

From the repository root in Claude Code:

```
/briefing
```

or manually, step by step:

```bash
python3 -m briefing fetch
python3 -m briefing pending            # {"days": [...], "weeks": [...]} still needing a briefing
python3 -m briefing digest 2026-10-06  # read this, then write data/2026-10-06/briefing.json
python3 -m briefing validate 2026-10-06
python3 -m briefing build
```

## Scheduling

arXiv announces new listings Sunday–Thursday at 20:00 US Eastern, so a weekday morning run in Europe
always sees a fresh listing. Example crontab entry running Claude Code headlessly:

```cron
30 7 * * 1-5 cd /path/to/arxiv-briefing && claude -p "/briefing" --allowedTools "Bash(python3 -m briefing:*)" "Bash(git add:*)" "Bash(git commit:*)" "Bash(git push:*)" "Read" "Write" "Edit" >> briefing.log 2>&1
```

A Claude Code cloud routine (`/schedule`) with the prompt `/briefing` works the same way.

## Publishing

Push the repository to GitHub and enable **Settings → Pages → Deploy from a branch** on the branch
root. Set `base_url` in `config.toml` to the Pages URL so that feed links are absolute.

## Adapting to another field

Everything field-specific lives in two files:

- `config.toml`: `[arxiv].categories` and the `[[buckets]]` list. Keywords match whole words,
  case-insensitively, with an optional plural `s`/`es`; title hits count double; ties go to the
  earlier bucket; papers matching no bucket are dropped.
- `prompts/briefing.md`: the **Reader profile** section, which steers what the agent treats as relevant.

To check how a keyword change affects bucketing, re-fetch and look at the counts:

```bash
python3 -m briefing fetch --force
```

## Tests

```bash
uv run pytest
```
