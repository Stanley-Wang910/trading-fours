# Use the official Node.js image
FROM node:20.11.1

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React app
RUN npm run build

# Install a simple HTTP server to serve the static files
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Serve the React app
CMD ["serve", "-s", "build"]
