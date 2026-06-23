import { Component, inject, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { InterviewService, Question } from '../../services/interview.service';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-conduct-interview',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="conduct-container">
      
      <!-- Connecting State -->
      <div *ngIf="connectionState === 'connecting'" class="loading-state glass-panel">
        <span class="material-symbols-outlined spinner text-neon-indigo">sync</span>
        <h2>Connecting to AI Agent Room</h2>
        <p>Orchestrating workflows, loading knowledge graphs...</p>
      </div>

      <!-- Error State -->
      <div *ngIf="connectionState === 'error'" class="error-state glass-panel">
        <span class="material-symbols-outlined text-neon-danger">error</span>
        <h2>Connection Lost</h2>
        <p>{{ errorText || 'Unable to establish streaming websocket with the evaluator agents.' }}</p>
        <button (click)="retryConnection()" class="btn btn-primary">Reconnect</button>
      </div>

      <!-- Active Interview Workspace -->
      <div *ngIf="connectionState === 'active' && !isFinished" class="workspace">
        
        <!-- Live Header Stats -->
        <div class="glass-panel stats-bar">
          <div class="stat-item">
            <span class="stat-label">Progress</span>
            <span class="stat-value text-neon-cyan">{{ currentQuestionNumber }} / {{ totalQuestionsPlanned }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Running Score</span>
            <span class="stat-value text-neon-indigo">{{ runningScore | number:'1.1-1' }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Timer</span>
            <span class="stat-value">{{ formattedTime }}</span>
          </div>
          <div class="stat-item flex-right">
            <span class="badge badge-info">{{ interviewDetails?.interview_type | uppercase }}</span>
            <span class="badge" [class.badge-success]="currentQuestion?.difficulty === 'easy'" [class.badge-warning]="currentQuestion?.difficulty === 'medium'" [class.badge-danger]="currentQuestion?.difficulty === 'hard'">
              {{ currentQuestion?.difficulty | uppercase }}
            </span>
          </div>
        </div>

        <!-- Main Splits -->
        <div class="workspace-body">
          
          <!-- Left: Question Panel -->
          <div class="glass-panel question-panel">
            <div class="panel-section-header">
              <span class="material-symbols-outlined text-neon-indigo">help_center</span>
              <h2>Active Question</h2>
            </div>
            
            <div class="question-content">
              {{ currentQuestion?.content }}
            </div>

            <div class="question-meta" *ngIf="currentQuestion?.skill_areas">
              <span class="meta-label">Focus Skills:</span>
              <span class="badge badge-info" *ngFor="let s of currentQuestion?.skill_areas">{{ s }}</span>
            </div>

            <!-- Hints Section -->
            <div class="hints-box" [class.expanded]="showHints">
              <div class="hints-header" (click)="toggleHints()">
                <span class="material-symbols-outlined">lightbulb</span>
                <span>Hints & Guidance</span>
                <span class="material-symbols-outlined chevron">{{ showHints ? 'expand_less' : 'expand_more' }}</span>
              </div>
              
              <div class="hints-body" *ngIf="showHints">
                <button *ngIf="!hintsList || hintsList.length === 0" (click)="getHint()" class="btn btn-secondary btn-sm">
                  Request AI Hint
                </button>
                <ul class="hints-list" *ngIf="hintsList && hintsList.length > 0">
                  <li *ngFor="let h of hintsList">{{ h }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Right: Answer Work Panel -->
          <div class="glass-panel answer-panel">
            <div class="panel-section-header">
              <span class="material-symbols-outlined text-neon-cyan">rate_review</span>
              <h2>Your Answer Workspace</h2>
            </div>

            <!-- Text/Code Input -->
            <div class="input-container">
              <textarea 
                [(ngModel)]="userAnswer" 
                [disabled]="isEvaluating" 
                class="form-control text-area-editor" 
                placeholder="Type your detailed answer or design outline here... Use paragraphs and structure to communicate clearly."
              ></textarea>
            </div>

            <div class="workspace-footer">
              <div class="editor-stats">
                <span>Words: {{ wordCount }}</span>
                <span>Chars: {{ userAnswer.length }}</span>
              </div>

              <!-- Button actions -->
              <button 
                (click)="submitAnswer()" 
                [disabled]="userAnswer.trim().length < 10 || isEvaluating" 
                class="btn btn-primary btn-submit"
              >
                <span *ngIf="isEvaluating" class="material-symbols-outlined spinner">sync</span>
                <span>{{ isEvaluating ? 'Evaluating Answer...' : 'Submit Answer' }}</span>
              </button>
            </div>
          </div>

        </div>

        <!-- Evaluation Overlay Dialog -->
        <div class="evaluation-overlay" *ngIf="latestEvaluation">
          <div class="glass-panel evaluation-card pulse-glow">
            <div class="eval-header">
              <span class="material-symbols-outlined logo-icon text-neon-indigo">verified</span>
              <h2>AI Agent Evaluation</h2>
              <span class="badge badge-success font-bold font-display text-lg">Score: {{ latestEvaluation.overall }}%</span>
            </div>

            <div class="eval-metrics">
              <div class="metric-progress">
                <span class="metric-name">Technical Accuracy:</span>
                <div class="bar-container">
                  <div class="bar success" [style.width.%]="latestEvaluation.technical_accuracy * 10"></div>
                </div>
                <span class="score-num">{{ latestEvaluation.technical_accuracy }}/10</span>
              </div>

              <div class="metric-progress">
                <span class="metric-name">Completeness:</span>
                <div class="bar-container">
                  <div class="bar success" [style.width.%]="latestEvaluation.completeness * 10"></div>
                </div>
                <span class="score-num">{{ latestEvaluation.completeness }}/10</span>
              </div>

              <div class="metric-progress">
                <span class="metric-name">Communication Quality:</span>
                <div class="bar-container">
                  <div class="bar success" [style.width.%]="latestEvaluation.communication_quality * 10"></div>
                </div>
                <span class="score-num">{{ latestEvaluation.communication_quality }}/10</span>
              </div>
            </div>

            <p class="summary-text">{{ latestEvaluation.feedback_summary }}</p>

            <div class="strengths-weaknesses">
              <div class="sw-column">
                <h4>Strengths Identified</h4>
                <ul>
                  <li *ngFor="let s of latestEvaluation.strengths">{{ s }}</li>
                </ul>
              </div>
              <div class="sw-column">
                <h4>Suggested Improvements</h4>
                <ul>
                  <li *ngFor="let i of latestEvaluation.improvements">{{ i }}</li>
                </ul>
              </div>
            </div>

            <div class="eval-actions">
              <button (click)="proceedToNext()" class="btn btn-primary">
                Proceed to {{ currentQuestionNumber >= totalQuestionsPlanned ? 'Interview Summary' : 'Next Question' }}
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- Report Card State (Completed) -->
      <div *ngIf="isFinished" class="report-card-container">
        <div class="glass-panel report-card pulse-glow">
          <div class="brand-header">
            <span class="material-symbols-outlined logo-icon text-neon-cyan">workspace_premium</span>
            <h1>Interview Finished</h1>
            <p>Generated by Feedback & Performance Agents</p>
          </div>

          <div class="overall-result">
            <div class="radial-score">
              <span class="score-percentage text-neon-cyan">{{ finalReport?.overall_score || 0 }}%</span>
              <span class="score-label">Overall Score</span>
            </div>
            <div class="score-trend-details">
              <h3>Performance Trend: <span class="badge" [class.badge-success]="finalReport?.score_trend === 'improving'" [class.badge-warning]="finalReport?.score_trend === 'stable'" [class.badge-danger]="finalReport?.score_trend === 'declining'">{{ finalReport?.score_trend }}</span></h3>
              <p>{{ finalReport?.message }}</p>
            </div>
          </div>

          <div class="actions-section">
            <button (click)="generatePlan()" [disabled]="isGeneratingPlan" class="btn btn-primary w-full btn-lg">
              <span *ngIf="isGeneratingPlan" class="material-symbols-outlined spinner">sync</span>
              <span>{{ isGeneratingPlan ? 'Generating Coach Plan...' : 'Generate Personalized Learning Plan' }}</span>
            </button>
            <button routerLink="/" class="btn btn-secondary w-full">Return to Dashboard</button>
          </div>
        </div>
      </div>

    </div>
  `,
  styles: [`
    .conduct-container {
      width: 100%;
    }
    
    .loading-state, .error-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 40px;
      text-align: center;
      gap: 16px;
      margin-top: 40px;
    }
    
    .loading-state span, .error-state span {
      font-size: 3.5rem !important;
    }
    
    .workspace {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    /* Stats Bar */
    .stats-bar {
      display: flex;
      align-items: center;
      gap: 32px;
      padding: 16px 24px;
      border-radius: var(--border-radius-sm);
    }
    
    .stat-item {
      display: flex;
      flex-direction: column;
    }
    
    .stat-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .stat-value {
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 1.15rem;
    }
    
    .flex-right {
      margin-left: auto;
      display: flex;
      gap: 8px;
    }
    
    /* Splits */
    .workspace-body {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 24px;
    }
    
    @media (max-width: 992px) {
      .workspace-body {
        grid-template-columns: 1fr;
      }
    }
    
    .panel-section-header {
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 12px;
      margin-bottom: 16px;
    }
    
    .panel-section-header h2 {
      font-size: 1.15rem;
    }
    
    .question-content {
      font-size: 1.05rem;
      line-height: 1.5;
      color: var(--text-primary);
      margin-bottom: 24px;
      white-space: pre-wrap;
    }
    
    .question-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--text-secondary);
      margin-bottom: 24px;
    }
    
    .meta-label {
      font-weight: 600;
    }
    
    /* Hints */
    .hints-box {
      border: 1px solid var(--glass-border);
      border-radius: var(--border-radius-sm);
      background: rgba(255, 255, 255, 0.01);
      overflow: hidden;
    }
    
    .hints-header {
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.9rem;
      user-select: none;
      color: var(--text-secondary);
    }
    
    .hints-header:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.02);
    }
    
    .hints-header .chevron {
      margin-left: auto;
    }
    
    .hints-body {
      padding: 16px;
      border-top: 1px solid var(--glass-border);
    }
    
    .hints-list {
      padding-left: 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    /* Answer Panel */
    .answer-panel {
      display: flex;
      flex-direction: column;
    }
    
    .input-container {
      flex: 1;
      min-height: 250px;
      margin-bottom: 16px;
    }
    
    .text-area-editor {
      width: 100%;
      height: 100%;
      min-height: 250px;
      font-family: var(--font-sans);
      line-height: 1.5;
      padding: 16px;
    }
    
    .workspace-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .editor-stats {
      font-size: 0.8rem;
      color: var(--text-muted);
      display: flex;
      gap: 16px;
    }
    
    .btn-submit {
      padding: 10px 24px;
    }
    
    /* Evaluation Overlay */
    .evaluation-overlay {
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      right: 0;
      background: rgba(4, 5, 12, 0.85);
      z-index: 200;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      backdrop-filter: blur(8px);
    }
    
    .evaluation-card {
      width: 100%;
      max-width: 650px;
      background: var(--bg-secondary);
      padding: 32px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    
    .eval-header {
      display: flex;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }
    
    .eval-header h2 {
      font-size: 1.3rem;
      margin-right: auto;
    }
    
    .eval-metrics {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 24px;
    }
    
    .metric-progress {
      display: grid;
      grid-template-columns: 180px 1fr 60px;
      align-items: center;
      gap: 16px;
    }
    
    .metric-name {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-secondary);
    }
    
    .bar-container {
      height: 6px;
      background: var(--bg-tertiary);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .bar {
      height: 100%;
      border-radius: 3px;
    }
    
    .bar.success {
      background: var(--success);
    }
    
    .score-num {
      font-size: 0.85rem;
      font-weight: 700;
      text-align: right;
    }
    
    .summary-text {
      font-size: 0.95rem;
      color: var(--text-secondary);
      line-height: 1.5;
      margin-bottom: 24px;
      background: rgba(255, 255, 255, 0.01);
      padding: 16px;
      border-radius: var(--border-radius-sm);
      border-left: 3px solid var(--primary);
    }
    
    .strengths-weaknesses {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 30px;
    }
    
    @media (max-width: 576px) {
      .strengths-weaknesses {
        grid-template-columns: 1fr;
      }
    }
    
    .sw-column h4 {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 12px;
    }
    
    .sw-column ul {
      padding-left: 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    .eval-actions {
      display: flex;
      justify-content: flex-end;
    }
    
    /* Report Card */
    .report-card-container {
      max-width: 600px;
      margin: 40px auto 0 auto;
    }
    
    .report-card {
      padding: 40px;
      text-align: center;
    }
    
    .overall-result {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
      margin: 32px 0;
    }
    
    .radial-score {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      border: 8px solid var(--primary-glow);
      border-top-color: var(--secondary);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 20px var(--primary-glow);
    }
    
    .score-percentage {
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 2rem;
    }
    
    .score-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    
    .score-trend-details h3 {
      font-size: 1.15rem;
      margin-bottom: 8px;
    }
    
    .score-trend-details p {
      font-size: 0.95rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }
    
    .actions-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .btn-lg {
      padding: 14px;
      font-size: 1rem;
    }
  `]
})
export class ConductInterviewComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private interviewService = inject(InterviewService);
  private learningService = inject(LearningService);

  interviewId = '';
  connectionState: 'connecting' | 'active' | 'error' = 'connecting';
  errorText = '';

  interviewDetails: any = null;
  currentQuestion: Question | null = null;
  currentQuestionNumber = 1;
  totalQuestionsPlanned = 5;
  runningScore = 70.0;
  
  userAnswer = '';
  isEvaluating = false;
  latestEvaluation: any = null;

  showHints = false;
  hintsList: string[] = [];

  isFinished = false;
  finalReport: any = null;
  isGeneratingPlan = false;

  // Timer Variables
  timerSeconds = 0;
  timerInterval: any = null;
  formattedTime = '00:00';

  // WebSocket Subscription
  private streamSubscription?: Subscription;

  ngOnInit(): void {
    this.interviewId = this.route.snapshot.paramMap.get('id') || '';
    if (!this.interviewId) {
      this.router.navigate(['/']);
      return;
    }

    this.fetchDetailsAndConnect();
  }

  ngOnDestroy(): void {
    this.cleanup();
  }

  get wordCount(): number {
    return this.userAnswer ? this.userAnswer.trim().split(/\s+/).filter(w => w.length > 0).length : 0;
  }

  private cleanup(): void {
    this.stopTimer();
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe();
    }
    this.interviewService.disconnect();
  }

  fetchDetailsAndConnect(): void {
    this.connectionState = 'connecting';
    
    this.interviewService.getInterview(this.interviewId).subscribe({
      next: (details) => {
        this.interviewDetails = details;
        this.totalQuestionsPlanned = details.total_questions_planned;
        this.runningScore = details.metrics?.overall_score || 70.0;
        this.currentQuestionNumber = details.current_question_index + 1;
        
        this.connectStream();
      },
      error: () => {
        this.connectionState = 'error';
        this.errorText = 'Could not load interview meta-details from backend database.';
      }
    });
  }

  connectStream(): void {
    const socket$ = this.interviewService.connectToStream(this.interviewId);
    
    this.streamSubscription = socket$.subscribe({
      next: (msg) => {
        this.handleSocketMessage(msg);
      },
      error: (err) => {
        console.error('Socket error', err);
        this.connectionState = 'error';
        this.errorText = 'Websocket connection interrupted. Real-time evaluations unavailable.';
      },
      complete: () => {
        console.log('Socket stream closed');
      }
    });
  }

  retryConnection(): void {
    this.cleanup();
    this.fetchDetailsAndConnect();
  }

  handleSocketMessage(msg: any): void {
    switch (msg.type) {
      case 'connected':
        this.connectionState = 'active';
        // Initialize interview flow
        this.interviewService.sendInit({
          interview_type: this.interviewDetails.interview_type,
          difficulty_level: this.interviewDetails.difficulty_level,
          total_questions: this.totalQuestionsPlanned
        });
        break;

      case 'question':
        this.currentQuestion = msg.question;
        this.currentQuestionNumber = msg.question_number;
        this.userAnswer = '';
        this.latestEvaluation = null;
        this.isEvaluating = false;
        this.hintsList = [];
        this.showHints = false;
        this.startTimer();
        break;

      case 'answer_received':
        this.isEvaluating = true;
        this.stopTimer();
        break;

      case 'evaluation':
        this.latestEvaluation = msg.evaluation;
        this.isEvaluating = false;
        break;

      case 'metrics_update':
        this.runningScore = msg.metrics.overall_score;
        break;

      case 'hint':
        this.hintsList = msg.hints;
        break;

      case 'interview_complete':
        this.isFinished = true;
        this.finalReport = msg.final_report;
        this.cleanup();
        break;

      case 'error':
        console.error('Agent error: ' + msg.message);
        this.isEvaluating = false;
        break;
    }
  }

  submitAnswer(): void {
    if (!this.userAnswer.trim() || this.isEvaluating) return;
    this.interviewService.sendAnswer(this.userAnswer);
  }

  getHint(): void {
    this.interviewService.requestHint();
  }

  toggleHints(): void {
    this.showHints = !this.showHints;
    if (this.showHints && (!this.hintsList || this.hintsList.length === 0)) {
      this.getHint();
    }
  }

  proceedToNext(): void {
    // Evaluation overlay action
    this.latestEvaluation = null;
  }

  generatePlan(): void {
    this.isGeneratingPlan = true;
    this.learningService.generateLearningPlan({
      based_on_interview_id: this.interviewId,
      target_proficiency: 85,
      available_hours_per_week: 10,
      interview_type: this.interviewDetails.interview_type
    }).subscribe({
      next: (plan) => {
        this.isGeneratingPlan = false;
        this.router.navigate(['/learning', plan.learning_plan_id]);
      },
      error: () => {
        this.isGeneratingPlan = false;
        // Proceed back to home if failure
        this.router.navigate(['/learning']);
      }
    });
  }

  // Timer Methods
  startTimer(): void {
    this.stopTimer();
    this.timerSeconds = 0;
    this.formattedTime = '00:00';
    
    this.timerInterval = setInterval(() => {
      this.timerSeconds++;
      const mins = Math.floor(this.timerSeconds / 60);
      const secs = this.timerSeconds % 60;
      this.formattedTime = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
  }

  stopTimer(): void {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }
}
