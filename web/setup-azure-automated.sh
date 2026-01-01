#!/bin/bash

# FreDeSa AI Platform - Automated Azure App Registration
# This script uses Azure CLI to create and configure the App Registration

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FreDeSa AI Platform - Azure App Registration Setup          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if logged in to Azure
echo -e "${YELLOW}🔍 Checking Azure CLI authentication...${NC}"
if ! az account show &> /dev/null; then
    echo -e "${RED}❌ Not logged in to Azure${NC}"
    echo ""
    echo "Please run: az login"
    echo ""
    exit 1
fi

TENANT_ID=$(az account show --query tenantId -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo -e "${GREEN}✅ Logged in to Azure${NC}"
echo "   Tenant ID: $TENANT_ID"
echo "   Subscription: $SUBSCRIPTION_NAME"
echo ""

# App details
APP_NAME="FreDeSa AI Platform - Development"
REDIRECT_URI="http://localhost:3000"

echo -e "${YELLOW}📝 Creating App Registration...${NC}"
echo "   Name: $APP_NAME"
echo "   Redirect URI: $REDIRECT_URI"
echo ""

# Check if app already exists
EXISTING_APP=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_APP" ]; then
    echo -e "${YELLOW}⚠️  App '$APP_NAME' already exists${NC}"
    echo "   Client ID: $EXISTING_APP"
    echo ""
    read -p "Do you want to use this existing app? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        CLIENT_ID="$EXISTING_APP"
        echo -e "${GREEN}✅ Using existing app${NC}"
    else
        echo -e "${RED}❌ Aborted. Please delete the existing app or choose a different name.${NC}"
        exit 1
    fi
else
    # Create the app registration with SPA redirect URI
    echo -e "${YELLOW}Creating new app registration...${NC}"
    
    CLIENT_ID=$(az ad app create \
        --display-name "$APP_NAME" \
        --sign-in-audience AzureADMyOrg \
        --web-redirect-uris "$REDIRECT_URI" \
        --enable-id-token-issuance true \
        --query appId -o tsv)
    
    if [ -z "$CLIENT_ID" ]; then
        echo -e "${RED}❌ Failed to create app registration${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ App registration created${NC}"
    echo "   Client ID: $CLIENT_ID"
    
    # Wait for propagation
    echo ""
    echo -e "${YELLOW}⏳ Waiting for Azure AD propagation (5 seconds)...${NC}"
    sleep 5
    
    # Configure SPA platform (required for MSAL.js)
    echo -e "${YELLOW}🔧 Configuring SPA platform settings...${NC}"
    
    az ad app update \
        --id "$CLIENT_ID" \
        --spa-redirect-uris "$REDIRECT_URI" \
        --set spa.redirectUris="[\"$REDIRECT_URI\"]" \
        2>/dev/null || echo "Note: SPA redirect URI already configured"
    
    # Add Microsoft Graph permissions (User.Read)
    echo -e "${YELLOW}🔧 Adding Microsoft Graph permissions...${NC}"
    
    GRAPH_APP_ID="00000003-0000-0000-c000-000000000000"
    USER_READ_PERMISSION="e1fe6dd8-ba31-4d61-89e7-88639da4683d"
    
    az ad app permission add \
        --id "$CLIENT_ID" \
        --api "$GRAPH_APP_ID" \
        --api-permissions "$USER_READ_PERMISSION=Scope" \
        2>/dev/null || echo "Note: Permission may already exist"
    
    echo -e "${GREEN}✅ Permissions configured${NC}"
fi

echo ""
echo -e "${YELLOW}📝 Updating application configuration...${NC}"

# Backup existing config
CONFIG_FILE="src/auth/authConfig.ts"
if [ -f "$CONFIG_FILE" ]; then
    BACKUP_FILE="src/auth/authConfig.ts.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$CONFIG_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backed up existing config to: $BACKUP_FILE${NC}"
fi

# Create the new authConfig.ts
cat > "$CONFIG_FILE" <<EOF
import type { Configuration, PopupRequest } from "@azure/msal-browser";

// Config object to be passed to Msal on creation
export const msalConfig: Configuration = {
    auth: {
        clientId: "$CLIENT_ID",
        authority: "https://login.microsoftonline.com/$TENANT_ID",
        redirectUri: "/",
        postLogoutRedirectUri: "/",
    },
    cache: {
        cacheLocation: "sessionStorage",
        storeAuthStateInCookie: false,
    },
};

// Add here scopes for id token to be used at MS Identity Platform endpoints.
export const loginRequest: PopupRequest = {
    scopes: ["User.Read"]
};

// Add here the endpoints for MS Graph API services you would like to use.
export const graphConfig = {
    graphMeEndpoint: "https://graph.microsoft.com/v1.0/me"
};
EOF

echo -e "${GREEN}✅ Configuration file updated${NC}"

# Create .env file for reference
cat > .env.azure <<EOF
# Azure AD Configuration
# Generated: $(date)

AZURE_CLIENT_ID=$CLIENT_ID
AZURE_TENANT_ID=$TENANT_ID
AZURE_REDIRECT_URI=$REDIRECT_URI
EOF

echo -e "${GREEN}✅ Created .env.azure with credentials${NC}"

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Setup Complete! 🎉                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Configuration Details:${NC}"
echo "  Client ID:  $CLIENT_ID"
echo "  Tenant ID:  $TENANT_ID"
echo "  Redirect:   $REDIRECT_URI"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Refresh your browser at http://localhost:3000"
echo "  2. Click 'Sign in with Microsoft'"
echo "  3. You should see the Microsoft login screen"
echo ""
echo -e "${BLUE}Portal URL:${NC}"
echo "  https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Overview/appId/$CLIENT_ID"
echo ""
echo -e "${GREEN}✨ Your app is ready to use!${NC}"
