# Erratum — v1.1 → v1.2 (2026-09-01)

We found and fixed an error in our own published data. This page records exactly what was
wrong, how it was found, what changed, and how you can check the correction yourself.

## What was wrong

Four of the 80 archived pages were behind Cloudflare. What we archived as `.html` for those
four was the interstitial (`Just a moment...` / `Attention Required! | Cloudflare`), not the
page. We *did* re-fetch all four as plain text at collection time — those files existed the
whole time, 7–20 KB each — but **the dossier builder read the `.html` and never touched the
recovered text.**

So four pages entered v1.1 with 9–127 words and **zero** extracted entities.

One of them matters a great deal:

| URL | v1.1 title | v1.1 type | actual title | correct type |
|---|---|---|---|---|
| `firstpagedigital.sg/resources/ai-seo/best-geo-agencies-in-singapore` | `Just a moment...` | `vendor_service_page` | **Best GEO Agencies in Singapore (2026)** | **`self_listicle`** |

A page whose URL and title both say *"best GEO agencies in Singapore"*, and which names six
agencies including its own publisher, was published as a plain vendor page with no mentions.

## What changed

**Data.** `page_dossiers.json`: 5 entries (4 pages, one of which appears with and without a
trailing slash) now carry the title, entity mentions and word count from the recovered text,
plus a `recovered_from: exa_text` field so the provenance is visible per-record.
`sources.csv`: 8 rows updated — **2 change `page_type`**, 6 gain a correct `fetched_title`
and `companies_mentioned_on_page`.

**Numbers in README.md.** Both are in the Google-organic (`serpapi-google`, n=18) source
profile, and both move in the same direction:

| Claim | v1.1 | v1.2 |
|---|---|---|
| Self-published listicles taken up by Google organic | 4 / 18 | **6 / 18** |
| Source profile | 13 vendor · 4 self-listicle · 1 third-party | **11 vendor · 6 self-listicle · 1 third-party** |

*"top-10 entries, never #1"* still holds — the two corrected rows sit at ranks 4 and 6.

**`method/probes.md`.** The line *"4 bot-walled pages recovered via Exa /contents"* described
an intent, not what the pipeline did. It now says what actually happened, and points here.

## What did NOT change

- **Headline cross-engine similarity is untouched.** Jaccard CN 0.171 / EN 0.091 is computed
  over *cited domains*, not page types. Re-verify: `data/similarity.json` vs `data/sources.csv`.
- Nothing outside those 4 pages moved. `python3 scripts/classify.py` still reports
  **116 agree / 0 disagree** — the classifier and its codebook were never the problem; the
  input to it was.

## The correction strengthens the original finding

v1.1 said self-published "Best X" listicles get cited by search surfaces even though every one
of them ranks its own publisher first. The corrected data contains **two more** such citations,
not fewer. We are reporting this because it was wrong, not because it was inconvenient.

## How this was found

Not by a reader — by an adversarial pre-publication audit of a *different* change (we were
preparing to open-source the dossier-building script). The auditor's job was to answer "can a
stranger actually verify this?", and the honest answer surfaced a 20 KB text file sitting
unused next to a 5 KB Cloudflare page.

That is the argument for publishing the machinery and not just the conclusions: **the reader
who can re-run your pipeline is the reader who can catch you.** We would rather be caught by
ourselves in public than trusted in private.

## Verify the correction yourself

```bash
git clone https://github.com/Canlah-AI/seven-engines-geo-forensics
cd seven-engines-geo-forensics
python3 scripts/classify.py                 # 116 agree / 0 disagree, exit 0
git log --oneline -- data/                  # every change to the data, with reasons
git diff v1.1..HEAD -- data/sources.csv     # the 8 corrected rows, if tags are present
```

The four recovered texts are third-party publisher content and are not redistributed here.
`sources.csv` carries `archived_html_sha256` for every row; the recovered text can be
supplied on request to anyone attempting replication.
