import React, { useState } from "react";
import TopHeader from "./TopHeader";
import UserAvatarMenu from "./UserAvatarMenu";
import { useAuth } from "../../context/AuthContext";

/**
 * Shared layout shell for all authenticated pages.
 * Renders: Floating Top NavBar + Full Width Content
 */
export default function AppShell({ children, topRight = null }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-jp-bg-app relative">
      
      {/* Floating Top Nav */}
      <TopHeader
        onMenuClick={() => setMobileMenuOpen(true)}
        right={
          topRight || (
            <UserAvatarMenu name={user?.name || "User"} />
          )
        }
      />

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto w-full relative z-10 px-4 md:px-8 pb-8">
        <div className="max-w-7xl mx-auto h-full animate-fade-in">
          {children}
        </div>
      </main>

    </div>
  );
}
