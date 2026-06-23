import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

export interface StartInterviewRequest {
  interview_type: string;
  difficulty_level: string;
  target_company?: string;
  target_role?: string;
  duration_minutes: number;
  total_questions: number;
}

export interface Question {
  question_id: string;
  content: string;
  difficulty: string;
  skill_areas: string[];
  estimated_time_minutes: number;
  followup_hints: string[];
}

export interface StartInterviewResponse {
  interview_id: string;
  session_id: string;
  status: string;
  interview_type: string;
  difficulty_level: string;
  started_at: string;
  first_question: Question | null;
  websocket_url: string;
}

@Injectable({
  providedIn: 'root'
})
export class InterviewService {
  private http = inject(HttpClient);
  private apiUrl = '/api/v1/interviews';
  private socket$?: WebSocketSubject<any>;

  startInterview(request: StartInterviewRequest): Observable<StartInterviewResponse> {
    return this.http.post<StartInterviewResponse>(`${this.apiUrl}/start`, request);
  }

  getInterview(interviewId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${interviewId}`);
  }

  listInterviews(limit = 20, offset = 0): Observable<any> {
    return this.http.get<any>(this.apiUrl, {
      params: { limit: limit.toString(), offset: offset.toString() }
    });
  }

  completeInterview(interviewId: string, finalScore: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/${interviewId}/complete`, {
      overall_score: finalScore,
      technical_score: finalScore,
      communication_score: finalScore
    });
  }

  getInterviewEvaluations(interviewId: string): Observable<any> {
    // Get evaluations for details display
    return this.http.get<any>(`${this.apiUrl}/${interviewId}/evaluations`);
  }

  /**
   * Connect to real-time interview stream
   */
  connectToStream(interviewId: string, wsUrl?: string): WebSocketSubject<any> {
    // Determine WS url: if it is relative or localhost, we rewrite it relative to current location
    let url = wsUrl;
    if (!url) {
      const loc = window.location;
      const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      url = `${proto}//${loc.host}/api/v1/interviews/${interviewId}/stream`;
    } else if (url.startsWith('ws://localhost:8000') || url.startsWith('wss://localhost:8000')) {
      // If we are testing on a different port or deployment, we match host
      const loc = window.location;
      const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      url = url.replace(/ws(s)?:\/\/localhost:8000/, `${proto}//${loc.host}`);
    }
    
    this.socket$ = webSocket({
      url: url,
      deserializer: msg => JSON.parse(msg.data),
      serializer: value => JSON.stringify(value)
    });
    
    return this.socket$;
  }

  disconnect(): void {
    if (this.socket$) {
      this.socket$.complete();
      this.socket$ = undefined;
    }
  }

  sendInit(config: { interview_type: string; difficulty_level: string; total_questions: number; user_skills?: any; user_context?: any }): void {
    if (this.socket$) {
      this.socket$.next({
        type: 'init',
        ...config
      });
    }
  }

  sendAnswer(answerText: string): void {
    if (this.socket$) {
      this.socket$.next({
        type: 'answer',
        answer_text: answerText
      });
    }
  }

  requestHint(): void {
    if (this.socket$) {
      this.socket$.next({
        type: 'request_hint'
      });
    }
  }
}
