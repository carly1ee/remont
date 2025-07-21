import { Component } from '@angular/core';
import { Navigation } from '../../components/navigation/navigation';
import { Requests } from '../../components/requests/requests';
import { Application } from '../../components/application/application';
import { Profile } from '../../components/profile/profile';

@Component({
  selector: 'app-manager-page',
  imports: [Navigation, Requests, Application, Profile],
  templateUrl: './manager-page.html',
  styleUrl: './manager-page.scss',
})
export class ManagerPage {}
