import React from 'react';
import { Link } from 'react-router-dom';
import Icon from './common/Icon';

function Footer() {
  return (
    <footer className="pt-20 pb-12 px-6 border-t border-jp-border-subtle bg-jp-bg-app text-jp-text-secondary">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-12">
        
        {/* Brand */}
        <div className="max-w-sm">
          <div className="flex items-center gap-2 mb-4">
            <Icon name="sparkles" fill className="text-jp-accent text-[24px]" />
            <span className="text-[18px] font-bold text-jp-text-primary tracking-tight">
              JobPilot AI
            </span>
          </div>
          <p className="text-[14px] leading-relaxed text-jp-text-tertiary">
            Elevating the job search experience with high-fidelity AI tools designed for modern professionals.
          </p>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-12 w-full md:w-auto">
          <div>
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-jp-text-primary mb-5">Platform</h4>
            <ul className="space-y-3 text-[13px]">
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/search">Search Jobs</Link></li>
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/profile">Analyze ATS</Link></li>
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/resumes">Resume Tailor</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-jp-text-primary mb-5">Company</h4>
            <ul className="space-y-3 text-[13px]">
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/">About</Link></li>
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/">Careers</Link></li>
              <li><Link className="hover:text-jp-accent transition-colors no-underline" to="/">Privacy</Link></li>
            </ul>
          </div>
          <div className="col-span-2 md:col-span-1">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-jp-text-primary mb-5">Updates</h4>
            <form onSubmit={(e) => { e.preventDefault(); alert("Joined successfully!"); }} className="flex gap-2">
              <input 
                className="bg-jp-bg-raised border border-jp-border rounded-lg px-3 py-2 text-[13px] w-full focus:border-jp-accent focus:outline-none text-jp-text-primary placeholder:text-jp-text-muted" 
                placeholder="Email address" 
                type="email"
                required
              />
              <button type="submit" className="jp-btn jp-btn-primary jp-btn-sm text-[12px] px-3">Join</button>
            </form>
          </div>
        </div>
      </div>
      
      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto mt-16 pt-6 border-t border-jp-border-subtle flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-[12px] text-jp-text-muted">© 2026 JobPilot AI. All rights reserved.</p>
        <div className="flex gap-4">
          <Link className="text-jp-text-muted hover:text-jp-text-primary transition-colors" to="#"><Icon name="share" className="text-[18px]" /></Link>
          <Link className="text-jp-text-muted hover:text-jp-text-primary transition-colors" to="#"><Icon name="forum" className="text-[18px]" /></Link>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
