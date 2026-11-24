# Cloudflare deployment

The Next.js app uses the OpenNext Cloudflare adapter to run on Cloudflare Workers. See [Cloudflare's OpenNext guidance](https://developers.cloudflare.com/workers/framework-guides/web-apps/opennext/) for adapter compatibility and deployment details.

Local `pnpm dev` remains a plain Next.js workflow and needs no Cloudflare account. During local Next development, the adapter exposes local Wrangler bindings; the catalog API reads the local R2 object when present and falls back to `data/processed/catalog.json` otherwise.

## One-time Cloudflare setup

The configuration defines separate staging and production Workers and data/cache buckets. Create the six R2 buckets in the intended Cloudflare account before deploying:

```bash
pnpm exec wrangler r2 bucket create plasma-flux-explorer-staging-data
pnpm exec wrangler r2 bucket create plasma-flux-explorer-staging-cache
pnpm exec wrangler r2 bucket create plasma-flux-explorer-production-data
pnpm exec wrangler r2 bucket create plasma-flux-explorer-production-cache
```

The base configuration is for local Wrangler preview and uses `plasma-flux-explorer-data` and `plasma-flux-explorer-cache`; create those too if you use the base environment. Authenticate with `pnpm exec wrangler login` and set the correct account in Wrangler configuration or `CLOUDFLARE_ACCOUNT_ID` in the shell. No credentials belong in this repository.

## Build and preview

Prepare real local records first. The catalog and raw data are intentionally gitignored.

```bash
pnpm data:bootstrap
pnpm data:validate
pnpm cf:build
pnpm cf:preview
```

The local preview uses Wrangler’s local R2 simulation. Remote staging bindings can be checked without deploying by passing the staging environment to Wrangler’s dev command.

To seed the local R2 emulator from the already generated catalog, set `PFE_R2_LOCAL=1` before publishing. This mode adds Wrangler's `--local` flag and does not contact the Cloudflare account:

```bash
PFE_R2_LOCAL=1 pnpm data:publish
```

## Publish catalog artifacts

Publishing requires Wrangler authentication and uploads data to the selected R2 account. This action is deliberately separate from building and previewing.

```bash
CF_ENV=staging PFE_R2_BUCKET=plasma-flux-explorer-staging-data pnpm data:publish
```

The publisher uploads the exact catalog bytes under a SHA-256 immutable path and updates `catalog.json` as a short-cache pointer. The deployed Worker reads that pointer from the `PFE_DATA` binding. The catalog currently contains frame arrays, so this initial publisher is suitable for the curated starter catalog; split large catalogs into frame artifacts before publishing full challenge records.

## Deploy

Build and review the staged Worker first. Deployment publishes a live service and must be run deliberately from an authenticated Cloudflare environment.

```bash
pnpm cf:build
pnpm cf:deploy -- --env staging
```

After validating staging, the production command is:

```bash
pnpm cf:deploy -- --env production
```

Deployment is manual; the CI workflow runs validation and does not publish a Worker. Worker observability is enabled in `wrangler.jsonc`. The catalog response uses short shared caching and each hashed catalog artifact uses a one-year immutable cache policy.

## Current deployment limits

- Account-specific R2 buckets must be created before deploy; this repository does not create remote resources.
- The catalog read and publishing paths use R2. Other scientific artifacts are served from the catalog representation.
- The deployment does not include request rate limiting or external error monitoring. Publishing large challenge catalogs requires splitting frame arrays into artifacts first.
- A successful local build or preview verifies local behavior only; hosted behavior depends on the configured Cloudflare account and deployment environment.
