import { Component, NgZone, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})

export class Chat {
  userMessage = '';
  messages: { sender: 'user'|'bot', text: string }[] = [];
  streamingAnswer = '';
  loading = false;

  constructor(private chatService: ChatService, private ngZone: NgZone, private router: Router, private cdr: ChangeDetectorRef) {}

  goHome() {
    this.router.navigate(['/']);
  }

  sendMessage() {
    const text = this.userMessage?.trim();
    if (!text) return;

    // push user message
    this.messages.push({ sender: 'user', text });
    this.loading = true;
    this.streamingAnswer = '';

    // subscribe to SSE
    this.chatService.sendMessage(text).subscribe({
      next: (event) => {
        if (event.type === 'token') {
          // update streaming fragment
          this.ngZone.run(() => {
            this.streamingAnswer += event.data.text;
            this.cdr.detectChanges();  // 👈 force refresh UI
          });
        } else if (event.type === 'full') {
          this.ngZone.run(() => {
            this.messages.push({ sender: 'bot', text: event.data.answer });
            this.streamingAnswer = '';
            this.loading = false;
            this.cdr.detectChanges();  // 👈 force refresh UI
          });
        }
      },
      error: (err) => {
        console.error('SSE error', err);
        this.ngZone.run(() => {
          this.messages.push({ sender: 'bot', text: 'Erreur de connexion au serveur.' });
          this.loading = false;
          this.streamingAnswer = '';
          this.cdr.detectChanges();  // 👈 force refresh UI
        });
      },
      complete: () => {
        // if no explicit full event was sent, commit streamingAnswer
        if (this.streamingAnswer) {
          this.ngZone.run(() => {
            this.messages.push({ sender: 'bot', text: this.streamingAnswer });
            this.streamingAnswer = '';
            this.loading = false;
            this.cdr.detectChanges();  // 👈 force refresh UI
          });
        }
      }
    });

    this.userMessage = '';
  }

}
