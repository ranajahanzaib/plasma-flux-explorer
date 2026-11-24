import { getCloudflareContext } from "@opennextjs/cloudflare";
import { readFile } from "node:fs/promises";
import path from "node:path";

export type CatalogRecord = {
  id: string;
  record_id: string | number;
  machine: string;
  configuration: string;
  revision: string;
  reference_available: boolean;
  prediction_available: boolean;
  frame_count: number;
  times: number[];
  frames: Array<Record<string, unknown>>;
  diagnostics?: Record<string, unknown>;
  [key: string]: unknown;
};

export type Catalog = {
  schema_version?: string;
  dataset?: string;
  revision?: string;
  updated_at?: string;
  records: CatalogRecord[];
};

export async function readCatalog(): Promise<Catalog | null> {
  try {
    const { env } = await getCloudflareContext({ async: true });
    const object = await env.PFE_DATA?.get("catalog.json");
    if (object) {
      const value: unknown = await object.json();
      if (isCatalog(value)) return value;
    }
  } catch {
    // Plain Next.js development uses the local generated catalog below.
  }

  try {
    const value: unknown = JSON.parse(
      await readFile(
        path.join(process.cwd(), "data/processed/catalog.json"),
        "utf8",
      ),
    );
    return isCatalog(value) ? value : null;
  } catch {
    return null;
  }
}

export function isCatalog(value: unknown): value is Catalog {
  return (
    !!value &&
    typeof value === "object" &&
    Array.isArray((value as { records?: unknown }).records)
  );
}

export function errorResponse(code: string, message: string, status: number) {
  return Response.json(
    { error: { code, message } },
    { status, headers: { "Cache-Control": "no-store" } },
  );
}

export function findRecord(catalog: Catalog, id: string) {
  return (
    catalog.records.find(
      (record) => record.id === id || String(record.record_id) === id,
    ) ?? null
  );
}
