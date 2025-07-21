import { Component, OnInit } from '@angular/core';
import { ManagerService } from '../../services/manager.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  engineers: any[] = [];
  currentPage = 1;
  perPage = 6;
  totalEngineers = 0;
  isLoading = false;
  selectedEngineer: any = null;
  isBalanceModalOpen = false;

  isCredentialsModalOpen = false;
  engineerCredentials: { login: string; password: string } | null = null;

  operationType: 'add' | 'subtract' = 'add';
  amount: number = 0;

  employees: any[] = [];

  constructor(private managerService: ManagerService) {}

  ngOnInit() {
    this.loadNextPage();
    this.loadAllEmployees();
  }

  loadNextPage(): void {
    if (this.isLoading) return;
    this.isLoading = true;

    this.managerService
      .fetchEngineersPage(this.currentPage, this.perPage)
      .subscribe((response) => {
        this.engineers.push(...response.engineers);
        this.totalEngineers = response.total;
        this.currentPage++;
        this.isLoading = false;
      });
  }

  openBalanceModal(engineer: any): void {
    this.selectedEngineer = engineer;
    this.isBalanceModalOpen = true;

    // Сброс полей
    this.operationType = 'add';
    this.amount = 0;
  }

  get hasMoreEngineers(): boolean {
    return this.engineers.length < this.totalEngineers;
  }

  closeBalanceModal() {
    this.isBalanceModalOpen = false;
  }

  adjustBalance(): void {
    if (!this.selectedEngineer) return;

    if (isNaN(this.amount) || this.amount <= 0) {
      alert('Введите корректную сумму');
      return;
    }

    let currentBalance = parseFloat(this.selectedEngineer.balance);
    if (isNaN(currentBalance)) currentBalance = 0;

    const newBalance =
      this.operationType === 'add'
        ? currentBalance + this.amount
        : currentBalance - this.amount;

    this.managerService
      .updateEngineerBalance(this.selectedEngineer.user_id, newBalance)
      .subscribe((res) => {
        if (res && res.message === 'Balance updated successfully') {
          this.selectedEngineer.balance = newBalance.toFixed(2);
          this.closeBalanceModal();
        } else {
          alert('Не удалось обновить баланс');
        }
      });
  }

  newEmployee = {
    role: 'engineer',
    name: '',
    login: '',
    password: '',
  };

  canCreateEmployee(): boolean {
    return (
      this.newEmployee.role.trim() !== '' &&
      this.newEmployee.name.trim() !== '' &&
      this.newEmployee.login.trim() !== '' &&
      this.newEmployee.password.trim() !== ''
    );
  }

  createEmployee() {
    if (!this.canCreateEmployee()) return;

    const employeeData = {
      role: this.newEmployee.role,
      name: this.newEmployee.name.trim(),
      login: this.newEmployee.login.trim(),
      password: this.newEmployee.password,
    };

    this.managerService.createUser(employeeData).subscribe((res) => {
      if (res && res.user_id) {
        this.newEmployee = {
          role: 'engineer',
          name: '',
          login: '',
          password: '',
        };

        if (employeeData.role === 'engineer') {
          const newEngineer = {
            user_id: res.user_id,
            engineer_name: employeeData.name,
            active_requests: 0,
            completed_in_month: 0,
            balance: '0.00',
          };

          this.engineers.unshift(newEngineer);
        }
      }
    });
  }

  showEngineerCredentials(engineer: any): void {
    this.selectedEngineer = engineer;
    this.engineerCredentials = null;
    this.isCredentialsModalOpen = true;

    this.managerService
      .getUserCredentials(engineer.user_id)
      .subscribe((data) => {
        if (data) {
          this.engineerCredentials = {
            login: data.login,
            password: data.password,
          };
        }
      });
  }

  closeEngineerCredentials(): void {
    this.isCredentialsModalOpen = false;
    this.selectedEngineer = null;
    this.engineerCredentials = null;
  }

  deleteUser(engineer: any): void {
    if (!confirm(`Удалить пользователя ${engineer.engineer_name}?`)) {
      return;
    }

    this.managerService.deleteUser(engineer.user_id).subscribe((response) => {
      if (response && response.user_id === engineer.user_id) {
        // Обновим локальный список инженеров — удалим удалённого
        this.engineers = this.engineers.filter(
          (e) => e.user_id !== engineer.user_id
        );

        // Если сейчас открыта модалка с этим инженером — закроем
        if (this.selectedEngineer?.user_id === engineer.user_id) {
          this.closeEngineerCredentials();
        }
      } else {
        alert('Не удалось удалить пользователя');
      }
    });
  }

  clearAmountIfZero(): void {
    if (this.amount === 0) {
      this.amount = null as any; // очищает поле визуально
    }
  }

  loadAllEmployees(): void {
    this.isLoading = true;

    this.managerService.getAllUsers().subscribe((users) => {
      this.employees = users
        .filter((user) => user.role === 'operator' || user.role === 'manager')
        .map((user) => ({
          ...user,
          display_name: user.name, // для шаблона
        }));
      this.isLoading = false;
    });
  }
}
