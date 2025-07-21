import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, delay } from 'rxjs/operators';
import { API } from '../constants/api.constants';

export interface FilterParams {
  engineer_id: number | null;
  status_ids: number[] | null;
  start_date: string | null;
  end_date: string | null;
  page: number;
  per_page: number;
}

@Injectable({
  providedIn: 'root',
})
export class ManagerService {
  private requestsSubject = new BehaviorSubject<any[]>([]);
  public requests$ = this.requestsSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getAuthHeaders(): HttpHeaders {
    const token = localStorage.getItem('token') || '';
    return new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true',
    });
  }

  fetchRequests(filters: FilterParams): Observable<any> {
    return this.http
      .post(API.FILTER_REQUESTS, filters, {
        headers: this.getAuthHeaders(),
      })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при загрузке заявок:', error);
          return of({ requests: [], total: 0 });
        })
      );
  }

  updateRequests(data: any[]) {
    this.requestsSubject.next(data);
  }

  getStoredRequests(): any[] {
    return this.requestsSubject.getValue();
  }

  getAllEngineers(): Observable<any[]> {
    const allEngineers: any[] = [];
    const perPage = 10;
    let page = 1;

    const loadPage = (): Observable<{ engineers: any[] }> => {
      return this.http
        .post<{ engineers: any[] }>(
          API.ENGINEERS_STATS,
          { page, per_page: perPage },
          { headers: this.getAuthHeaders() }
        )
        .pipe(catchError(() => of({ engineers: [] })));
    };

    return new Observable<any[]>((observer) => {
      const load = () => {
        loadPage().subscribe((response) => {
          if (!response || response.engineers.length === 0) {
            observer.next(allEngineers);
            observer.complete();
            return;
          }

          allEngineers.push(...response.engineers);
          page++;
          load();
        });
      };
      load();
    });
  }

  updateRequest(requestId: number, data: any): Observable<any> {
    return this.http
      .put(API.REQUEST_BY_ID(requestId), data, {
        headers: this.getAuthHeaders(),
      })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при обновлении заявки:', error);
          return of(null);
        })
      );
  }

  assignEngineerToRequest(
    requestId: number,
    engineerId: number
  ): Observable<any> {
    return this.updateRequest(requestId, { engineer_id: engineerId });
  }

  getRequestHistory(requestId: number): Observable<any> {
    return this.http
      .get(API.REQUEST_HISTORY(requestId), {
        headers: this.getAuthHeaders(),
      })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при получении истории:', error);
          return of({ history: [], request_id: requestId });
        })
      );
  }

  public lastUsedFilters: FilterParams = {
    engineer_id: null,
    status_ids: [1, 2, 3, 4],
    start_date: null,
    end_date: null,
    page: 1,
    per_page: 10,
  };

  createRequest(data: any): Observable<any> {
    return new Observable((observer) => {
      this.http
        .post(API.REQUESTS + '/', data, {
          headers: this.getAuthHeaders(),
        })
        .pipe(
          catchError((error) => {
            console.error('Ошибка при создании заявки:', error);
            observer.next(null);
            observer.complete();
            return of(null);
          })
        )
        .subscribe((res: any) => {
          if (res && res.request_id) {
            // После успешного создания — обновляем заявки
            const currentFilters = {
              ...this.lastUsedFilters, // добавим это поле ниже
              page: 1,
            };

            this.fetchRequests(currentFilters).subscribe((response) => {
              this.updateRequests(response.requests || []);
            });
          }

          observer.next(res);
          observer.complete();
        });
    });
  }

  fetchEngineersPage(page: number, per_page: number): Observable<any> {
    return this.http
      .post(
        API.ENGINEERS_STATS,
        { page, per_page },
        { headers: this.getAuthHeaders() }
      )
      .pipe(
        catchError((error) => {
          console.error('Ошибка при загрузке инженеров:', error);
          return of({ engineers: [], total: 0 }); // Возврат пустого результата при ошибке
        })
      );
  }

  useMock = false;

  updateEngineerBalance(
    engineerId: number,
    newBalance: number
  ): Observable<any> {
    if (this.useMock) {
      console.log(
        `[MOCK] Обновление баланса инженера ${engineerId} на ${newBalance}`
      );
      // Эмулируем успешный ответ с задержкой 500мс
      return of({
        message: 'Balance updated successfully',
        new_balance: newBalance,
        old_balance: '0.00',
      }).pipe(delay(500));
    } else {
      const body = { new_balance: newBalance };
      return this.http
        .put(API.BALANCE_UPDATE(engineerId), body, {
          headers: this.getAuthHeaders(),
        })
        .pipe(
          catchError((error) => {
            console.error('Ошибка при обновлении баланса:', error);
            return of(null);
          })
        );
    }
  }

  createUser(employee: any): Observable<any> {
    const roleMapping: { [key: string]: number } = {
      engineer: 1,
      operator: 2,
      manager: 3,
    };

    const payload: any = {
      name: employee.name,
      login: employee.login,
      password: employee.password,
      role_id: roleMapping[employee.role],
      phone: '89000000000', // можно заменить на динамическое значение
      email: 'test@example.com', // можно заменить на динамическое значение
    };

    if (payload.role_id === 1) {
      payload.schedule = 'с пятницы по среду с 8 до 6';
    }

    return this.http.post(API.USERS, payload, {
      headers: this.getAuthHeaders(),
    });
  }

  deleteRequest(requestId: number): Observable<any> {
    const url = API.DELETE_REQUEST(requestId);
    return this.http.put(url, null, { headers: this.getAuthHeaders() }).pipe(
      catchError((error) => {
        console.error('Ошибка при удалении заявки:', error);
        return of(null);
      })
    );
  }

  getUserCredentials(userId: number): Observable<any> {
    return this.http
      .get(API.SHOW_LOGIN(userId), {
        headers: this.getAuthHeaders(),
      })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при получении логина и пароля:', error);
          return of(null);
        })
      );
  }

  deleteUser(userId: number): Observable<any> {
    return this.http
      .delete(API.DELETE_USER(userId), { headers: this.getAuthHeaders() })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при удалении пользователя:', error);
          return of(null);
        })
      );
  }

  getAllUsers(): Observable<any[]> {
    return this.http
      .get<any[]>(API.GET_USERS, {
        headers: this.getAuthHeaders(),
      })
      .pipe(
        catchError((error) => {
          console.error('Ошибка при получении всех пользователей:', error);
          return of([]);
        })
      );
  }
}
