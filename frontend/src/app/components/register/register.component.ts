import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  template: `
    <div class="register-container">
      <div class="glass-panel register-card pulse-glow">
        <div class="brand-header">
          <span class="material-symbols-outlined logo-icon text-neon-cyan">psychology</span>
          <h1 class="brand-title text-neon-cyan">ANTIGRAVITY</h1>
          <p class="brand-subtitle">AI Interview Intelligence Platform</p>
        </div>

        <h2 class="card-title">Create Account</h2>
        <p class="card-subtitle">Get started with your smart interview helper</p>

        <form [formGroup]="registerForm" (ngSubmit)="onSubmit()" class="register-form">
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
              placeholder="Alex Johnson"
              [class.invalid]="isFieldInvalid('full_name')"
            />
            <div *ngIf="isFieldInvalid('full_name')" class="validation-error">
              Full name is required
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="username">Username</label>
            <input
              type="text"
              id="username"
              formControlName="username"
              class="form-control"
              placeholder="alexj"
              [class.invalid]="isFieldInvalid('username')"
            />
            <div *ngIf="isFieldInvalid('username')" class="validation-error">
              Username is required (min 3 chars)
            </div>
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

          <button type="submit" [disabled]="registerForm.invalid || isLoading" class="btn btn-accent w-full">
            <span *ngIf="isLoading" class="material-symbols-outlined spinner">sync</span>
            <span>{{ isLoading ? 'Creating Account...' : 'Create Account' }}</span>
          </button>
        </form>

        <div class="card-footer">
          <p>Already have an account? <a routerLink="/login">Sign in</a></p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .register-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 20px;
    }
    .register-card {
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
    .register-form {
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
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  registerForm = this.fb.group({
    full_name: ['', Validators.required],
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]]
  });

  isLoading = false;
  errorMessage = '';

  isFieldInvalid(field: string): boolean {
    const control = this.registerForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit(): void {
    if (this.registerForm.invalid) return;

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.register(this.registerForm.value).subscribe({
      next: () => {
        // Automatically login the user after successful registration or navigate to login
        this.authService.login({
          email: this.registerForm.value.email,
          password: this.registerForm.value.password
        }).subscribe({
          next: () => {
            this.router.navigate(['/']);
          },
          error: () => {
            this.router.navigate(['/login']);
          }
        });
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || err.error?.error || 'Registration failed. Username or email may already be in use.';
      }
    });
  }
}
