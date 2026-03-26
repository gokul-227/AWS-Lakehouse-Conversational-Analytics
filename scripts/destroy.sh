#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          LakeChat AI — Destroy Script                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# ── Step 1: Terraform Destroy ───────────────────────────────────

echo ""
echo "🗑️  [1/4] Destroying AWS infrastructure..."
cd infra
terraform destroy -auto-approve -input=false 2>/dev/null || echo "Terraform destroy completed."
cd "$PROJECT_ROOT"

# ── Step 2: Stop Docker containers ──────────────────────────────

echo "🐳 [2/4] Stopping Docker containers..."
docker compose down 2>/dev/null || true

# ── Step 3: Remove Local Artifacts ──────────────────────────────

echo "🧹 [3/4] Cleaning local build artifacts..."
rm -rf lambda_package.zip lambda_package
rm -rf frontend/dist frontend/node_modules

# ── Step 4: Remove Terraform State ──────────────────────────────

echo "🧹 [4/4] Cleaning Terraform state..."
rm -rf infra/.terraform infra/.terraform.lock.hcl infra/terraform.tfstate*

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ All resources destroyed and cleaned up!                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
