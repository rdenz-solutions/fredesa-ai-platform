#!/bin/bash

# FreDeSa AI Platform - Azure Configuration Script
# Usage: ./configure-azure.sh "CLIENT_ID" "TENANT_ID"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ "$#" -ne 2 ]; then
    echo -e "${RED}❌ Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: ./configure-azure.sh \"CLIENT_ID\" \"TENANT_ID\""
    echo ""
    echo "Example:"
    echo "  ./configure-azure.sh \"a1b2c3d4-e5f6-7890-abcd-ef1234567890\" \"9z8y7x6w-5v4u-3t2s-1r0q-p0o9i8u7y6t5\""
    echo ""
    exit 1
fi

CLIENT_ID="$1"
TENANT_ID="$2"

# Validate UUID format (basic check)
UUID_REGEX='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

if ! [[ $CLIENT_ID =~ $UUID_REGEX ]]; then
    echo -e "${RED}❌ Error: CLIENT_ID doesn't look like a valid UUID${NC}"
    echo "Got: $CLIENT_ID"
    exit 1
fi

if ! [[ $TENANT_ID =~ $UUID_REGEX ]]; then
    echo -e "${RED}❌ Error: TENANT_ID doesn't look like a valid UUID${NC}"
    echo "Got: $TENANT_ID"
    exit 1
fi

echo -e "${GREEN}🔧 Configuring Azure AD Authentication...${NC}"
echo ""
echo "Client ID: $CLIENT_ID"
echo "Tenant ID: $TENANT_ID"
echo ""

# Backup existing config
if [ -f "src/auth/authConfig.ts" ]; then
    cp src/auth/authConfig.ts "src/auth/authConfig.ts.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}📦 Backed up existing configuration${NC}"
fi

# Create the new authConfig.ts
cat > src/auth/authConfig.ts <<EOF
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

echo -e "${GREEN}✅ Configuration updated successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Refresh your browser at http://localhost:3000"
echo "2. Click 'Sign in with Microsoft'"
echo "3. You should see the Microsoft login screen"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
