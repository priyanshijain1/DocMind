"use client";

import { useAuth } from "@/lib/auth";

interface HeaderProps {
  onOpenAuth: () => void;
}

export default function Header({ onOpenAuth }: HeaderProps) {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-5 shrink-0">
      <div className="flex items-center gap-2.5">
        <svg className="w-5 h-5 text-[#43A047]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span className="font-semibold text-gray-900 text-base">DocMind</span>
      </div>

      <div className="flex items-center gap-3">
        {user ? (
          <>
            <span className="text-sm text-gray-500">{user.email}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onOpenAuth}
              className="text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
              Log in
            </button>
            <button
              onClick={onOpenAuth}
              className="text-sm bg-[#66BB6A] hover:bg-[#43A047] text-white font-medium px-3.5 py-1.5 rounded-lg transition-colors"
            >
              Sign up
            </button>
          </>
        )}
      </div>
    </header>
  );
}
