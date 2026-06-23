import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-learning-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="detail-container">
      <div *ngIf="isLoading" class="loading-state glass-panel">
        <span class="material-symbols-outlined spinner text-neon-cyan">sync</span>
        <p>Retrieving milestones and resources...</p>
      </div>

      <div *ngIf="!isLoading && plan" class="plan-details">
        
        <!-- Header Panel -->
        <div class="glass-panel header-card">
          <div class="header-main">
            <h1 class="plan-title text-neon-indigo">{{ plan.title }}</h1>
            <span class="badge" [class.badge-success]="plan.status === 'completed'" [class.badge-info]="plan.status === 'in_progress'">
              {{ plan.status }}
            </span>
          </div>
          <p class="plan-description">{{ plan.description || 'Structured milestones to achieve proficiency.' }}</p>
          
          <div class="progress-section">
            <div class="progress-meta">
              <span>Overall Progress</span>
              <span>{{ completionPercentage }}% Completed</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill" [style.width.%]="completionPercentage"></div>
            </div>
          </div>
        </div>

        <!-- Milestones Area -->
        <div class="milestones-timeline">
          <h2 class="timeline-title">Study Milestones</h2>
          
          <div class="milestones-list">
            <div class="milestone-item" *ngFor="let m of plan.milestones">
              
              <!-- Milestone Card -->
              <div class="glass-panel milestone-card" [class.completed]="m.status === 'completed'">
                <div class="milestone-header">
                  <div class="step-num">M{{ m.sequence_number }}</div>
                  <div class="milestone-title-area">
                    <h3>{{ m.name }}</h3>
                  </div>
                  <span class="badge" [class.badge-success]="m.status === 'completed'" [class.badge-info]="m.status === 'in_progress'">
                    {{ m.status }}
                  </span>
                </div>

                <!-- Resources checklist -->
                <div class="resources-section">
                  <h4>Required Resources</h4>
                  <div class="resources-list">
                    <div class="resource-item" *ngFor="let r of m.resources" [class.done]="r.isCompleted">
                      <div class="checkbox-container" (click)="toggleResource(m, r)">
                        <span class="material-symbols-outlined check-icon">
                          {{ r.isCompleted ? 'check_box' : 'check_box_outline_blank' }}
                        </span>
                      </div>
                      
                      <div class="resource-info">
                        <span class="res-title">{{ r.title }}</span>
                        <div class="res-meta">
                          <span class="badge badge-info">{{ r.resource_type }}</span>
                          <span>{{ r.estimated_time_minutes }} mins</span>
                          <a *ngIf="r.url" [href]="r.url" target="_blank" class="resource-link" (click)="$event.stopPropagation()">
                            <span class="material-symbols-outlined">open_in_new</span>
                            Link
                          </a>
                        </div>
                      </div>
                    </div>
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
    .detail-container {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 40px;
      text-align: center;
      gap: 16px;
    }
    
    .spinner {
      font-size: 2.5rem !important;
    }
    
    /* Header Card */
    .header-card {
      margin-bottom: 32px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .header-main {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }
    
    .plan-title {
      font-size: 1.6rem;
      font-weight: 800;
    }
    
    .plan-description {
      font-size: 0.95rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }
    
    .progress-section {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .progress-meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 500;
    }
    
    .progress-bar-container {
      height: 8px;
      background: var(--bg-tertiary);
      border-radius: 4px;
      overflow: hidden;
    }
    
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--secondary) 0%, var(--primary) 100%);
      border-radius: 4px;
      transition: width var(--transition-normal) ease-out;
    }
    
    /* Timeline */
    .timeline-title {
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 8px;
    }
    
    .milestones-list {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    .milestone-card {
      padding: 24px;
      transition: border-color var(--transition-normal);
    }
    
    .milestone-card.completed {
      border-color: rgba(16, 185, 129, 0.3);
    }
    
    .milestone-header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      border-bottom: 1px solid var(--glass-border);
      padding-bottom: 12px;
    }
    
    .step-num {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--primary-glow);
      color: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-family: var(--font-display);
      font-size: 0.9rem;
    }
    
    .milestone-title-area {
      flex: 1;
    }
    
    .milestone-title-area h3 {
      font-size: 1.1rem;
      font-weight: 600;
    }
    
    /* Resources */
    .resources-section h4 {
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 12px;
    }
    
    .resources-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .resource-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 16px;
      border-radius: var(--border-radius-sm);
      background: rgba(255, 255, 255, 0.01);
      border: 1px solid var(--glass-border);
      transition: var(--transition-fast);
    }
    
    .resource-item:hover {
      background: rgba(255, 255, 255, 0.03);
      border-color: var(--glass-border-focused);
    }
    
    .resource-item.done {
      background: rgba(16, 185, 129, 0.02);
      border-color: rgba(16, 185, 129, 0.15);
    }
    
    .checkbox-container {
      cursor: pointer;
      color: var(--text-muted);
      display: flex;
      align-items: center;
    }
    
    .resource-item.done .check-icon {
      color: var(--success);
    }
    
    .resource-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    
    .res-title {
      font-size: 0.9rem;
      font-weight: 500;
    }
    
    .resource-item.done .res-title {
      color: var(--text-secondary);
      text-decoration: line-through;
    }
    
    .res-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    
    .resource-link {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    
    .resource-link span {
      font-size: 0.9rem !important;
    }
  `]
})
export class LearningDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private learningService = inject(LearningService);

  planId = '';
  plan: any = null;
  isLoading = true;

  ngOnInit(): void {
    this.planId = this.route.snapshot.paramMap.get('id') || '';
    if (this.planId) {
      this.fetchPlanDetails();
    }
  }

  fetchPlanDetails(): void {
    this.isLoading = true;
    this.learningService.getLearningPlan(this.planId).subscribe({
      next: (res) => {
        // Map UI helper field for checklist interaction
        if (res && res.milestones) {
          res.milestones.forEach((m: any) => {
            if (m.resources) {
              m.resources.forEach((r: any) => {
                r.isCompleted = !!r.completed_at;
              });
            }
          });
        }
        this.plan = res;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  get completionPercentage(): number {
    if (!this.plan || !this.plan.milestones) return 0;
    let total = 0;
    let done = 0;
    this.plan.milestones.forEach((m: any) => {
      if (m.resources) {
        m.resources.forEach((r: any) => {
          total++;
          if (r.isCompleted) done++;
        });
      }
    });
    return total > 0 ? Math.round((done / total) * 100) : 0;
  }

  toggleResource(milestone: any, resource: any): void {
    resource.isCompleted = !resource.isCompleted;
    
    // Check if all resources in milestone are done to update milestone status
    const allDone = milestone.resources.every((r: any) => r.isCompleted);
    milestone.status = allDone ? 'completed' : 'in_progress';

    // Check if all milestones are completed to update plan status
    const allMilestonesDone = this.plan.milestones.every((m: any) => m.status === 'completed');
    this.plan.status = allMilestonesDone ? 'completed' : 'in_progress';
  }
}
