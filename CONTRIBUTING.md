# Contributing

Thanks for considering a contribution to OpenSource Atlas.

## Before starting
1. Open an issue describing the bug or proposed feature.
2. Check existing issues and pull requests to avoid duplicate work.
3. For substantial changes, discuss the design before implementation.

## Development
```bash
python -m venv .venv
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## Pull request checklist
- [ ] Explain the problem and solution.
- [ ] Add or update tests.
- [ ] Keep GitHub API tokens and secrets out of commits.
- [ ] Update documentation when behaviour changes.
- [ ] Do not add unsupported claims about adoption or eligibility.

Use clear, respectful communication. Small focused pull requests are easier to review.
