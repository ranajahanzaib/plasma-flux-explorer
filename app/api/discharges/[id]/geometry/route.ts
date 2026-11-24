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
  return Response.json(
    {
      record_id: record.id,
      provenance: record.reference_available
        ? "Derived from reference reconstruction"
        : "Unavailable",
      measurements: record.frames.map((frame, index) => ({
        frame: index,
        time_ms: frame.time_ms,
        geometry: frame.geometry ?? null,
        parameters: frame.parameters ?? {},
        parameters_provenance: frame.parameters_provenance ?? "Unavailable",
      })),
    },
    {
      headers: {
        "Cache-Control":
          "public, max-age=60, s-maxage=300, stale-while-revalidate=3600",
      },
    },
  );
}
