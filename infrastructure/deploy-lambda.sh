#!/bin/bash
set -e

# Lambda deployment script for Ipswich Story Weaver
# Creates a deployment package and uploads to Lambda

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
BUILD_DIR="$PROJECT_ROOT/build/lambda"
STACK_NAME="${STACK_NAME:-ipswich-story-weaver}"
REGION="${AWS_REGION:-us-east-1}"

echo "=== Building Lambda deployment package ==="

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Install dependencies into build directory
echo "Installing dependencies..."
pip install \
    --platform manylinux2014_x86_64 \
    --target "$BUILD_DIR" \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    -r "$BACKEND_DIR/requirements.txt" 2>/dev/null || \
pip install --target "$BUILD_DIR" --upgrade -r "$BACKEND_DIR/requirements.txt"

# Copy application code
echo "Copying application code..."
cp -r "$BACKEND_DIR/app" "$BUILD_DIR/"
cp "$BACKEND_DIR/mangum_handler.py" "$BUILD_DIR/"
cp "$BACKEND_DIR/alembic.ini" "$BUILD_DIR/" 2>/dev/null || true
cp -r "$BACKEND_DIR/alembic" "$BUILD_DIR/" 2>/dev/null || true

# Remove unnecessary files to reduce package size
echo "Cleaning up..."
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true
rm -rf "$BUILD_DIR/boto3" "$BUILD_DIR/botocore" 2>/dev/null || true  # Already in Lambda runtime

# Create zip file
echo "Creating zip file..."
cd "$BUILD_DIR"
zip -r -q ../lambda-package.zip .
cd "$PROJECT_ROOT"

PACKAGE_SIZE=$(du -h "$PROJECT_ROOT/build/lambda-package.zip" | cut -f1)
echo "Package created: build/lambda-package.zip ($PACKAGE_SIZE)"

# Get Lambda function name from CloudFormation
LAMBDA_FUNCTION=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='LambdaFunction'].OutputValue" \
    --output text \
    --region "$REGION" 2>/dev/null)

if [ -z "$LAMBDA_FUNCTION" ] || [ "$LAMBDA_FUNCTION" == "None" ]; then
    echo ""
    echo "CloudFormation stack not ready yet. Deploy manually with:"
    echo "  aws lambda update-function-code --function-name FUNCTION_NAME --zip-file fileb://build/lambda-package.zip"
    exit 0
fi

echo ""
echo "=== Deploying to Lambda: $LAMBDA_FUNCTION ==="

aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION" \
    --zip-file "fileb://$PROJECT_ROOT/build/lambda-package.zip" \
    --region "$REGION"

echo ""
echo "=== Lambda deployment complete! ==="

# Get the function URL
FUNCTION_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" \
    --output text \
    --region "$REGION")

echo "API URL: $FUNCTION_URL"
echo ""
echo "Test with: curl ${FUNCTION_URL}healthz"
