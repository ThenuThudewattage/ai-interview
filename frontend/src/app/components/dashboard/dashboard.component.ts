import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService, User } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="app-layout">
      <!-- Sidebar -->
      <aside class="sidebar" [class.open]="isSidebarOpen">
        <div class="sidebar-header">
          <span class="material-symbols-outlined logo-icon text-neon-cyan">psychology</span>
          <span class="logo-text">ANTIGRAVITY</span>
        </div>

        <nav class="sidebar-nav">
          <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" class="nav-item" (click)="closeSidebarOnMobile()">
            <span class="material-symbols-outlined nav-icon">dashboard</span>
            <span class="nav-label">Overview</span>
          </a>
          <a routerLink="/interviews/start" routerLinkActive="active" class="nav-item" (click)="closeSidebarOnMobile()">
            <span class="material-symbols-outlined nav-icon">play_circle</span>
            <span class="nav-label">New Interview</span>
          </a>
          <a routerLink="/learning" routerLinkActive="active" class="nav-item" (click)="closeSidebarOnMobile()">
            <span class="material-symbols-outlined nav-icon">school</span>
            <span class="nav-label">Learning Plans</span>
          </a>
          <a routerLink="/profile" routerLinkActive="active" class="nav-item" (click)="closeSidebarOnMobile()">
            <span class="material-symbols-outlined nav-icon">account_circle</span>
            <span class="nav-label">Profile & Skills</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <button (click)="onLogout()" class="btn btn-secondary logout-btn">
            <span class="material-symbols-outlined">logout</span>
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      <!-- Main Panel -->
      <div class="main-panel">
        <header class="header glass-panel">
          <div class="header-left">
            <button class="mobile-toggle" (click)="toggleSidebar()">
              <span class="material-symbols-outlined">menu</span>
            </button>
            <h1 class="page-title">{{ getPageTitle() }}</h1>
          </div>

          <div class="header-right">
            <div class="user-badge" routerLink="/profile">
              <div class="avatar">
                {{ userInitials }}
              </div>
              <span class="user-name">{{ currentUser?.full_name }}</span>
            </div>
          </div>
        </header>

        <main class="content-area">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .app-layout {
      display: flex;
      min-height: 100vh;
    }
    
    /* Sidebar Styles */
    .sidebar {
      width: var(--sidebar-width);
      background: rgba(10, 13, 30, 0.95);
      border-right: 1px solid var(--glass-border);
      display: flex;
      flex-direction: column;
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      z-index: 100;
      transition: transform var(--transition-normal);
    }
    
    .sidebar-header {
      height: var(--header-height);
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 24px;
      border-bottom: 1px solid var(--glass-border);
    }
    
    .logo-icon {
      font-size: 2.2rem !important;
    }
    
    .logo-text {
      font-family: var(--font-display);
      font-weight: 800;
      font-size: 1.3rem;
      letter-spacing: 0.05em;
      background: linear-gradient(135deg, var(--text-primary) 30%, var(--text-secondary) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .sidebar-nav {
      flex: 1;
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .nav-item {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 12px 16px;
      border-radius: var(--border-radius-sm);
      color: var(--text-secondary);
      transition: var(--transition-fast);
    }
    
    .nav-item:hover {
      background: rgba(255, 255, 255, 0.03);
      color: var(--text-primary);
    }
    
    .nav-item.active {
      background: var(--primary-glow);
      color: var(--primary);
      border-left: 3px solid var(--primary);
      border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0;
      padding-left: 13px;
    }
    
    .nav-icon {
      font-size: 1.4rem !important;
    }
    
    .nav-label {
      font-weight: 500;
      font-size: 0.95rem;
    }
    
    .sidebar-footer {
      padding: 24px 16px;
      border-top: 1px solid var(--glass-border);
    }
    
    .logout-btn {
      width: 100%;
      justify-content: flex-start;
    }
    
    /* Main Panel Styles */
    .main-panel {
      flex: 1;
      margin-left: var(--sidebar-width);
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    
    .header {
      height: var(--header-height);
      border-radius: 0;
      border-top: none;
      border-left: none;
      border-right: none;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 40px;
      position: sticky;
      top: 0;
      z-index: 90;
    }
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .mobile-toggle {
      display: none;
      background: none;
      border: none;
      color: var(--text-primary);
      cursor: pointer;
    }
    
    .page-title {
      font-size: 1.4rem;
      font-weight: 700;
    }
    
    .header-right {
      display: flex;
      align-items: center;
    }
    
    .user-badge {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 6px 14px;
      border-radius: 30px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--glass-border);
      cursor: pointer;
      transition: var(--transition-fast);
    }
    
    .user-badge:hover {
      background: rgba(255, 255, 255, 0.06);
      border-color: var(--text-muted);
    }
    
    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.85rem;
      font-family: var(--font-display);
    }
    
    .user-name {
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--text-primary);
    }
    
    .content-area {
      flex: 1;
      padding: 40px;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
    }
    
    /* Responsive Adjustments */
    @media (max-width: 992px) {
      .sidebar {
        transform: translateX(-100%);
      }
      .sidebar.open {
        transform: translateX(0);
      }
      .main-panel {
        margin-left: 0;
      }
      .mobile-toggle {
        display: block;
      }
      .header {
        padding: 0 20px;
      }
      .content-area {
        padding: 20px;
      }
      .user-name {
        display: none;
      }
    }
  `]
})
export class DashboardLayoutComponent implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);

  currentUser: User | null = null;
  isSidebarOpen = false;
  userInitials = '';

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
      if (user?.full_name) {
        const parts = user.full_name.split(' ');
        this.userInitials = parts.map(p => p[0]).join('').substring(0, 2).toUpperCase();
      }
    });
  }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  closeSidebarOnMobile(): void {
    this.isSidebarOpen = false;
  }

  onLogout(): void {
    this.authService.logout();
  }

  getPageTitle(): string {
    const url = this.router.url;
    if (url === '/') return 'Dashboard';
    if (url.startsWith('/interviews/start')) return 'Prepare New Interview';
    if (url.startsWith('/interviews/')) return 'Interview Session';
    if (url.startsWith('/learning')) return 'Learning Pathways';
    if (url.startsWith('/profile')) return 'User Profile';
    return 'Dashboard';
  }
}
