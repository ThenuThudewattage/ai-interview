import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardLayoutComponent } from './components/dashboard/dashboard.component';
import { OverviewComponent } from './components/overview/overview.component';
import { StartInterviewComponent } from './components/start-interview/start-interview.component';
import { ConductInterviewComponent } from './components/conduct-interview/conduct-interview.component';
import { LearningComponent } from './components/learning/learning.component';
import { LearningDetailComponent } from './components/learning-detail/learning-detail.component';
import { ProfileComponent } from './components/profile/profile.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  },
  {
    path: '',
    component: DashboardLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        component: OverviewComponent
      },
      {
        path: 'interviews/start',
        component: StartInterviewComponent
      },
      {
        path: 'interviews/:id',
        component: ConductInterviewComponent
      },
      {
        path: 'learning',
        component: LearningComponent
      },
      {
        path: 'learning/:id',
        component: LearningDetailComponent
      },
      {
        path: 'profile',
        component: ProfileComponent
      }
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];
