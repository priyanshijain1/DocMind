"use client";

import Chat from "@/components/Chat";
import FileUpload from "@/components/FileUpload";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <FileUpload onUploaded={() => window.location.reload()} />
      <Chat />
    </main>
  );
}
