FROM node:18-alpine

WORKDIR /app

# Copy shared utilities
COPY ../../shared ./shared

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the project
RUN npm run build

# Create data directory
RUN mkdir -p /workspace/data && \
    chown -R node:node /workspace/data

# Switch to non-root user
USER node

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]