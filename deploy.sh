#!/bin/bash
set -e

echo "🚀 Fast Lane Price Service Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "serverless.yml" ]; then
    echo -e "${RED}❌ Error: serverless.yml not found. Run this script from the project root.${NC}"
    exit 1
fi

# Check for AWS credentials
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: AWS credentials not configured.${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials OK${NC}"

# Check for Node.js and npm
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js not found. Install Node.js first.${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Error: npm not found. Install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js and npm OK${NC}"

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
npm install -g serverless
npm install serverless-python-requirements

# Validate serverless config
echo -e "${YELLOW}🔍 Validating configuration...${NC}"
serverless print > /dev/null

# Deploy to AWS
echo -e "${YELLOW}🚀 Deploying to AWS...${NC}"
STAGE=${1:-prod}
REGION=${2:-us-east-1}

echo "Stage: $STAGE"
echo "Region: $REGION"

serverless deploy --stage "$STAGE" --region "$REGION" --verbose

# Get the endpoint URL
ENDPOINT=$(serverless info --stage "$STAGE" --region "$REGION" | grep -o 'https://[^/]*/[^/]*' | head -1)

if [ -n "$ENDPOINT" ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "🔗 API Endpoints:"
    echo "   Price: $ENDPOINT/price"
    echo "   Health: $ENDPOINT/health"
    echo ""
    echo "🧪 Test it:"
    echo "   curl $ENDPOINT/price"
    echo ""
    echo "📱 For Siri Shortcut, use: $ENDPOINT/price"
    echo ""
    
    # Test the endpoint
    echo -e "${YELLOW}🧪 Testing endpoint...${NC}"
    if curl -s "$ENDPOINT/health" | grep -q "healthy"; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
    fi
    
    # Save endpoint to file for reference
    echo "$ENDPOINT/price" > .api-endpoint
    echo "💾 Endpoint saved to .api-endpoint"
    
else
    echo -e "${RED}❌ Deployment failed or endpoint not found${NC}"
    exit 1
fi