import React from 'react';
import { Link } from 'react-router-dom';
import Icon from './common/Icon';

function Footer() {
  return (
    <footer className="bg-jp-bg-app border-t border-jp-border-subtle overflow-hidden relative z-10">
      
      {/* ── Newsletter Banner ─────────────────────────────────── */}
      <div className="border-b border-jp-border-subtle bg-jp-bg-surface/30">
        <div className="max-w-7xl mx-auto px-6 py-12 md:py-16 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="max-w-xl text-center md:text-left">
            <h3 className="text-[18px] md:text-[20px] font-bold text-jp-text-primary mb-2">Subscribe to JobPilot Insights</h3>
            <p className="text-[14px] text-jp-text-secondary leading-relaxed">
              Stay updated with AI hiring trends, platform releases, and exclusive career insights delivered to your inbox.
            </p>
          </div>
          <form onSubmit={(e) => { e.preventDefault(); alert("Joined successfully!"); }} className="w-full md:w-auto flex flex-col sm:flex-row gap-3">
            <div className="relative w-full sm:w-[300px]">
              <Icon name="mail" className="absolute left-3 top-1/2 -translate-y-1/2 text-jp-text-muted text-[16px]" />
              <input 
                className="w-full bg-jp-bg-raised border border-jp-border rounded-xl pl-10 pr-4 py-2.5 text-[14px] focus:border-jp-accent focus:ring-1 focus:ring-jp-accent/50 outline-none text-jp-text-primary placeholder:text-jp-text-muted transition-all shadow-inner" 
                placeholder="Enter your email" 
                type="email"
                required
              />
            </div>
            <button type="submit" className="px-6 py-2.5 bg-jp-text-primary text-jp-bg-app font-bold text-[14px] rounded-xl hover:bg-jp-text-secondary transition-colors shadow-md whitespace-nowrap">
              Subscribe
            </button>
          </form>
        </div>
      </div>

      {/* ── Main Footer Links ─────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-12 flex flex-col lg:flex-row justify-between gap-16 lg:gap-8">
        
        {/* Brand Column */}
        <div className="flex flex-col gap-6 max-w-sm">
          <Link to="/" className="flex items-center gap-3 no-underline group w-max">
            <img src="/logo.png" alt="JobPilot Logo" className="w-8 h-8 rounded-lg shadow-[0_0_12px_var(--color-jp-accent-glow)] group-hover:shadow-[0_0_20px_var(--color-jp-accent-glow)] transition-shadow duration-300" />
            <span className="text-[18px] font-bold text-jp-text-primary tracking-tight">JobPilot AI</span>
          </Link>
          <p className="text-[14px] leading-relaxed text-jp-text-tertiary">
            The high-performance operating system for your career. Search, tailor, and apply with unprecedented AI precision.
          </p>
          
          {/* Socials */}
          <div className="flex items-center gap-3 mt-2">
            <a href="#" className="flex items-center justify-center w-8 h-8 rounded-full bg-jp-bg-raised border border-jp-border text-jp-text-secondary hover:text-jp-text-primary hover:border-jp-accent/50 hover:bg-jp-accent/10 transition-all cursor-pointer no-underline">
              <span className="font-bold font-serif italic text-[14px]">X</span>
            </a>
            <a href="#" className="flex items-center justify-center w-8 h-8 rounded-full bg-jp-bg-raised border border-jp-border text-jp-text-secondary hover:text-jp-text-primary hover:border-jp-accent/50 hover:bg-jp-accent/10 transition-all cursor-pointer no-underline">
              <span className="font-bold text-[14px]">in</span>
            </a>
            <a href="#" className="flex items-center justify-center w-8 h-8 rounded-full bg-jp-bg-raised border border-jp-border text-jp-text-secondary hover:text-jp-text-primary hover:border-jp-accent/50 hover:bg-jp-accent/10 transition-all cursor-pointer no-underline">
              <Icon name="code" className="text-[16px]" />
            </a>
            <a href="#" className="flex items-center justify-center w-8 h-8 rounded-full bg-jp-bg-raised border border-jp-border text-jp-text-secondary hover:text-jp-text-primary hover:border-jp-accent/50 hover:bg-jp-accent/10 transition-all cursor-pointer no-underline">
              <Icon name="forum" className="text-[16px]" />
            </a>
          </div>

          {/* Trust */}
          <div className="flex items-center gap-4 mt-2">
            <span className="flex items-center gap-1.5 text-[11px] font-semibold text-jp-success">
              <Icon name="verified" className="text-[14px]" /> ATS Friendly
            </span>
            <span className="flex items-center gap-1.5 text-[11px] font-semibold text-jp-accent">
              <Icon name="security" className="text-[14px]" /> Privacy First
            </span>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-x-8 gap-y-12 w-full lg:w-2/3">
          {/* Product */}
          <div className="flex flex-col gap-4">
            <h4 className="text-[12px] font-semibold text-jp-text-primary">Product</h4>
            <ul className="flex flex-col gap-3 text-[13px] text-jp-text-secondary">
              <li><Link to="/search" className="hover:text-jp-text-primary transition-colors no-underline">AI Job Search</Link></li>
              <li><Link to="/resumes" className="hover:text-jp-text-primary transition-colors no-underline">Resume Tailor</Link></li>
              <li><Link to="/profile" className="hover:text-jp-text-primary transition-colors no-underline">ATS Analyzer</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Skill Gap Analysis</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Pricing</Link></li>
            </ul>
          </div>
          
          {/* Company */}
          <div className="flex flex-col gap-4">
            <h4 className="text-[12px] font-semibold text-jp-text-primary">Company</h4>
            <ul className="flex flex-col gap-3 text-[13px] text-jp-text-secondary">
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">About Us</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Careers</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Blog</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Contact</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Roadmap</Link></li>
            </ul>
          </div>
          
          {/* Resources */}
          <div className="flex flex-col gap-4">
            <h4 className="text-[12px] font-semibold text-jp-text-primary">Resources</h4>
            <ul className="flex flex-col gap-3 text-[13px] text-jp-text-secondary">
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Documentation</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Help Center</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline flex items-center gap-2">API <span className="bg-jp-accent/20 text-jp-accent px-1.5 py-0.5 rounded text-[9px] font-bold">BETA</span></Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">FAQs</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Changelog</Link></li>
            </ul>
          </div>

          {/* Legal */}
          <div className="flex flex-col gap-4">
            <h4 className="text-[12px] font-semibold text-jp-text-primary">Legal</h4>
            <ul className="flex flex-col gap-3 text-[13px] text-jp-text-secondary">
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Privacy Policy</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Terms of Service</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Cookie Policy</Link></li>
              <li><Link to="/" className="hover:text-jp-text-primary transition-colors no-underline">Security</Link></li>
            </ul>
          </div>
        </div>
      </div>

      {/* ── Bottom Bar ─────────────────────────────────── */}
      <div className="border-t border-jp-border-subtle mt-4">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-jp-success animate-pulse"></div>
            <span className="text-[12px] text-jp-text-muted font-medium">All systems operational</span>
          </div>
          <div className="flex flex-col sm:flex-row items-center gap-1 sm:gap-4 text-[12px] text-jp-text-muted">
            <span>© 2026 JobPilot AI Inc.</span>
            <span className="hidden sm:inline text-jp-border-subtle">•</span>
            <span className="flex items-center">Made with <Icon name="favorite" className="text-red-500 text-[12px] inline-block mx-1" fill /> for modern job seekers</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
