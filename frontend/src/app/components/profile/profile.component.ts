import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="profile-container">
      <div class="profile-grid">
        
        <!-- Left: Profile Form -->
        <div class="profile-settings-column">
          <div class="glass-panel settings-card">
            <h2 class="card-title text-neon-indigo">Profile Settings</h2>
            <p class="card-subtitle">Manage your personal information and mock preferences</p>

            <form [formGroup]="profileForm" (ngSubmit)="onSubmit()" class="profile-form">
              <div *ngIf="successMessage" class="success-banner">
                <span class="material-symbols-outlined">check_circle</span>
                {{ successMessage }}
              </div>
              <div *ngIf="errorMessage" class="error-banner">
                <span class="material-symbols-outlined">error</span>
                {{ errorMessage }}
              </div>

              <div class="form-group">
                <label class="form-label" for="fullName">Full Name</label>
                <input 
                  type="text" 
                  id="fullName" 
                  formControlName="full_name" 
                  class="form-control"
                />
              </div>

              <div class="form-group">
                <label class="form-label" for="bio">Short Professional Bio</label>
                <textarea 
                  id="bio" 
                  formControlName="bio" 
                  class="form-control" 
                  placeholder="Tell us about your background, goals, or target roles..."
                ></textarea>
              </div>

              <div class="grid-2">
                <div class="form-group">
                  <label class="form-label" for="difficulty">Preferred Difficulty</label>
                  <select id="difficulty" formControlName="preferred_difficulty" class="form-control">
                    <option value="easy">Easy (Junior)</option>
                    <option value="medium">Medium (Mid-level)</option>
                    <option value="hard">Hard (Senior/Staff)</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label" for="timezone">Timezone</label>
                  <input 
                    type="text" 
                    id="timezone" 
                    formControlName="timezone" 
                    class="form-control" 
                    placeholder="UTC, EST, PST"
                  />
                </div>
              </div>

              <button type="submit" [disabled]="profileForm.invalid || isSaving" class="btn btn-primary w-full">
                <span *ngIf="isSaving" class="material-symbols-outlined spinner">sync</span>
                <span>{{ isSaving ? 'Saving Changes...' : 'Save Profile' }}</span>
              </button>
            </form>
          </div>
        </div>

        <!-- Right: Skills and Gaps -->
        <div class="skills-column">
          
          <!-- Skills levels -->
          <div class="glass-panel skills-card margin-bottom-32">
            <h2 class="card-title">My Skill Matrix</h2>
            <p class="card-subtitle font-normal">Historical levels analyzed from past performance</p>

            <div *ngIf="isLoadingSkills" class="loading-state">
              <span class="material-symbols-outlined spinner text-neon-cyan">sync</span>
              <p>Retrieving skills...</p>
            </div>

            <div *ngIf="!isLoadingSkills && skills.length === 0" class="empty-state">
              <p>No skills recorded. Start a mock interview to map your proficiencies.</p>
            </div>

            <div class="skills-levels-list" *ngIf="!isLoadingSkills && skills.length > 0">
              <div class="skill-level-item" *ngFor="let s of skills">
                <div class="level-header">
                  <span class="level-name font-bold">{{ s.skill_name }}</span>
                  <span class="level-score">{{ s.proficiency_score }}%</span>
                </div>
                <div class="level-bar-bg">
                  <div class="level-bar-fill" [style.width.%]="s.proficiency_score"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Gaps -->
          <div class="glass-panel gaps-card">
            <h2 class="card-title">Identified Skill Gaps</h2>
            <p class="card-subtitle">Areas requiring study to meet target levels</p>

            <div *ngIf="isLoadingGaps" class="loading-state">
              <span class="material-symbols-outlined spinner">sync</span>
            </div>

            <div *ngIf="!isLoadingGaps && gaps.length === 0" class="empty-state">
              <p>Great job! No skill gaps identified yet.</p>
            </div>

            <div class="gaps-list" *ngIf="!isLoadingGaps && gaps.length > 0">
              <div class="gap-item" *ngFor="let g of gaps">
                <div class="gap-marker">
                  <span class="material-symbols-outlined text-neon-cyan">priority_high</span>
                </div>
                <div class="gap-info">
                  <span class="gap-name font-bold">{{ g.skill }}</span>
                  <span class="gap-severity">Severity: {{ g.gap_severity * 100 | number:'1.0-0' }}%</span>
                </div>
                <span class="badge badge-warning" *ngIf="!g.is_resolved">Needs Attention</span>
                <span class="badge badge-success" *ngIf="g.is_resolved">Resolved</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  `,
  styles: [`
    .profile-container {
      width: 100%;
    }
    
    .profile-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 32px;
    }
    
    @media (max-width: 992px) {
      .profile-grid {
        grid-template-columns: 1fr;
      }
    }
    
    .settings-card, .skills-card, .gaps-card {
      padding: 32px;
    }
    
    .margin-bottom-32 {
      margin-bottom: 32px;
    }
    
    .card-title {
      font-size: 1.3rem;
      font-weight: 700;
      margin-bottom: 4px;
    }
    
    .card-subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 24px;
    }
    
    .profile-form {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    
    .w-full {
      width: 100%;
    }
    
    .loading-state, .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 0;
      text-align: center;
      gap: 8px;
      font-size: 0.9rem;
      color: var(--text-muted);
    }
    
    .spinner {
      font-size: 2.2rem !important;
    }
    
    .success-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--success-glow);
      border: 1px solid rgba(16, 185, 129, 0.2);
      color: var(--success);
      padding: 12px;
      border-radius: var(--border-radius-sm);
      font-size: 0.9rem;
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
    
    /* Skill Matrix */
    .skills-levels-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .skill-level-item {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    
    .level-header {
      display: flex;
      justify-content: space-between;
      font-size: 0.9rem;
    }
    
    .level-bar-bg {
      height: 6px;
      background: var(--bg-tertiary);
      border-radius: 3px;
      overflow: hidden;
    }
    
    .level-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
      border-radius: 3px;
    }
    
    /* Gaps */
    .gaps-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .gap-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: rgba(255, 255, 255, 0.01);
      border: 1px solid var(--glass-border);
      border-radius: var(--border-radius-sm);
    }
    
    .gap-marker {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: var(--warning-glow);
      color: var(--warning);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .gap-marker span {
      font-size: 1rem !important;
      font-weight: bold;
    }
    
    .gap-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    
    .gap-name {
      font-size: 0.9rem;
    }
    
    .gap-severity {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
  `]
})
export class ProfileComponent implements OnInit {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);
  private authService = inject(AuthService);

  profileForm = this.fb.group({
    full_name: ['', Validators.required],
    bio: [''],
    preferred_difficulty: ['medium', Validators.required],
    timezone: ['']
  });

  isSaving = false;
  successMessage = '';
  errorMessage = '';

  skills: any[] = [];
  isLoadingSkills = true;

  gaps: any[] = [];
  isLoadingGaps = true;

  ngOnInit(): void {
    this.fetchProfile();
    this.fetchSkills();
    this.fetchGaps();
  }

  fetchProfile(): void {
    this.http.get<any>('/api/v1/users/profile').subscribe({
      next: (profile) => {
        this.profileForm.patchValue({
          full_name: profile.full_name,
          bio: profile.bio || '',
          preferred_difficulty: profile.preferences?.preferred_difficulty || 'medium',
          timezone: profile.preferences?.timezone || ''
        });
      }
    });
  }

  fetchSkills(): void {
    this.isLoadingSkills = true;
    this.http.get<any>('/api/v1/users/skills').subscribe({
      next: (res) => {
        this.skills = res.skills || [];
        this.isLoadingSkills = false;
      },
      error: () => {
        this.isLoadingSkills = false;
      }
    });
  }

  fetchGaps(): void {
    this.isLoadingGaps = true;
    this.http.get<any>('/api/v1/users/skill-gaps').subscribe({
      next: (res) => {
        this.gaps = res.skill_gaps || [];
        this.isLoadingGaps = false;
      },
      error: () => {
        this.isLoadingGaps = false;
      }
    });
  }

  onSubmit(): void {
    if (this.profileForm.invalid) return;

    this.isSaving = true;
    this.successMessage = '';
    this.errorMessage = '';

    this.http.put<any>('/api/v1/users/profile', this.profileForm.value).subscribe({
      next: (res) => {
        this.isSaving = false;
        this.successMessage = 'Profile updated successfully!';
        
        // Refresh local cache of user full_name if changed
        const currentCached = this.authService.getCurrentUser();
        if (currentCached && this.profileForm.value.full_name) {
          currentCached.full_name = this.profileForm.value.full_name;
          localStorage.setItem('current_user', JSON.stringify(currentCached));
          // Trigger BehaviourSubject refresh
          this.authService.login({email: '', password: ''}).subscribe({error: () => {}}); // dummy reload
        }
      },
      error: (err) => {
        this.isSaving = false;
        this.errorMessage = err.error?.detail || err.error?.error || 'Failed to save changes.';
      }
    });
  }
}
