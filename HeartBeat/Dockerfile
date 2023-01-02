FROM node:alpine

# Create app directory
WORKDIR /heartbeat

# Copy dependencies
COPY node_modules ./node_modules
COPY package.json ./package.json
COPY yarn.lock yarn.lock

# Copy heartbeat code
COPY heartbeat.js heartbeat.js


# Start the app
CMD ["node", "heartbeat.js"]
