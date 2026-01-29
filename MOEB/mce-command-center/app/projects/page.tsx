import Link from "next/link";
import { createServerSupabaseClient } from "../ssr/client";

export default async function ProjectsPage() {
  const supabase = createServerSupabaseClient();
  const { data: projects } = await supabase
    .from("projects")
    .select("id, code, name, status, progress_pct, pm:profiles(display_name)")
    .order("created_at", { ascending: false });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Projects</h1>
        <div className="flex gap-2">
          <Link className="rounded border px-3 py-1.5 text-sm" href="/projects/new">
            + New Project
          </Link>
          <Link className="rounded border px-3 py-1.5 text-sm" href="/projects/export">
            Export CSV
          </Link>
        </div>
      </div>

      <div className="rounded-lg border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">Code</th>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">PM</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Progress</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {(projects ?? []).map((project) => (
              <tr key={project.id} className="border-b last:border-0">
                <td className="px-4 py-2 font-medium">{project.code}</td>
                <td className="px-4 py-2">{project.name}</td>
                <td className="px-4 py-2">-</td>
                <td className="px-4 py-2">{project.status}</td>
                <td className="px-4 py-2">{project.progress_pct ?? 0}%</td>
                <td className="px-4 py-2">
                  <Link className="text-sm text-blue-600" href={`/projects/${project.id}`}>
                    Open
                  </Link>
                </td>
              </tr>
            ))}
            {projects?.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-sm text-slate-500" colSpan={6}>
                  No projects yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
