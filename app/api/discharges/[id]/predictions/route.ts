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
  return Response.json({
    record_id: record.id,
    predictions: record.predictions ?? [],
    availability: record.prediction_available ? "available" : "unavailable",
    note: record.prediction_available
      ? "Prediction artifact is registered for this exact record."
      : "No persisted model prediction is registered. Imported predictions remain in the current browser session.",
  });
}
