import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { InterviewService } from '../../services/interview.service';

@Component({
  selector: 'app-start-interview',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="start-container">
      <div class="glass-panel form-card">
        <h2 class="form-title text-neon-indigo">Configure Mock Interview</h2>
        <p class="form-subtitle">Choose your parameters to build a custom session tailored by AI agents</p>

        <form [formGroup]="configForm" (ngSubmit)="onSubmit()" class="config-form">
          
          <!-- Interview Type (Interactive Selection Grid) -->
          <div class="form-group">
            <label class="form-label">Interview Type</label>
            <div class="type-grid">
              <div 
                class="type-card" 
                [class.selected]="selectedType === 'system_design'"
                (click)="selectType('system_design')"
              >
                <span class="material-symbols-outlined type-icon text-neon-indigo">dns</span>
                <h3>System Design</h3>
                <p>Architectures, databases, microservices, scalability</p>
              </div>

              <div 
                class="type-card" 
                [class.selected]="selectedType === 'algorithms'"
                (click)="selectType('algorithms')"
              >
                <span class="material-symbols-outlined type-icon text-neon-cyan">code_blocks</span>
                <h3>Algorithms</h3>
                <p>Data structures, complexities, search & sort logic</p>
              </div>

              <div 
                class="type-card" 
                [class.selected]="selectedType === 'behavioral'"
                (click)="selectType('behavioral')"
              >
                <span class="material-symbols-outlined type-icon">forum</span>
                <h3>Behavioral</h3>
                <p>STAR method, leadership, conflict resolution, teamwork</p>
              </div>

              <div 
                class="type-card" 
                [class.selected]="selectedType === 'coding'"
                (click)="selectType('coding')"
              >
                <span class="material-symbols-outlined type-icon">terminal</span>
                <h3>Coding Practice</h3>
                <p>Language proficiency, general coding exercises</p>
              </div>

              <div 
                class="type-card" 
                [class.selected]="selectedType === 'ml'"
                (click)="selectType('ml')"
              >
                <span class="material-symbols-outlined type-icon">model_training</span>
                <h3>Machine Learning</h3>
                <p>Training pipelines, features, deep learning models</p>
              </div>
            </div>
          </div>

          <!-- Target Parameters -->
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="company">Target Company (Optional)</label>
              <input 
                type="text" 
                id="company" 
                formControlName="target_company" 
                class="form-control" 
                placeholder="Google, Stripe, Netflix"
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="role">Target Role (Optional)</label>
              <input 
                type="text" 
                id="role" 
                formControlName="target_role" 
                class="form-control" 
                placeholder="Senior Backend Engineer"
              />
            </div>
          </div>

          <!-- Difficulty and Length -->
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label" for="difficulty">Difficulty Level</label>
              <select id="difficulty" formControlName="difficulty_level" class="form-control">
                <option value="easy">Easy (Junior level)</option>
                <option value="medium">Medium (Mid level)</option>
                <option value="hard">Hard (Senior/Staff level)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="questions">Number of Questions</label>
              <select id="questions" formControlName="total_questions" class="form-control">
                <option [ngValue]="3">3 Questions (Short)</option>
                <option [ngValue]="5">5 Questions (Standard)</option>
                <option [ngValue]="8">8 Questions (Long)</option>
              </select>
            </div>
          </div>

          <div *ngIf="errorMessage" class="error-banner">
            <span class="material-symbols-outlined">error</span>
            {{ errorMessage }}
          </div>

          <div class="form-footer">
            <button type="submit" [disabled]="configForm.invalid || isLoading" class="btn btn-primary btn-launch">
              <span *ngIf="isLoading" class="material-symbols-outlined spinner">sync</span>
              <span>{{ isLoading ? 'Initializing Session...' : 'Launch AI Interview' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .start-container {
      max-width: 900px;
      margin: 0 auto;
    }
    
    .form-card {
      padding: 40px;
    }
    
    .form-title {
      font-size: 1.8rem;
      font-weight: 800;
      margin-bottom: 6px;
    }
    
    .form-subtitle {
      color: var(--text-secondary);
      font-size: 0.95rem;
      margin-bottom: 32px;
    }
    
    .config-form {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    
    /* Grid Selection Cards */
    .type-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-top: 8px;
    }
    
    @media (max-width: 768px) {
      .type-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .type-card {
      padding: 20px;
      border-radius: var(--border-radius-sm);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      cursor: pointer;
      transition: var(--transition-normal);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .type-card:hover {
      border-color: var(--glass-border-focused);
      background: rgba(255, 255, 255, 0.04);
      transform: translateY(-2px);
    }
    
    .type-card.selected {
      background: var(--primary-glow);
      border-color: var(--primary);
      box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
    }
    
    .type-icon {
      font-size: 2.2rem !important;
      margin-bottom: 4px;
    }
    
    .type-card h3 {
      font-size: 1.05rem;
      font-weight: 600;
    }
    
    .type-card p {
      font-size: 0.8rem;
      color: var(--text-secondary);
      line-height: 1.3;
    }
    
    .btn-launch {
      width: 100%;
      padding: 14px 28px;
      font-size: 1.05rem;
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
    
    .form-footer {
      margin-top: 16px;
    }
  `]
})
export class StartInterviewComponent {
  private fb = inject(FormBuilder);
  private interviewService = inject(InterviewService);
  private router = inject(Router);

  configForm = this.fb.group({
    interview_type: ['system_design', Validators.required],
    difficulty_level: ['medium', Validators.required],
    target_company: [''],
    target_role: [''],
    duration_minutes: [60],
    total_questions: [5, Validators.required]
  });

  selectedType = 'system_design';
  isLoading = false;
  errorMessage = '';

  selectType(type: string): void {
    this.selectedType = type;
    this.configForm.patchValue({ interview_type: type });
  }

  onSubmit(): void {
    if (this.configForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';

    const reqData = {
      interview_type: this.configForm.value.interview_type || 'system_design',
      difficulty_level: this.configForm.value.difficulty_level || 'medium',
      target_company: this.configForm.value.target_company || undefined,
      target_role: this.configForm.value.target_role || undefined,
      duration_minutes: this.configForm.value.duration_minutes || 60,
      total_questions: this.configForm.value.total_questions || 5
    };

    this.interviewService.startInterview(reqData).subscribe({
      next: (res) => {
        // Direct route to the newly created interview session
        this.router.navigate(['/interviews', res.interview_id]);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || err.error?.error || 'Failed to start interview session. Please try again.';
      }
    });
  }
}
