import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Icon from './common/Icon';

function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="fixed top-4 md:top-6 left-1/2 -translate-x-1/2 w-[calc(100%-2rem)] max-w-6xl z-50 bg-jp-bg-surface/70 backdrop-blur-2xl border border-jp-border-subtle h-16 rounded-2xl md:rounded-full flex justify-between items-center px-4 md:px-6 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
      <div className="flex items-center gap-3">
        <img src="/logo.png" alt="JobPilot Logo" className="w-8 h-8 rounded-lg shadow-[0_0_12px_var(--color-jp-accent-glow)]" />
        <Link to="/" className="text-[18px] font-bold text-jp-text-primary tracking-tight no-underline">
          JobPilot AI
        </Link>
      </div>

      {user ? (
        <nav className="hidden md:flex items-center gap-8">
          <Link className="text-[13px] font-medium text-jp-text-primary hover:text-jp-accent transition-colors no-underline" to="/dashboard">Dashboard</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/search">Jobs</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/resumes">Resumes</Link>
          <Link className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" to="/profile">Profile</Link>
        </nav>
      ) : (
        <nav className="hidden md:flex items-center gap-8">
          <a className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" href="#features">Features</a>
          <a className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" href="#how-it-works">How It Works</a>
          <a className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" href="#pricing">Pricing</a>
          <a className="text-[13px] font-medium text-jp-text-secondary hover:text-jp-text-primary transition-colors no-underline" href="#testimonials">Testimonials</a>
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
