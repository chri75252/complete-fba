import { auth } from "@clerk/nextjs/server";
import Link from "next/link";
import { upsertProfile } from "../ssr/profile";
import { createServerSupabaseClient } from "../ssr/client";

function daysUntil(date: Date) {
  const diff = date.getTime() - new Date().getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

export default async function DashboardPage() {
  const { userId } = await auth();
  if (!userId) {
    return null;
  }

  await upsertProfile();
  const supabase = createServerSupabaseClient();

  const [{ data: tenders }, { data: milestones }, { data: notifications }] =
    await Promise.all([
      supabase.from("tenders").select("id, reference, deadline_at, status, next_followup_at"),
      supabase
        .from("project_milestones")
        .select("id, title, due_date, status, project:projects(code, name)"),
      supabase
        .from("notifications")
        .select("id, severity, ack_required, acked_at")
        .eq("severity", "critical"),
    ]);

  const tendersDue = {
    today: 0,
    d1: 0,
    d3: 0,
    d7: 0,
    d14: 0,
  };

  (tenders ?? []).forEach((tender) => {
    if (!tender.deadline_at) return;
    const days = daysUntil(new Date(tender.deadline_at));
    if (days <= 0) tendersDue.today += 1;
    if (days <= 1) tendersDue.d1 += 1;
    if (days <= 3) tendersDue.d3 += 1;
    if (days <= 7) tendersDue.d7 += 1;
    if (days <= 14) tendersDue.d14 += 1;
  });

  const upcomingMilestones = (milestones ?? [])
    .filter((item) => item.due_date)
    .sort((a, b) =>
      new Date(a.due_date as string).getTime() -
      new Date(b.due_date as string).getTime()
    )
    .slice(0, 10);

  const criticalUnacked = (notifications ?? []).filter(
    (note) => note.ack_required && !note.acked_at
  ).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <div className="flex gap-2">
          <Link className="rounded border px-3 py-1.5 text-sm" href="/projects/new">
            + New Project
          </Link>
          <Link className="rounded border px-3 py-1.5 text-sm" href="/tenders/new">
            + New Tender
          </Link>
          <Link className="rounded border px-3 py-1.5 text-sm" href="/documents">
            Upload Document
          </Link>
          <Link className="rounded border px-3 py-1.5 text-sm" href="/notifications">
            View Notifications
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-5">
        <div className="rounded-lg border bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Tenders due 14d</div>
          <div className="text-2xl font-semibold">{tendersDue.d14}</div>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Due 7d</div>
          <div className="text-2xl font-semibold">{tendersDue.d7}</div>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Due 3d</div>
          <div className="text-2xl font-semibold">{tendersDue.d3}</div>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Due 1d</div>
          <div className="text-2xl font-semibold">{tendersDue.d1}</div>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <div className="text-xs uppercase text-slate-500">Due today</div>
          <div className="text-2xl font-semibold">{tendersDue.today}</div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-4">
          <div className="mb-3 text-sm font-semibold">Tenders due soon</div>
          <div className="space-y-2 text-sm">
            {(tenders ?? []).slice(0, 8).map((tender) => (
              <div key={tender.id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{tender.reference}</div>
                  <div className="text-xs text-slate-500">
                    {tender.deadline_at ? new Date(tender.deadline_at).toLocaleString() : ""}
                  </div>
                </div>
                <div className="text-xs text-slate-500">
                  {tender.deadline_at
                    ? `T-${daysUntil(new Date(tender.deadline_at))}`
                    : ""}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border bg-white p-4">
          <div className="mb-3 text-sm font-semibold">Upcoming milestones (next 10)</div>
          <div className="space-y-2 text-sm">
            {upcomingMilestones.map((milestone) => (
              <div key={milestone.id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{milestone.title}</div>
                  <div className="text-xs text-slate-500"></div>
                </div>
                <div className="text-xs text-slate-500">
                  {milestone.due_date
                    ? `T-${daysUntil(new Date(milestone.due_date as string))}`
                    : ""}
                </div>
              </div>
            ))}
            {upcomingMilestones.length === 0 && (
              <div className="text-sm text-slate-500">No milestones due yet.</div>
            )}
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-white p-4">
        <div className="mb-3 text-sm font-semibold">Critical notifications unacknowledged</div>
        <div className="text-2xl font-semibold">{criticalUnacked}</div>
      </div>
    </div>
  );
}
