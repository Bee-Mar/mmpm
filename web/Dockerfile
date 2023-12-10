# Use a multi-stage build to keep the final image as small as possible
FROM node:18 as build-stage

WORKDIR /app

# Copy package.json and install dependencies
COPY angular-app/package*.json ./
RUN npm install

# Copy the rest of the Angular app and build it
COPY . ./
RUN rm -rf node_modules
RUN npm run build

# Copy the built Angular app from the previous stage
COPY --from=build-stage /app/dist/ /app/angular-app

# Expose the port the app runs on
EXPOSE 6789

# Start both the Angular app and the Python server
CMD ["sh", "-c", "cd angular-app && npx http-server"]

