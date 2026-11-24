# Contributing

Contributions to Plasma Flux Explorer are welcome. For substantial changes, open an issue to discuss the scope before starting work. For small fixes, a pull request with context is sufficient.

## Development setup

Install Node.js 20.9 or newer, pnpm 10 or newer, Python 3.11 or newer, and uv. Then install dependencies and start the local app:

```bash
pnpm install
uv sync
pnpm dev
```

Local data is optional for the application shell. To download the small official demo selection used by the explorer, run `pnpm data:bootstrap`; the downloaded files and generated catalog remain local and are not committed.

## Before opening a pull request

Run the checks relevant to your change:

```bash
pnpm test
pnpm lint
pnpm typecheck
pnpm build
```

Describe the problem and the approach taken. Include screenshots for visible interface changes and explain any data schema, scientific method, or API contract changes. Keep source measurements, derived quantities, predictions, and synthetic teaching examples clearly distinguished. New data handling should preserve source attribution, units, time bases, and license terms.

Do not commit credentials, downloaded datasets, generated catalogs, or machine-specific files. See the [data source notes](docs/data-sources.md) and [security policy](.github/SECURITY.md) before sharing data or reporting a vulnerability.
