# Dashboard Frontend Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY dashboard/frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY dashboard/frontend/src ./src
COPY dashboard/frontend/public ./public
COPY dashboard/frontend/tailwind.config.js ./
COPY dashboard/frontend/postcss.config.js ./

# Expose the port
EXPOSE 3000

# Start the development server
CMD ["npm", "start"]