# 🧠 AI Stock Trader

A fully containerized, reproducible stock trading application powered by AI algorithms and modern Python infrastructure. This project uses **Conda** for environment management, **Docker** for deployment, and **pre-commit hooks** to enforce code quality.

---

## 📦 Features

- Python 3.11 with Conda environment
- Docker support for clean deployments
- Pre-commit hooks (Black, Flake8, Mypy, YAML/JSON validation)
- Makefile for standardized workflows
- Custom hooks for `.env` safety and reproducibility enforcement

---

## 📁 Project Structure

```
ai-stock-trader/
├── app/                  # Main application logic
├── tests/                # Unit tests
├── scripts/              # Custom utilities (e.g., docstring checker)
├── environment.yml       # Conda environment definition
├── Dockerfile            # Conda-based Docker container
├── docker-compose.yml    # (Optional) Docker orchestration
├── Makefile              # CLI shortcuts
├── .pre-commit-config.yaml
└── README.md
```

---

## ⚙️ Setup Instructions

### 🔹 Conda Environment (Local)

```bash
make conda-create        # Create the Conda environment
make conda-activate      # Display the command to activate the env
make conda-update        # Update env from environment.yml
make conda-remove        # Delete the environment
make conda-export        # Export current env to environment.yml
```

> 🔁 Always run `conda activate ai-stock-trader` after creating or switching environments.

---

### 🐳 Docker (Containerized)

```bash
make docker-build        # Build the Docker image
make docker-run          # Run the container (executes app/main.py)
make docker-bash         # Open interactive shell inside container
make docker-compose-up   # Spin up with docker-compose (if used)
make docker-compose-down # Tear down docker-compose stack
```

---

### 🧪 Development Utilities

```bash
make run                 # Run the main app (app/main.py)
make test                # Run all unit tests using pytest
make lint                # Format code using Black
make format              # Alias for `make lint`
make shell               # Launch IPython shell in Conda env
```

---

### 🛡️ Pre-Commit Hooks

```bash
make install-hooks       # Installs Git hooks in your repo
make run-hooks           # Manually run hooks on all files
```

Included hooks:
- ✅ Black formatting
- ✅ Flake8 linting
- ✅ Mypy static typing
- ✅ YAML/JSON validation
- ✅ Docstring enforcement (custom)
- ✅ Environment freshness check (custom)
- ✅ Secret file protection (blocks `.env` commits)

---

## 📄 Scripts

Custom scripts live in `/scripts`:

- `scripts/check_docstrings.py` ensures all Python modules have a top-level docstring

---

## 📚 Best Practices

- Run `make run-hooks` before committing
- Always export `environment.yml` after installing new packages
- Avoid committing `.env` or secrets
- Use Docker or Conda, not both at the same time

---

Thought for 5 seconds


Below is a Python file whose single variable **`readme_text`** holds the complete Markdown *without* using triple‑backtick fences (so nothing inside the string can accidentally close the code block).  You can copy‐paste this file directly into your repo.


### 🔖 Lightweight Commit‑Message Playbook


---

#### 1  Template

    <type>(<scope>): <imperative‑mood summary>

    <body — optional, wrap ≤ 88 chars per line>

    <footer — optional>

* **`type`** – one of the canonical verbs below.
* **`scope`** – a short noun (file, folder, feature); omit if obvious.
* **Summary** – start with a verb in _imperative mood_ (“Add…”, “Fix…”). Keep ≤ 50 chars.
* **Body** – explain **why** more than **how**. Use bullets for multiple points,
  reference issues (`Closes #42`).
* **Footer** – `BREAKING CHANGE:` notes, co‑authors, etc.

---

#### 2 Standard **`type`** Verbs

| Type      | When to use                                                                    |
|-----------|--------------------------------------------------------------------------------|
| `feat`    | New user‑visible feature or capability                                         |
| `fix`     | Bug fix that turns failing tests green                                         |
| `docs`    | Documentation only (README, tutorials, docstrings)                             |
| `style`   | Pure formatting / lint fixes (no code logic changes)                           |
| `refactor`| Internal restructuring, no external behaviour change                           |
| `test`    | Add or update tests                                                            |
| `data`    | Add / update large datasets or `.sha256` artefacts                             |
| `ci`      | Continuous‑integration config, pre‑commit hooks, GitHub Actions, env updates   |
| `chore`   | Misc. maintenance (dependency bumps, tool configs)                             |

---

#### 3 Examples

| Situation                                                        | Good commit message                                  |
|------------------------------------------------------------------|------------------------------------------------------|
| Added SHA‑256 hooks & aligned lint width                         | `ci: add .sha256 hooks and sync Flake8 to 88`        |
| Implemented Alpaca headline fetcher                              | `feat(news): add Alpaca ticker‑headline pipeline`    |
| Fixed type errors in `dump_rows`                                 | `fix(news): relax dump_rows typing for mypy`         |
| Black reformat across pipelines                                  | `style(pipelines): run Black formatter`              |
| Updated `environment.yml`                                        | `ci: refresh conda environment snapshot`             |

---

#### 4 Guidelines & Tips

* **One idea per commit** when practical—easier reverts and reviews.
* **Imperative mood**: think “this commit *will* …” (e.g. _Add_, _Remove_,
  _Refactor_).
* Keep the **subject line ≤ 50 chars**; wrap body text at 88 chars.
* Skip the body if the summary says it all; add it if context matters.
* Use `data:` commits when adding bulk files so others can pull selectively
  (e.g., via Git LFS).
* Consistent conventions enable automated changelogs
  (semantic‑release, changelog‑ci) later.

---

> ✨ **Result:** a git history that reads like a clear diary, not a puzzle.




## 🙋 Support

Need help or want to suggest improvements? Open an issue or contact the project maintainer.
