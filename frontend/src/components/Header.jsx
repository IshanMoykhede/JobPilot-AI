import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Icon from './common/Icon';

function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="fixed top-0 w-full z-50 bg-jp-bg-surface/80 backdrop-blur-xl border-b border-jp-border-subtle h-16 flex justify-between items-center px-6">
      <div className="flex items-center gap-2">
        <Icon name="sparkles" fill className="text-jp-accent text-[24px]" />
        <Link to="/" className="text-[18px] font-bold text-jp-text-primary tracking-tight no-underline">
          JobPilot AI
        </Link>
      </div>

      {user && (
        <nav className="hidden md:flex items-center gap-8">
          <Link className="text-[13px] font-medium text-jp-text-primary hover:text-jp-accent transition-colors no-underline" to="/dashboard">Dashboard</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/search">Jobs</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/resumes">Resumes</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/profile">Profile</Link>
        </nav>
      )}

      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-4">
            <Link to="/profile" className="w-8 h-8 rounded-full bg-jp-accent-muted flex items-center justify-center text-[11px] font-bold text-jp-accent-text no-underline">
              {user.name ? user.name.split(" ").map(n => n[0]).join("").toUpperCase().slice(0, 2) : "US"}
            </Link>
            <button onClick={logout} className="jp-btn jp-btn-secondary jp-btn-sm text-[12px]">
              Sign Out
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link to="/auth" className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline hidden sm:block">
              Sign In
            </Link>
            <Link to="/auth" className="jp-btn jp-btn-primary jp-btn-sm text-[13px] no-underline">
              Get Started
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;
