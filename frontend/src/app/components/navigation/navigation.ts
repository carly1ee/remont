import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-navigation',
  imports: [],
  templateUrl: './navigation.html',
  styleUrl: './navigation.scss',
})
export class Navigation implements OnInit {
  userName: string = '';
  userRole: string = '';
  userAvatarLetter: string = '';

  constructor(private authService: AuthService) {}

  private roleMap: { [key: string]: string } = {
    operator: 'Оператор',
    engineer: 'Инженер',
    manager: 'Менеджер',
  };

  ngOnInit() {
    const user = this.authService.getUser();
    if (user) {
      this.userName = user.name;
      this.userRole = user.role;
      this.userAvatarLetter = user.name
        ? user.name.charAt(0).toUpperCase()
        : '';
    }

    const roleKey = user?.role as keyof typeof this.roleMap;
    this.userRole = this.roleMap[roleKey] || 'Неизвестная роль';
  }

  showLogin() {
    // сюда логику выхода или показа логина
    this.authService.logout();
  }
}
