# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Accept build arguments
ARG VITE_API_BASE_URL=http://localhost:8001
ARG VITE_BCRA_URL=http://localhost:8002
ARG VITE_COMEX_URL=http://localhost:8003
ARG VITE_SENASA_URL=http://localhost:8004
ARG VITE_AUDITOR_URL=http://localhost:8005

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_BCRA_URL=$VITE_BCRA_URL
ENV VITE_COMEX_URL=$VITE_COMEX_URL
ENV VITE_SENASA_URL=$VITE_SENASA_URL
ENV VITE_AUDITOR_URL=$VITE_AUDITOR_URL

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]