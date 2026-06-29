import React, { useState } from "react";
import Sidebar from "./Sidebar";
import TopHeader from "./TopHeader";
import Breadcrumb from "./Breadcrumb";
import UserAvatarMenu from "./UserAvatarMenu";
import { useAuth } from "../../context/AuthContext";

/**
 * Shared layout shell for all authenticated pages.
 * Renders: Sidebar | TopBar + Content
 *
 * Usage:
 *   <AppShell breadcrumbs={[{ label: "Dashboard" }]}>
 *     <DashboardContent />
 *   </AppShell>
 */
export default function AppShell({ children, breadcrumbs = [], topRight = null }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="flex h-screen overflow-hidden bg-jp-bg-app">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        mobileOpen={mobileMenuOpen}
        onMobileClose={() => setMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <TopHeader
          onMenuClick={() => setMobileMenuOpen(true)}
          left={
            breadcrumbs.length > 0 ? (
              <Breadcrumb items={breadcrumbs} />
            ) : null
          }
          right={
            topRight || (
              <UserAvatarMenu name={user?.name || "User"} />
            )
          }
        />

        <main className="flex-1 overflow-y-auto bg-jp-bg-surface">
          <div className="jp-page-enter">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
