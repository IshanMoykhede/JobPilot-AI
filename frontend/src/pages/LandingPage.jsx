import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from '../components/Header';
import Footer from '../components/Footer';

function LandingPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user && !loading) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, loading, navigate]);

  return (
    <>
      <Header />
      <main>
{/* Hero Section */}
<section className="hero-gradient pt-2xl pb-3xl px-margin">
<div className="max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-2xl">
<div className="lg:w-1/2 text-center lg:text-left">
<h1 className="font-headline-xl text-headline-xl text-on-background mb-md leading-tight">
                        Find Jobs Faster. <span className="text-primary">Generate Tailored Resumes.</span> Increase Your Interview Chances.
                    </h1>
<p className="font-body-lg text-body-lg text-on-surface-variant mb-xl max-w-xl mx-auto lg:mx-0">
                        Upload your resume, discover matching jobs, identify missing skills, and generate job-specific resumes in seconds.
                    </p>
<div className="flex flex-col sm:flex-row gap-md justify-center lg:justify-start">
<Link to="/auth?mode=signup" className="inline-block text-center bg-primary text-white font-label-md text-label-md px-2xl py-md rounded-lg shadow-lg hover:shadow-xl transition-all scale-100 hover:scale-[1.02] active:scale-95">Get Started</Link>
<Link to="/auth?mode=signup" className="inline-block text-center bg-white border border-outline-variant text-on-surface font-label-md text-label-md px-2xl py-md rounded-lg hover:bg-surface-container transition-colors">Upload Resume</Link>
</div>
</div>
<div className="lg:w-1/2 relative">
<div className="rounded-xl overflow-hidden shadow-2xl border border-outline-variant bg-white">
<img alt="JobPilot AI Dashboard Mockup" className="w-full h-auto" data-alt="A high-fidelity software dashboard interface displayed on a clean white background. The interface features a left-hand navigation sidebar, a central job search results table with company logos, job titles, and a circular progress bar showing match scores. The overall aesthetic is professional, minimalist, and uses a light mode color palette of soft blues, grays, and whites, reflecting a modern recruitment technology platform." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBVAL-IaGIrRDzqRTDPHuxZpFg81cJnmxfuthOfOXgdOsv2dfU7J9Ix0z0j2gmqzZE1WFXl0Q5JKZLIm5bKlvPtWxGaDCoZ8AF2S2VIT_PN-qcG-hIPHzkVI_blrtYAR4i-RuLN_aSCILHoY3zXNgok-yQG5kaFviu3gEOYu2SKubxba3h1A83OodLpM3VQ93KLGLXoHE0pd9l7iwRWEMrzFNwnpy8urNGz99vKrw0qGkfva3ojXWGaYjM0S2-p_kNqZKAdtJPZyb9m" />
</div>
{/* Decorative Element */}
<div className="absolute -z-10 -top-12 -right-12 w-64 h-64 bg-primary-container opacity-10 rounded-full blur-3xl"></div>
</div>
</div>
</section>
{/* Features Section */}
<section className="py-3xl px-margin bg-white" id="features">
<div className="max-w-7xl mx-auto">
<div className="text-center mb-2xl">
<h2 className="font-headline-lg text-headline-lg text-on-surface mb-md">Everything You Need For Smarter Job Applications</h2>
<div className="h-1.5 w-20 bg-primary mx-auto rounded-full"></div>
</div>
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-lg">
{/* Feature 1 */}
<div className="bento-card p-xl bg-surface-container-low rounded-xl border border-outline-variant hover:border-primary transition-colors">
<div className="w-12 h-12 bg-primary-container rounded-lg flex items-center justify-center mb-md text-on-primary-fixed">
<span className="material-symbols-outlined">search</span>
</div>
<h3 className="font-headline-sm text-headline-sm mb-xs">AI Job Search</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">Search jobs using natural language queries such as "DevOps Engineer in Pune" or "Frontend Developer Remote".</p>
</div>
{/* Feature 2 */}
<div className="bento-card p-xl bg-surface-container-low rounded-xl border border-outline-variant hover:border-primary transition-colors">
<div className="w-12 h-12 bg-primary-container rounded-lg flex items-center justify-center mb-md text-on-primary-fixed">
<span className="material-symbols-outlined">target</span>
</div>
<h3 className="font-headline-sm text-headline-sm mb-xs">Resume Matching</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">Compare your resume against job requirements and receive an AI-generated match score.</p>
</div>
{/* Feature 3 */}
<div className="bento-card p-xl bg-surface-container-low rounded-xl border border-outline-variant hover:border-primary transition-colors">
<div className="w-12 h-12 bg-primary-container rounded-lg flex items-center justify-center mb-md text-on-primary-fixed">
<span className="material-symbols-outlined">bar_chart</span>
</div>
<h3 className="font-headline-sm text-headline-sm mb-xs">Skill Gap Analysis</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">Identify missing skills and understand what employers are looking for in top candidates.</p>
</div>
{/* Feature 4 */}
<div className="bento-card p-xl bg-surface-container-low rounded-xl border border-outline-variant hover:border-primary transition-colors">
<div className="w-12 h-12 bg-primary-container rounded-lg flex items-center justify-center mb-md text-on-primary-fixed">
<span className="material-symbols-outlined">description</span>
</div>
<h3 className="font-headline-sm text-headline-sm mb-xs">Resume Tailoring</h3>
<p className="font-body-sm text-body-sm text-on-surface-variant">Generate job-specific resumes perfectly aligned with each unique job description.</p>
</div>
</div>
</div>
</section>
{/* How It Works */}
<section className="py-3xl px-margin bg-surface-container" id="how-it-works">
<div className="max-w-7xl mx-auto">
<div className="text-center mb-2xl">
<h2 className="font-headline-lg text-headline-lg text-on-surface">How JobPilot AI Works</h2>
</div>
<div className="flex flex-col md:flex-row justify-between items-start gap-xl relative">
{/* Step 1 */}
<div className="flex-1 text-center group">
<div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-md border-2 border-primary text-primary font-bold text-xl shadow-md group-hover:scale-110 transition-transform">1</div>
<h4 className="font-label-md text-label-md font-bold mb-xs">Upload Resume</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">Start by importing your current professional profile.</p>
</div>
<div className="hidden md:block w-px h-16 bg-outline-variant mt-8 opacity-50"></div>
{/* Step 2 */}
<div className="flex-1 text-center group">
<div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-md border-2 border-primary text-primary font-bold text-xl shadow-md group-hover:scale-110 transition-transform">2</div>
<h4 className="font-label-md text-label-md font-bold mb-xs">Search Jobs</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">Find the perfect roles using our intelligent search engine.</p>
</div>
<div className="hidden md:block w-px h-16 bg-outline-variant mt-8 opacity-50"></div>
{/* Step 3 */}
<div className="flex-1 text-center group">
<div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-md border-2 border-primary text-primary font-bold text-xl shadow-md group-hover:scale-110 transition-transform">3</div>
<h4 className="font-label-md text-label-md font-bold mb-xs">Get Match Scores</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">See exactly how well you fit every job requirement instantly.</p>
</div>
<div className="hidden md:block w-px h-16 bg-outline-variant mt-8 opacity-50"></div>
{/* Step 4 */}
<div className="flex-1 text-center group">
<div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-md border-2 border-primary text-primary font-bold text-xl shadow-md group-hover:scale-110 transition-transform">4</div>
<h4 className="font-label-md text-label-md font-bold mb-xs">Generate Tailored Resume</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">One-click optimization for your best application ever.</p>
</div>
</div>
</div>
</section>
{/* Benefits Section */}
<section className="py-3xl px-margin">
<div className="max-w-7xl mx-auto">
<div className="text-center mb-2xl">
<h2 className="font-headline-lg text-headline-lg text-on-surface">Apply Smarter, Not Harder</h2>
</div>
<div className="grid grid-cols-1 lg:grid-cols-3 gap-xl">
<div className="p-xl bg-white rounded-xl border border-outline-variant flex gap-md">
<div className="text-primary"><span className="material-symbols-outlined text-4xl">rocket_launch</span></div>
<div>
<h4 className="font-headline-sm text-headline-sm mb-xs">Find Relevant Opportunities</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">Stop wasting time on jobs that don't match your background. Our AI filters through the noise to bring you high-intent roles.</p>
</div>
</div>
<div className="p-xl bg-white rounded-xl border border-outline-variant flex gap-md">
<div className="text-primary"><span className="material-symbols-outlined text-4xl">lightbulb</span></div>
<div>
<h4 className="font-headline-sm text-headline-sm mb-xs">Understand Skill Gaps</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">Get actionable insights into what skills you need to develop to land your dream role in today's competitive market.</p>
</div>
</div>
<div className="p-xl bg-white rounded-xl border border-outline-variant flex gap-md">
<div className="text-primary"><span className="material-symbols-outlined text-4xl">verified</span></div>
<div>
<h4 className="font-headline-sm text-headline-sm mb-xs">Improve Application Quality</h4>
<p className="font-body-sm text-body-sm text-on-surface-variant">Increase your response rate by presenting a resume that speaks the employer's language and highlights exactly what they need.</p>
</div>
</div>
</div>
</div>
</section>
{/* Final CTA Section */}
<section className="py-3xl px-margin">
<div className="max-w-4xl mx-auto bg-primary rounded-3xl p-2xl text-center text-white relative overflow-hidden">
{/* Abstract Background Ornament */}
<div className="absolute -bottom-12 -left-12 w-48 h-48 bg-white opacity-10 rounded-full"></div>
<div className="absolute -top-12 -right-12 w-48 h-48 bg-white opacity-10 rounded-full"></div>
<h2 className="font-headline-xl text-headline-xl mb-md">Ready to Find Your Next Opportunity?</h2>
<p className="font-body-lg text-body-lg mb-2xl opacity-90">Start searching jobs and generating tailored resumes today.</p>
<div className="flex flex-col sm:flex-row gap-md justify-center items-center">
<Link to="/auth?mode=signup" className="inline-block text-center bg-white text-primary font-label-md text-label-md px-2xl py-md rounded-lg hover:bg-surface-container-highest transition-colors w-full sm:w-auto">Get Started</Link>
<Link to="/auth?mode=login" className="inline-block text-center bg-transparent border border-white text-white font-label-md text-label-md px-2xl py-md rounded-lg hover:bg-white hover:text-primary transition-all w-full sm:w-auto">Login</Link>
</div>
</div>
</section>
</main>
{/* Footer */}
      <Footer />
    </>
  );
}

export default LandingPage;
