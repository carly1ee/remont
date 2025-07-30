//const BASE_URL = 'http://192.168.31.248:5000';
const BASE_URL = 'http://localhost:5000/api';

export const API = {
  LOGIN: `${BASE_URL}/users/login`, // Авторизация пользователя
  USERS: `${BASE_URL}/users/register`, // Создание нового пользователя
  REQUESTS: `${BASE_URL}/requests`, // Создание новой заявки
  FILTER_REQUESTS: `${BASE_URL}/requests/filter`, // Получение заявок по фильтру
  ENGINEERS_STATS: `${BASE_URL}/requests/engineers/stats`, // Получение статистики по инженерам
  REQUEST_BY_ID: (id: number) => `${BASE_URL}/requests/engineer/${id}`, // Обновление заявки по ID
  REQUEST_HISTORY: (id: number) => `${BASE_URL}/requests/history/${id}`, // Получение истории изменений по заявке
  BALANCE_UPDATE: (id: number) => `${BASE_URL}/balance/${id}`, // Обновление баланса инженера
  ENGINEER_REQUESTS: `${BASE_URL}/requests/engineer`, // Получение заявок для инженера
  DELETE_REQUEST: (id: number) => `${BASE_URL}/requests/delete/${id}`, //удаление заявки
  SHOW_LOGIN: (id: number) => `${BASE_URL}/users/${id}/credentials`, // просмотр логинов пользователей
  DELETE_USER: (id: number) => `${BASE_URL}/users/${id}`, //удаление кадра
  GET_USERS: `${BASE_URL}/users/`, //получение всех кадров
};
