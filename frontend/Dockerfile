# Use a Debian-based Node image
FROM node:18-slim AS builder

WORKDIR /app

# Copy package.json and lockfile first for caching
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .

# Build the Next.js app
RUN npm run build

# ---- Production image ----
FROM node:18-slim

WORKDIR /app

# Copy only the built files + node_modules
COPY --from=builder /app ./

EXPOSE 3000

# Run production server
CMD ["npm", "run", "start"]
