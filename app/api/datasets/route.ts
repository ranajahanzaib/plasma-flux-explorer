export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { readCatalog } from "@/lib/catalog";

export async function GET() {
  const catalog = await readCatalog();
  const configurations = new Map<
    string,
    { records: number; reference_frames: number; machines: Set<string> }
  >();
  for (const record of catalog?.records ?? []) {
    const value = configurations.get(record.configuration) ?? {
      records: 0,
      reference_frames: 0,
      machines: new Set<string>(),
    };
    value.records += 1;
    value.reference_frames += record.frames.length;
    value.machines.add(record.machine);
    configurations.set(record.configuration, value);
  }
  return Response.json({
    dataset: catalog?.dataset ?? null,
    revision: catalog?.revision ?? null,
    configurations: [...configurations].map(([configuration, value]) => ({
      configuration,
      records: value.records,
      reference_frames: value.reference_frames,
      machines: [...value.machines],
    })),
  });
}
