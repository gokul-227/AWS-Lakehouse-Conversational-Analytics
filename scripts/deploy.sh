PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Step 0: Get Alert Email ──────────────────────────────────────

ALERT_EMAIL=$1
if [ -z "$ALERT_EMAIL" ]; then
  read -p "📧 Enter email for SNS alerts and Cognito admin: " ALERT_EMAIL
fi

if [ -z "$ALERT_EMAIL" ]; then
  echo "❌ Alert email is required."
  exit 1
fi

# ── Step 1: Network Configuration ────────────────────────────────

echo "🌐 [1/7] Fetching network configuration..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text | tr '\t' ',')

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    echo "⚠️  No default VPC found. Lambda will be deployed without VPC access."
    VPC_ARG=""
else
    echo "✅ Found VPC: $VPC_ID"
    VPC_ARG="-var='vpc_id=$VPC_ID' -var='subnet_ids=[\"$(echo $SUBNET_IDS | sed 's/,/","/g')\"]'"
fi

# ── Step 4: Build and Push Docker Image ─────────────────────────

echo "🐳 [4/7] Building and pushing Docker image..."
REGION=$(aws configure get region)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Create ECR repo if not exists
aws ecr describe-repositories --repository-names lakechat-api || \
aws ecr create-repository --repository-name lakechat-api

docker build -t lakechat-api "$PROJECT_ROOT/backend"
docker tag lakechat-api:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/lakechat-api:latest
docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/lakechat-api:latest

# ── Step 5: Provision Infrastructure ──────────────────────────

echo "🏗️  [5/7] Provisioning infrastructure with Terraform..."
cd infra
terraform init -input=false
eval terraform apply -auto-approve -input=false -var="alert_email=$ALERT_EMAIL" -var="lambda_image_uri='${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/lakechat-api:latest'" $VPC_ARG

API_URL=$(terraform output -raw api_gateway_url)
FRONTEND_URL=$(terraform output -raw cloudfront_url)
COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
COGNITO_CLIENT_ID=$(terraform output -raw cognito_client_id)
FRONTEND_BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
DIST_ID=$(terraform output -raw cloudfront_distribution_id)

# ── Step 6: Build and Deploy Frontend ─────────────────────────

echo "🔨 [6/7] Building frontend with Docker..."
cd "$PROJECT_ROOT"
# Create .env for frontend
cat > frontend/.env << EOF
VITE_COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID
VITE_COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID
VITE_API_URL=$API_URL
EOF
docker run --rm -v "$PROJECT_ROOT/frontend":/app -w /app node:18-alpine sh -c "npm install && npm run build"

echo "🚀 [7/7] Deploying frontend to CloudFront..."
aws s3 sync "$PROJECT_ROOT/frontend/dist" "s3://${FRONTEND_BUCKET_NAME}" --delete --quiet

echo "🧹 Invalidating CloudFront cache..."
if [ -n "$DIST_ID" ] && [ "$DIST_ID" != "None" ]; then
    aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*" > /dev/null
    echo "✅ Invalidation triggered for $DIST_ID"
else
    echo "⚠️ Distribution ID not found. Invalidation skipped."
fi

# ── Step 7: Create Admin User ───────────────────────────────────

echo "👤 [7/7] Creating admin user..."
TEMP_PASS="TempPassword123!"
aws cognito-idp admin-create-user \
  --user-pool-id "$COGNITO_USER_POOL_ID" \
  --username "$ALERT_EMAIL" \
  --user-attributes Name=email,Value="$ALERT_EMAIL" Name=email_verified,Value=true \
  --temporary-password "$TEMP_PASS" \
  --message-action SUPPRESS > /dev/null || true

# Save to .env for local dev
cat > "$PROJECT_ROOT/frontend/.env" << EOF
VITE_COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID
VITE_COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID
VITE_API_URL=$API_URL
EOF

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Deployment Complete!                                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  URL:      $FRONTEND_URL"
echo "║  Email:    $ALERT_EMAIL"
echo "║  Password: $TEMP_PASS"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Please change your password on first login."

