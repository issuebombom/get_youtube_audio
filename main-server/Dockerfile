# main-server
FROM node:18 AS builder
WORKDIR /app
COPY package*.json /app/
RUN npm install

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules/ /app/node_modules/
COPY . .
RUN npm run build
CMD ["node", "dist/main.js"]