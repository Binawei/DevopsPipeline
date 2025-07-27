FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

RUN addgroup -g 1001 -S appuser && adduser -S appuser -G appuser
USER appuser

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]