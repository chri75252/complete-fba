"use server";

import { createServerSupabaseClient } from "./client";

export async function writeAudit(
  action: string,
  entityType: string,
  entityId: string | null,
  metadata: Record<string, unknown> = {}
) {
  const supabase = createServerSupabaseClient();
  const { data: profile } = await supabase
    .from("profiles")
    .select("id")
    .single();

  if (!profile) {
    throw new Error("Profile not found");
  }

  const { error } = await supabase.from("audit_log").insert({
    actor_profile_id: profile.id,
    action,
    entity_type: entityType,
    entity_id: entityId,
    metadata,
  });

  if (error) {
    throw new Error(error.message);
  }
}
