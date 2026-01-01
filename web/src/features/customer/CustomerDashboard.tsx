// @ts-nocheck
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useMsal } from '@azure/msal-react';
import { getProposals, getUserProfile } from '../../api/client';

export const CustomerDashboard: React.FC = () => {
  const { instance } = useMsal();

  // Fetch user profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => getUserProfile(instance),
  });

  // Fetch proposals
  const { data: proposalsData, isLoading: proposalsLoading, error } = useQuery({
    queryKey: ['proposals'],
    queryFn: () => getProposals(instance),
  });

  const isLoading = profileLoading || proposalsLoading;

  if (isLoading) {
    return (
      <div className="p-8 bg-white min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-white min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">⚠️ Connection Error</h3>
          <p className="text-red-600 text-sm">Unable to load data from API. Please check your connection.</p>
        </div>
      </div>
    );
  }

  const proposals = proposalsData?.proposals || [];
  const activeProposals = proposals.filter(p => p.status === 'active');
  const totalProposals = proposals.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-7xl mx-auto p-8">
        <header className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">
              👋 Welcome back, {profile?.name || 'User'}
            </h1>
            <p className="text-slate-600 text-lg">Manage your Federal Proposals and AI Agents</p>
          </div>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-all shadow-md hover:shadow-lg">
            + New Proposal
          </button>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">Total Proposals</h3>
            <p className="text-4xl font-bold text-slate-900">{totalProposals}</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-emerald-600 uppercase tracking-wide mb-3">Active</h3>
            <p className="text-4xl font-bold text-slate-900">{activeProposals.length}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-3">Win Rate</h3>
            <p className="text-4xl font-bold text-slate-900">
              {totalProposals > 0 ? Math.round((activeProposals.length / totalProposals) * 100) : 0}%
            </p>
          </div>
        </div>

        {/* Proposals List */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <div className="bg-gradient-to-r from-slate-100 to-slate-50 px-6 py-4 border-b border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900">📋 Your Proposals</h2>
          </div>
          
          {proposals && proposals.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {proposals.map((proposal) => (
                <div key={proposal.id} className="px-6 py-5 hover:bg-slate-50 transition-colors cursor-pointer group">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                        {proposal.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 mb-3">
                        <span className="flex items-center gap-1.5">
                          🏢 <strong className="font-medium text-slate-700">{proposal.customer}</strong>
                        </span>
                        <span className="flex items-center gap-1.5">
                          🏛️ <strong className="font-medium text-slate-700">{proposal.agency}</strong>
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-3 text-sm">
                        <span className={`px-4 py-1.5 rounded-full font-semibold uppercase tracking-wide text-xs ${
                          proposal.status === 'active' 
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                            : proposal.status === 'pending'
                            ? 'bg-amber-100 text-amber-700 border border-amber-200'
                            : 'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}>
                          {proposal.status.charAt(0).toUpperCase() + proposal.status.slice(1)}
                        </span>
                        <span className="flex items-center gap-1.5 text-slate-600">
                          📅 Due: <strong className="font-medium text-slate-700">{new Date(proposal.dueDate).toLocaleDateString()}</strong>
                        </span>
                        <span className="flex items-center gap-1.5 font-semibold text-blue-600">
                          💰 ${proposal.value.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    
                    <button className="p-2 rounded-lg hover:bg-slate-100 transition-colors text-slate-400 hover:text-slate-600 flex-shrink-0">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <p className="text-slate-400 text-lg">No proposals yet</p>
              <p className="text-slate-500 text-sm mt-2">Create your first proposal to get started</p>
            </div>
          )}
        </div>

        {/* API Connection Status */}
        <div className="mt-8 flex items-center justify-center">
          <div className="bg-white border border-emerald-200 rounded-full px-4 py-2 shadow-sm">
            <p className="text-sm text-emerald-700 font-medium flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
              Connected to FreDeSa API
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
