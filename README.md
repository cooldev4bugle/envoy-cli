# envoy-cli

> A CLI tool to manage and sync `.env` files across local and remote environments securely.

---

## Installation

```bash
pip install envoy-cli
```

Or install from source:

```bash
git clone https://github.com/yourusername/envoy-cli.git
cd envoy-cli && pip install -e .
```

---

## Usage

```bash
# Push your local .env to a remote environment
envoy push --env production

# Pull the latest .env from a remote environment
envoy pull --env staging

# List all managed environments
envoy list

# Diff your local .env against a remote environment
envoy diff --env production
```

Variables are encrypted in transit and at rest. Configure your remote backend in `~/.envoy/config.toml`.

```toml
[remote]
provider = "s3"
bucket = "my-env-store"
region = "us-east-1"
```

---

## Features

- 🔒 End-to-end encryption for all `.env` files
- ☁️ Supports S3, GCS, and custom backends
- 🔁 Easy sync between local and remote environments
- 🧩 Simple CLI interface with minimal setup

---

## License

This project is licensed under the [MIT License](LICENSE).