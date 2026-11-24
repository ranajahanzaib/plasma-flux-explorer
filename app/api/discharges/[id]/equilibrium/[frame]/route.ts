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
  const frame = record.frames[index];
  if (!frame)
    return errorResponse(
      "frame_not_found",
      `Frame ${index} has no released equilibrium data.`,
      404,
    );
  return Response.json(
    {
      record_id: record.id,
      frame: index,
      provenance: record.reference_available
        ? "EFIT reference reconstruction"
        : "Reference equilibrium unavailable",
      data: frame,
    },
    {
      headers: {
        "Cache-Control":
          "public, max-age=60, s-maxage=300, stale-while-revalidate=3600",
      },
    },
  );
}
