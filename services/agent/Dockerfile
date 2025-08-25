FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev for building)
RUN npm install

# Copy source code
COPY . .

# Build the project
RUN npm run build

# Remove dev dependencies
RUN npm prune --omit=dev

# Create data directory
RUN mkdir -p /workspace/data && \
    chown -R node:node /workspace/data

# Switch to non-root user
USER node

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]