# OpenSource Atlas 🧭

OpenSource Atlas is an open-source dashboard for exploring public GitHub repository metadata, language composition, recent commits, contributors, issues, pull requests, and dependencies declared in common manifest files.

> **Status:** Early MVP. It is not an official GitHub product and does not measure real-world users, downloads, or programme eligibility.

## Features

- Public repository lookup using the GitHub REST API.
- Stars, forks, open issue count, default branch, licence, and timestamps.
- Language composition chart.
- Recent commit activity chart and commit list.
- Contributor contribution chart.
- Recent issues and pull requests.
- Basic dependency extraction from `requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`, and `go.mod`.
- Optional GitHub token to increase API rate limits.

## Run locally

Requires Python 3.10 or newer.

```bash
git clone https://github.com/YOUR-USERNAME/opensource-atlas.git
cd opensource-atlas
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
source .venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit.

## GitHub token (optional)

Unauthenticated GitHub API requests have a low rate limit. Create a fine-grained token with public read-only access if you need a higher limit. Do not commit tokens to the repository. Paste it into the app's sidebar for the current session only.

## Tests

```bash
pytest -q
```

## Limitations

- GitHub API results are snapshots and may be incomplete due to API limits.
- The dashboard shows repository metadata, not verified end-user adoption.
- The contributor list and commit list are limited to the latest API page.
- Dependency parsing is intentionally lightweight; it is not a full package resolver or software bill of materials (SBOM).
- Dependency manifests are fetched only from the repository root.
- No private repository data is accessed.
- No claim of eligibility for any grant, subscription, or open-source programme is made.

## Roadmap

- [ ] Add pagination and date-range filters.
- [ ] Add caching with clear refresh controls.
- [ ] Support nested manifests and lockfiles.
- [ ] Export repository snapshots to CSV/JSON.
- [ ] Add dependency graph visualization.
- [ ] Add scheduled historical snapshots (opt-in deployment).
- [ ] Add accessibility and localization improvements.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and pull requests are welcome. Please include tests for new parsing or analytics features.

## Licence

MIT. See [LICENSE](LICENSE).
