import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="login-container">
      <div class="glass-panel login-card pulse-glow">
        <div class="brand-header">
          <span class="material-symbols-outlined logo-icon text-neon-indigo">psychology</span>
          <h1 class="brand-title text-neon-indigo">ANTIGRAVITY</h1>
          <p class="brand-subtitle">AI Interview Intelligence Platform</p>
        </div>

        <h2 class="card-title">Welcome Back</h2>
        <p class="card-subtitle">Sign in to continue your interview prep journey</p>

        <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="login-form">
          <div *ngIf="errorMessage" class="error-banner">
            <span class="material-symbols-outlined">error</span>
            {{ errorMessage }}
          </div>

          <div class="form-group">
            <label class="form-label" for="email">Email Address</label>
            <input
              type="email"
              id="email"
              formControlName="email"
              class="form-control"
              placeholder="name@company.com"
              [class.invalid]="isFieldInvalid('email')"
            />
            <div *ngIf="isFieldInvalid('email')" class="validation-error">
              Please enter a valid email address
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="password">Password</label>
            <input
              type="password"
              id="password"
              formControlName="password"
              class="form-control"
              placeholder="••••••••"
              [class.invalid]="isFieldInvalid('password')"
            />
            <div *ngIf="isFieldInvalid('password')" class="validation-error">
              Password must be at least 6 characters
            </div>
          </div>

          <button type="submit" [disabled]="loginForm.invalid || isLoading" class="btn btn-primary w-full">
            <span *ngIf="isLoading" class="material-symbols-outlined spinner">sync</span>
            <span>{{ isLoading ? 'Signing In...' : 'Sign In' }}</span>
          </button>
        </form>

        <div class="card-footer">
          <p>Don't have an account? <a routerLink="/register">Create one free</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    .login-card {
      width: 100%;
      max-width: 440px;
      padding: 40px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    .brand-header {
      text-align: center;
      margin-bottom: 30px;
    }
    .logo-icon {
      font-size: 3rem !important;
      margin-bottom: 8px;
    }
    .brand-title {
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 1.8rem;
      letter-spacing: 0.05em;
    }
    .brand-subtitle {
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-top: 4px;
    }
    .card-title {
      font-size: 1.5rem;
      margin-bottom: 6px;
      font-weight: 600;
    }
    .card-subtitle {
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-bottom: 24px;
    }
    .login-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .w-full {
      width: 100%;
    }
    .card-footer {
      text-align: center;
      margin-top: 24px;
      font-size: 0.9rem;
      color: var(--text-secondary);
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
      margin-bottom: 8px;
    }
    .validation-error {
      color: var(--error);
      font-size: 0.75rem;
      margin-top: 4px;
    }
    .form-control.invalid {
      border-color: rgba(239, 68, 68, 0.4);
    }
    .form-control.invalid:focus {
      box-shadow: 0 0 0 3px var(--error-glow);
    }
  `]
})
export class LoginComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  isLoading = false;
  errorMessage = '';

  isFieldInvalid(field: string): boolean {
    const control = this.loginForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || err.error?.error || 'Invalid email or password. Please try again.';
      }
    });
  }
}
