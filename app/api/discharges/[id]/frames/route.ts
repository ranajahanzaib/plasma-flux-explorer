export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { errorResponse, findRecord, readCatalog } from "@/lib/catalog";

export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const url = new URL(request.url);
  const offset = Number(url.searchParams.get("offset") ?? 0);
  const limit = Number(url.searchParams.get("limit") ?? 100);
  if (
    !Number.isInteger(offset) ||
    offset < 0 ||
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > 250
  ) {
    return errorResponse(
      "invalid_pagination",
      "offset must be nonnegative and limit must be between 1 and 250.",
      400,
    );
  }
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
  let frames = record.frames;
  const from = url.searchParams.has("from_ms")
    ? Number(url.searchParams.get("from_ms"))
    : null;
  const to = url.searchParams.has("to_ms")
    ? Number(url.searchParams.get("to_ms"))
    : null;
  if (
    (from != null && !Number.isFinite(from)) ||
    (to != null && !Number.isFinite(to)) ||
    (from != null && to != null && from > to)
  ) {
    return errorResponse(
      "invalid_time_range",
      "from_ms and to_ms must be finite and ordered.",
      400,
    );
  }
  if (from != null)
    frames = frames.filter((frame) => Number(frame.time_ms) >= from);
  if (to != null)
    frames = frames.filter((frame) => Number(frame.time_ms) <= to);
  return Response.json(
    {
      record_id: record.id,
      provenance: record.reference_available
        ? "EFIT reference reconstruction"
        : "Reference equilibrium unavailable",
      total: frames.length,
      offset,
      limit,
      frames: frames.slice(offset, offset + limit),
    },
    {
      headers: {
        "Cache-Control":
          "public, max-age=60, s-maxage=300, stale-while-revalidate=3600",
      },
    },
  );
}
