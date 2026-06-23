import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GenerateLearningPlanRequest {
  based_on_interview_id?: string;
  target_proficiency: number;
  available_hours_per_week: number;
  interview_type?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LearningService {
  private http = inject(HttpClient);
  private apiUrl = '/api/v1/learning-plans';

  generateLearningPlan(request: GenerateLearningPlanRequest): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/generate`, request);
  }

  getLearningPlan(planId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${planId}`);
  }

  listLearningPlans(): Observable<any> {
    return this.http.get<any>(this.apiUrl);
  }
}
