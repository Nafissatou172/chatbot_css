import { Component, signal } from '@angular/core';
import { RouterLink, RouterModule, RouterOutlet } from '@angular/router';
import { Chat} from './chat/chat/chat'; // chemin à adapter


@Component({
  selector: 'app-root', 
  standalone : true,
  imports: [RouterOutlet, Chat, RouterLink, RouterModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
