export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { errorResponse, findRecord, readCatalog } from "@/lib/catalog";

export async function GET(
  _request: Request,
  context: { params: Promise<{ artifact: string }> },
) {
  const { artifact } = await context.params;
  const catalog = await readCatalog();
  if (!catalog)
    return errorResponse(
      "catalog_unavailable",
      "No local or R2 catalog is available.",
      503,
    );
  const record = findRecord(catalog, decodeURIComponent(artifact));
  if (!record)
    return errorResponse(
      "artifact_not_found",
      `No catalog artifact matches ${artifact}.`,
      404,
    );
  return Response.json({
    artifact: record.id,
    source: record.dataset,
    source_url: record.source_url,
    dataset_revision: record.revision,
    configuration: record.configuration,
    sha256: record.sha256,
    raw_path: record.raw_path,
    schema_fingerprint: record.schema_fingerprint,
    source_columns: record.source_columns,
    reference_available: record.reference_available,
    prediction_available: record.prediction_available,
  });
}
