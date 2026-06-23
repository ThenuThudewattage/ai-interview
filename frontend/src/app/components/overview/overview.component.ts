import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-overview',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="overview-container">
      <!-- Loading State -->
      <div *ngIf="isLoading" class="loading-state">
        <span class="material-symbols-outlined spinner text-neon-cyan">sync</span>
        <p>Loading your dashboard analytics...</p>
      </div>

      <!-- Main Content -->
      <div *ngIf="!isLoading" class="dashboard-grid">
        
        <!-- Metrics Row -->
        <div class="metrics-row">
          <div class="glass-panel metric-card">
            <div class="metric-icon success">
              <span class="material-symbols-outlined">analytics</span>
            </div>
            <div class="metric-info">
              <span class="metric-value">{{ data?.interview_stats?.average_score || 0 }}%</span>
              <span class="metric-label">Average Score</span>
            </div>
          </div>

          <div class="glass-panel metric-card">
            <div class="metric-icon primary">
              <span class="material-symbols-outlined">assignment_turned_in</span>
            </div>
            <div class="metric-info">
              <span class="metric-value">{{ data?.interview_stats?.completed_interviews || 0 }}</span>
              <span class="metric-label">Completed Sessions</span>
            </div>
          </div>

          <div class="glass-panel metric-card">
            <div class="metric-icon secondary">
              <span class="material-symbols-outlined">speed</span>
            </div>
            <div class="metric-info">
              <span class="metric-value">{{ data?.interview_stats?.completion_rate || 0 }}%</span>
              <span class="metric-label">Completion Rate</span>
            </div>
          </div>

          <div class="glass-panel metric-card">
            <div class="metric-icon warning">
              <span class="material-symbols-outlined">warning</span>
            </div>
            <div class="metric-info">
              <span class="metric-value">{{ data?.skill_overview?.active_skill_gaps || 0 }}</span>
              <span class="metric-label">Active Skill Gaps</span>
            </div>
          </div>
        </div>

        <div class="dashboard-body">
          <!-- Left Column: Skill Matrix -->
          <div class="dashboard-left">
            <div class="glass-panel skill-card">
              <h2 class="panel-title">Skill Profiler</h2>
              <p class="panel-subtitle">Your parsed proficiencies across major interview domains</p>
              
              <div *ngIf="!data?.skill_breakdown || data.skill_breakdown.length === 0" class="empty-list">
                <span class="material-symbols-outlined">info</span>
                <p>Complete your first interview or upload a resume to view skill analysis.</p>
              </div>

              <div class="skills-list" *ngIf="data?.skill_breakdown && data.skill_breakdown.length > 0">
                <div class="skill-item" *ngFor="let s of data.skill_breakdown">
                  <div class="skill-info">
                    <span class="skill-name">{{ s.skill }}</span>
                    <span class="skill-val">{{ s.proficiency }}%</span>
                  </div>
                  <!-- Beautiful Glowing Progress Bar -->
                  <div class="progress-container">
                    <div class="progress-bar" [style.width.%]="s.proficiency" [class.high]="s.proficiency >= 70" [class.medium]="s.proficiency >= 50 && s.proficiency < 70" [class.low]="s.proficiency < 50"></div>
                  </div>
                  <div class="skill-meta">
                    <span class="badge badge-info">{{ s.category }}</span>
                    <span class="confidence">Confidence: {{ s.confidence }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Recent Sessions & Quick Start -->
          <div class="dashboard-right">
            <div class="glass-panel action-card">
              <h3 class="panel-title text-neon-cyan">Ready to excel?</h3>
              <p class="panel-description">Start a mock interview session and get structured real-time AI feedback.</p>
              <button routerLink="/interviews/start" class="btn btn-accent w-full">
                <span class="material-symbols-outlined">play_circle</span>
                <span>Start Mock Session</span>
              </button>
            </div>

            <div class="glass-panel recent-card">
              <h2 class="panel-title">Recent Interviews</h2>
              
              <div *ngIf="!data?.recent_interviews || data.recent_interviews.length === 0" class="empty-list">
                <p>No interviews taken yet.</p>
              </div>

              <div class="recent-list" *ngIf="data?.recent_interviews && data.recent_interviews.length > 0">
                <div class="recent-item" *ngFor="let i of data.recent_interviews">
                  <div class="recent-meta">
                    <span class="recent-title">{{ i.interview_type | uppercase }}</span>
                    <span class="recent-date">{{ i.started_at | date:'shortDate' }}</span>
                  </div>
                  <div class="recent-details">
                    <span class="badge" [class.badge-success]="i.status === 'completed'" [class.badge-warning]="i.status !== 'completed'">{{ i.status }}</span>
                    <span class="recent-score" *ngIf="i.overall_score !== null">Score: <strong>{{ i.overall_score }}%</strong></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .overview-container {
      width: 100%;
    }
    
    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 100px 0;
      gap: 16px;
      color: var(--text-secondary);
    }
    
    .spinner {
      font-size: 3rem !important;
    }
    
    .dashboard-grid {
      display: flex;
      flex-direction: column;
      gap: 32px;
    }
    
    /* Metrics Row */
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 24px;
    }
    
    @media (max-width: 1200px) {
      .metrics-row {
        grid-template-columns: repeat(2, 1fr);
      }
    }
    
    @media (max-width: 576px) {
      .metrics-row {
        grid-template-columns: 1fr;
      }
    }
    
    .metric-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px 24px;
    }
    
    .metric-icon {
      width: 48px;
      height: 48px;
      border-radius: var(--border-radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .metric-icon span {
      font-size: 1.8rem !important;
    }
    
    .metric-icon.success {
      background: var(--success-glow);
      color: var(--success);
    }
    
    .metric-icon.primary {
      background: var(--primary-glow);
      color: var(--primary);
    }
    
    .metric-icon.secondary {
      background: var(--secondary-glow);
      color: var(--secondary);
    }
    
    .metric-icon.warning {
      background: var(--warning-glow);
      color: var(--warning);
    }
    
    .metric-info {
      display: flex;
      flex-direction: column;
    }
    
    .metric-value {
      font-family: var(--font-display);
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
    }
    
    .metric-label {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    /* Dashboard Body */
    .dashboard-body {
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 32px;
    }
    
    @media (max-width: 992px) {
      .dashboard-body {
        grid-template-columns: 1fr;
      }
    }
    
    .panel-title {
      font-size: 1.25rem;
      font-weight: 700;
      margin-bottom: 4px;
    }
    
    .panel-subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    
    /* Skill List */
    .skills-list {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    
    .skill-item {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .skill-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .skill-name {
      font-weight: 600;
      font-size: 0.95rem;
    }
    
    .skill-val {
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-primary);
    }
    
    .progress-container {
      height: 6px;
      background: var(--bg-tertiary);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .progress-bar {
      height: 100%;
      border-radius: 3px;
      transition: width var(--transition-slow) ease-out;
    }
    
    .progress-bar.high {
      background: linear-gradient(90deg, var(--secondary) 0%, var(--primary) 100%);
      box-shadow: 0 0 10px var(--secondary-glow);
    }
    
    .progress-bar.medium {
      background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
      box-shadow: 0 0 10px var(--primary-glow);
    }
    
    .progress-bar.low {
      background: linear-gradient(90deg, var(--warning) 0%, var(--error) 100%);
      box-shadow: 0 0 10px var(--warning-glow);
    }
    
    .skill-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    
    /* Quick Action Card */
    .action-card {
      background: linear-gradient(135deg, rgba(15, 19, 42, 0.6) 0%, rgba(99, 102, 241, 0.05) 100%);
      border-color: rgba(99, 102, 241, 0.2);
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 32px;
    }
    
    .panel-description {
      font-size: 0.9rem;
      color: var(--text-secondary);
      line-height: 1.4;
    }
    
    /* Recent Interviews List */
    .recent-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-top: 16px;
    }
    
    .recent-item {
      padding: 16px;
      border-radius: var(--border-radius-sm);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .recent-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .recent-title {
      font-weight: 700;
      font-size: 0.9rem;
      font-family: var(--font-display);
      color: var(--text-primary);
    }
    
    .recent-date {
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    
    .recent-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .recent-score {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }
    
    .recent-score strong {
      color: var(--primary);
    }
    
    .empty-list {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 0;
      color: var(--text-muted);
      text-align: center;
      gap: 8px;
      font-size: 0.9rem;
    }
    
    .w-full {
      width: 100%;
    }
  `]
})
export class OverviewComponent implements OnInit {
  private analyticsService = inject(AnalyticsService);

  isLoading = true;
  data: any = null;

  ngOnInit(): void {
    this.analyticsService.getDashboardAnalytics().subscribe({
      next: (res) => {
        this.data = res;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
