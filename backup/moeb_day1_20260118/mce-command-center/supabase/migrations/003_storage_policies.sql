alter table storage.objects enable row level security;

create policy storage_documents_select
on storage.objects
for select
to authenticated
using (
  bucket_id = 'mce-documents'
  and exists (
    select 1
    from public.documents d
    where d.storage_bucket = storage.objects.bucket_id
      and d.storage_path = storage.objects.name
      and (
        public.is_admin_role()
        or (d.project_id is not null and public.can_view_project(d.project_id))
        or (d.tender_id is not null and public.can_view_tender(d.tender_id))
      )
  )
);

create policy storage_documents_insert
on storage.objects
for insert
to authenticated
with check (
  bucket_id = 'mce-documents'
  and exists (
    select 1
    from public.documents d
    where d.storage_bucket = storage.objects.bucket_id
      and d.storage_path = storage.objects.name
      and d.uploaded_by_profile_id = public.current_profile_id()
      and (
        (d.project_id is not null and public.can_edit_project(d.project_id))
        or (d.tender_id is not null and public.can_edit_tender(d.tender_id))
      )
  )
);

create policy storage_documents_delete
on storage.objects
for delete
to authenticated
using (
  bucket_id = 'mce-documents'
  and exists (
    select 1
    from public.documents d
    where d.storage_bucket = storage.objects.bucket_id
      and d.storage_path = storage.objects.name
      and public.is_admin_role()
  )
);
