FROM nginx:stable-alpine3.17-slim
# Use a multi-stage build to keep the final image as small as possible
# Stage 1: Build the Angular app
FROM node:14 as build-stage

ARG MMPM_VERSION

WORKDIR /app

# Copy package.json and install dependencies
COPY angular-app/package*.json ./
RUN npm install

# Copy the rest of the Angular app and build it
COPY angular-app/ ./
RUN npm run build

# Stage 2: Set up the Python environment
FROM python:3.8

# Install gevent and gunicorn (or any other dependencies)
RUN python3 -m pip install gevent gevent-websocket gunicorn socketio

# Create a directory for the app
WORKDIR /app

# Copy the built Angular app from the previous stage
COPY --from=build-stage /app/dist/angular-app /app/angular-app

# Copy the Python server script
COPY log_server.py /app

# Expose the port the app runs on
EXPOSE 6789

# Start both the Angular app and the Python server
CMD ["sh", "-c", "cd angular-app && npx http-server & python log_server.py"]


