import { Routes } from '@angular/router';
import { Chat } from './chat/chat/chat';
import { Home } from './home/home';
import { App } from './app';

export const routes: Routes = [
  { path: 'chat', component: Chat },
  //{ path: '', component: App },
  { path: '', component: Home },
  { path: '**', redirectTo: '' }
];
