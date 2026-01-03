/**
 * API Client Configuration
 * Handles all backend communication with Azure AD authentication
 */

import { PublicClientApplication } from "@azure/msal-browser";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Debug logging for environment variables
console.log('[API Client] Environment:', import.meta.env.MODE);
console.log('[API Client] API_BASE_URL:', API_BASE_URL);
console.log('[API Client] All env vars:', import.meta.env);

/**
 * Get access token for API calls
 */
export async function getAccessToken(msalInstance: PublicClientApplication): Promise<string> {
    const accounts = msalInstance.getAllAccounts();
    
    if (accounts.length === 0) {
        throw new Error("No authenticated user");
    }

    const request = {
        scopes: ["api://257a158a-c6d6-4595-8dc3-df07e83504ac/access_as_user"],
        account: accounts[0]
    };

    try {
        const response = await msalInstance.acquireTokenSilent(request);
        return response.accessToken;
    } catch (error) {
        // If silent acquisition fails, try interactive
        const response = await msalInstance.acquireTokenPopup(request);
        return response.accessToken;
    }
}

/**
 * Authenticated API request wrapper
 */
export async function apiRequest<T>(
    endpoint: string,
    msalInstance: PublicClientApplication,
    options: RequestInit = {}
): Promise<T> {
    const token = await getAccessToken(msalInstance);
    
    const headers = {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
        ...options.headers
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
}

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface UserProfile {
    user_id: string;
    email: string;
    name: string;
    role: string;
    tenant_id: string;
}

export interface Proposal {
    id: string;
    title: string;
    agency: string;
    value: string;
    status: string;
    due_date: string;
    completion: number;
}

export interface ProposalDetail extends Proposal {
    contract_type: string;
    sections: Array<{
        name: string;
        status: string;
        word_count: number;
    }>;
    team: Array<{
        name: string;
        role: string;
    }>;
    created_by: string;
    created_at: string;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Get current user profile
 */
export async function getUserProfile(msalInstance: PublicClientApplication): Promise<UserProfile> {
    return apiRequest<UserProfile>("/api/user/profile", msalInstance);
}

/**
 * Get list of proposals
 */
export async function getProposals(msalInstance: PublicClientApplication): Promise<{ proposals: Proposal[], total: number, user_role: string }> {
    return apiRequest("/api/proposals", msalInstance);
}

/**
 * Get specific proposal details
 */
export async function getProposal(proposalId: string, msalInstance: PublicClientApplication): Promise<ProposalDetail> {
    return apiRequest(`/api/proposals/${proposalId}`, msalInstance);
}

/**
 * Admin: Get all users
 */
export async function getUsers(msalInstance: PublicClientApplication) {
    return apiRequest("/api/admin/users", msalInstance);
}

/**
 * Admin: Get analytics
 */
export async function getAnalytics(msalInstance: PublicClientApplication) {
    return apiRequest("/api/admin/analytics", msalInstance);
}
