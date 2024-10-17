FROM node:16-alpine
WORKDIR /frontend
COPY package.json package-lock.json /frontend/
RUN npm ci
COPY bundles-src bundles-src

