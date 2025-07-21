import { Component, OnInit } from '@angular/core';
import { ManagerService } from '../../services/manager.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-application',
  imports: [FormsModule, CommonModule],
  templateUrl: './application.html',
  styleUrls: ['./application.scss'],
})
export class Application implements OnInit {
  clientName = '';
  phone = '';
  address = '';
  techniq = '';
  assignedTime = '';
  description = '';
  selectedEngineerId: number | null = null;

  engineers: { id: number; name: string }[] = [];
  isLoading = false;
  message = '';

  constructor(private managerService: ManagerService) {}

  ngOnInit() {
    this.loadEngineers();
  }

  loadEngineers() {
    this.managerService.getAllEngineers().subscribe((engineers) => {
      this.engineers = engineers.map((eng: any) => ({
        id: eng.user_id, // правильное поле
        name: eng.engineer_name, // правильное поле
      }));
    });
  }

  // Конвертируем дату из datetime-local в формат GMT, как требует API
  convertToGMT(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toUTCString(); // возвращает формат типа "Wed, 30 Jul 2025 12:29:32 GMT"
  }

  createRequest() {
    if (!this.phone || !this.address || !this.techniq || !this.description) {
      this.message = 'Пожалуйста, заполните все обязательные поля.';
      return;
    }

    this.isLoading = true;
    this.message = '';

    // Определяем статус
    const status_id = this.selectedEngineerId ? 2 : 1;

    // Формируем тело запроса
    const requestData: any = {
      status_id,
      phone: this.phone,
      address: this.address,
      techniq: this.techniq,
      description: this.description,
    };

    if (this.clientName.trim()) {
      requestData.customer_name = this.clientName.trim(); // если нужно отправлять имя
    }

    if (this.assignedTime) {
      requestData.assigned_time = this.convertToISO(this.assignedTime);
    }

    if (this.selectedEngineerId) {
      requestData.engineer_id = this.selectedEngineerId;
    }

    this.managerService.createRequest(requestData).subscribe((res) => {
      this.isLoading = false;
      if (res && res.request_id) {
        this.message = `Заявка создана успешно, ID: ${res.request_id}`;
        this.resetForm();
      } else {
        this.message = 'Ошибка при создании заявки.';
      }
    });
  }

  resetForm() {
    this.clientName = '';
    this.phone = '';
    this.address = '';
    this.techniq = '';
    this.assignedTime = '';
    this.description = '';
    this.selectedEngineerId = null;
  }

  convertToISO(dateString: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);

    const pad = (n: number) => n.toString().padStart(2, '0');

    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1);
    const day = pad(date.getDate());
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());

    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`; // Локальное ISO
  }
}
