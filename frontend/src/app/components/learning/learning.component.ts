import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { LearningService } from '../../services/learning.service';

@Component({
  selector: 'app-learning',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="learning-container">
      <div class="learning-grid">
        
        <!-- Left: Current plans -->
        <div class="plans-list-section">
          <div class="glass-panel section-card">
            <h2 class="section-title">Your Learning Pathways</h2>
            <p class="section-subtitle">AI-generated paths targeting key skill gaps identified in interviews</p>

            <div *ngIf="isLoading" class="loading-state">
              <span class="material-symbols-outlined spinner text-neon-cyan">sync</span>
              <p>Loading plans...</p>
            </div>

            <div *ngIf="!isLoading && plans.length === 0" class="empty-state">
              <span class="material-symbols-outlined">school</span>
              <p>No learning plans generated yet. Complete an interview or create a plan below.</p>
            </div>

            <div class="plans-list" *ngIf="!isLoading && plans.length > 0">
              <div class="plan-card glass-panel-hover" *ngFor="let p of plans" [routerLink]="['/learning', p.learning_plan_id]">
                <div class="plan-info">
                  <h3>{{ p.title }}</h3>
                  <div class="plan-meta">
                    <span class="badge" [class.badge-success]="p.status === 'completed'" [class.badge-info]="p.status === 'in_progress'">{{ p.status }}</span>
                    <span>Target score: <strong>{{ p.target_proficiency_score }}%</strong></span>
                  </div>
                </div>
                <div class="plan-chevron">
                  <span class="material-symbols-outlined">chevron_right</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Generator Form -->
        <div class="generator-section">
          <div class="glass-panel section-card">
            <h2 class="section-title text-neon-cyan">Generate Custom Plan</h2>
            <p class="section-subtitle">Define your goals to trigger the AI Coach agent</p>

            <form [formGroup]="genForm" (ngSubmit)="onGenerate()" class="gen-form">
              <div class="form-group">
                <label class="form-label" for="type">Focus Domain</label>
                <select id="type" formControlName="interview_type" class="form-control">
                  <option value="system_design">System Design</option>
                  <option value="algorithms">Algorithms & Data Structures</option>
                  <option value="behavioral">Behavioral (STAR Method)</option>
                  <option value="coding">Coding & Languages</option>
                  <option value="ml">Machine Learning Engineering</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label" for="proficiency">Target Score (%)</label>
                <input 
                  type="number" 
                  id="proficiency" 
                  formControlName="target_proficiency" 
                  class="form-control" 
                  min="50" 
                  max="100"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="hours">Study Time (Hours / Week)</label>
                <input 
                  type="number" 
                  id="hours" 
                  formControlName="available_hours_per_week" 
                  class="form-control" 
                  min="1" 
                  max="40"
                />
              </div>

              <div *ngIf="errorMessage" class="error-banner">
                <span class="material-symbols-outlined">error</span>
                {{ errorMessage }}
              </div>

              <button type="submit" [disabled]="genForm.invalid || isGenerating" class="btn btn-accent w-full">
                <span *ngIf="isGenerating" class="material-symbols-outlined spinner">sync</span>
                <span>{{ isGenerating ? 'Coaching AI...' : 'Create Path' }}</span>
              </button>
            </form>
          </div>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .learning-container {
      width: 100%;
    }
    
    .learning-grid {
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 32px;
    }
    
    @media (max-width: 992px) {
      .learning-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .section-card {
      padding: 32px;
    }
    
    .section-title {
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 4px;
    }
    
    .section-subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    
    .loading-state, .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 0;
      color: var(--text-secondary);
      text-align: center;
      gap: 12px;
    }
    
    .spinner {
      font-size: 2.5rem !important;
    }
    
    /* Plans List */
    .plans-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .plan-card {
      padding: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.01);
      cursor: pointer;
    }
    
    .plan-info h3 {
      font-size: 1rem;
      margin-bottom: 6px;
    }
    
    .plan-meta {
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 0.8rem;
      color: var(--text-secondary);
    }
    
    .plan-chevron {
      color: var(--text-muted);
    }
    
    /* Form */
    .gen-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .w-full {
      width: 100%;
    }
    
    .error-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--error-glow);
      border: 1px solid rgba(239, 68, 68, 0.2);
      color: var(--error);
      padding: 12px;
      border-radius: var(--border-radius-sm);
      font-size: 0.9rem;
    }
  `]
})
export class LearningComponent implements OnInit {
  private fb = inject(FormBuilder);
  private learningService = inject(LearningService);
  private router = inject(Router);

  plans: any[] = [];
  isLoading = true;
  isGenerating = false;
  errorMessage = '';

  genForm = this.fb.group({
    interview_type: ['system_design', Validators.required],
    target_proficiency: [80, [Validators.required, Validators.min(50), Validators.max(100)]],
    available_hours_per_week: [8, [Validators.required, Validators.min(1), Validators.max(40)]]
  });

  ngOnInit(): void {
    this.fetchPlans();
  }

  fetchPlans(): void {
    this.isLoading = true;
    this.learningService.listLearningPlans().subscribe({
      next: (res) => {
        this.plans = res.plans || [];
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  onGenerate(): void {
    if (this.genForm.invalid) return;

    this.isGenerating = true;
    this.errorMessage = '';

    const req = {
      target_proficiency: this.genForm.value.target_proficiency || 80,
      available_hours_per_week: this.genForm.value.available_hours_per_week || 8,
      interview_type: this.genForm.value.interview_type || 'system_design'
    };

    this.learningService.generateLearningPlan(req).subscribe({
      next: (plan) => {
        this.isGenerating = false;
        this.router.navigate(['/learning', plan.learning_plan_id]);
      },
      error: (err) => {
        this.isGenerating = false;
        this.errorMessage = err.error?.detail || err.error?.error || 'Could not generate plan. Please try again.';
      }
    });
  }
}
