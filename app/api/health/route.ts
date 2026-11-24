export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { getCloudflareContext } from "@opennextjs/cloudflare";
import { access } from "node:fs/promises";
import path from "node:path";

export async function GET() {
  let catalog = false;
  let source: "r2" | "filesystem" | "unavailable" = "unavailable";
  try {
    const { env } = await getCloudflareContext({ async: true });
    catalog = Boolean(await env.PFE_DATA?.head("catalog.json"));
    if (catalog) source = "r2";
  } catch {
    // Cloudflare bindings are absent in a plain Next.js runtime.
  }

  try {
    if (!catalog) {
      await access(path.join(process.cwd(), "data/processed/catalog.json"));
      catalog = true;
      source = "filesystem";
    }
  } catch {
    // The health response reports a missing catalog as data, not as a failed process check.
  }
  return Response.json({ status: "ok", catalog, source });
}
