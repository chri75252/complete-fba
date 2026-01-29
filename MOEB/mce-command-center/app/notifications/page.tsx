import { acknowledgeNotification } from "../ssr/notifications";
import { createServerSupabaseClient } from "../ssr/client";

export default async function NotificationsPage() {
  const supabase = createServerSupabaseClient();
  const { data: notifications } = await supabase
    .from("notifications")
    .select("id, message, severity, ack_required, acked_at, created_at")
    .order("created_at", { ascending: false });

  async function handleAck(formData: FormData) {
    "use server";
    const id = formData.get("id")?.toString();
    if (!id) {
      throw new Error("Missing notification id");
    }
    await acknowledgeNotification(id);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Notifications</h1>
      <div className="rounded-lg border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">Message</th>
              <th className="px-4 py-2">Severity</th>
              <th className="px-4 py-2">Ack Required</th>
              <th className="px-4 py-2">Acked</th>
              <th className="px-4 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {(notifications ?? []).map((note) => (
              <tr key={note.id} className="border-b last:border-0">
                <td className="px-4 py-2">{note.message}</td>
                <td className="px-4 py-2">{note.severity}</td>
                <td className="px-4 py-2">{note.ack_required ? "Yes" : "No"}</td>
                <td className="px-4 py-2">{note.acked_at ? "Yes" : "No"}</td>
                <td className="px-4 py-2">
                  {note.ack_required && !note.acked_at ? (
                    <form action={handleAck}>
                      <input type="hidden" name="id" value={note.id} />
                      <button className="rounded border px-2 py-1 text-xs" type="submit">
                        Acknowledge
                      </button>
                    </form>
                  ) : (
                    ""
                  )}
                </td>
              </tr>
            ))}
            {notifications?.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-sm text-slate-500" colSpan={5}>
                  No notifications yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
