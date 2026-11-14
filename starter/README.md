# Data ingestion and vector retrieval (Chroma)

This folder contains the runnable pipeline used for the individual benchmark. It ingests the OpenStax _Principles of Management_ PDF, builds fixed-size and paragraph-based chunks, embeds them with FastEmbed, stores them in persistent Chroma collections, and evaluates A/B/C retrieval strategies.

The current benchmark uses local embeddings and Chroma; it does not require Docker, PostgreSQL, or an API key. `docker-compose.yml` and `init.sql` remain as optional PostgreSQL + pgvector alternatives and are not used by the recorded results.

## Project layout

```text
starter/
├── data/
│   ├── benchmark.json       # fixed dev/test questions and gold evidence
│   ├── manifest.json        # source, license, selected pages, and filter metadata
│   └── raw/                 # place the source PDF here; do not commit it
├── results/                 # traces, summaries, logs, and manual audits
├── scripts/                 # setup, gold/evidence checks, and audit helpers
└── src/
    ├── ingestion.py         # PDF parsing and text normalization
    ├── normalize.py         # cleanup and paragraph/heading detection
    ├── chunking.py          # fixed-size and paragraph chunking
    ├── embeddings.py        # BAAI/bge-small-en-v1.5 via FastEmbed
    ├── store.py             # persistent Chroma, cosine distance, metadata filters
    ├── evaluation.py        # top-k retrieval traces and metrics
    └── run.py               # end-to-end benchmark runner
```

## Setup

Use Python 3.11–3.14; the recorded environment used Python 3.13.17. From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

Obtain the PDF from the source URL in `data/manifest.json` and place it at `data/raw/principles-management.pdf`. The model is downloaded on first use, so that run needs network access. The model runs locally after download; no paid API is used. Do not commit `.env`, secrets, the virtual environment, or data you are not permitted to redistribute.

## Validate and run

Run commands from `starter/`, since the pipeline uses paths relative to its working directory:

```powershell
python scripts\check_gold.py
python scripts\check_evidence.py
python -m src.run --split dev --tag _v2_b1000
python -m src.run --split test
```

The dev run evaluates A (fixed 1,000 characters, 100-character overlap), B (paragraph chunks capped at 1,000 characters), and C (the same B chunks with the `chapter` filter when the question specifies one). Use `--b-max 600 --tag _v2_b600` for the additional B-size experiment. A tag selects a separate default Chroma path such as `data/chroma_v2_b1000`; `CHROMA_PATH`, if set, overrides that path.

Each run writes traces and summaries under `results/`. Re-running a split rewrites its corresponding trace, summary, and generated audit sheets. Do not rerun a benchmark after manually labeling its audit CSVs unless you intend to regenerate those files.

## Manual audits and submission

`scripts/make_test_audit.py` creates the test grounding and metadata audit CSVs. Fill the score/reason and metadata columns manually, then use `scripts/label_test.py` to resume incomplete labels. `scripts/summarize_test.py` reports retrieval metrics. The manual grounding score assesses retrieved evidence, not LLM answer accuracy.

Report the exact commands, model/version, corpus and filter limitations, results for dev and test, and all five benchmark criteria. See the repository-level [GUIDE.md](../GUIDE.md), [BENCHMARK.md](../BENCHMARK.md), and [SUBMISSION.md](../SUBMISSION.md) for grading and packaging requirements.
