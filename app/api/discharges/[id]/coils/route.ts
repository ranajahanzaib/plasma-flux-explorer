export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { errorResponse, findRecord, readCatalog } from "@/lib/catalog";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const catalog = await readCatalog();
  if (!catalog)
    return errorResponse(
      "catalog_unavailable",
      "No local or R2 catalog is available.",
      503,
    );
  const record = findRecord(catalog, decodeURIComponent(id));
  if (!record)
    return errorResponse(
      "discharge_not_found",
      `No released record matches ${id}.`,
      404,
    );
  const diagnostics = record.diagnostics ?? {};
  return Response.json({
    record_id: record.id,
    coil_signals: diagnostics.coil_signals ?? [],
    geometry: diagnostics.coil_geometry ?? {},
    provenance:
      "Supplied actuator signal; native released units and time bases retained",
  });
}
