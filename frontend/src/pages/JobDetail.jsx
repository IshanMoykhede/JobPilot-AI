import React from 'react';
import Header from '../components/Header';

function JobDetail() {
  return (
    <>
      <Header />
      <div className="p-xl space-y-lg">
        {/* HEADER SECTION: Job Overview Card */}
        <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg flex flex-col md:flex-row items-center gap-lg">
          <div className="w-20 h-20 bg-surface-container rounded-xl flex items-center justify-center p-4">
            <img alt="CloudStream Solutions Logo" className="w-full h-full object-contain" data-alt="A clean, minimalist tech company logo featuring a stylized geometric 'S' integrated with a cloud-like stream element. The color palette is professional primary blue and crisp white, conveying high-trust corporate reliability. It's set against a light-mode grey background with soft ambient lighting for a modern SaaS aesthetic." src="https://lh3.googleusercontent.com/aida-public/AB6AXuC9s7eyf9NXaonDAu6UAhF0OuKJhJcVCqvSRqLlEvrAB-NRBqNV7dD0IUdcxBX5irBBcdDc1u8lEqbyMX4eo8FJKQ_L_VhwsNXqs-I9BtzWolz_LZy7PgAIrDNFwKFIjZuNLwT6KopwPt34Ezv__nlGaTG3NVJ070bWj-z9PhHgBTbXHipdNN8g1HsNnHcplLsYNXIv20mOHnQSuQgzDowgRxNpwjQi7zdQVjuagTPl97lAt0QRdQqHOQ5KrVDYkX7Ynaol3FYDlpEC" />
          </div>
          <div className="flex-1 text-center md:text-left">
            <h2 className="font-headline-md text-headline-md text-on-surface">Senior DevOps Architect</h2>
            <div className="flex flex-wrap justify-center md:justify-start items-center gap-md mt-1 text-on-surface-variant">
              <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">business</span> CloudStream Solutions</span>
              <span className="flex items-center gap-1"><span className="material-symbols-outlined text-sm">location_on</span> Pune, Hybrid</span>
              <span className="bg-surface-container px-2 py-0.5 rounded text-label-sm font-semibold text-primary">Full-time</span>
            </div>
          </div>
          <div className="flex items-center gap-xl">
            <div className="relative w-24 h-24">
              <svg className="w-full h-full transform -rotate-90" viewbox="0 0 36 36">
                <path className="text-surface-container" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3"></path>
                <path className="text-primary animate-progress" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="89, 100" strokeLinecap="round" strokeWidth="3"></path>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-xl font-bold text-primary">89%</span>
                <span className="text-[8px] uppercase font-bold text-outline">Match</span>
              </div>
            </div>
            <div className="flex flex-col gap-3">
              <button className="bg-primary text-on-primary px-6 py-2.5 rounded-lg font-label-md hover:bg-primary-container transition-all shadow-sm">Generate Tailored Resume</button>
              <button className="border border-outline-variant text-on-surface px-6 py-2.5 rounded-lg font-label-md hover:bg-surface-container-low transition-all">Apply Now</button>
            </div>
          </div>
        </section>
        {/* THREE COLUMN DASHBOARD STRUCTURE */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg">
          {/* COLUMN 1: Job Description (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-lg">
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col h-[700px]">
              <div className="p-md border-b border-outline-variant">
                <h3 className="font-label-md text-label-md text-primary uppercase tracking-wider">Job Requirements</h3>
              </div>
              <div className="p-lg overflow-y-auto custom-scrollbar space-y-lg">
                <div>
                  <h4 className="font-headline-sm text-headline-sm mb-4">Responsibilities</h4>
                  <ul className="space-y-3 text-body-sm text-on-surface-variant list-disc pl-5">
                    <li>Architect and maintain highly scalable, fault-tolerant infrastructure on AWS using best practices.</li>
                    <li>Automate CI/CD pipelines for complex microservices architectures using Jenkins and GitHub Actions.</li>
                    <li>Design container orchestration strategies with Docker and Kubernetes (EKS).</li>
                    <li>Lead security hardening initiatives and compliance audits for infrastructure.</li>
                    <li>Collaborate with development teams to optimize application performance and monitoring.</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-headline-sm text-headline-sm mb-4">Qualifications</h4>
                  <ul className="space-y-3 text-body-sm text-on-surface-variant list-disc pl-5">
                    <li>8+ years of experience in DevOps or Infrastructure Engineering roles.</li>
                    <li>Deep expertise in Terraform and Infrastructure as Code (IaC).</li>
                    <li>Strong background in Linux administration and Shell scripting.</li>
                    <li>Certifications: AWS Solutions Architect Professional preferred.</li>
                  </ul>
                </div>
                <div className="pt-4 border-t border-outline-variant">
                  <h4 className="font-label-md text-label-md mb-3">Key Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">AWS</span>
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">Terraform</span>
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">Docker</span>
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">CI/CD</span>
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">Kubernetes</span>
                    <span className="bg-surface-container px-3 py-1 rounded-full text-label-sm text-primary">Python</span>
                  </div>
                </div>
              </div>
            </section>
          </div>
          {/* COLUMN 2: AI Analysis (4 cols) */}
          <div className="lg:col-span-4 space-y-lg">
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg space-y-lg">
              <div className="flex items-center justify-between">
                <h3 className="font-label-md text-label-md text-primary uppercase tracking-wider">AI Match Analysis</h3>
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-tight">High Confidence</span>
              </div>
              {/* Readiness Bar */}
              <div className="bg-surface-container-low p-4 rounded-xl border border-outline-variant/30">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-label-md font-bold text-on-surface">Application Readiness</span>
                  <span className="text-label-md font-bold text-primary">82%</span>
                </div>
                <div className="h-2 w-full bg-surface rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: "82%" }}></div>
                </div>
              </div>
              {/* Analysis Cards */}
              <div className="space-y-4">
                <div className="bg-surface p-4 rounded-xl border-l-4 border-primary shadow-sm">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-primary">auto_awesome</span>
                    <div>
                      <p className="font-label-md font-bold">Why This Job Matches You</p>
                      <p className="text-body-sm text-on-surface-variant mt-1">Your 5 years of AWS experience directly aligns with their architectural needs. Your Kubernetes background exceeds their base requirements.</p>
                    </div>
                  </div>
                </div>
                <div className="bg-surface p-4 rounded-xl border-l-4 border-error shadow-sm">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-error">warning</span>
                    <div>
                      <p className="font-label-md font-bold">Missing Skills</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        <span className="bg-error-container text-on-error-container text-[11px] font-bold px-2 py-0.5 rounded">Terraform</span>
                        <span className="bg-error-container text-on-error-container text-[11px] font-bold px-2 py-0.5 rounded">Jenkins</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-surface p-4 rounded-xl border-l-4 border-secondary shadow-sm">
                  <div className="flex gap-3">
                    <span className="material-symbols-outlined text-secondary">lightbulb</span>
                    <div>
                      <p className="font-label-md font-bold">Improvement Suggestions</p>
                      <p className="text-body-sm text-on-surface-variant mt-1 italic">"Add specific deployment metrics (e.g., 'reduced downtime by 30%') to your past CloudStream project."</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>
            {/* Modifications Section */}
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg">
              <h3 className="font-label-md text-label-md text-primary uppercase tracking-wider mb-lg">AI Modifications</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-2">
                  <div className="p-3 bg-red-50/50 border border-red-100 rounded-lg">
                    <span className="text-[10px] font-bold text-red-700 uppercase">Before</span>
                    <p className="text-body-sm text-on-surface-variant mt-1">Worked on Docker containers for various internal projects.</p>
                  </div>
                  <div className="p-3 bg-green-50/50 border border-green-100 rounded-lg">
                    <span className="text-[10px] font-bold text-green-700 uppercase">After</span>
                    <p className="text-body-sm text-on-surface-variant mt-1 font-medium">Implemented Docker containerization for scalable microservices, improving deployment speed by 40%.</p>
                  </div>
                </div>
              </div>
            </section>
          </div>
          {/* COLUMN 3: Workspace (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-lg">
            <section className="bg-surface-container-lowest border border-outline-variant rounded-xl flex flex-col h-full overflow-hidden">
              <div className="p-md border-b border-outline-variant flex items-center justify-between">
                <h3 className="font-label-md text-label-md text-primary uppercase tracking-wider">Tailored Resume Generator</h3>
                <button className="text-primary hover:text-primary-container p-1"><span className="material-symbols-outlined">fullscreen</span></button>
              </div>
              {/* Resume Preview */}
              <div className="flex-1 bg-surface-container-low p-md overflow-hidden relative group">
                <div className="h-full w-full bg-white shadow-lg border border-outline-variant/30 p-lg custom-scrollbar overflow-y-auto">
                  <div className="w-full h-4 bg-primary/10 rounded mb-4"></div>
                  <div className="w-2/3 h-4 bg-primary/10 rounded mb-8"></div>
                  <div className="space-y-4">
                    <div className="h-2 w-full bg-on-surface-variant/10 rounded"></div>
                    <div className="h-2 w-5/6 bg-on-surface-variant/10 rounded"></div>
                    <div className="h-2 w-full bg-on-surface-variant/10 rounded"></div>
                    <div className="h-2 w-4/6 bg-on-surface-variant/10 rounded"></div>
                  </div>
                  <div className="mt-8 pt-8 border-t border-outline-variant/20">
                    <div className="h-4 w-1/4 bg-primary/10 rounded mb-4"></div>
                    <div className="h-2 w-full bg-on-surface-variant/10 rounded mb-2"></div>
                    <div className="h-2 w-full bg-on-surface-variant/10 rounded mb-2"></div>
                    <div className="h-2 w-2/3 bg-on-surface-variant/10 rounded"></div>
                  </div>
                  <div className="mt-8">
                    <div className="h-4 w-1/4 bg-primary/10 rounded mb-4"></div>
                    <div className="flex flex-wrap gap-2">
                      <div className="h-6 w-12 bg-surface-container rounded-full"></div>
                      <div className="h-6 w-16 bg-surface-container rounded-full"></div>
                      <div className="h-6 w-14 bg-surface-container rounded-full"></div>
                    </div>
                  </div>
                </div>
                <div className="absolute inset-0 bg-surface-container-low/40 backdrop-blur-[2px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="bg-white px-4 py-2 rounded-lg shadow-xl border border-outline-variant font-label-md text-primary flex items-center gap-2">
                    <span className="material-symbols-outlined">edit</span> Edit Resume
                  </button>
                </div>
              </div>
              {/* Workspace Controls */}
              <div className="p-lg bg-surface border-t border-outline-variant space-y-4">
                <div>
                  <label className="text-label-sm font-bold text-outline uppercase mb-2 block">Resume Focus</label>
                  <select className="w-full bg-white border border-outline-variant rounded-lg px-4 py-2.5 text-body-sm focus:ring-2 focus:ring-primary/20 outline-none appearance-none cursor-pointer">
                    <option>Balanced (Recommended)</option>
                    <option>Skills-Heavy</option>
                    <option>Projects-Focused</option>
                    <option>Leadership &amp; Strategy</option>
                  </select>
                </div>
                <button className="w-full bg-primary text-on-primary py-3 rounded-lg font-label-md hover:bg-primary-container transition-all flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined">bolt</span> Generate Tailored Resume
                </button>
                <p className="text-[11px] text-center text-on-surface-variant/60">Takes ~15 seconds to rebuild with AI</p>
              </div>
            </section>
          </div>
        </div>
      </div>
      {/* FLOATING PANEL: Application Checklist */}
      <div className="fixed bottom-xl right-xl w-72 glass-panel rounded-xl shadow-2xl overflow-hidden transition-transform hover:-translate-y-1">
        <div className="bg-primary px-lg py-3 flex items-center justify-between">
          <span className="text-on-primary font-bold text-label-md flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">checklist</span>
            Application Checklist
          </span>
          <span className="bg-on-primary/20 text-on-primary px-2 py-0.5 rounded text-[10px] font-bold">3/5</span>
        </div>
        <div className="p-lg space-y-3">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input checked="" className="w-4 h-4 rounded border-outline text-primary focus:ring-primary/20" type="checkbox" />
            <span className="text-body-sm text-on-surface-variant group-hover:text-on-surface transition-colors">Resume Uploaded</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input checked="" className="w-4 h-4 rounded border-outline text-primary focus:ring-primary/20" type="checkbox" />
            <span className="text-body-sm text-on-surface-variant group-hover:text-on-surface transition-colors">Job Selected</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input checked="" className="w-4 h-4 rounded border-outline text-primary focus:ring-primary/20" type="checkbox" />
            <span className="text-body-sm text-on-surface-variant group-hover:text-on-surface transition-colors">Match Score Generated</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input className="w-4 h-4 rounded border-outline text-primary focus:ring-primary/20" type="checkbox" />
            <span className="text-body-sm text-on-surface-variant group-hover:text-on-surface transition-colors">Resume Tailored</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer group">
            <input className="w-4 h-4 rounded border-outline text-primary focus:ring-primary/20" type="checkbox" />
            <span className="text-body-sm text-on-surface-variant group-hover:text-on-surface transition-colors">Apply on Portal</span>
          </label>
        </div>
        <div className="px-lg pb-lg">
          <button className="w-full py-2 bg-surface-container-high text-primary font-bold text-[11px] rounded-lg border border-primary/10 hover:bg-surface-container transition-all">VIEW NEXT STEPS</button>
        </div>
      </div>
    </>
  );
}

export default JobDetail;