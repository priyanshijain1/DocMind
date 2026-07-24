"use client";

import { useState } from "react";
import { AuthProvider, useAuth } from "@/lib/auth";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";
import Sidebar from "@/components/Sidebar";
import Chat from "@/components/Chat";

function AppShell() {
  const { user } = useAuth();
  const [authOpen, setAuthOpen] = useState(false);
  const [uploading, setUploading] = useState(false);

  const openAuth = () => setAuthOpen(true);

  return (
    <div className="flex flex-col h-screen bg-[#E8F5E9]">
      <Header onOpenAuth={openAuth} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar onUploadStart={() => setUploading(true)} onUploadDone={() => setUploading(false)} />
        <Chat requireAuth={openAuth} />
      </div>
      <AuthModal open={authOpen} onClose={() => setAuthOpen(false)} />
    </div>
  );
}

export default function Home() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  );
}
