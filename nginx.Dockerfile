# Этап сборки Angular приложения
FROM node AS build

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY frontend/package*.json ./

# Устанавливаем все зависимости (включая devDependencies для Angular CLI)
RUN npm ci

# Копируем исходный код
COPY frontend/ ./

# Собираем приложение для продакшена
RUN npm run build

# Этап nginx
FROM nginx:alpine

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем собранное Angular приложение
COPY --from=build /app/dist/techRepair/browser /usr/share/nginx/html

# Открываем порт 80
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]
