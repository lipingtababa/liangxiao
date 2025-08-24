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

# Switch to non-root user
USER node

# Start the poller
CMD ["npm", "start"]