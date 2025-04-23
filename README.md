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


## 🙋 Support

Need help or want to suggest improvements? Open an issue or contact the project maintainer.
