import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const catalogPath = path.join(root, "data/processed/catalog.json");
const environment = process.env.CF_ENV;
const environmentBucket =
  environment === "production"
    ? "plasma-flux-explorer-production-data"
    : environment === "staging"
      ? "plasma-flux-explorer-staging-data"
      : "plasma-flux-explorer-data";
const bucket = process.env.PFE_R2_BUCKET || environmentBucket;
const envArgs = environment ? ["--env", environment] : [];
const localArgs = process.env.PFE_R2_LOCAL === "1" ? ["--local"] : [];

let bytes;
try {
  bytes = await readFile(catalogPath);
} catch {
  console.error(
    "Catalog missing. Run `pnpm data:bootstrap` and `pnpm data:validate` first.",
  );
  process.exit(1);
}

const hash = createHash("sha256").update(bytes).digest("hex");
const immutableKey = `catalogs/${hash}.json`;

function put(key, cacheControl) {
  return new Promise((resolve, reject) => {
    const child = spawn(
      "pnpm",
      [
        "exec",
        "wrangler",
        "r2",
        "object",
        "put",
        `${bucket}/${key}`,
        ...envArgs,
        ...localArgs,
        "--file",
        catalogPath,
        "--content-type",
        "application/json",
        "--cache-control",
        cacheControl,
        "--force",
      ],
      { cwd: root, stdio: "inherit", env: process.env },
    );
    child.once("error", reject);
    child.once("exit", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`wrangler exited with ${code}`)),
    );
  });
}

await put(immutableKey, "public, max-age=31536000, immutable");
await put(
  "catalog.json",
  "public, max-age=60, s-maxage=300, stale-while-revalidate=3600",
);
console.log(
  `Published SHA-256 ${hash} to ${bucket}/${immutableKey} and ${bucket}/catalog.json`,
);
