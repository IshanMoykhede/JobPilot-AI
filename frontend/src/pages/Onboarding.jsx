import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';

function Onboarding() {
  return (
    <>
      <Header />
      {/* Main Content Canvas */}
<main className="pt-24 pb-20 px-gutter max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-gutter">
{/* Left/Main Column */}
<div className="lg:col-span-8 space-y-xl">
{/* Success Banner (Conditional State) */}
<div className="bg-tertiary-container text-on-tertiary-container px-lg py-md rounded-lg flex items-center gap-md animate-in fade-in slide-in-from-top-4 duration-500" id="success-banner">
<span className="material-symbols-outlined">check_circle</span>
<span className="font-label-md">Resume analyzed successfully. Your profile is ready.</span>
</div>
{/* Onboarding Header */}
<div className="text-center md:text-left">
<div className="inline-flex items-center gap-xs px-md py-base bg-primary-container text-on-primary-container rounded-full font-label-sm mb-md">
<span className="w-2 h-2 rounded-full bg-on-primary-container"></span>
                    Step 1 of 1
                </div>
<h1 className="font-headline-xl text-headline-xl text-on-surface mb-xs">Let's Build Your Job Profile</h1>
<p className="text-body-lg text-on-surface-variant max-w-2xl">Upload your resume and we'll automatically extract your skills and experience to personalize job recommendations.</p>
</div>
{/* Profile Preview Section (Main Content) */}
<div className="grid grid-cols-1 gap-gutter">
{/* Candidate Summary Card */}
<section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-xl shadow-sm">
<div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-md mb-xl">
<div className="flex items-center gap-md">
<div className="w-16 h-16 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
<span className="material-symbols-outlined text-4xl">person_search</span>
</div>
<div>
<h2 className="font-headline-md text-headline-md">Alex Chen</h2>
<p className="text-on-surface-variant">alex.chen@example.com • 5 years exp.</p>
</div>
</div>
<div className="flex flex-col items-end">
<div className="text-label-sm text-outline mb-base">Profile Strength</div>
<div className="flex items-center gap-md">
<div className="w-32 h-2 bg-surface-container-high rounded-full overflow-hidden">
<div className="h-full bg-primary w-[85%]"></div>
</div>
<span className="font-bold text-primary">85%</span>
</div>
</div>
</div>
<div className="space-y-xl">
{/* Detected Skills */}
<div>
<h3 className="font-label-md text-on-surface mb-md flex items-center gap-xs">
<span className="material-symbols-outlined text-sm">bolt</span> Skills Detected
                            </h3>
<div className="flex flex-wrap gap-xs">
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">React</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">Node.js</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">AWS</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">Docker</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">Kubernetes</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">Python</span>
<span className="px-md py-base bg-surface-container-high text-on-surface-variant rounded-md font-label-sm border border-outline-variant/30">SQL</span>
</div>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 gap-xl">
{/* Education */}
<div>
<h3 className="font-label-md text-on-surface mb-md flex items-center gap-xs">
<span className="material-symbols-outlined text-sm">school</span> Education
                                </h3>
<div className="p-md bg-surface-container-low rounded-lg border border-outline-variant/20">
<div className="font-headline-sm text-sm">BS in Computer Science</div>
<div className="text-body-sm text-on-surface-variant">State University • 2019</div>
</div>
</div>
{/* Current Role */}
<div>
<h3 className="font-label-md text-on-surface mb-md flex items-center gap-xs">
<span className="material-symbols-outlined text-sm">work</span> Experience
                                </h3>
<div className="p-md bg-surface-container-low rounded-lg border border-outline-variant/20">
<div className="font-headline-sm text-sm">Senior Frontend Engineer</div>
<div className="text-body-sm text-on-surface-variant">Current Position</div>
</div>
</div>
</div>
{/* Projects */}
<div>
<h3 className="font-label-md text-on-surface mb-md flex items-center gap-xs">
<span className="material-symbols-outlined text-sm">folder_open</span> Featured Projects
                            </h3>
<div className="grid grid-cols-1 md:grid-cols-3 gap-md">
<div className="p-md border border-outline-variant rounded-lg hover:bg-surface-container-low transition-colors cursor-pointer">
<div className="font-label-md mb-xs">E-commerce Platform</div>
<div className="text-xs text-on-surface-variant line-clamp-2">Built a high-scale React marketplace.</div>
</div>
<div className="p-md border border-outline-variant rounded-lg hover:bg-surface-container-low transition-colors cursor-pointer">
<div className="font-label-md mb-xs">Open Source CLI</div>
<div className="text-xs text-on-surface-variant line-clamp-2">Node.js automation tool with 1k+ stars.</div>
</div>
<div className="p-md border border-outline-variant rounded-lg hover:bg-surface-container-low transition-colors cursor-pointer">
<div className="font-label-md mb-xs">Cloud Migration</div>
<div className="text-xs text-on-surface-variant line-clamp-2">Led AWS migration for legacy systems.</div>
</div>
</div>
</div>
</div>
</section>
{/* AI Suggestions Bento Grid */}
<section className="grid grid-cols-1 md:grid-cols-2 gap-md">
<div className="ai-gradient-border p-md flex items-center gap-md border border-transparent shadow-sm">
<div className="w-10 h-10 rounded-full bg-primary-container/10 flex items-center justify-center text-primary">
<span className="material-symbols-outlined">auto_awesome</span>
</div>
<div>
<div className="font-label-md text-primary">Add measurable project impact</div>
<div className="text-xs text-on-surface-variant">e.g., "Increased performance by 40%"</div>
</div>
</div>
<div className="ai-gradient-border p-md flex items-center gap-md border border-transparent shadow-sm">
<div className="w-10 h-10 rounded-full bg-primary-container/10 flex items-center justify-center text-primary">
<span className="material-symbols-outlined">auto_awesome</span>
</div>
<div>
<div className="font-label-md text-primary">Include deployment experience</div>
<div className="text-xs text-on-surface-variant">Add CI/CD or Jenkins details</div>
</div>
</div>
</section>
{/* Action Buttons */}
<div className="flex flex-col sm:flex-row items-center justify-center gap-md pt-xl border-t border-outline-variant/30">
<button className="w-full sm:w-auto px-2xl py-md bg-primary-container text-on-primary-container font-label-md rounded-lg shadow-md hover:opacity-90 active:scale-95 transition-all">
                        Continue To Dashboard
                    </button>
<button className="w-full sm:w-auto px-2xl py-md bg-surface border border-outline-variant text-on-surface font-label-md rounded-lg hover:bg-surface-container-low active:scale-95 transition-all">
                        Upload Different Resume
                    </button>
</div>
</div>
</div>
{/* Right Column / Sidebar */}
<aside className="lg:col-span-4 space-y-gutter">
{/* What Happens Next Card */}
<div className="bg-surface-container-low border border-outline-variant rounded-xl p-lg">
<h2 className="font-headline-sm mb-lg">What Happens Next?</h2>
<ul className="space-y-lg">
<li className="flex gap-md">
<span className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-xs shrink-0">1</span>
<div>
<div className="font-label-md">Search Jobs</div>
<p className="text-body-sm text-on-surface-variant">Browse 10k+ verified listings matched to you.</p>
</div>
</li>
<li className="flex gap-md opacity-60">
<span className="w-8 h-8 rounded-full bg-outline text-on-primary flex items-center justify-center font-bold text-xs shrink-0">2</span>
<div>
<div className="font-label-md">Get Match Scores</div>
<p className="text-body-sm text-on-surface-variant">See how well your skills align with requirements.</p>
</div>
</li>
<li className="flex gap-md opacity-60">
<span className="w-8 h-8 rounded-full bg-outline text-on-primary flex items-center justify-center font-bold text-xs shrink-0">3</span>
<div>
<div className="font-label-md">Analyze Skill Gaps</div>
<p className="text-body-sm text-on-surface-variant">Identify what you need to learn for your dream role.</p>
</div>
</li>
<li className="flex gap-md opacity-60">
<span className="w-8 h-8 rounded-full bg-outline text-on-primary flex items-center justify-center font-bold text-xs shrink-0">4</span>
<div>
<div className="font-label-md">Generate Tailored Resume</div>
<p className="text-body-sm text-on-surface-variant">Let AI customize your pitch for every application.</p>
</div>
</li>
</ul>
</div>
{/* Uploading State Card (Dynamic Mockup) */}
<div className="hidden bg-surface-container-low border border-outline-variant rounded-xl p-lg space-y-md animate-pulse" id="processing-card">
<div className="flex justify-between items-center">
<span className="font-label-md">Uploading Resume...</span>
<span className="text-primary font-bold">72%</span>
</div>
<div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
<div className="h-full bg-primary transition-all duration-300" style={{width: "72%"}}></div>
</div>
<div className="pt-md space-y-xs">
<div className="flex items-center gap-xs text-body-sm">
<span className="material-symbols-outlined text-tertiary text-sm">check_circle</span>
<span>Extracting Skills</span>
</div>
<div className="flex items-center gap-xs text-body-sm">
<span className="material-symbols-outlined text-tertiary text-sm">check_circle</span>
<span>Education Detected</span>
</div>
<div className="flex items-center gap-xs text-body-sm text-on-surface-variant">
<span className="material-symbols-outlined text-sm animate-spin">refresh</span>
<span>Analyzing Experience</span>
</div>
<div className="flex items-center gap-xs text-body-sm text-outline">
<span className="material-symbols-outlined text-sm">circle</span>
<span>Building Profile</span>
</div>
</div>
</div>
{/* Initial Upload Card (Visible initially, hidden in this "preview" layout) */}
<div className="hidden cursor-pointer group bg-surface-container-lowest border-2 border-dashed border-outline-variant rounded-xl p-3xl text-center hover:border-primary hover:bg-primary-container/5 transition-all" id="upload-card">
<div className="w-16 h-16 bg-surface-container-high rounded-full flex items-center justify-center mx-auto mb-lg group-hover:scale-110 transition-transform">
<span className="material-symbols-outlined text-3xl text-primary">upload</span>
</div>
<h3 className="font-headline-sm mb-xs">Drag and drop your resume here</h3>
<p className="text-body-sm text-on-surface-variant mb-xl">or <span className="text-primary font-bold">Browse Files</span></p>
<div className="text-label-sm text-outline">Supported: PDF, DOCX (Max 5MB)</div>
</div>
</aside>
</main>
      <Footer />
    </>
  );
}

export default Onboarding;
