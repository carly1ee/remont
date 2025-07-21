import { Component, OnInit } from '@angular/core';
import { ManagerService, FilterParams } from '../../services/manager.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-requests',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './requests.html',
  styleUrls: ['./requests.scss'],
})
export class Requests implements OnInit {
  filters: FilterParams = {
    engineer_id: null,
    status_ids: [1, 2, 3, 4],
    start_date: null,
    end_date: null,
    page: 1,
    per_page: 10,
  };

  totalRequests = 0;
  isLoading = false;
  openedDetailsId: number | null = null;

  editingRequestId: number | null = null;
  editableRequest: any = null;

  allEngineers: any[] = [];
  selectedEngineerId: number | null = null;
  selectedStatusId: number | null = null;
  startDate: string | null = null;
  endDate: string | null = null;

  historyMap: { [key: number]: any[] } = {}; // история по заявке
  openedHistoryId: number | null = null;
  loadingHistoryId: number | null = null;

  constructor(public managerService: ManagerService) {}

  ngOnInit(): void {
    this.loadRequests();
    this.loadEngineers();
  }

  onApplyFilters(): void {
    const statusIds =
      this.selectedStatusId !== null && this.selectedStatusId !== undefined
        ? [this.selectedStatusId]
        : [1, 2, 3, 4]; // статусы по умолчанию

    const newFilters: Partial<FilterParams> = {
      engineer_id: this.selectedEngineerId,
      status_ids: statusIds,
      start_date: this.startDate ? this.startDate + 'T00:00:00' : null,
      end_date: this.endDate ? this.endDate + 'T23:59:59' : null,
      page: 1,
    };

    this.applyFilters(newFilters);
  }

  loadRequests(): void {
    this.isLoading = true;
    this.managerService.fetchRequests(this.filters).subscribe({
      next: (response) => {
        const prev = this.managerService.getStoredRequests();
        const combined = [...prev, ...response.requests];
        this.managerService.updateRequests(combined);
        this.totalRequests = response.total;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  loadMore(): void {
    this.filters.page++;
    this.loadRequests();
  }

  resetRequests(): void {
    this.managerService.updateRequests([]);
    this.filters.page = 1;
  }

  applyFilters(newFilters: Partial<FilterParams>): void {
    this.resetRequests();
    this.filters = { ...this.filters, ...newFilters };
    this.loadRequests();
  }

  toggleDetails(requestId: number): void {
    this.openedDetailsId =
      this.openedDetailsId === requestId ? null : requestId;
  }

  startEditing(request: any): void {
    this.editingRequestId = request.request_id;
    this.editableRequest = { ...request };
  }

  cancelEdit(): void {
    this.editingRequestId = null;
    this.editableRequest = null;
  }

  saveEdit(): void {
    if (!this.editableRequest) return;

    const updatedFields = {
      customer_name: this.editableRequest.customer_name,
      techniq: this.editableRequest.equipment,
      adress: this.editableRequest.address,
      phone: this.editableRequest.phone,
      description: this.editableRequest.description,

      // Новые поля
      status_id: Number(this.editableRequest.status_id),

      creation_date: this.editableRequest.creation_date,
      assigned_time: this.editableRequest.assigned_time,
      in_works_time: this.editableRequest.in_works_time,
      done_time: this.editableRequest.done_time,
    };

    this.managerService
      .updateRequest(this.editableRequest.request_id, updatedFields)
      .subscribe({
        next: () => {
          const requests = this.managerService.getStoredRequests();
          const index = requests.findIndex(
            (r) => r.request_id === this.editableRequest.request_id
          );

          if (index !== -1) {
            requests[index] = {
              ...requests[index],
              ...updatedFields,

              // для отображения
              equipment: updatedFields.techniq,
              address: updatedFields.adress,
            };
            this.managerService.updateRequests(requests);
          }

          this.cancelEdit();
        },
        error: (err) => {
          console.error('Ошибка при сохранении заявки:', err);
        },
      });
  }

  loadEngineers(): void {
    this.managerService.getAllEngineers().subscribe((engineers) => {
      this.allEngineers = engineers;
    });
  }

  assignEngineerToRequest(request: any, engineer: any): void {
    const payload = {
      engineer_id: engineer.user_id,
      status_id: 2,
    };

    this.managerService.updateRequest(request.request_id, payload).subscribe({
      next: () => {
        request.engineer_id = engineer.user_id;
        request.engineer_name = engineer.engineer_name;
        request.status_id = 2;
      },
      error: (err) => {
        console.error('Ошибка при назначении инженера:', err);
      },
    });
  }

  getEngineerById(id: string): any {
    return this.allEngineers.find((e) => e.user_id.toString() === id);
  }

  onEngineerChange(event: Event, request: any): void {
    const select = event.target as HTMLSelectElement;
    const selectedEngineer = this.getEngineerById(select.value);
    if (selectedEngineer) {
      this.assignEngineerToRequest(request, selectedEngineer);
    }
  }

  toggleHistory(requestId: number): void {
    if (this.openedHistoryId === requestId) {
      this.openedHistoryId = null;
      return;
    }

    // Если история уже загружена
    if (this.historyMap[requestId]) {
      this.openedHistoryId = requestId;
      return;
    }

    this.loadingHistoryId = requestId;

    this.managerService.getRequestHistory(requestId).subscribe((response) => {
      this.historyMap[requestId] = response.history;
      this.openedHistoryId = requestId;
      this.loadingHistoryId = null;
    });
  }

  formatDate(dateStr: string | null | undefined): string {
    if (!dateStr) return ''; // ничего не возвращаем, если null или undefined

    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return ''; // некорректная дата

    return date.toLocaleString('ru-RU', {
      timeZone: 'UTC',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  getReadableFieldName(field: string): string {
    const fieldNames: Record<string, string> = {
      techniq: 'Оборудования',
      status_id: 'Статуса',
      request_id: 'ID заявки',
      customer_name: 'Имя клиента',
      adress: 'Адреса',
      phone: 'Телефона',
      description: 'Описания',
      creation_date: 'Дата создания',
      assigned_time: 'Дата назначения',
      in_works_time: 'Начало работы',
      done_time: 'Завершено',
      engineer_id: 'Инженера',
    };
    return fieldNames[field] || field;
  }

  deleteRequest(requestId: number): void {
    this.managerService.deleteRequest(requestId).subscribe((response) => {
      if (response && response.new_status === 'deleted') {
        // Удаляем заявку из локального списка
        const requests = this.managerService
          .getStoredRequests()
          .filter((r) => r.request_id !== requestId);
        this.managerService.updateRequests(requests);

        // Если открыты детали этой заявки — закрываем
        if (this.openedDetailsId === requestId) {
          this.openedDetailsId = null;
        }
      } else {
      }
    });
  }
}
