import { Component } from '@angular/core';
import { Navigation } from '../../components/navigation/navigation';
import { Application } from '../../components/application/application';
import { Requests } from '../../components/requests/requests';

@Component({
  selector: 'app-operator-page',
  imports: [Navigation, Application, Requests],
  templateUrl: './operator-page.html',
  styleUrl: './operator-page.scss',
})
export class OperatorPage {}
