import React from 'react';
import Header from '../components/Header';

function Resumes() {
  return (
    <>
      <Header />
      {/* Main Content Area */}
<main className="ml-64 mt-16 p-gutter min-h-screen">
<div className="max-w-[1600px] mx-auto flex flex-col lg:flex-row gap-gutter">
{/* Main Grid & Filters */}
<div className="flex-1 space-y-gutter">
{/* Filter Bar */}
<section className="bg-surface-container-lowest p-md rounded-xl border border-outline-variant shadow-sm flex flex-wrap items-center gap-md">
<div className="flex-1 min-w-[240px] relative">
<span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline" data-icon="search">search</span>
<input className="w-full pl-10 pr-4 py-2 bg-surface border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none text-body-md" placeholder="Search resumes..." type="text"/>
</div>
<div className="flex items-center gap-sm">
<select className="bg-surface border border-outline-variant rounded-lg px-3 py-2 text-label-md outline-none focus:border-primary">
<option>All Dates</option>
<option>Today</option>
<option>This Week</option>
</select>
<select className="bg-surface border border-outline-variant rounded-lg px-3 py-2 text-label-md outline-none focus:border-primary">
<option>Role: All</option>
<option>DevOps</option>
<option>Backend</option>
<option>Frontend</option>
</select>
<select className="bg-surface border border-outline-variant rounded-lg px-3 py-2 text-label-md outline-none focus:border-primary">
<option>Sort: Match Score</option>
<option>Sort: Newest</option>
<option>Sort: Oldest</option>
</select>
</div>
</section>
{/* Resume Grid */}
<section className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-gutter">
{/* Resume Card 1 */}
<div className="resume-card group bg-surface-container-lowest border border-outline-variant rounded-xl p-lg relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-primary/30">
<div className="flex justify-between items-start mb-md">
<div className="h-12 w-12 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
<span className="material-symbols-outlined" data-icon="terminal">terminal</span>
</div>
<span className="bg-surface-variant text-primary px-2 py-1 rounded text-label-sm font-bold">v1.2</span>
</div>
<div className="mb-lg">
<h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">Senior DevOps Engineer</h3>
<p className="text-on-surface-variant text-body-md">Infosys • Global Services</p>
<p className="text-outline text-label-sm mt-md flex items-center gap-1">
<span className="material-symbols-outlined text-[16px]" data-icon="schedule">schedule</span>
                                Generated Today
                            </p>
</div>
<div className="flex items-center justify-between pt-lg border-t border-outline-variant">
<div className="flex items-center gap-3">
<div className="relative w-12 h-12">
<svg className="w-full h-full" viewbox="0 0 36 36">
<path className="text-outline-variant" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="100, 100" strokeWidth="3"></path>
<path className="text-primary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="89, 100" strokeLinecap="round" strokeWidth="3"></path>
</svg>
<span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-on-surface">89%</span>
</div>
<span className="text-label-sm text-on-surface-variant">Match Score</span>
</div>
<div className="flex gap-1">
<button className="p-2 hover:bg-primary-fixed rounded-lg text-primary transition-colors" title="Download PDF">
<span className="material-symbols-outlined" data-icon="download">download</span>
</button>
<button className="p-2 hover:bg-surface-variant rounded-lg text-on-surface-variant transition-colors" title="More options">
<span className="material-symbols-outlined" data-icon="more_vert">more_vert</span>
</button>
</div>
</div>
{/* Hover Action Overlay */}
<div className="action-overlay absolute inset-0 bg-primary/5 opacity-0 pointer-events-none transition-opacity duration-300"></div>
</div>
{/* Resume Card 2 */}
<div className="resume-card group bg-surface-container-lowest border border-outline-variant rounded-xl p-lg relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-primary/30">
<div className="flex justify-between items-start mb-md">
<div className="h-12 w-12 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
<span className="material-symbols-outlined" data-icon="code">code</span>
</div>
<span className="bg-surface-variant text-primary px-2 py-1 rounded text-label-sm font-bold">v1.0</span>
</div>
<div className="mb-lg">
<h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">Lead Backend Architect</h3>
<p className="text-on-surface-variant text-body-md">Google Cloud Platform</p>
<p className="text-outline text-label-sm mt-md flex items-center gap-1">
<span className="material-symbols-outlined text-[16px]" data-icon="schedule">schedule</span>
                                2 days ago
                            </p>
</div>
<div className="flex items-center justify-between pt-lg border-t border-outline-variant">
<div className="flex items-center gap-3">
<div className="relative w-12 h-12">
<svg className="w-full h-full" viewbox="0 0 36 36">
<path className="text-outline-variant" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="100, 100" strokeWidth="3"></path>
<path className="text-primary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="94, 100" strokeLinecap="round" strokeWidth="3"></path>
</svg>
<span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-on-surface">94%</span>
</div>
<span className="text-label-sm text-on-surface-variant">Match Score</span>
</div>
<div className="flex gap-1">
<button className="p-2 hover:bg-primary-fixed rounded-lg text-primary transition-colors">
<span className="material-symbols-outlined" data-icon="download">download</span>
</button>
<button className="p-2 hover:bg-surface-variant rounded-lg text-on-surface-variant transition-colors">
<span className="material-symbols-outlined" data-icon="more_vert">more_vert</span>
</button>
</div>
</div>
</div>
{/* Resume Card 3 */}
<div className="resume-card group bg-surface-container-lowest border border-outline-variant rounded-xl p-lg relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-primary/30">
<div className="flex justify-between items-start mb-md">
<div className="h-12 w-12 rounded-lg bg-surface-container-high flex items-center justify-center text-primary">
<span className="material-symbols-outlined" data-icon="brush">brush</span>
</div>
<span className="bg-surface-variant text-primary px-2 py-1 rounded text-label-sm font-bold">v2.1</span>
</div>
<div className="mb-lg">
<h3 className="font-headline-sm text-headline-sm text-on-surface mb-1">Senior UX Designer</h3>
<p className="text-on-surface-variant text-body-md">Stripe • Design Systems</p>
<p className="text-outline text-label-sm mt-md flex items-center gap-1">
<span className="material-symbols-outlined text-[16px]" data-icon="schedule">schedule</span>
                                1 week ago
                            </p>
</div>
<div className="flex items-center justify-between pt-lg border-t border-outline-variant">
<div className="flex items-center gap-3">
<div className="relative w-12 h-12">
<svg className="w-full h-full" viewbox="0 0 36 36">
<path className="text-outline-variant" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="100, 100" strokeWidth="3"></path>
<path className="text-primary" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeDasharray="82, 100" strokeLinecap="round" strokeWidth="3"></path>
</svg>
<span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-on-surface">82%</span>
</div>
<span className="text-label-sm text-on-surface-variant">Match Score</span>
</div>
<div className="flex gap-1">
<button className="p-2 hover:bg-primary-fixed rounded-lg text-primary transition-colors">
<span className="material-symbols-outlined" data-icon="download">download</span>
</button>
<button className="p-2 hover:bg-surface-variant rounded-lg text-on-surface-variant transition-colors">
<span className="material-symbols-outlined" data-icon="more_vert">more_vert</span>
</button>
</div>
</div>
</div>
{/* Empty/New Card Placeholder */}
<button className="flex flex-col items-center justify-center border-2 border-dashed border-outline-variant rounded-xl p-lg hover:border-primary hover:bg-primary-fixed/30 transition-all group">
<span className="material-symbols-outlined text-4xl text-outline group-hover:text-primary transition-colors" data-icon="add_circle">add_circle</span>
<span className="mt-md font-headline-sm text-headline-sm text-on-surface-variant group-hover:text-primary transition-colors">Generate New</span>
</button>
</section>
</div>
{/* Right Panel: Statistics */}
<aside className="w-full lg:w-[320px] space-y-gutter">
{/* Resume Statistics Card */}
<section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
<h3 className="font-headline-sm text-headline-sm text-on-surface mb-lg flex items-center gap-2">
<span className="material-symbols-outlined text-primary" data-icon="analytics">analytics</span>
                        Resume Statistics
                    </h3>
<div className="space-y-md">
<div className="flex justify-between items-center">
<span className="text-body-md text-on-surface-variant">Total Resumes</span>
<span className="font-bold text-headline-sm text-on-surface">15</span>
</div>
<div className="flex justify-between items-center">
<span className="text-body-md text-on-surface-variant">Most Targeted</span>
<span className="bg-tertiary-fixed text-on-tertiary-fixed px-2 py-1 rounded text-label-sm font-bold">DevOps</span>
</div>
<div className="flex justify-between items-center">
<span className="text-body-md text-on-surface-variant">Last Generated</span>
<span className="text-label-md font-medium">Today</span>
</div>
</div>
<div className="mt-lg pt-lg border-t border-outline-variant">
<div className="h-2 w-full bg-surface-container rounded-full overflow-hidden">
<div className="h-full bg-primary rounded-full" style={{width: "65%"}}></div>
</div>
<p className="text-label-sm text-outline mt-2">Storage: 6.5 MB of 10 MB used</p>
</div>
</section>
{/* Recent Activity */}
<section className="bg-surface-container-lowest border border-outline-variant rounded-xl p-lg shadow-sm">
<h3 className="font-headline-sm text-headline-sm text-on-surface mb-lg">Recent Activity</h3>
<ul className="space-y-lg">
<li className="flex gap-md">
<div className="w-2 h-2 mt-2 rounded-full bg-primary flex-shrink-0"></div>
<div>
<p className="text-body-md text-on-surface font-medium leading-tight">DevOps Resume updated</p>
<p className="text-label-sm text-outline">14 mins ago</p>
</div>
</li>
<li className="flex gap-md">
<div className="w-2 h-2 mt-2 rounded-full bg-secondary flex-shrink-0"></div>
<div>
<p className="text-body-md text-on-surface font-medium leading-tight">PDF Exported: Google Cloud</p>
<p className="text-label-sm text-outline">2 hours ago</p>
</div>
</li>
<li className="flex gap-md">
<div className="w-2 h-2 mt-2 rounded-full bg-tertiary flex-shrink-0"></div>
<div>
<p className="text-body-md text-on-surface font-medium leading-tight">Shared with 3 recruiters</p>
<p className="text-label-sm text-outline">Yesterday</p>
</div>
</li>
</ul>
<button className="w-full mt-lg text-primary font-label-md hover:underline flex items-center justify-center gap-1">
                        View full history
                        <span className="material-symbols-outlined text-[18px]" data-icon="chevron_right">chevron_right</span>
</button>
</section>
{/* AI Tips Card */}
<section className="bg-primary-container p-lg rounded-xl text-on-primary-container relative overflow-hidden">
<div className="relative z-10">
<h4 className="font-headline-sm text-headline-sm mb-2 flex items-center gap-2">
<span className="material-symbols-outlined" data-icon="lightbulb">lightbulb</span>
                            AI Suggestion
                        </h4>
<p className="text-body-md opacity-90 mb-lg">Try targeting "Cloud Infrastructure" keywords to increase your DevOps match score by 12%.</p>
<button className="bg-on-primary-container text-primary-container px-md py-sm rounded-lg font-bold text-label-md hover:bg-on-primary-container/90 transition-colors">Apply Optimizations</button>
</div>
{/* Decorative Abstract Shapes */}
<div className="absolute -right-4 -bottom-4 w-24 h-24 bg-on-primary-container/10 rounded-full blur-2xl"></div>
</section>
</aside>
</div>
</main>
{/* Floating Action Button for Mobile / Quick Action */}
<button className="fixed bottom-gutter right-gutter h-14 w-14 bg-primary text-on-primary rounded-full shadow-2xl flex items-center justify-center group hover:scale-110 transition-all md:hidden z-50">
<span className="material-symbols-outlined" data-icon="add">add</span>
</button>
    </>
  );
}

export default Resumes;
