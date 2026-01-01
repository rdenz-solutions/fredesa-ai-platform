// @ts-nocheck
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useMsal } from '@azure/msal-react';
import { getProposals, getUserProfile, getProposal } from '../../api/client';
import type { ProposalDetail } from '../../api/client';

export const CustomerDashboard: React.FC = () => {
  const { instance } = useMsal();
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null);

  // Fetch user profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['userProfile'],
    queryFn: () => getUserProfile(instance as any),
  });

  // Fetch proposals
  const { data: proposalsData, isLoading: proposalsLoading, error } = useQuery({
    queryKey: ['proposals'],
    queryFn: () => getProposals(instance as any),
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
  const totalProposals = proposals.length;
  
  // Calculate stats based on API status values: draft, in_review, submitted
  const inProgressProposals = proposals.filter(p => p.status === 'draft' || p.status === 'in_review');
  const submittedProposals = proposals.filter(p => p.status === 'submitted');
  const avgCompletion = totalProposals > 0 
    ? Math.round(proposals.reduce((sum, p) => sum + p.completion, 0) / totalProposals)
    : 0;

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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-3">Total Proposals</h3>
            <p className="text-4xl font-bold text-slate-900">{totalProposals}</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-amber-600 uppercase tracking-wide mb-3">In Progress</h3>
            <p className="text-4xl font-bold text-slate-900">{inProgressProposals.length}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-emerald-600 uppercase tracking-wide mb-3">Submitted</h3>
            <p className="text-4xl font-bold text-slate-900">{submittedProposals.length}</p>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <h3 className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-3">Avg Completion</h3>
            <p className="text-4xl font-bold text-slate-900">{avgCompletion}%</p>
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
                <div 
                  key={proposal.id} 
                  className="px-6 py-5 hover:bg-slate-50 transition-colors cursor-pointer group"
                  onClick={() => setSelectedProposalId(proposal.id)}
                >
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                          {proposal.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600 mb-3">
                          <span className="flex items-center gap-1.5">
                            🏛️ <strong className="font-medium text-slate-700">{proposal.agency}</strong>
                          </span>
                          <span className="flex items-center gap-1.5">
                            📅 Due: <strong className="font-medium text-slate-700">{new Date(proposal.due_date).toLocaleDateString()}</strong>
                          </span>
                          <span className="flex items-center gap-1.5 font-semibold text-blue-600">
                            💰 {proposal.value}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-3 text-sm">
                          <span className={`px-4 py-1.5 rounded-full font-semibold uppercase tracking-wide text-xs ${
                            proposal.status === 'submitted' 
                              ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                              : proposal.status === 'in_review'
                              ? 'bg-blue-100 text-blue-700 border border-blue-200'
                              : proposal.status === 'draft'
                              ? 'bg-amber-100 text-amber-700 border border-amber-200'
                              : 'bg-slate-100 text-slate-700 border border-slate-200'
                          }`}>
                            {proposal.status.replace('_', ' ')}
                          </span>
                        </div>
                      </div>
                      
                      <button className="p-2 rounded-lg hover:bg-slate-100 transition-colors text-slate-400 hover:text-slate-600 flex-shrink-0">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-600 font-medium">Completion</span>
                        <span className="text-slate-900 font-semibold">{proposal.completion}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all ${
                            proposal.completion === 100 
                              ? 'bg-emerald-500' 
                              : proposal.completion >= 70 
                              ? 'bg-blue-500' 
                              : proposal.completion >= 40
                              ? 'bg-amber-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${proposal.completion}%` }}
                        />
                      </div>
                    </div>
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

      {/* Proposal Detail Modal */}
      {selectedProposalId && (
        <ProposalDetailModal 
          proposalId={selectedProposalId}
          onClose={() => setSelectedProposalId(null)}
        />
      )}
    </div>
  );
};

// Proposal Detail Modal Component
const ProposalDetailModal: React.FC<{ proposalId: string; onClose: () => void }> = ({ proposalId, onClose }) => {
  const { instance } = useMsal();
  
  const { data: proposal, isLoading } = useQuery({
    queryKey: ['proposal', proposalId],
    queryFn: () => getProposal(proposalId, instance as any),
  });

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
        <div className="bg-white rounded-xl p-8 max-w-4xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!proposal) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-6 rounded-t-xl">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">{proposal.title}</h2>
              <div className="flex flex-wrap gap-4 text-sm">
                <span className="flex items-center gap-1.5">
                  🏛️ {proposal.agency}
                </span>
                <span className="flex items-center gap-1.5">
                  📄 {proposal.contract_type}
                </span>
                <span className="flex items-center gap-1.5">
                  💰 {proposal.value}
                </span>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-8 space-y-8">
          {/* Status and Progress */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-50 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-600 uppercase mb-3">Status</h3>
              <span className={`inline-block px-4 py-2 rounded-full font-semibold uppercase tracking-wide text-sm ${
                proposal.status === 'submitted' 
                  ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' 
                  : proposal.status === 'in_review'
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'bg-amber-100 text-amber-700 border border-amber-200'
              }`}>
                {proposal.status.replace('_', ' ')}
              </span>
              <div className="mt-4">
                <p className="text-sm text-slate-600 mb-1">Due Date</p>
                <p className="text-lg font-semibold text-slate-900">{new Date(proposal.due_date).toLocaleDateString('en-US', { dateStyle: 'long' })}</p>
              </div>
            </div>

            <div className="bg-slate-50 rounded-xl p-6">
              <h3 className="text-sm font-semibold text-slate-600 uppercase mb-3">Progress</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-3xl font-bold text-slate-900">{proposal.completion}%</span>
                  <span className="text-sm text-slate-600">Complete</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${
                      proposal.completion === 100 
                        ? 'bg-emerald-500' 
                        : proposal.completion >= 70 
                        ? 'bg-blue-500' 
                        : 'bg-amber-500'
                    }`}
                    style={{ width: `${proposal.completion}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Sections */}
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-4">📄 Proposal Sections</h3>
            <div className="space-y-3">
              {proposal.sections.map((section, idx) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-slate-900 mb-1">{section.name}</h4>
                      <p className="text-sm text-slate-600">{section.word_count.toLocaleString()} words</p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      section.status === 'complete' 
                        ? 'bg-emerald-100 text-emerald-700' 
                        : section.status === 'in_progress'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-slate-100 text-slate-600'
                    }`}>
                      {section.status === 'complete' ? '✓ Complete' : 
                       section.status === 'in_progress' ? '⟳ In Progress' : 
                       '○ Not Started'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Team */}
          <div>
            <h3 className="text-xl font-bold text-slate-900 mb-4">👥 Team Members</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {proposal.team.map((member, idx) => (
                <div key={idx} className="bg-slate-50 rounded-lg p-4 flex items-center gap-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-xl font-bold text-blue-600">{member.name.charAt(0)}</span>
                  </div>
                  <div>
                    <p className="font-semibold text-slate-900">{member.name}</p>
                    <p className="text-sm text-slate-600">{member.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-slate-50 rounded-lg p-4 text-sm text-slate-600">
            <div className="flex flex-wrap gap-6">
              <div>
                <span className="font-semibold">Created by:</span> {proposal.created_by}
              </div>
              <div>
                <span className="font-semibold">Created:</span> {new Date(proposal.created_at).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
