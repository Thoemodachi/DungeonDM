# ---- Build stage ----
FROM node:18-slim AS builder

WORKDIR /app

# Copy package files first (caching)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# ---- Production stage ----
FROM node:18-slim

WORKDIR /app

# Copy built app and node_modules from builder
COPY --from=builder /app ./

# Expose port for ECS/ALB
EXPOSE 3000

# Run Next.js production server
CMD ["npm", "run", "dev"]
