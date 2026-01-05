# Frontend Environment Specification
**FreDeSa AI Platform - Test vs Production Frontend Design**

**Created:** January 5, 2026  
**Status:** Specification - Ready for Implementation  
**Stakeholders:** Frontend Team, DevOps, Product Management

---

## Executive Summary

This document defines the visual, functional, and architectural differences between **Test** and **Production** frontend environments. The goal is to:

1. **Prevent User Confusion:** Clear visual indicators of which environment users are in
2. **Enable Safe Testing:** Test environment has additional debugging tools and looser restrictions
3. **Protect Production Data:** Production has stricter validation and no test data indicators
4. **Maintain Brand Integrity:** Production reflects professional FreDeSa branding

---

## Environment URLs

| Environment | Frontend URL | Backend API URL | Purpose |
|-------------|-------------|-----------------|---------|
| **Local Development** | http://localhost:3000 | http://localhost:8000 | Developer workstations |
| **Test** | https://test.fredesa.com | https://fredesa-api-test.eastus.azurecontainerapps.io | Automated testing, QA validation |
| **Staging** | https://staging.fredesa.com | https://fredesa-api-staging.eastus.azurecontainerapps.io | Pre-production validation |
| **Production** | https://app.fredesa.com | https://api.fredesa.com | Live customer environment |

---

## 1. Visual Differences

### 1.1 Environment Banner

**Test Environment:**
```tsx
<div className="bg-amber-500 text-white px-4 py-2 text-sm font-semibold flex items-center justify-center gap-2 shadow-md">
  <span>⚠️ TEST ENVIRONMENT</span>
  <span className="opacity-80">|</span>
  <span className="opacity-90">Safe to experiment - No real data will be affected</span>
</div>
```

**Production Environment:**
- **NO BANNER** - Clean, professional appearance
- Optional: Subtle footer indicator "FreDeSa AI Platform v1.0" in small text

### 1.2 Color Scheme Adjustments

**Test Environment:**
- Primary color: Amber/Orange accents (`bg-amber-500`, `text-amber-600`)
- Border colors: Warmer tones
- Button primary: `bg-amber-600 hover:bg-amber-700`
- Status indicators: More saturated colors

**Production Environment:**
- Primary color: Professional Blue (`bg-blue-600`, `text-blue-700`)
- Border colors: Neutral slate tones
- Button primary: `bg-blue-600 hover:bg-blue-700`
- Status indicators: Muted, professional colors

### 1.3 Logo & Branding

**Test Environment:**
```tsx
<div className="flex items-center gap-2">
  <img src="/logo.svg" alt="FreDeSa" className="h-8" />
  <span className="bg-amber-100 text-amber-700 px-2 py-1 rounded text-xs font-bold">TEST</span>
</div>
```

**Production Environment:**
```tsx
<div className="flex items-center">
  <img src="/logo.svg" alt="FreDeSa" className="h-8" />
</div>
```

### 1.4 Favicon

**Test:** Orange/amber colored favicon with "T" indicator  
**Production:** Standard FreDeSa blue favicon

---

## 2. Functional Differences

### 2.1 Feature Flags

| Feature | Test | Production | Rationale |
|---------|------|------------|-----------|
| **Debug Console** | ✅ Enabled | ❌ Disabled | Developers need debugging info |
| **API Request Logging** | ✅ Verbose | ⚠️ Errors Only | Test needs full visibility |
| **Mock Data Toggle** | ✅ Available | ❌ Not Available | Test can use fake data |
| **Performance Metrics** | ✅ Visible | ❌ Hidden | Test monitors performance |
| **Error Details** | ✅ Full Stack Traces | ⚠️ User-Friendly Messages | Production hides internal errors |
| **Feature Previews** | ✅ All Features | ⚠️ Stable Features Only | Test environment for beta features |
| **Rate Limiting** | ⚠️ Relaxed (100/min) | ✅ Strict (60/min) | Test allows more requests |
| **Session Timeout** | ⚠️ 8 hours | ✅ 1 hour | Test has longer sessions |

### 2.2 Data Handling

**Test Environment:**
- Display "🧪 TEST DATA" badge on all records
- Allow data reset/cleanup
- Show database connection status
- Display API response times
- Mock data available via toggle switch

**Production Environment:**
- No test data indicators
- No data reset capabilities
- Hide internal system status
- No API performance metrics visible to end users
- Only real customer data

### 2.3 Error Handling

**Test Environment:**
```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <h4 className="text-red-800 font-semibold mb-2">Error Details (Test Mode)</h4>
    <pre className="text-xs text-red-700 overflow-auto">
      {JSON.stringify(error, null, 2)}
    </pre>
    <details className="mt-2">
      <summary className="cursor-pointer text-red-600">Stack Trace</summary>
      <pre className="text-xs mt-2">{error.stack}</pre>
    </details>
  </div>
)}
```

**Production Environment:**
```tsx
{error && (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <h4 className="text-red-800 font-semibold mb-2">Something went wrong</h4>
    <p className="text-red-600 text-sm">
      We're experiencing technical difficulties. Please try again or contact support.
    </p>
    <button onClick={handleRetry} className="mt-3 bg-red-600 text-white px-4 py-2 rounded">
      Try Again
    </button>
  </div>
)}
```

---

## 3. Developer Tools & Debugging

### 3.1 Debug Panel (Test Only)

**Location:** Bottom-right floating panel  
**Visibility:** Test environment only

```tsx
// Test Environment Only
{import.meta.env.VITE_ENVIRONMENT === 'test' && (
  <DebugPanel>
    <Section title="Environment">
      <KeyValue label="Mode" value={import.meta.env.MODE} />
      <KeyValue label="API URL" value={import.meta.env.VITE_API_URL} />
      <KeyValue label="Build" value={import.meta.env.VITE_BUILD_ID} />
    </Section>
    
    <Section title="Authentication">
      <KeyValue label="User ID" value={user?.id} />
      <KeyValue label="Role" value={user?.role} />
      <KeyValue label="Token Expiry" value={tokenExpiry} />
    </Section>
    
    <Section title="API Performance">
      <KeyValue label="Last Request" value={`${lastRequestTime}ms`} />
      <KeyValue label="Avg Response" value={`${avgResponseTime}ms`} />
      <KeyValue label="Failed Requests" value={failedRequestCount} />
    </Section>
    
    <Section title="Actions">
      <Button onClick={clearCache}>Clear Cache</Button>
      <Button onClick={resetAuth}>Reset Auth</Button>
      <Button onClick={toggleMockData}>Toggle Mock Data</Button>
    </Section>
  </DebugPanel>
)}
```

### 3.2 Console Logging Levels

**Test Environment:**
```typescript
// Verbose logging
console.log('[API] Request:', endpoint, payload);
console.log('[API] Response:', response);
console.log('[Auth] Token acquired:', token.substring(0, 20) + '...');
console.log('[Performance] Render time:', renderTime, 'ms');
```

**Production Environment:**
```typescript
// Errors only, no sensitive data
console.error('[API] Request failed:', endpoint);
// No token logging
// No performance metrics
```

---

## 4. Authentication & Security

### 4.1 Session Management

| Setting | Test | Production |
|---------|------|------------|
| **Session Duration** | 8 hours | 1 hour |
| **Idle Timeout** | 4 hours | 30 minutes |
| **Remember Me** | ✅ Available | ⚠️ Limited to 7 days |
| **Multi-Device Login** | ✅ Unlimited | ⚠️ Max 3 concurrent |

### 4.2 Error Messages

**Test Environment:**
```typescript
// Detailed technical errors
"Authentication failed: Token expired at 2026-01-05T08:00:00Z. 
Current time: 2026-01-05T08:15:00Z. 
Refresh token invalid: RefreshTokenExpiredError"
```

**Production Environment:**
```typescript
// User-friendly messages
"Your session has expired. Please sign in again."
```

---

## 5. Performance & Monitoring

### 5.1 Performance Metrics Display

**Test Environment:**
- Show API response times on every request
- Display render performance metrics
- Show bundle size and load times
- Network waterfall visible in debug panel

**Production Environment:**
- No visible performance metrics
- Silent monitoring via Application Insights
- Error tracking via Sentry (no user visibility)

### 5.2 Loading States

**Test Environment:**
```tsx
<div className="flex items-center gap-2 text-amber-600">
  <Spinner />
  <span>Loading proposals... (API: test.fredesa.com)</span>
</div>
```

**Production Environment:**
```tsx
<div className="flex items-center gap-2 text-blue-600">
  <Spinner />
  <span>Loading proposals...</span>
</div>
```

---

## 6. User Experience Differences

### 6.1 Onboarding & Help

**Test Environment:**
- Prominent "🧪 You're in Test Mode" tooltips
- Guided tours available for all features
- "Report Bug" button visible on every page
- Help documentation links to test-specific guides

**Production Environment:**
- Professional onboarding flow
- Context-sensitive help only
- "Contact Support" button (not "Report Bug")
- Help documentation links to public docs

### 6.2 Notifications & Alerts

**Test Environment:**
```tsx
<Toast type="info" className="bg-amber-50 border-amber-200">
  <span className="text-amber-700">
    ℹ️ Test Environment: This notification is for demonstration purposes
  </span>
</Toast>
```

**Production Environment:**
```tsx
<Toast type="info" className="bg-blue-50 border-blue-200">
  <span className="text-blue-700">
    Your proposal has been submitted successfully
  </span>
</Toast>
```

---

## 7. Data & Content Differences

### 7.1 Sample Data

**Test Environment:**
- Display sample/seed data with "🧪 Sample Data" badges
- Allow users to generate test proposals
- Pre-populated demo accounts (e.g., "Acme Federal Contractor")
- Fake email addresses (test@example.com)

**Production Environment:**
- Real customer data only
- No sample data generation
- Real customer accounts
- Real email addresses

### 7.2 Data Indicators

**Test Environment:**
```tsx
<ProposalCard proposal={proposal}>
  {proposal.isSampleData && (
    <Badge className="bg-amber-100 text-amber-700 text-xs">
      🧪 Sample Data
    </Badge>
  )}
</ProposalCard>
```

**Production Environment:**
```tsx
<ProposalCard proposal={proposal}>
  {/* No sample data indicators */}
</ProposalCard>
```

---

## 8. Implementation Guide

### 8.1 Environment Detection

**Create:** `@fredesa-ai-platform:web/src/utils/environment.ts`

```typescript
export const ENV = {
  MODE: import.meta.env.MODE,
  API_URL: import.meta.env.VITE_API_URL,
  IS_PRODUCTION: import.meta.env.VITE_ENVIRONMENT === 'production',
  IS_TEST: import.meta.env.VITE_ENVIRONMENT === 'test',
  IS_STAGING: import.meta.env.VITE_ENVIRONMENT === 'staging',
  IS_DEV: import.meta.env.MODE === 'development',
  ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  ENABLE_MOCK_DATA: import.meta.env.VITE_ENABLE_MOCK_DATA === 'true',
};

export const getEnvironmentConfig = () => ({
  showBanner: !ENV.IS_PRODUCTION,
  bannerColor: ENV.IS_TEST ? 'amber' : ENV.IS_STAGING ? 'purple' : 'blue',
  bannerText: ENV.IS_TEST ? '⚠️ TEST ENVIRONMENT' : ENV.IS_STAGING ? '🚧 STAGING ENVIRONMENT' : '',
  enableDebugPanel: ENV.IS_TEST || ENV.IS_DEV,
  verboseLogging: !ENV.IS_PRODUCTION,
  showPerformanceMetrics: ENV.IS_TEST,
  sessionDuration: ENV.IS_PRODUCTION ? 3600 : 28800, // 1 hour vs 8 hours
});
```

### 8.2 Environment Banner Component

**Create:** `@fredesa-ai-platform:web/src/components/EnvironmentBanner.tsx`

```typescript
import React from 'react';
import { ENV, getEnvironmentConfig } from '../utils/environment';

export const EnvironmentBanner: React.FC = () => {
  const config = getEnvironmentConfig();

  if (!config.showBanner) return null;

  return (
    <div className={`bg-${config.bannerColor}-500 text-white px-4 py-2 text-sm font-semibold flex items-center justify-center gap-2 shadow-md`}>
      <span>{config.bannerText}</span>
      <span className="opacity-80">|</span>
      <span className="opacity-90">
        {ENV.IS_TEST && 'Safe to experiment - No real data will be affected'}
        {ENV.IS_STAGING && 'Pre-production environment - Testing before launch'}
      </span>
      {config.enableDebugPanel && (
        <>
          <span className="opacity-80">|</span>
          <span className="opacity-90 text-xs">
            API: {ENV.API_URL}
          </span>
        </>
      )}
    </div>
  );
};
```

### 8.3 Theme Configuration

**Create:** `@fredesa-ai-platform:web/src/config/theme.ts`

```typescript
import { ENV } from '../utils/environment';

export const theme = {
  primary: ENV.IS_TEST ? {
    50: '#fffbeb',
    100: '#fef3c7',
    500: '#f59e0b', // Amber
    600: '#d97706',
    700: '#b45309',
  } : {
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6', // Blue
    600: '#2563eb',
    700: '#1d4ed8',
  },
  // ... rest of theme
};
```

### 8.4 Required Environment Variables

**Test Environment (`.env.test`):**
```bash
VITE_ENVIRONMENT=test
VITE_API_URL=https://fredesa-api-test.eastus.azurecontainerapps.io
VITE_ENABLE_DEBUG=true
VITE_ENABLE_MOCK_DATA=true
VITE_SESSION_DURATION=28800
VITE_LOG_LEVEL=verbose
```

**Production Environment (`.env.production`):**
```bash
VITE_ENVIRONMENT=production
VITE_API_URL=https://api.fredesa.com
VITE_ENABLE_DEBUG=false
VITE_ENABLE_MOCK_DATA=false
VITE_SESSION_DURATION=3600
VITE_LOG_LEVEL=error
```

---

## 9. Testing Checklist

### 9.1 Visual Testing

- [ ] Test banner displays correctly in test environment
- [ ] No banner shows in production
- [ ] Logo has "TEST" badge in test environment
- [ ] Favicon is different between environments
- [ ] Color scheme matches specification (amber vs blue)
- [ ] All UI components use environment-aware colors

### 9.2 Functional Testing

- [ ] Debug panel only appears in test environment
- [ ] API logging is verbose in test, silent in production
- [ ] Error messages show details in test, friendly in production
- [ ] Mock data toggle works in test environment
- [ ] Performance metrics visible in test only
- [ ] Session timeout differs between environments
- [ ] Rate limiting enforced correctly

### 9.3 Security Testing

- [ ] No sensitive data logged in production
- [ ] Stack traces not exposed in production
- [ ] API URLs not visible to end users in production
- [ ] Debug endpoints not accessible in production
- [ ] Authentication tokens not logged anywhere

---

## 10. Rollout Plan

### Phase 1: Foundation (Week 1)
- [ ] Create environment detection utility
- [ ] Implement environment banner component
- [ ] Add environment-aware theme configuration
- [ ] Update build scripts to inject environment variables

### Phase 2: Visual Changes (Week 2)
- [ ] Update logo with environment indicators
- [ ] Create environment-specific favicons
- [ ] Apply color scheme changes across components
- [ ] Update button styles for environment awareness

### Phase 3: Functional Changes (Week 3)
- [ ] Implement debug panel for test environment
- [ ] Add conditional logging based on environment
- [ ] Create error message formatter (detailed vs friendly)
- [ ] Implement mock data toggle for test

### Phase 4: Testing & Validation (Week 4)
- [ ] Manual QA testing in all environments
- [ ] Automated visual regression tests
- [ ] Security audit of environment separation
- [ ] Performance impact assessment

### Phase 5: Documentation & Training (Week 5)
- [ ] Update developer documentation
- [ ] Create user guide for test environment
- [ ] Train support team on environment differences
- [ ] Create troubleshooting guide

---

## 11. Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **User Confusion Reduction** | 90% reduction in "wrong environment" support tickets | Support ticket analysis |
| **Developer Productivity** | 30% faster debugging in test environment | Developer survey |
| **Production Stability** | 0 incidents from test data in production | Incident tracking |
| **Visual Clarity** | 95% of users can identify environment within 3 seconds | User testing |

---

## 12. Future Enhancements

### Phase 2 (Q2 2026)
- [ ] Environment switcher for admins (test → staging → production)
- [ ] Custom branding per customer tenant
- [ ] A/B testing framework for features
- [ ] Real-time performance dashboards

### Phase 3 (Q3 2026)
- [ ] Automated screenshot comparison between environments
- [ ] Feature flag management UI
- [ ] Environment-specific analytics dashboards
- [ ] Customer-facing "sandbox mode"

---

## 13. References

- GitHub Actions Workflows: `.github/workflows/deploy-*.yml`
- Current Frontend Code: `web/src/App.tsx`, `web/src/features/customer/CustomerDashboard.tsx`
- API Client: `web/src/api/client.ts`
- Environment Template: `config/.env.template`
- Deployment Checklists: `docs/deployment/*_DEPLOYMENT_CHECKLIST.md`

---

## Appendix A: Quick Reference Table

| Feature | Local Dev | Test | Staging | Production |
|---------|-----------|------|---------|------------|
| **Banner** | Yellow | Amber | Purple | None |
| **Debug Panel** | ✅ | ✅ | ⚠️ Limited | ❌ |
| **Verbose Logs** | ✅ | ✅ | ⚠️ Errors | ❌ Errors Only |
| **Mock Data** | ✅ | ✅ | ❌ | ❌ |
| **Session Length** | 24h | 8h | 2h | 1h |
| **Rate Limit** | None | 100/min | 80/min | 60/min |
| **Error Details** | Full | Full | Partial | User-Friendly |
| **Performance Metrics** | ✅ | ✅ | ⚠️ Admin Only | ❌ |

---

**Document Version:** 1.0  
**Last Updated:** January 5, 2026  
**Next Review:** March 1, 2026  
**Owner:** Frontend Team Lead  
**Approvers:** CTO, Product Manager, UX Lead
