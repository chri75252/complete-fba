import Link from "next/link";
import { createServerSupabaseClient } from "../ssr/client";

export default async function TendersPage() {
  const supabase = createServerSupabaseClient();
  const { data: tenders } = await supabase
    .from("tenders")
    .select("id, reference, deadline_at, status, owner:profiles(display_name)")
    .order("deadline_at", { ascending: true });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Tenders</h1>
        <div className="flex gap-2">
          <Link className="rounded border px-3 py-1.5 text-sm" href="/tenders/new">
            + New Tender
          </Link>
          <Link className="rounded border px-3 py-1.5 text-sm" href="/tenders/export">
            Export CSV
          </Link>
        </div>
      </div>

      <div className="rounded-lg border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">Reference</th>
              <th className="px-4 py-2">Deadline</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Owner</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(tenders ?? []).map((tender) => (
              <tr key={tender.id} className="border-b last:border-0">
                <td className="px-4 py-2 font-medium">{tender.reference}</td>
                <td className="px-4 py-2">
                  {tender.deadline_at ? new Date(tender.deadline_at).toLocaleString() : ""}
                </td>
                <td className="px-4 py-2">{tender.status}</td>
                <td className="px-4 py-2">{tender.owner?.display_name ?? "-"}</td>
                <td className="px-4 py-2">
                  <Link className="text-sm text-blue-600" href={`/tenders/${tender.id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
            {tenders?.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-sm text-slate-500" colSpan={5}>
                  No tenders yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
