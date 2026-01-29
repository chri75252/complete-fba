"use server";

import { createServerSupabaseClient } from "./client";
import { upsertProfile } from "./profile";
import { writeAudit } from "./audit";

export async function addTenderComms(input: {
  tenderId: string;
  channel: string;
  notes: string;
  outcome?: string;
}) {
  await upsertProfile();
  const supabase = createServerSupabaseClient();

  const { data: profile } = await supabase
    .from("profiles")
    .select("id")
    .single();

  if (!profile) {
    throw new Error("Profile not found");
  }

  const { data: event, error } = await supabase
    .from("tender_comms_events")
    .insert({
      tender_id: input.tenderId,
      actor_profile_id: profile.id,
      channel: input.channel,
      notes: input.notes,
      outcome: input.outcome,
    })
    .select("id")
    .single();

  if (error || !event) {
    throw new Error(error?.message ?? "Failed to add comms event");
  }

  await writeAudit("create", "tender_comms", event.id, {
    tenderId: input.tenderId,
  });
}
