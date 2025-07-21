import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API } from '../constants/api.constants';

export interface RequestItem {
  address: string;
  assigned_time: string;
  creation_date: string;
  customer_name: string;
  description: string;
  done_time: string | null;
  engineer_id: number;
  equipment: string;
  in_works_time: string | null;
  operator_id: number;
  phone: string;
  request_id: number;
  status_id: number;
}

export interface EngineerRequestsResponse {
  date_filter: string;
  engineer_id: string;
  requests: RequestItem[];
  total: number;
}

export interface CompletedRequestsResponse {
  engineer_id: string;
  page: number;
  per_page: number;
  requests: RequestItem[];
  total: number;
}

@Injectable({
  providedIn: 'root',
})
export class EngineerService {
  private readonly baseUrl = API.ENGINEER_REQUESTS;

  constructor(private http: HttpClient) {}

  getEngineerRequests(date: string): Observable<EngineerRequestsResponse> {
    const headers = this.createAuthHeaders();
    const url = `${this.baseUrl}?date=${encodeURIComponent(date)}`;
    return this.http.get<EngineerRequestsResponse>(url, { headers });
  }

  getEngineerActive(): Observable<EngineerRequestsResponse> {
    const headers = this.createAuthHeaders();
    const url = `${this.baseUrl}/active`;
    return this.http.get<EngineerRequestsResponse>(url, { headers });
  }

  updateRequestTimes(
    requestId: number,
    payload: Partial<RequestItem>
  ): Observable<any> {
    const headers = this.createAuthHeaders(true);
    const url = `${this.baseUrl}/${requestId}`;
    return this.http.put(url, payload, { headers });
  }

  private createAuthHeaders(withJsonContent = false): HttpHeaders {
    const token = localStorage.getItem('token') || '';
    let headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
      'ngrok-skip-browser-warning': 'true',
    });
    return withJsonContent
      ? headers.set('Content-Type', 'application/json')
      : headers;
  }

  getCompletedRequests(page: number): Observable<CompletedRequestsResponse> {
    const headers = this.createAuthHeaders();
    const url = `${this.baseUrl}/completed/${page}`;
    return this.http.get<CompletedRequestsResponse>(url, { headers });
  }

  getEngineerStats(page: number, perPage: number) {
    const headers = this.createAuthHeaders(true);
    const body = { page, per_page: perPage };
    return this.http.post<any>(API.ENGINEERS_STATS, body, { headers });
  }
}
