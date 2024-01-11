# main-server
FROM node:18-alpine
COPY package*.json /app/
COPY package-lock.json /app/
WORKDIR /app/
RUN npm install
COPY . .
RUN npm run build
CMD ["node", "dist/main.js"]