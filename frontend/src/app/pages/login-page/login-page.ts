import { Component } from '@angular/core';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './login-page.html',
  styleUrl: './login-page.scss',
})
export class LoginPage {
  email: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  login(): void {
    if (!this.email || !this.password) {
      this.errorMessage = 'Введите email и пароль';
      return;
    }

    this.authService
      .login({ login: this.email, password: this.password })
      .subscribe({
        next: (response) => {
          const role = response.user.role;

          switch (role) {
            case 'operator':
              this.router.navigate(['/operator']);
              break;
            case 'engineer':
              this.router.navigate(['/engineer']);
              break;
            case 'manager':
              this.router.navigate(['/manager']);
              break;
            default:
              this.errorMessage = 'Неизвестная роль';
          }
        },
        error: () => {
          this.errorMessage = 'Неверный логин или пароль';
        },
      });
  }
}
