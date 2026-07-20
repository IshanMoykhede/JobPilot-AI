import React, { useState } from 'react';
import AppShell from '../components/layout/AppShell';
import Icon from '../components/common/Icon';
import { testSerp } from '../services/agentApi';

export default function Testing() {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleTest = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await testSerp(query, location);
      setResults(data);
    } catch (err) {
      setError(err.message || 'An error occurred during testing.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell breadcrumbs={[
      { label: 'Dashboard', href: '/dashboard' },
      { label: 'API Testing', href: '/testing' }
    ]}>
      <div className="max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="mb-10 flex flex-col items-center text-center">
          <div className="w-16 h-16 rounded-2xl bg-jp-accent/10 flex items-center justify-center mb-6 ring-1 ring-jp-accent/20">
            <Icon name="science" className="text-3xl text-jp-accent" />
          </div>
          <h1 className="text-3xl font-bold text-jp-text-primary">SerpAPI Integration Test</h1>
          <p className="mt-3 text-jp-text-secondary max-w-xl">
            Directly test the raw connection to Google Jobs via SerpAPI. This bypasses the LLM orchestrator and returns exactly what Google returns.
          </p>
        </div>

        <div className="bg-jp-bg-surface border border-jp-border rounded-2xl shadow-xl overflow-hidden mb-8">
          <div className="p-6 border-b border-jp-border-subtle bg-jp-bg-raised">
            <form onSubmit={handleTest} className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-[13px] font-semibold text-jp-text-secondary mb-1.5 uppercase tracking-wider">Search Query</label>
                <div className="relative">
                  <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-jp-text-tertiary" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g. Frontend Developer"
                    className="w-full bg-jp-bg-surface border border-jp-border rounded-xl pl-10 pr-4 py-3 text-jp-text-primary focus:border-jp-accent focus:ring-1 focus:ring-jp-accent transition-all outline-none"
                    required
                  />
                </div>
              </div>
              
              <div className="flex-1 md:max-w-xs">
                <label className="block text-[13px] font-semibold text-jp-text-secondary mb-1.5 uppercase tracking-wider">Location (Optional)</label>
                <div className="relative">
                  <Icon name="place" className="absolute left-3 top-1/2 -translate-y-1/2 text-jp-text-tertiary" />
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. New York, Remote"
                    className="w-full bg-jp-bg-surface border border-jp-border rounded-xl pl-10 pr-4 py-3 text-jp-text-primary focus:border-jp-accent focus:ring-1 focus:ring-jp-accent transition-all outline-none"
                  />
                </div>
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={isLoading || !query.trim()}
                  className="w-full md:w-auto jp-btn jp-btn-primary h-[48px] px-8 rounded-xl font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Icon name="refresh" className="animate-spin text-[20px]" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <Icon name="send" className="text-[20px]" />
                      Send Request
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {error && (
            <div className="p-6 bg-red-500/10 border-b border-red-500/20">
              <div className="flex items-center gap-3 text-red-400">
                <Icon name="error" className="text-xl" />
                <span className="font-medium">{error}</span>
              </div>
            </div>
          )}

          {results && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-jp-text-primary flex items-center gap-2">
                  <Icon name="data_object" className="text-jp-accent" />
                  Validation Results
                </h3>
                <span className="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded-full text-xs font-bold uppercase tracking-wider">
                  {results.jobs_count || 0} Jobs Found
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="p-4 bg-jp-bg-surface border border-jp-border-subtle rounded-xl">
                  <div className="text-[11px] font-bold text-jp-text-tertiary uppercase tracking-wider mb-1">Original Query</div>
                  <div className="text-jp-text-primary text-[15px]">{results.original_query}</div>
                </div>
                
                <div className="p-4 bg-jp-bg-surface border border-jp-border-subtle rounded-xl flex gap-4">
                  <div className="flex-1">
                    <div className="text-[11px] font-bold text-jp-text-tertiary uppercase tracking-wider mb-1">Parsed Role</div>
                    <div className="text-jp-accent font-semibold text-[15px]">{results.parsed_role || <span className="opacity-50 italic">null</span>}</div>
                  </div>
                  <div className="flex-1 border-l border-jp-border-subtle pl-4">
                    <div className="text-[11px] font-bold text-jp-text-tertiary uppercase tracking-wider mb-1">Parsed Location</div>
                    <div className="text-jp-accent font-semibold text-[15px]">{results.parsed_location || <span className="opacity-50 italic">null</span>}</div>
                  </div>
                </div>
                
                <div className="md:col-span-2 p-4 bg-jp-bg-surface border border-jp-border-subtle rounded-xl">
                  <div className="text-[11px] font-bold text-jp-text-tertiary uppercase tracking-wider mb-1">Exact SerpAPI Request Parameters</div>
                  <div className="font-mono text-[13px] text-jp-text-secondary bg-black/20 p-2 rounded-lg mt-1 border border-white/5">
                    <span className="text-blue-400">q:</span> "{results.serp_params?.q}" <span className="text-blue-400 ml-4">location:</span> "{results.serp_params?.location}"
                  </div>
                </div>
              </div>

              <div className="bg-[#0D1117] rounded-xl overflow-hidden border border-jp-border-subtle shadow-inner">
                <div className="flex items-center gap-2 px-4 py-2 bg-[#161B22] border-b border-jp-border-subtle">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="ml-2 text-[12px] font-mono text-jp-text-tertiary">sample_jobs.json</span>
                </div>
                <div className="p-4 overflow-x-auto max-h-[600px] overflow-y-auto custom-scrollbar">
                  <pre className="text-[13px] font-mono text-jp-text-secondary leading-relaxed">
                    {JSON.stringify(results.jobs, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          )}
          
          {!results && !error && !isLoading && (
            <div className="p-16 flex flex-col items-center justify-center text-center">
              <Icon name="api" className="text-5xl text-jp-text-muted mb-4 opacity-50" />
              <p className="text-jp-text-tertiary">Enter a query above to see the raw API output.</p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
