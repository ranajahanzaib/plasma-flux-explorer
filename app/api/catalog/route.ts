export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { errorResponse, readCatalog } from "@/lib/catalog";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get("page") ?? 1);
  const limit = Number(url.searchParams.get("limit") ?? 100);
  if (
    !Number.isInteger(page) ||
    page < 1 ||
    !Number.isInteger(limit) ||
    limit < 1 ||
    limit > 100
  ) {
    return errorResponse(
      "invalid_pagination",
      "page must be positive and limit must be between 1 and 100.",
      400,
    );
  }

  const catalog = await readCatalog();
  if (!catalog) {
    return Response.json(
      { records: [], status: "not_bootstrapped", total: 0, page, limit },
      {
        headers: {
          "Cache-Control": "no-store",
          "X-Data-Source": "unavailable",
        },
      },
    );
  }

  const machine = url.searchParams.get("machine");
  const configuration = url.searchParams.get("configuration");
  const search = url.searchParams.get("search")?.trim().toLowerCase();
  const matching = catalog.records.filter(
    (record) =>
      (!machine || record.machine === machine) &&
      (!configuration || record.configuration === configuration) &&
      (!search ||
        `${record.id} ${record.record_id} ${record.machine} ${record.configuration}`
          .toLowerCase()
          .includes(search)),
  );
  const start = (page - 1) * limit;
  return Response.json(
    {
      ...catalog,
      records: matching.slice(start, start + limit),
      pagination: {
        page,
        limit,
        total: matching.length,
        pages: Math.ceil(matching.length / limit),
      },
    },
    {
      headers: {
        "Cache-Control":
          "public, max-age=60, s-maxage=300, stale-while-revalidate=3600",
      },
    },
  );
}
