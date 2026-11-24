export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { readCatalog } from "@/lib/catalog";

export async function GET() {
  const catalog = await readCatalog();
  const models = new Map<string, Record<string, unknown>>();
  for (const record of catalog?.records ?? []) {
    for (const prediction of (record.predictions ?? []) as Array<
      Record<string, unknown>
    >) {
      if (prediction.model && typeof prediction.model === "object") {
        const model = prediction.model as Record<string, unknown>;
        const id = String(model.id ?? model.name ?? "");
        if (id) models.set(`${id}:${String(model.version ?? "")}`, model);
      }
    }
  }
  return Response.json({
    models: [...models.values()],
    status: models.size ? "available" : "no_registered_models",
  });
}
