import { Injectable } from '@angular/core';
import {
  CanActivate,
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  UrlTree,
} from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean | UrlTree {
    const isLoggedIn = this.authService.isLoggedIn();
    const userRole = this.authService.getRole();

    if (!isLoggedIn) {
      // Если не авторизован — редирект на логин
      return this.router.createUrlTree(['']);
    }

    const allowedRoles: string[] = route.data['roles'];
    if (allowedRoles && !allowedRoles.includes(userRole || '')) {
      // Если роль не разрешена для этого маршрута — редирект на логин
      return this.router.createUrlTree(['']);
    }

    return true; // Доступ разрешён
  }
}
