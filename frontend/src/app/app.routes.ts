import { Routes } from '@angular/router';
import { LoginPage } from './pages/login-page/login-page';
import { OperatorPage } from './pages/operator-page/operator-page';
import { EngineerPage } from './pages/engineer-page/engineer-page';
import { ManagerPage } from './pages/manager-page/manager-page';

import { AuthGuard } from './services/auth.guard';

export const routes: Routes = [
  { path: '', component: LoginPage },

  {
    path: 'operator',
    component: OperatorPage,
    canActivate: [AuthGuard],
    data: { roles: ['operator'] },
  },
  {
    path: 'engineer',
    component: EngineerPage,
    canActivate: [AuthGuard],
    data: { roles: ['engineer'] },
  },
  {
    path: 'manager',
    component: ManagerPage,
    canActivate: [AuthGuard],
    data: { roles: ['manager'] },
  },

  { path: '**', redirectTo: '' },
];
