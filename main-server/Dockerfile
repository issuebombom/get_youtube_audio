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

# 아래 방식이 위 방식보다 이미지 크기가 50mb가량 더 나감
# FROM node:18-alpine
# WORKDIR /app
# COPY package*.json /app/
# RUN npm install
# COPY . .
# RUN npm run build
# CMD ["node", "dist/main.js"]