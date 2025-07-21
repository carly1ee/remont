import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, Observable, of, tap } from 'rxjs';
import { API } from '../constants/api.constants';

interface LoginRequest {
  login: string;
  password: string;
}

interface User {
  email: string;
  name: string;
  phone: string;
  role: string;
  user_id: number;
}

interface LoginResponse {
  access_token: string;
  user: User;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = API.LOGIN;

  constructor(private http: HttpClient, private router: Router) {}

  //Отправляет логин и пароль на сервер.
  login(data: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(this.apiUrl, data).pipe(
      tap((response) => {
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
      })
    );
  }

  //Удаляет токен и пользователя из localStorage,
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.router.navigate(['/']);
  }

  //Удаляет токен и пользователя из localStorage,
  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }

  //Возвращает токен из localStorage.
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  //Возвращает объект пользователя (имя и роль) из localStorage.
  getUser(): {
    user_id: any;
    name: string;
    role: string;
  } | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  //Возвращает роль текущего пользователя (например: "operator", "engineer", "manager").
  getRole(): string | null {
    const user = this.getUser();
    return user ? user.role : null;
  }
}
