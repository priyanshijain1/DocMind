"use client";

import { useState, useRef } from "react";
import { uploadPDF } from "@/lib/api";

export default function FileUpload({ onUploaded }: { onUploaded: () => void }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await uploadPDF(file);
      onUploaded();
      if (inputRef.current) inputRef.current.value = "";
    } catch {
      setError("Upload failed. Check backend.");
    }
    setUploading(false);
  };

  return (
    <div className="border-2 border-dashed rounded-lg p-4 text-center">
      <input ref={inputRef} type="file" accept=".pdf" onChange={handleUpload} className="hidden" />
      <button
        className="bg-green-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
      >
        {uploading ? "Uploading..." : "Upload PDF"}
      </button>
      {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
    </div>
  );
}
