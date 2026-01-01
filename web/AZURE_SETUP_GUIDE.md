# Azure App Registration Setup Guide

## 🎯 Goal
Register the FreDeSa AI Platform with Azure Entra ID to enable Microsoft authentication.

## 📋 Prerequisites
- Access to Azure Portal (portal.azure.com)
- Permissions to create App Registrations in your Azure tenant

## 🚀 Step-by-Step Instructions

### Step 1: Navigate to Azure Entra ID
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Azure Entra ID" (formerly Azure Active Directory)
3. Click on **App registrations** in the left menu
4. Click **+ New registration**

### Step 2: Configure Basic Settings
Fill in the registration form:

**Name:** `FreDeSa AI Platform - Development`

**Supported account types:** 
- Choose "Accounts in this organizational directory only (Single tenant)"

**Redirect URI:**
- Platform: **Single-page application (SPA)**
- URI: `http://localhost:3000`

Click **Register**

### Step 3: Copy Essential Information
After registration, you'll see the Overview page. Copy these values:

1. **Application (client) ID** - Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
2. **Directory (tenant) ID** - Example: `9z8y7x6w-5v4u-3t2s-1r0q-p0o9i8u7y6t5`

### Step 4: Configure Authentication Settings (Optional but Recommended)
1. Click **Authentication** in the left menu
2. Under "Implicit grant and hybrid flows":
   - ✅ Check **ID tokens** (for sign-in)
3. Under "Advanced settings":
   - Set **Allow public client flows**: No
4. Click **Save**

### Step 5: Configure API Permissions (Already set by default)
1. Click **API permissions** in the left menu
2. Verify **Microsoft Graph > User.Read** is present (it should be added automatically)
3. If not present, click **+ Add a permission** → Microsoft Graph → Delegated → User.Read

### Step 6: Update Your Application
Once you have the Client ID and Tenant ID, run this command:

```bash
cd "/Users/delchaplin/Project Files/fredesa-ai-platform/web"
./configure-azure.sh "YOUR_CLIENT_ID" "YOUR_TENANT_ID"
```

Or manually edit `src/auth/authConfig.ts`:
```typescript
export const msalConfig: Configuration = {
    auth: {
        clientId: "YOUR_CLIENT_ID_HERE",
        authority: "https://login.microsoftonline.com/YOUR_TENANT_ID_HERE",
        redirectUri: "/",
        postLogoutRedirectUri: "/",
    },
    // ...
};
```

### Step 7: Test the Application
1. Save the file
2. Refresh your browser at `http://localhost:3000`
3. Click **Sign in with Microsoft**
4. You should see the Microsoft login screen

## 🔐 Production Configuration (Later)

When deploying to Azure Static Web Apps, add a production redirect URI:

1. Go back to **Authentication** in your App Registration
2. Click **+ Add a platform** → Single-page application
3. Add: `https://your-production-domain.azurestaticapps.net`
4. Click **Configure**

Then create a production environment configuration that uses the same Client ID but points to the production URL.

## 🛟 Troubleshooting

**"AADSTS50011: The redirect URI specified in the request does not match"**
- Verify redirect URI is exactly `http://localhost:3000` (no trailing slash)
- Check that you selected "Single-page application (SPA)" platform type

**"Invalid client" error**
- Verify Client ID is copied correctly (no extra spaces)
- Verify Tenant ID is correct

**Login popup blocked**
- Check browser popup blocker settings
- Try using "Sign in with Redirect" instead of popup

## 📚 Additional Resources

- [Microsoft Identity Platform Documentation](https://learn.microsoft.com/en-us/entra/identity-platform/)
- [MSAL.js Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js)
- [Azure Static Web Apps Authentication](https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-authorization)
