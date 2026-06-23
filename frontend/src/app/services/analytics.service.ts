import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  private http = inject(HttpClient);
  private apiUrl = '/api/v1/analytics';

  getDashboardAnalytics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/dashboard`);
  }
}
