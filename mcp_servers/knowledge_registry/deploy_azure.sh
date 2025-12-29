#!/bin/bash
# Deploy FreDeSa Knowledge Registry MCP Server to Azure Container Apps

set -e

# Configuration
RESOURCE_GROUP="fredesa-resources"
LOCATION="eastus"
ACR_NAME="fredesaacr"
APP_NAME="fredesa-mcp-server"
CONTAINER_APP_ENV="fredesa-containerapps-env"
IMAGE_NAME="knowledge-registry-mcp"
IMAGE_TAG="latest"

# Azure Key Vault for secrets
KEY_VAULT_NAME="fredesa-kv-e997e3"

echo "🚀 Starting Azure Container Apps deployment..."

# Step 1: Login to Azure (if needed)
echo "📋 Checking Azure login..."
az account show > /dev/null 2>&1 || az login

# Step 2: Create or verify Container Registry
echo "📦 Setting up Azure Container Registry..."
az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP > /dev/null 2>&1 || \
  az acr create \
    --name $ACR_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Basic \
    --admin-enabled true

# Step 3: Build and push Docker image
echo "🔨 Building Docker image..."
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$IMAGE_TAG \
  --file Dockerfile \
  .

# Step 4: Get ACR credentials
echo "🔑 Retrieving ACR credentials..."
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query passwords[0].value -o tsv)

# Step 5: Get PostgreSQL password from Key Vault
echo "🔒 Retrieving database credentials from Key Vault..."
POSTGRES_PASSWORD=$(az keyvault secret show --vault-name $KEY_VAULT_NAME --name postgres-password --query value -o tsv)

# Step 6: Create Container Apps Environment (if doesn't exist)
echo "🌍 Setting up Container Apps Environment..."
az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP > /dev/null 2>&1 || \
  az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Step 7: Deploy Container App
echo "🚢 Deploying container app..."
az containerapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    POSTGRES_HOST="fredesa-db-dev.postgres.database.azure.com" \
    POSTGRES_PORT="5432" \
    POSTGRES_DB="postgres" \
    POSTGRES_USER="fredesaadmin" \
    POSTGRES_SSLMODE="require" \
    AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME" \
  --secrets \
    postgres-password="$POSTGRES_PASSWORD" || \
  az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --set-env-vars \
      POSTGRES_HOST="fredesa-db-dev.postgres.database.azure.com" \
      POSTGRES_PORT="5432" \
      POSTGRES_DB="postgres" \
      POSTGRES_USER="fredesaadmin" \
      POSTGRES_SSLMODE="require" \
      AZURE_KEY_VAULT_NAME="$KEY_VAULT_NAME"

# Step 8: Get the public URL
echo "🌐 Getting public URL..."
APP_URL=$(az containerapp show \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📍 MCP Server URL: https://$APP_URL"
echo ""
echo "🔧 Endpoints:"
echo "   Health Check:  https://$APP_URL/health"
echo "   Tools List:    https://$APP_URL/tools"
echo "   MCP SSE:       https://$APP_URL/mcp/sse"
echo "   Stats:         https://$APP_URL/stats"
echo ""
echo "📋 Next Steps:"
echo "   1. Test health: curl https://$APP_URL/health"
echo "   2. Register in Airia Custom MCP Server dialog:"
echo "      - URL: https://$APP_URL/mcp/sse"
echo "      - Auth: None (or configure if needed)"
echo "   3. Attach to test agent (8800c4f0-1cdd-4ba2-aa05-8df35d986d72)"
echo ""
