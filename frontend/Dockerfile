FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 5173

# Custom Nginx configuration to listen on 5173 and proxy to backend
RUN printf 'server {\n\
    listen 5173;\n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html index.htm;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    location /api/ {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /health {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /analyze {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /rewrite {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /conversations {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /insights {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
    location /samples {\n\
        proxy_pass http://backend:8000;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]

