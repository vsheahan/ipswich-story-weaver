#!/bin/bash
set -e

# Frontend deployment script for Ipswich Story Weaver

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
STACK_NAME="${STACK_NAME:-ipswich-story-weaver}"
REGION="${AWS_REGION:-us-east-1}"

echo "=== Building frontend ==="

cd "$FRONTEND_DIR"

# Install dependencies
npm ci

# Get the API URL for the build
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

# Build with API URL (frontend will proxy /api to this)
VITE_API_URL="$API_URL" npm run build

echo ""
echo "=== Deploying to S3 ==="

# Get S3 bucket from CloudFormation
S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucket'].OutputValue" \
    --output text \
    --region "$REGION")

if [ -z "$S3_BUCKET" ] || [ "$S3_BUCKET" == "None" ]; then
    echo "Error: Could not get S3 bucket from CloudFormation"
    exit 1
fi

# Sync to S3
aws s3 sync dist/ "s3://$S3_BUCKET" --delete --region "$REGION"

echo ""
echo "=== Invalidating CloudFront cache ==="

# Get CloudFront distribution ID
DISTRIBUTION_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?Origins.Items[?Id=='S3Origin'] && contains(Origins.Items[].DomainName, '$S3_BUCKET')].Id" \
    --output text \
    --region "$REGION" 2>/dev/null || echo "")

if [ -n "$DISTRIBUTION_ID" ] && [ "$DISTRIBUTION_ID" != "None" ]; then
    aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --region "$REGION" > /dev/null
    echo "CloudFront cache invalidated"
fi

# Get website URL
WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='WebsiteURL'].OutputValue" \
    --output text \
    --region "$REGION")

echo ""
echo "=== Frontend deployment complete! ==="
echo "Website URL: $WEBSITE_URL"
