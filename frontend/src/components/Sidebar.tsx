"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "@/lib/auth";
import { listDocuments, deleteDocument, uploadPDF } from "@/lib/api";

interface Doc {
  id: string;
  filename: string;
  num_pages: number;
  num_chunks: number;
}

interface SidebarProps {
  onUploadStart: () => void;
  onUploadDone: () => void;
}

export default function Sidebar({ onUploadStart, onUploadDone }: SidebarProps) {
  const { user } = useAuth();
  const [docs, setDocs] = useState<Doc[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = useCallback(async () => {
    if (!user) return;
    try {
      setDocs(await listDocuments());
    } catch {
      /* ignore */
    }
  }, [user]);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    onUploadStart();
    try {
      await uploadPDF(file);
      await fetchDocs();
      onUploadDone();
    } catch {
      /* ignore */
    }
    setUploading(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith(".pdf")) handleUpload(file);
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      setDocs((prev) => prev.filter((d) => d.id !== docId));
    } catch {
      /* ignore */
    }
  };

  return (
    <aside
      className={`w-60 bg-white border-r border-gray-200 flex flex-col shrink-0 transition-colors ${
        dragOver ? "bg-[#f0faf0] border-[#66BB6A]" : ""
      }`}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <div className="p-3">
        <input ref={inputRef} type="file" accept=".pdf" onChange={handleFileInput} className="hidden" />
        <button
          onClick={() => {
            if (!user) return;
            inputRef.current?.click();
          }}
          disabled={uploading}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-[#66BB6A] hover:bg-[#43A047] text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          {uploading ? "Uploading..." : "Upload PDF"}
        </button>
        {!user && (
          <p className="text-xs text-gray-400 text-center mt-2">Log in to upload</p>
        )}
      </div>

      <div className="border-t border-gray-100" />

      <div className="flex-1 overflow-y-auto p-3">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Documents</p>
        {docs.length === 0 ? (
          <p className="text-xs text-gray-400">No documents yet</p>
        ) : (
          <div className="space-y-1">
            {docs.map((doc) => (
              <div
                key={doc.id}
                className="group flex items-start gap-2 p-2 rounded-lg hover:bg-[#f0faf0] transition-colors"
              >
                <svg className="w-4 h-4 text-[#66BB6A] mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                </svg>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700 truncate">{doc.filename}</p>
                  <p className="text-xs text-gray-400">{doc.num_pages} pages</p>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="opacity-0 group-hover:opacity-100 text-gray-300 hover:text-red-400 transition-all shrink-0"
                >
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
