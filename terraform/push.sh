#!/usr/bin/env bash
set -euo pipefail

PROJECT="dungeondm"
REGION="ap-southeast-2"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

BACKEND_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-backend"
FRONTEND_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-frontend"

aws ecr get-login-password --region "${REGION}" | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

# Backend
docker build -t "${PROJECT}-backend:latest" ../backend
docker tag "${PROJECT}-backend:latest" "${BACKEND_REPO}:latest"
docker push "${BACKEND_REPO}:latest"

# Frontend
docker build -t "${PROJECT}-frontend:latest" ../frontend
docker tag "${PROJECT}-frontend:latest" "${FRONTEND_REPO}:latest"
docker push "${FRONTEND_REPO}:latest"
