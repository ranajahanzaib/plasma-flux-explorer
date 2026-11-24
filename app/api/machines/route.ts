export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { readCatalog } from "@/lib/catalog";

export async function GET() {
  const catalog = await readCatalog();
  const counts = new Map<
    string,
    { records: number; reference_frames: number }
  >();
  for (const record of catalog?.records ?? []) {
    const value = counts.get(record.machine) ?? {
      records: 0,
      reference_frames: 0,
    };
    value.records += 1;
    value.reference_frames += record.frames.length;
    counts.set(record.machine, value);
  }
  return Response.json({
    machines: [...counts].map(([machine, coverage]) => ({
      machine,
      ...coverage,
    })),
  });
}
