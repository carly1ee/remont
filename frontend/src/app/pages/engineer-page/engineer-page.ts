import {
  AfterViewInit,
  Component,
  ElementRef,
  OnInit,
  ViewChild,
} from '@angular/core';
import { Navigation } from '../../components/navigation/navigation';
import { EngineerService } from '../../services/engineer.service';
import { CommonModule } from '@angular/common';

interface EngineerRequest {
  address: string;
  assigned_time: string;
  creation_date: string;
  customer_name: string;
  description: string;
  done_time: string | null;
  engineer_id: number;
  equipment: string;
  in_works_time: string | null;
  operator_id: number;
  phone: string;
  request_id: number;
  status_id: number;
}

@Component({
  selector: 'app-engineer-page',
  imports: [Navigation, CommonModule],
  templateUrl: './engineer-page.html',
  styleUrl: './engineer-page.scss',
})
export class EngineerPage implements OnInit {
  @ViewChild('calendarScroll') calendarScrollRef!: ElementRef;

  requests: EngineerRequest[] = [];
  expandedRequestId: number | null = null;
  days: { date: Date; weekDay: string }[] = [];
  selectedDate: Date = new Date();
  expandedEventId: number | null = null;

  expandedCompletedRequestId: number | null = null;
  completedRequests: EngineerRequest[] = [];
  completedPage = 1;
  completedTotal = 0;
  isLoadingCompleted = false;

  events: EngineerRequest[] = [];

  engineerId: number = 0;
  activeRequests: number = 0;
  completedThisMonth: number = 0;
  balance: string = '0';
  perPage = 10;

  constructor(private engineerService: EngineerService) {}

  ngOnInit(): void {
    this.requests = [];

    this.events = [...this.requests];

    this.fetchEngineerIdAndStats();

    this.engineerService.getEngineerActive().subscribe({
      next: (response) => {
        this.requests = response.requests;
        this.events = [...response.requests];
        console.log('Заявки инженера:', response);
      },
      error: (error) => {
        console.error('Ошибка при загрузке заявок:', error);
      },
    });

    this.days = this.generateDaysWithPast(7, 14);
    this.loadCompletedRequests();

    const myEngineerId = Number(localStorage.getItem('user_id'));

    this.engineerService.getEngineerStats(1, 20).subscribe({
      next: (response) => {
        const currentEngineer = response.engineers.find(
          (eng: any) => eng.user_id === myEngineerId
        );

        if (currentEngineer) {
          this.activeRequests = currentEngineer.active_requests;
          this.completedThisMonth = currentEngineer.completed_in_month;
          this.balance = currentEngineer.balance;
        }
      },
      error: (error) => {
        console.error('Ошибка при получении статистики инженера:', error);
      },
    });
  }

  toggleDetails(id: number): void {
    this.expandedRequestId = this.expandedRequestId === id ? null : id;
  }

  markInProgress(request: EngineerRequest): void {
    const now = this.getLocalISOString();
    request.status_id = 3;
    request.in_works_time = now;

    this.engineerService
      .updateRequestTimes(request.request_id, {
        in_works_time: now,
        status_id: 3,
      })
      .subscribe({
        next: () => console.log('Отправлено: начало работ', now),
        error: (error) => console.error('Ошибка при обновлении:', error),
      });
  }

  markDone(request: EngineerRequest): void {
    const now = this.getLocalISOString();
    request.status_id = 4;
    request.done_time = now;

    this.engineerService
      .updateRequestTimes(request.request_id, {
        done_time: now,
        status_id: 4,
      })
      .subscribe({
        next: () => console.log('Отправлено: завершение работ', now),
        error: (error) => console.error('Ошибка при обновлении:', error),
      });
  }

  private getLocalISOString(): string {
    const now = new Date();
    const offsetMs = now.getTimezoneOffset() * 60 * 1000;
    const localTime = new Date(now.getTime() - offsetMs);
    return localTime.toISOString().slice(0, 19); // YYYY-MM-DDTHH:mm:ss
  }

  ngAfterViewInit() {
    setTimeout(() => {
      const scrollContainer = this.calendarScrollRef
        .nativeElement as HTMLElement;
      const todayEl = document.getElementById('today');

      if (todayEl && scrollContainer) {
        const gap = 12; // отступ между днями в px, подстрой под свой CSS
        const scrollLeft =
          todayEl.offsetLeft -
          scrollContainer.offsetLeft -
          (todayEl.offsetWidth + gap);

        // Чтобы не получить отрицательное значение
        const finalScrollLeft = scrollLeft > 0 ? scrollLeft : 0;

        scrollContainer.scrollTo({
          left: finalScrollLeft,
          behavior: 'smooth',
        });
      }
    }, 0);
  }

  generateDaysWithPast(past: number, future: number) {
    const result = [];
    const today = new Date();

    for (let i = -past; i <= future; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);

      result.push({
        date,
        weekDay: this.getWeekDayName(date.getDay()),
      });
    }

    return result;
  }

  getWeekDayName(dayIndex: number): string {
    const names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    return names[(dayIndex + 6) % 7];
  }

  isToday(date: Date): boolean {
    const now = new Date();
    return (
      date.getDate() === now.getDate() &&
      date.getMonth() === now.getMonth() &&
      date.getFullYear() === now.getFullYear()
    );
  }

  isSameDay(date1: Date, date2: Date): boolean {
    return (
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate()
    );
  }

  get eventsForSelectedDay() {
    return this.events.filter((event) =>
      this.isSameDay(new Date(event.assigned_time), this.selectedDate)
    );
  }

  onSelectDay(dayDate: Date) {
    this.selectedDate = dayDate;

    const formattedDate = dayDate.toISOString().split('T')[0]; // YYYY-MM-DD
    console.log('отправляю данные', formattedDate);

    this.engineerService.getEngineerRequests(formattedDate).subscribe({
      next: (response) => {
        this.events = [...response.requests];
        console.log('Заявки на выбранный день:', this.events);
      },
      error: (error) => {
        console.error('Ошибка при загрузке заявок на дату:', error);
      },
    });
  }

  toggleEventDetails(id: number): void {
    this.expandedEventId = this.expandedEventId === id ? null : id;
  }

  loadCompletedRequests(): void {
    if (this.isLoadingCompleted) return;

    this.isLoadingCompleted = true;

    this.engineerService.getCompletedRequests(this.completedPage).subscribe({
      next: (response) => {
        this.completedRequests.push(...response.requests);
        this.completedPage++;
        this.completedTotal = response.total;

        this.isLoadingCompleted = false;
      },
      error: (error) => {
        console.error('Ошибка при загрузке выполненных заявок:', error);
        this.isLoadingCompleted = false;
      },
    });
  }

  toggleCompletedDetails(id: number): void {
    this.expandedCompletedRequestId =
      this.expandedCompletedRequestId === id ? null : id;
  }

  private fetchEngineerIdAndStats(): void {
    this.engineerService.getEngineerActive().subscribe({
      next: (response) => {
        this.engineerId = Number(response.engineer_id);
        this.loadEngineerStats();
      },
      error: (err) => {
        console.error('Ошибка при получении engineer_id:', err);
      },
    });
  }

  private loadEngineerStats(page = 1): void {
    this.engineerService.getEngineerStats(page, this.perPage).subscribe({
      next: (response) => {
        const engineers = response.engineers || [];

        const match = engineers.find((e: any) => e.user_id === this.engineerId);

        if (match) {
          this.activeRequests = match.active_requests;
          this.completedThisMonth = match.completed_in_month;
          this.balance = match.balance;
        } else if (engineers.length === this.perPage) {
          // Пробуем следующую страницу
          this.loadEngineerStats(page + 1);
        } else {
          // Не найден, устанавливаем нули (по умолчанию уже 0)
          console.warn('Инженер не найден в списке статистики');
        }
      },
      error: (err) => {
        console.error('Ошибка при загрузке статистики:', err);
      },
    });
  }
}
