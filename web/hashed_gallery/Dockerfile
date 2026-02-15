# Use Node.js LTS version
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY src/package*.json ./

# Install dependencies
RUN npm install --production

# Copy application source
COPY src/ .

# Expose the application port
EXPOSE 3000

# Set environment variable
ENV PORT=3000

# Start the application
CMD ["npm", "start"]
