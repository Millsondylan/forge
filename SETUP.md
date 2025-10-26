# Setup and installation

## Via Homebrew + pipx (recommended)

- Install prerequisites:
  - brew install python@3.11 pipx
  - pipx ensurepath
- Install Forge from GitHub:
  - pipx install "git+https://github.com/Millsondylan/forge.git#egg=forge-cli"
- Verify:
  - forge --help

## Anthropic Login

- Run: forge auth anthropic
- A browser will open; grant access. The SDK will cache credentials.

## Quickstart

- Initialize: forge init
- Pick a model: forge model select
- Enqueue: forge queue add "build hello module"
- Run 500 agents on queue: forge queue run --concurrency 500 --model $(forge model list | head -n1)

## Uninstall

- pipx uninstall forge-cli
