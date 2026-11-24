export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { errorResponse, findRecord, readCatalog } from "@/lib/catalog";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string; frame: string }> },
) {
  const { id, frame: frameParam } = await context.params;
  const index = Number(frameParam);
  if (!Number.isInteger(index) || index < 0)
    return errorResponse(
      "invalid_frame",
      "frame must be a nonnegative integer.",
      400,
    );
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
  const selected = record.frames[index];
  if (!selected)
    return errorResponse(
      "frame_not_found",
      `Frame ${index} has no released equilibrium data.`,
      404,
    );
  return Response.json({
    record_id: record.id,
    frame: index,
    time_ms: selected.time_ms,
    provenance: record.reference_available
      ? "Derived from reference reconstruction"
      : "Unavailable",
    topology: selected.topology ?? {
      status: "unavailable",
      o_points: [],
      x_points: [],
    },
  });
}
