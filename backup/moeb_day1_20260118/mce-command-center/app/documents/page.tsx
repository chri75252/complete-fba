"use client";

import { useState } from "react";
import { prepareDocumentUpload, createSignedDownload } from "../ssr/documents";

export default function DocumentsPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [projectId, setProjectId] = useState("");
  const [tenderId, setTenderId] = useState("");
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  async function handleUpload() {
    if (!selectedFile) return;

    const { signedUrl } = await prepareDocumentUpload({
      fileName: selectedFile.name,
      fileType: selectedFile.type,
      fileSize: selectedFile.size,
      projectId: projectId || undefined,
      tenderId: tenderId || undefined,
      title: selectedFile.name,
    });

    const response = await fetch(signedUrl, {
      method: "PUT",
      headers: { "Content-Type": selectedFile.type },
      body: selectedFile,
    });

    if (!response.ok) {
      setUploadStatus("Upload failed");
      return;
    }

    setUploadStatus("Upload complete");
  }

  async function handleDownload() {
    if (!projectId) return;
    const { signedUrl } = await createSignedDownload(projectId);
    window.open(signedUrl, "_blank");
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Documents</h1>
        <button
          className="rounded border px-3 py-1.5 text-sm"
          onClick={handleDownload}
          type="button"
        >
          Create Signed URL
        </button>
      </div>

      <div className="rounded-lg border bg-white p-4">
        <div className="text-sm font-semibold">Upload Document</div>
        <div className="mt-3 grid gap-3 text-sm">
          <input
            className="rounded border px-3 py-2"
            placeholder="Project ID"
            value={projectId}
            onChange={(event) => setProjectId(event.target.value)}
          />
          <input
            className="rounded border px-3 py-2"
            placeholder="Tender ID (optional)"
            value={tenderId}
            onChange={(event) => setTenderId(event.target.value)}
          />
          <input
            className="block text-sm"
            type="file"
            onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          />
        </div>
        <button
          className="mt-3 rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white"
          onClick={handleUpload}
          type="button"
        >
          Upload
        </button>
        {uploadStatus && <p className="mt-2 text-sm text-slate-500">{uploadStatus}</p>}
      </div>
    </div>
  );
}
